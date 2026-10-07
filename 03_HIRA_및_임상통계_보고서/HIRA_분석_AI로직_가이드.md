# 심사평가원(HIRA) 청구 DB 기반 의료 적정성 분석 — AI 수행 로직 가이드

> **분석 파이프라인**: 현황 파악(회귀) → 기관 분류(DEA) → 균형 예측(Nash) → 시나리오(Monte Carlo) → 효과 검증(DID)

---

## 목차

1. [데이터 구조 및 전처리](#1-데이터-구조-및-전처리)
2. [STEP 1 — 현황 파악: 패널 회귀분석](#2-step-1--현황-파악-패널-회귀분석)
3. [STEP 2 — 기관 분류: DEA 효율성 분석](#3-step-2--기관-분류-dea-효율성-분석)
4. [STEP 3 — 균형 예측: Nash 균형 모형](#4-step-3--균형-예측-nash-균형-모형)
5. [STEP 4 — 시나리오: Monte Carlo 시뮬레이션](#5-step-4--시나리오-monte-carlo-시뮬레이션)
6. [STEP 5 — 효과 검증: 이중차분(DID)](#6-step-5--효과-검증-이중차분did)
7. [통합 파이프라인 실행 흐름](#7-통합-파이프라인-실행-흐름)
8. [AI 수행 체크리스트](#8-ai-수행-체크리스트)

---

## 1. 데이터 구조 및 전처리

### 1.1 HIRA 청구 DB 주요 테이블

```
TB_CLAIM_HEADER   : 청구 헤더 (기관코드, 진료년월, 청구금액, 진료과, 입/외래 구분)
TB_CLAIM_DETAIL   : 청구 명세 (행위코드, 약제코드, 재료코드, 수량, 단가)
TB_INSTITUTION    : 요양기관 정보 (종별코드, 병상수, 개설지역, 설립구분)
TB_PATIENT        : 환자 정보 (성별, 연령, 보험종별, 주상병코드 KCD)
TB_PRICE          : 수가 기준 (행위코드별 점수, 환산지수)
```

### 1.2 분석 단위 정의

| 분석 수준 | 단위 | 기간 |
|-----------|------|------|
| 기관별 분석 | 요양기관코드 × 진료년도 | 연도 패널 |
| 진료과별 분석 | 기관코드 × 표시과목코드 × 연도 | 연도 패널 |
| 환자 수준 | 환자ID × 에피소드 | 에피소드 기준 |

### 1.3 AI 전처리 로직

```python
# ── [AI TASK 1] 데이터 정합성 검증 ──────────────────────────────────
def validate_data(df_claim, df_inst):
    """
    수행 항목:
    1. 기관코드 누락 여부 확인 → 0.1% 초과 시 경고
    2. 청구금액 음수 값 제거 (취소청구 식별 후 상계)
    3. 극단값 탐지: IQR × 3 초과 기관 플래그 처리 (삭제 아님)
    4. 종별코드 표준화 (01=상급종합, 11=종합병원, 21=병원, 31=의원)
    5. 주상병 KCD 7단위 → 3단위 그룹 축약
    """
    checks = {
        "missing_inst_code": df_claim["기관코드"].isna().mean(),
        "negative_amount": (df_claim["청구금액"] < 0).sum(),
        "outlier_flag": detect_outliers(df_claim, "기관별_연간청구액", method="IQR", k=3),
    }
    return checks

# ── [AI TASK 2] 분석용 패널 데이터 생성 ─────────────────────────────
def build_panel(df_claim, df_inst, df_patient):
    """
    요양기관 × 연도 패널 생성
    산출 변수:
      - total_cost    : 연간 총 청구액
      - visit_count   : 연간 진료건수
      - cost_per_visit: 건당 진료비 (= total_cost / visit_count)
      - bed_count     : 병상수 (TB_INSTITUTION 조인)
      - specialty_mix : 진료과별 건수 비율 벡터
      - case_mix_index: DRG 기반 환자 중증도 지수 (CMI)
      - region_code   : 진료권역 (시도 → 70개 진료권 매핑)
    """
    panel = (
        df_claim
        .merge(df_inst, on="기관코드")
        .merge(df_patient.groupby(["기관코드","연도"]).agg(CMI=("중증도점수","mean")), ...)
        .groupby(["기관코드","연도"])
        .agg(...)
    )
    return panel
```

---

## 2. STEP 1 — 현황 파악: 패널 회귀분석

### 2.1 분석 목적

- 기관 특성(병상수·종별·지역·진료과 구성)이 비용에 미치는 영향 계수 추정
- 환자 중증도(CMI) 보정 후 **기대비용 대비 실제비용 잔차** 산출 → 과다·과소 청구 기관 식별

### 2.2 모형 명세

```
log(cost_per_visit_it) = α_i + β₁·log(bed_it) + β₂·CMI_it
                        + β₃·specialty_mix_it + β₄·region_i
                        + β₅·year_t + ε_it

  i = 기관, t = 연도
  α_i = 기관 고정효과 (FE) — 관찰 불가 기관 특성 통제
  CMI = Case Mix Index (환자 중증도)
```

### 2.3 AI 수행 로직

```python
# ── [AI TASK 3] 고정효과 패널 회귀 ──────────────────────────────────
def run_panel_regression(panel_df):
    """
    라이브러리: linearmodels (Python) 또는 plm (R)

    수행 절차:
    1. Hausman 검정으로 FE vs RE 선택
       - p < 0.05 → 고정효과(FE) 채택
       - p ≥ 0.05 → 랜덤효과(RE) 고려
    2. 이분산 robust 표준오차 (Driscoll-Kraay) 적용
    3. 잔차 ε_it 저장 → 다음 단계 DEA 인풋으로 활용
    4. 종속변수 정규성 검정 (Jarque-Bera), 자기상관 검정 (Wooldridge)
    """
    from linearmodels import PanelOLS
    model = PanelOLS.from_formula(
        "log_cost_per_visit ~ log_bed + CMI + year_dummy + EntityEffects",
        data=panel_df.set_index(["기관코드","연도"])
    )
    result = model.fit(cov_type="driscoll-kraay")

    # 잔차 = 실제 - 예측: 양수면 고비용 기관
    panel_df["residual"] = result.resids
    panel_df["high_cost_flag"] = panel_df["residual"] > panel_df["residual"].quantile(0.75)

    return result, panel_df

# ── [AI TASK 4] 진료과별 세부 분석 ──────────────────────────────────
def specialty_regression(panel_df, specialty_code):
    """
    내과·외과·정형외과 등 진료과별로 동일 모형 반복 수행
    각 진료과의 건당 비용 결정요인 계수 비교 테이블 생성
    """
    results = {}
    for sp in panel_df["표시과목코드"].unique():
        subset = panel_df[panel_df["표시과목코드"] == sp]
        results[sp] = run_panel_regression(subset)
    return results
```

### 2.4 출력물

| 항목 | 내용 |
|------|------|
| 회귀계수 표 | 변수별 계수·표준오차·p값·95%CI |
| 잔차 분포도 | 기관별 고비용/저비용 분류 히스토그램 |
| 종별·진료과별 계수 비교 표 | 상급종합 vs 의원 건당 비용 격차 |

---

## 3. STEP 2 — 기관 분류: DEA 효율성 분석

### 3.1 분석 목적

회귀 잔차가 높은 기관이 실제로 **비효율적**인지, 아니면 고비용 고품질인지 구분합니다. DEA는 투입-산출 비율의 효율 프론티어를 구성해 상대적 효율 점수(0~1)를 부여합니다.

### 3.2 투입-산출 변수 정의

```
[투입 변수]
  X₁ = 연간 총 청구액 (비용 투입)
  X₂ = 의사 수 (인력 투입)
  X₃ = 병상 수 (자본 투입)

[산출 변수]
  Y₁ = 조정 진료건수 (= 진료건수 × CMI)  — 중증도 보정 산출량
  Y₂ = 재입원율 역수 (= 1 - 30일 재입원율) — 질 산출량
  Y₃ = 환자만족도 점수 (있는 경우)
```

### 3.3 AI 수행 로직

```python
# ── [AI TASK 5] DEA 효율성 점수 산출 ────────────────────────────────
def run_dea(panel_df, orientation="input", returns="VRS"):
    """
    라이브러리: pyDEA 또는 Deap (Python), Benchmarking (R)

    orientation:
      "input"  → 동일 산출 달성 시 투입 최소화 관점 (비용 절감 목표)
      "output" → 동일 투입으로 산출 최대화 관점 (서비스 확대 목표)

    returns:
      "CRS" → 규모수익불변 (소규모 기관 불리할 수 있음)
      "VRS" → 규모수익가변 (권장: 기관 규모 차이 통제)

    수행 절차:
    1. 투입·산출 행렬 정규화 (min-max 또는 z-score)
    2. 선형계획 풀이 → 기관별 효율점수 θ_i ∈ (0, 1]
    3. θ < 1 기관의 slack 변수 분석 → 어떤 투입이 과다한지 파악
    4. 규모효율성 = CRS 점수 / VRS 점수 → 최적규모 여부 판단
    5. Malmquist 지수: 연도 간 생산성 변화 = 기술변화 × 효율변화
    """
    from pyDEA import DEA_Model
    inputs  = panel_df[["총청구액","의사수","병상수"]].values
    outputs = panel_df[["조정진료건수","재입원역수"]].values

    model = DEA_Model(inputs, outputs, orientation=orientation, rts=returns)
    scores = model.solve()
    panel_df["DEA_score"] = scores
    panel_df["efficiency_tier"] = pd.cut(
        scores,
        bins=[0, 0.6, 0.8, 0.95, 1.0],
        labels=["하위", "중하위", "중상위", "효율"]
    )
    return panel_df

# ── [AI TASK 6] Tobit 2단계 — 효율성 결정요인 ───────────────────────
def tobit_stage2(panel_df):
    """
    DEA 점수가 1에서 상한 절단(censored)되므로 OLS 대신 Tobit 사용

    종속변수: DEA_score (0~1, 우상단 절단)
    독립변수: 소유형태(공공/민간), 지역(수도권/비수도권),
              설립연도, 진료과 집중도 HHI, 입원비율

    → 비효율성의 체계적 원인 파악
    """
    from statsmodels.regression.linear_model import Tobit
    result = Tobit(
        endog=panel_df["DEA_score"],
        exog=panel_df[["소유형태","수도권","HHI","입원비율"]],
        limit_upper=1.0
    ).fit()
    return result

# ── [AI TASK 7] 벤치마크 클러스터링 ────────────────────────────────
def cluster_institutions(panel_df):
    """
    DEA 점수 + 회귀 잔차 + 기관 특성 기반 K-means 클러스터링
    클러스터별 대표 벤치마크 기관 선정 → 개선 목표값 설정에 활용
    """
    from sklearn.cluster import KMeans
    features = panel_df[["DEA_score","residual","병상수","CMI"]].dropna()
    km = KMeans(n_clusters=5, random_state=42).fit(features)
    panel_df["cluster"] = km.labels_
    return panel_df
```

### 3.4 출력물

| 항목 | 내용 |
|------|------|
| DEA 점수 분포 | 기관별 효율 점수 분포 (산포도 + 히스토그램) |
| 효율 등급 매트릭스 | 종별 × 지역별 평균 DEA 점수 교차표 |
| Slack 분석 | 과다 투입 항목별 절감 가능액 추정 |
| 벤치마크 기관 목록 | 클러스터별 효율 상위 기관 명세 |

---

## 4. STEP 3 — 균형 예측: Nash 균형 모형

### 4.1 분석 목적

수가 변경·급여 정책 개편 시 **의사·병원·보험자**가 어떤 새로운 균형 상태로 이동하는지 예측합니다.

### 4.2 게임 구조 명세

```
플레이어 집합: N = {보험자, 병원_1, ..., 병원_K, 의사_1, ..., 의사_M}

보험자 전략: w ∈ [w_min, w_max]  (수가 수준)
병원 전략:   q_k ∈ [0, Q_max]    (진료량 — 쿠르노 경쟁)
의사 전략:   e_m ∈ {표준진료, 과잉진료}  (이산 전략)

보수함수:
  보험자: U_ins = -|재정수지| - α·(총진료량 - 적정량)²
  병원_k: U_k   = w·q_k - C_k(q_k) - β·(q_k - q̄)²
  의사_m: U_m   = fee(e_m) - d·e_m - γ·적발위험(e_m)

균형 조건 (순수전략 NE):
  ∂U_k/∂q_k = 0  →  q_k* = (w - c_k) / (2b_k + Σ_{j≠k} b_j)
  w* = MC_사회적 + (도덕적해이 보정)
```

### 4.3 AI 수행 로직

```python
# ── [AI TASK 8] 쿠르노 균형 수치 계산 ──────────────────────────────
def compute_cournot_nash(institutions_in_region, price_schedule):
    """
    동일 진료권 내 병원 간 쿠르노 경쟁 Nash 균형 반복 계산

    알고리즘: Best-Response Iteration (BRI)
      1. 모든 병원 초기 진료량 q_k = 0으로 설정
      2. 각 병원이 타 병원 진료량 고정 가정 하 최적 반응 계산
         BR_k(q_{-k}) = max(0, (w - c_k - b·Σq_{j≠k}) / (2b))
      3. 모든 병원이 동시에 업데이트 → 수렴까지 반복
      4. 수렴 조건: max|q_k^(t+1) - q_k^(t)| < 1e-6
      5. 균형 총 진료량 Q* = Σq_k* 및 균형 실효수가 계산
    """
    q = {k: 0 for k in institutions_in_region}
    w = price_schedule["수가"]
    b = 0.01  # 수요 기울기 (데이터로 추정)

    for iteration in range(10000):
        q_new = {}
        for k, inst in institutions_in_region.items():
            sum_others = sum(q[j] for j in q if j != k)
            q_new[k] = max(0, (w - inst["MC"] - b * sum_others) / (2 * b))
        if max(abs(q_new[k] - q[k]) for k in q) < 1e-6:
            break
        q = q_new

    return q  # Nash 균형 진료량 벡터

# ── [AI TASK 9] 보험자 최적 수가 도출 ──────────────────────────────
def optimal_insurer_price(panel_df, moral_hazard_param=0.1):
    """
    보험자의 사회적 최적 수가 = 사회적 한계비용 + 도덕적 해이 보정항

    w* = MC_social + λ·(수요탄력성 역수)
    λ = 도덕적해이 가중치 (추정 또는 문헌값)

    수가별 균형 진료량 Q*(w) 계산 → 재정수지 균형점 탐색:
      재정수지 = 보험료 수입 - w·Q*(w) = 0 조건 하 w* 도출
    """
    from scipy.optimize import brentq

    def budget_balance(w):
        Q_star = sum(compute_cournot_nash(get_region_insts(panel_df), {"수가": w}).values())
        revenue = panel_df["보험료수입"].sum()
        expenditure = w * Q_star
        return revenue - expenditure

    w_star = brentq(budget_balance, 50, 500)  # 수가 범위 내 이분탐색
    return w_star

# ── [AI TASK 10] 의사 전략 혼합전략 균형 ────────────────────────────
def physician_mixed_strategy(detection_prob, penalty, fee_excess):
    """
    의사의 혼합전략 균형 (과잉진료 vs 표준진료)
    
    기대 보수 균등화 조건:
      fee_standard = (1 - p)·fee_excess - p·penalty
      p* = (fee_excess - fee_standard) / (fee_excess + penalty)
    
    해석: p* = 적발 확률이 이 값보다 높으면 과잉진료 유인 소멸
    """
    fee_standard = 1.0  # 정규화
    p_star = (fee_excess - fee_standard) / (fee_excess + penalty)
    overtreatment_rate = 1 - detection_prob / p_star if detection_prob < p_star else 0
    return {"임계적발확률": p_star, "예상과잉진료율": overtreatment_rate}

# ── [AI TASK 11] 수가 변화 → 새 균형 이동 분석 ─────────────────────
def nash_comparative_statics(panel_df, price_change_pct_list):
    """
    수가를 [-20%, -10%, 0%, +10%, +20%] 로 변화시킬 때
    각 시나리오에서 Nash 균형 진료량·비용 계산
    → 수가탄력성 곡선 도출
    """
    results = []
    base_price = panel_df["평균수가"].mean()
    for delta in price_change_pct_list:
        w_new = base_price * (1 + delta / 100)
        Q_star = compute_total_equilibrium(panel_df, w_new)
        total_cost = w_new * Q_star
        results.append({"수가변화율": delta, "균형진료량": Q_star, "총비용": total_cost})
    return pd.DataFrame(results)
```

### 4.4 출력물

| 항목 | 내용 |
|------|------|
| 진료권별 Nash 균형 진료량 | 지역별 쿠르노 균형 산출 |
| 최적 수가 w* | 재정균형 조건 하 권장 수가 수준 |
| 임계 적발 확률 p* | 과잉진료 억제에 필요한 최소 심사 강도 |
| 수가-진료량 탄력성 표 | 수가 변화 시나리오별 균형 이동 |

---

## 5. STEP 4 — 시나리오: Monte Carlo 시뮬레이션

### 5.1 분석 목적

Nash 균형 예측값은 점 추정이므로, **파라미터 불확실성**과 **수요 변동성**을 반영해 정책 효과의 신뢰구간과 최악·최선 시나리오를 산출합니다.

### 5.2 불확실성 파라미터

```
θ ~ 분포 정의:
  수요탄력성 ε     ~ N(-0.3, 0.05²)       # 문헌 메타분석 값 활용
  한계비용 MC_k    ~ LogNormal(μ_k, σ_k²) # DEA 잔차로 추정
  도덕적해이 λ     ~ Uniform(0.05, 0.20)  # 전문가 범위 설정
  비용상승률 π     ~ N(CPI_의료, 0.01²)   # 통계청 의료서비스 CPI
  인구구조 변화     ~ 코호트 생명표 기반 확정적 경로
```

### 5.3 AI 수행 로직

```python
# ── [AI TASK 12] Monte Carlo 엔진 ───────────────────────────────────
import numpy as np

def monte_carlo_simulation(panel_df, policy_scenario, n_sim=10000):
    """
    수행 절차:
    1. 파라미터 사전분포에서 n_sim회 무작위 추출 (준무작위: Sobol 수열 권장)
    2. 각 추출값으로 Nash 균형 진료량 Q*(θ) 계산
    3. 정책 시나리오 적용 후 10년 누적 비용 계산
    4. 결과 분포에서 퍼센타일 추출 (P5, P25, P50, P75, P95)
    5. 민감도 분석: Sobol 지수 계산 → 결과에 가장 큰 영향 파라미터 식별
    """
    rng = np.random.default_rng(seed=42)
    results = []

    for sim in range(n_sim):
        # 파라미터 샘플링
        epsilon = rng.normal(-0.3, 0.05)        # 수요탄력성
        lambda_ = rng.uniform(0.05, 0.20)       # 도덕적해이 계수
        mc_shock = rng.lognormal(0, 0.1)        # 비용 충격

        # 정책 시나리오별 수가 설정
        w_policy = apply_policy(panel_df, policy_scenario, lambda_)

        # Nash 균형 진료량 계산
        Q_star = compute_equilibrium_quantity(w_policy, epsilon, mc_shock)

        # 10년 비용 경로 추적
        cost_path = project_costs(Q_star, w_policy, horizon=10)
        results.append({
            "총비용_10년": sum(cost_path),
            "연평균증가율": np.mean(np.diff(cost_path) / cost_path[:-1]),
            "5년차비용": cost_path[4],
        })

    df_sim = pd.DataFrame(results)
    summary = df_sim.quantile([0.05, 0.25, 0.50, 0.75, 0.95])
    return df_sim, summary

# ── [AI TASK 13] 정책 시나리오 정의 ────────────────────────────────
POLICY_SCENARIOS = {
    "BASE":      {"수가조정율": 0,     "심사강도": 1.0, "급여확대율": 0},
    "수가인하10": {"수가조정율": -0.10, "심사강도": 1.0, "급여확대율": 0},
    "심사강화":   {"수가조정율": 0,     "심사강도": 1.5, "급여확대율": 0},
    "급여확대":   {"수가조정율": 0,     "심사강도": 1.0, "급여확대율": 0.15},
    "패키지":    {"수가조정율": -0.05, "심사강도": 1.3, "급여확대율": 0.10},
}

def compare_scenarios(panel_df, n_sim=10000):
    """
    5개 시나리오 동시 실행 → 비용-편익 비교 매트릭스 생성
    각 시나리오: (중앙값 비용, 95% VaR, 재정균형 달성 확률) 보고
    """
    output = {}
    for name, scenario in POLICY_SCENARIOS.items():
        df_sim, summary = monte_carlo_simulation(panel_df, scenario, n_sim)
        output[name] = {
            "중앙값_10년비용": summary.loc[0.50, "총비용_10년"],
            "95th_VaR":        summary.loc[0.95, "총비용_10년"],
            "재정균형확률":    (df_sim["총비용_10년"] <= panel_df["보험료예상수입"].sum()).mean(),
        }
    return pd.DataFrame(output).T

# ── [AI TASK 14] Sobol 민감도 분석 ─────────────────────────────────
def sobol_sensitivity(panel_df, n_sim=2000):
    """
    SALib 라이브러리로 1차·총 Sobol 지수 계산
    → 어떤 파라미터의 불확실성이 결과 분산을 가장 크게 키우는지 식별
    → 정책 우선순위 결정에 활용
    """
    from SALib.sample import saltelli
    from SALib.analyze import sobol

    problem = {
        "num_vars": 4,
        "names": ["수요탄력성", "도덕적해이", "비용충격", "인구증가율"],
        "bounds": [[-0.5, -0.1], [0.05, 0.20], [0.8, 1.2], [0.98, 1.02]],
    }
    X = saltelli.sample(problem, n_sim)
    Y = np.array([run_model_for_sobol(row) for row in X])
    Si = sobol.analyze(problem, Y)
    return Si
```

### 5.4 출력물

| 항목 | 내용 |
|------|------|
| 시나리오별 비용 팬 차트 | P5~P95 범위 + 중앙값 경로 (10년) |
| 시나리오 비교 매트릭스 | 비용·재정균형확률·절감액 비교 |
| Sobol 민감도 막대그래프 | 파라미터별 결과 기여도 순위 |
| 최악 시나리오 프로파일 | P95 경우 발생 조건 분석 |

---

## 6. STEP 5 — 효과 검증: 이중차분(DID)

### 6.1 분석 목적

기존 제도 변화(과거 수가 개편, 심사 강화 등)가 실제로 진료량·비용에 미친 **인과적 효과**를 추정해 Monte Carlo 예측의 파라미터를 보정합니다.

### 6.2 설계 조건

```
처치: 특정 수가 개편 또는 심사 기준 변경 (예: 2019년 문재인 케어 단계적 급여화)
처치군: 해당 항목 다빈도 청구 기관
대조군: 해당 항목 청구 비중 낮은 유사 기관
시점: 개편 전 3년 / 개편 후 3년 (최소 6년 패널 필요)

평행 추세 가정 검증:
  → 처치 전 기간: 처치군·대조군의 결과변수 추세가 평행한지 확인
  → Event-Study 그래프로 시각화 (계수가 처치 이전에 0에 가까워야)
```

### 6.3 AI 수행 로직

```python
# ── [AI TASK 15] 처치-대조군 매칭 (PSM) ────────────────────────────
def propensity_score_matching(panel_df, treatment_col):
    """
    PSM으로 처치·대조군 사전 균형화
    매칭 변수: 병상수, CMI, 지역, 종별코드, 처치 이전 비용 추세
    방법: 1:1 최근접 이웃 매칭 (caliper = 0.01)
    균형 검증: SMD (표준화평균차) < 0.1 요건 확인
    """
    from causalinference import CausalModel
    X = panel_df[["log_bed","CMI","수도권","종별코드","사전비용추세"]].values
    T = panel_df[treatment_col].values
    Y = panel_df["log_cost_per_visit"].values
    model = CausalModel(Y, T, X)
    model.est_via_matching(matches=1, bias_adj=True)
    return model

# ── [AI TASK 16] 이중차분 추정 ─────────────────────────────────────
def run_did(panel_df, event_year, outcome="log_cost_per_visit"):
    """
    모형:
      Y_it = α + β₁·Post_t + β₂·Treat_i + δ·(Post_t × Treat_i)
           + X_it'γ + α_i + τ_t + ε_it

      δ = DID 추정량 = 처치 효과 (주요 관심 계수)

    확장 (Event-Study):
      Y_it = α_i + Σ_{k=-3}^{+3} δ_k·(Treat_i × 1[t = event+k]) + X_it'γ + ε_it

      δ_k 플롯 → 선제 효과(pre-trend) 부재, 사후 효과 지속성 확인
    """
    panel_df["Post"] = (panel_df["연도"] >= event_year).astype(int)
    panel_df["DiD_term"] = panel_df["Post"] * panel_df["Treat"]

    from linearmodels import PanelOLS
    formula = f"{outcome} ~ Post + DiD_term + log_bed + CMI + EntityEffects + TimeEffects"
    result = PanelOLS.from_formula(formula, data=panel_df.set_index(["기관코드","연도"])).fit()

    # Event-Study 계수 추출
    event_study = run_event_study(panel_df, event_year, outcome, lags=3, leads=3)

    return result, event_study

# ── [AI TASK 17] 평행 추세 검증 ────────────────────────────────────
def test_parallel_trends(panel_df, event_year, outcome):
    """
    처치 전 기간만 사용해 가상 처치 시점(Placebo) DID 수행
    → 유의한 사전 효과 없으면 평행 추세 가정 지지
    조건: p > 0.10 인 경우 통과 판정
    """
    pre_period = panel_df[panel_df["연도"] < event_year].copy()
    placebo_year = event_year - 2
    _, event_pre = run_did(pre_period, placebo_year, outcome)
    pre_coeffs = [c for k, c in event_pre.items() if k < 0]
    all_insignificant = all(abs(c["t_stat"]) < 1.645 for c in pre_coeffs)
    return {"평행추세_통과": all_insignificant, "사전계수": pre_coeffs}

# ── [AI TASK 18] 추정 결과 → 파라미터 역보정 ─────────────────────
def update_mc_params(mc_params, did_result):
    """
    DID 추정된 실제 탄력성으로 Monte Carlo 사전분포 업데이트 (Bayesian 갱신)
    δ_DID → 수가 탄력성 사후분포 평균 갱신
    → STEP 4 Monte Carlo 재실행 시 보다 좁은 신뢰구간 확보
    """
    delta = did_result.params["DiD_term"]
    se    = did_result.std_errors["DiD_term"]
    prior_mean, prior_var = mc_params["수요탄력성"]
    likelihood_prec = 1 / se**2
    prior_prec = 1 / prior_var
    posterior_mean = (prior_prec * prior_mean + likelihood_prec * delta) / (prior_prec + likelihood_prec)
    posterior_var  = 1 / (prior_prec + likelihood_prec)
    mc_params["수요탄력성"] = (posterior_mean, posterior_var)
    return mc_params
```

### 6.4 출력물

| 항목 | 내용 |
|------|------|
| DID 계수 δ 및 신뢰구간 | 처치 효과의 크기와 유의성 |
| Event-Study 그래프 | 처치 전후 계수 경로 (평행추세 확인) |
| 갱신된 MC 파라미터 | Bayesian 업데이트된 탄력성 분포 |
| 정책 효과 절감액 환산 | δ 계수를 비용 절감액(억 원)으로 환산 |

---

## 7. 통합 파이프라인 실행 흐름

```python
# ── 전체 파이프라인 오케스트레이션 ───────────────────────────────────
def run_full_pipeline(
    raw_claim_path: str,
    raw_inst_path: str,
    policy_event_year: int,
    scenarios: dict = POLICY_SCENARIOS,
    n_sim: int = 10000,
):
    # ── 0. 데이터 로드 및 전처리
    df_claim = load_and_validate(raw_claim_path)      # TASK 1
    panel_df = build_panel(df_claim, raw_inst_path)   # TASK 2

    # ── STEP 1: 패널 회귀
    reg_result, panel_df = run_panel_regression(panel_df)    # TASK 3
    specialty_results    = specialty_regression(panel_df)    # TASK 4

    # ── STEP 2: DEA 효율성 분석
    panel_df = run_dea(panel_df)                             # TASK 5
    tobit_result = tobit_stage2(panel_df)                    # TASK 6
    panel_df = cluster_institutions(panel_df)                # TASK 7

    # ── STEP 3: Nash 균형 예측
    nash_results = nash_comparative_statics(panel_df, [-20,-10,0,10,20])  # TASK 11
    w_star = optimal_insurer_price(panel_df)                 # TASK 9
    physician_eq = physician_mixed_strategy(
        detection_prob=0.15, penalty=500, fee_excess=1.3)    # TASK 10

    # ── STEP 4: Monte Carlo 시뮬레이션
    scenario_comparison = compare_scenarios(panel_df, n_sim) # TASK 13
    sobol_result = sobol_sensitivity(panel_df)               # TASK 14

    # ── STEP 5: DID 효과 검증
    parallel_test = test_parallel_trends(panel_df, policy_event_year, "log_cost_per_visit")
    did_result, event_study = run_did(panel_df, policy_event_year)        # TASK 16
    mc_params_updated = update_mc_params(DEFAULT_MC_PARAMS, did_result)   # TASK 18

    # ── 최종 보고서 생성
    report = generate_report(
        reg=reg_result,
        dea=panel_df[["기관코드","DEA_score","efficiency_tier","cluster"]],
        nash={"nash_results": nash_results, "w_star": w_star, "physician": physician_eq},
        mc=scenario_comparison,
        did={"result": did_result, "event_study": event_study},
        updated_params=mc_params_updated,
    )
    return report
```

---

## 8. AI 수행 체크리스트

### STEP별 완료 기준

```
[ ] STEP 0 — 전처리
    □ 청구 누락률 < 0.1%
    □ 음수 청구액 정리 완료
    □ 극단값 플래그 처리 (삭제 아님)
    □ 패널 균형성 확인 (attrition rate < 5%)

[ ] STEP 1 — 회귀
    □ Hausman 검정으로 FE/RE 선택 근거 확인
    □ 잔차 정규성 및 이분산 진단 통과
    □ 진료과별 계수 부호 방향 타당성 확인

[ ] STEP 2 — DEA
    □ 투입·산출 변수 방향성 확인 (투입 ↑ → 비효율)
    □ CRS vs VRS 규모효율성 분해 완료
    □ Tobit 2단계 잔차 정규성 확인
    □ 클러스터 실루엣 점수 > 0.4

[ ] STEP 3 — Nash
    □ BRI 수렴 확인 (반복 < 1,000회)
    □ 균형 유일성 검증 (다중 초기값 테스트)
    □ 재정균형 조건 w* 존재성 확인
    □ 의사 혼합전략 p* 범위 타당성 (0 < p* < 1)

[ ] STEP 4 — Monte Carlo
    □ n_sim ≥ 10,000 (수렴 확인: n=5,000 vs 10,000 결과 비교)
    □ Sobol 지수 합계 ≈ 1.0 검증
    □ 시나리오 도미넌스 확인 (패키지안이 재정균형 + 비용 절감 우월)

[ ] STEP 5 — DID
    □ PSM 균형 후 SMD < 0.1
    □ 평행 추세 검정 통과 (사전 계수 p > 0.10)
    □ Placebo 연도 테스트 무유의성 확인
    □ MC 파라미터 Bayesian 업데이트 반영
```

### 필요 Python 라이브러리

```
pandas, numpy, scipy         # 데이터 처리
linearmodels                 # 패널 회귀 (FE/RE/Tobit)
pyDEA 또는 pydea-research    # DEA 효율성 분석
sklearn                      # K-means 클러스터링, PSM
SALib                        # Sobol 민감도 분석
causalinference 또는 econml  # PSM, DID
matplotlib, seaborn, plotly  # 시각화
statsmodels                  # GLM, 진단검정
```

### 데이터 보안 주의사항

> HIRA 청구 DB는 개인정보보호법 및 의료법상 민감정보를 포함합니다.
> - 환자 ID는 분석 전 **가명처리** (SHA-256 해시 또는 HIRA 제공 가명ID 사용)
> - 분석 서버는 폐쇄망 또는 HIRA 빅데이터 분석 전용 시스템 내에서만 운용
> - 기관 수준 집계 결과만 외부 반출 (개별 환자 데이터 반출 금지)
> - 소수 기관 식별 가능 셀 (n < 5) k-익명성 처리 후 공개

---

*작성 기준: 2026년 9월 | 심사평가원 청구 DB 기반 의료 적정성 분석 AI 로직 가이드*
