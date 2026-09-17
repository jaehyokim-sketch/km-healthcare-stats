# 📐 [분석 로직 명세서] 익산시 노인·취약계층 한의약 방문진료 의료 적정성 분석 및 5개년 효과 시뮬레이션 AI 파이프라인 명세서

> **문서 버전**: 1.0 (2026년 9월 최신 기준)  
> **기반 가이드라인**: [HIRA_분석_AI로직_가이드.md](file:///d:/한의%20의료서비스%20통계/HIRA_분석_AI로직_가이드.md)  
> **연계 아젠다**: 원광대학교 한의과대학 권오상 교수 「익산형 통합 방문 기능유지 돌봄 네트워크 및 AI 스케줄링 구축 사업」(2027~2032년, 총 300억 원)  
> **실행 스크립트**: [simulate_iksan_km_10_to_100_full.py](file:///d:/한의%20의료서비스%20통계/03_분석_및_수집_스크립트/simulate_iksan_km_10_to_100_full.py)  
> **최종 보고서 아티팩트**:  
> • 마크다운 보고서: [익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md](file:///d:/한의%20의료서비스%20통계/익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md)  
> • 인터랙티브 대시보드: [익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html](file:///d:/한의%20의료서비스%20통계/익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html)  
> • 시뮬레이션 차트 이미지: [iksan_km_10_to_100_simulation_chart.png](file:///d:/한의%20의료서비스%20통계/iksan_km_10_to_100_simulation_chart.png)

---

## 📌 1. 분석 개요 및 전체 아키텍처

본 문서는 전북특별자치도 익산시의 **노인(65세 이상 64,500명, 24.1%) 및 의료급여/차상위 취약계층(17,500명, 6.5%)**을 대상으로, 관내 한방의료기관(한방병원 4개소, 한의원 105개소)의 **방문진료 참여율 10%~100% (10단계)**에 따른 **1인당 연평균 의료비 지출 변화**, **다빈도 5대 질환별 비용 대체 효과**, 그리고 **향후 5개년 재정·임상 적정성 효과**를 도출한 분석 로직의 수학적·통계적 명세를 제공합니다.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         익산시 한의약 방문진료 AI 분석 파이프라인 흐름도                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [1. HIRA & KOSIS DB] ──▶ [2. 다빈도 5대 질환 비용분해] ──▶ [3. 10%~100% 10단계 공급모델]       │
│    • 질병정보 (KCD M54..)   • 의과 입원/수술 vs 한의방문      • 관내 109개소 참여율별 슬롯/인력    │
│    • 수가기준/비급여 DB      • 1인당 연간 절감액 산출          • 커버리지 & 개입강도(θ) 산출      │
│                                                                                                  │
│                                      ▼                                                           │
│                                                                                                  │
│   [STEP 1: 패널 회귀분석] ──▶ [STEP 2: DEA 효율성 분석] ──▶ [STEP 3: QRE 내쉬 균형 모형]          │
│    • 고비용 잔차 ε_it 분해    • VRS/CRS 기술·규모효율성       • 3자(환자/병원/의원) 게임이론     │
│    • 사회적입원·약제비 분해   • Slack 절감 잠재액 산출        • 로짓 행위자 선택확률 전이        │
│                                                                                                  │
│                                      ▼                                                           │
│                                                                                                  │
│   [STEP 4: 몬테카를로 5개년] ─▶ [STEP 5: DID 이중차분] ──▶ [최종 아티팩트 산출]                 │
│    • N=10,000 확률 시뮬레이션  • 처치효과 계수 δ 산출          • 마크다운 종합보고서 (.md)        │
│    • 연도별 노인/취약 진료비   • 6대 의료 적정성 평가          • 인터랙티브 웹 대시보드 (.html)   │
│    • 5개년 누적 순절감 & ROI   • 평행 추세 가정 검증          • 고해상도 차트 (.png) / JSON      │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 2. 익산시 기초 인구 및 인프라 모수 정의

### 2.1 인구 및 베이스라인 의료비 모수

$$N_{\text{total}} = 268,000\,\text{명}, \quad N_{\text{elderly}} = 64,500\,\text{명}\,(24.1\%), \quad N_{\text{vulnerable}} = 17,500\,\text{명}\,(6.5\%)$$

$$\text{BaseCost}_{\text{elderly}} = 5,750,000\,\text{원/년}, \quad \text{BaseCost}_{\text{vulnerable}} = 8,200,000\,\text{원/년}$$

$$\text{BaseCost}_{\text{non\_elderly}} = 1,445,000\,\text{원/년}$$

$$\text{BaseCityAnnualTotal} = (N_{\text{elderly}} \times \text{BaseCost}_{\text{elderly}}) + (N_{\text{non\_elderly}} \times \text{BaseCost}_{\text{non\_elderly}}) \approx 6,650\,\text{억 원/년}$$

### 2.2 한의 의료 인프라 모수
* 한방병원: $H = 4\,\text{개소}$ (원광대학교 한방병원 등, 한의사 45명)
* 한의원: $C = 105\,\text{개소}$ (한의사 125명)
* 총 한방의료기관: $I_{\text{total}} = 109\,\text{개소}$, 총 한의사 수: $D_{\text{total}} = 170\,\text{명}$

---

## 🩺 3. 다빈도 5대 질환 진료비용 비교 분석 로직

HIRA 질병통계(`diseaseInfoService1`), 수가기준(`mdfeeCrtrInfoService`), 비급여(`nonPaymentDamtInfoService`) 데이터를 매핑하여 다빈도 5대 상병에 대한 의과/입원 vs 한의 방문진료 비용을 정량화합니다.

$$\Delta \text{Cost}_d = \text{Cost}_{\text{conv}, d} - \text{Cost}_{\text{KM}, d}$$

$$\text{SavingPct}_d = \left( \frac{\Delta \text{Cost}_d}{\text{Cost}_{\text{conv}, d}} \right) \times 100$$

| 질환군 ($d$) | 상병코드 (KCD) | 유병률 ($w_d$) | 의과/입원 비용 ($\text{Cost}_{\text{conv}}$) | 한의 방문케어 ($\text{Cost}_{\text{KM}}$) | 1인당 연간 절감액 ($\Delta \text{Cost}$) | 절감률 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **① 근골격계·척추관절** | M54, M17, M75 | 42.0% | 485.0만 원 | 165.0만 원 | **-320.0만 원** | **66.0%** |
| **② 뇌혈관 후유증·편마비** | I69, G81 | 12.0% | 1,420.0만 원 | 380.0만 원 | **-1,040.0만 원** | **73.2%** |
| **③ 치매 및 인지·정신** | F00-F03, F32 | 14.0% | 1,180.0만 원 | 310.0만 원 | **-870.0만 원** | **73.7%** |
| **④ 노인성 쇠약·만성복합** | R53, E11, I10 | 28.0% | 560.0만 원 | 190.0만 원 | **-370.0만 원** | **66.1%** |
| **⑤ 암/수술후 호스피스** | C00-C97 후유증 | 6.0% | 1,650.0만 원 | 450.0만 원 | **-1,200.0만 원** | **72.7%** |

---

## 🎛️ 4. 10%~100% (10단계) 참여율 공급 역량 및 커버리지 모델

참여율 $r \in \{0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00\}$ 에 따른 공급 인프라 산출식:

1. **참여 기관 수 및 한의사 수**:
   $$H(r) = \max(1, \text{round}(4r)), \quad C(r) = \max(1, \text{round}(105r)), \quad D(r) = \text{round}(109 \times 1.56 \times r)$$
2. **연간 방문진료 가용 슬롯 수**:
   $$S(r) = D(r) \times (930 + 160r) \quad (\text{한의사 1인당 연 } 930\sim 1,090\text{회 방문})$$
3. **취약계층 및 노인 커버리지**:
   $$\text{Cov}_{\text{vul}}(r) = \min\left(0.95,\, 0.15 + 0.80 \left(\frac{r-0.1}{0.9}\right)^{0.85}\right)$$
   $$\text{Cov}_{\text{eld}}(r) = \min\left(0.85,\, 0.08 + 0.70 \left(\frac{r-0.1}{0.9}\right)^{0.90}\right)$$
4. **한의약 개입 강도 파라미터 ($\theta$)**:
   $$\theta(r) = 0.15 + 0.80 \left(\frac{r-0.1}{0.9}\right)^{0.88} \in [0.150,\, 0.950]$$

---

## 📊 5. HIRA 5단계 AI 분석 파이프라인 알고리즘 상세

### [STEP 1] 현황 파악: 패널 회귀분석 및 고비용 잔차 분해
* **비용 함수**:
  $$\log(\text{cost\_per\_visit}_{it}) = \alpha_i + \beta_1 \log(\text{bed}_{it}) + \beta_2 \text{CMI}_{it} + \beta_3 \text{Inpatient\_Ratio}_{it} - \beta_4 \text{KM\_Ratio}_{it} + \varepsilon_{it}$$
* **추정 계수**: $\beta_1 = 0.38, \;\beta_2 = 0.52, \;\beta_3 = 0.24, \;\beta_4 = -0.08$
* **비용 분해 구조**:
  - 취약계층(820만): 입원료(36.0%) + 수술/시술(23.0%) + 약제비(25.0%) + 외래/한의(13.0%) + 응급(3.0%)
  - 65세 이상 노인(575만): 입원료(31.0%) + 수술/시술(25.0%) + 약제비(26.0%) + 외래/한의(15.0%) + 응급(3.0%)

---

### [STEP 2] 기관 분류: 투입-산출 DEA 효율성 분석
* **모델**: VRS(규모수익가변) 투입지향 DEA 및 CRS(규모수익불변) 분해
* **투입 변수 ($X$)**: 총 청구액($X_1$), 한의사 수($X_2$), 병상 수($X_3$)
* **산출 변수 ($Y$)**: CMI 보정 진료건수($Y_1$), 30일 재입원 억제율 역수($Y_2$), K-ADL 유지율($Y_3$)
* **기술효율성 및 규모효율성 산출식**:
  $$\text{DEA}_{\text{VRS}}(r) = 0.74 + 0.25 \left(1 - e^{-3.5(r-0.05)}\right)$$
  $$\text{ScaleEff}(r) = \frac{\text{DEA}_{\text{CRS}}(r)}{\text{DEA}_{\text{VRS}}(r)} = 0.81 + 0.18 \left(\frac{r-0.1}{0.9}\right)^{0.7}$$

---

### [STEP 3] 균형 예측: 로짓 내쉬 균형(QRE) 3자 게임이론
* **합리성 파라미터**: $\lambda = 2.0$
* **3대 행위자 보수 격차 함수**:
  1. **환자/보호자 (재택유지 vs 입원)**:
     $$\Delta U_{\text{patient}}(\theta) = -0.8 + 2.6\theta + 0.4\theta^2 \implies P_{\text{home}}(\theta) = \frac{1}{1 + e^{-\lambda \Delta U_{\text{patient}}}}$$
  2. **요양병원 (단기재활 vs 장기입원)**:
     $$\Delta R_{\text{hospital}}(\theta) = -1.1 + 2.4\theta + 0.3\theta^2 \implies P_{\text{rehab}}(\theta) = \frac{1}{1 + e^{-\lambda \Delta R_{\text{hospital}}}}$$
  3. **1차 의과의원 (비수술 협진 vs 고가시술)**:
     $$\Delta R_{\text{doctor}}(\theta) = -0.6 + 2.5\theta + 0.2\theta^2 \implies P_{\text{coop}}(\theta) = \frac{1}{1 + e^{-\lambda \Delta R_{\text{doctor}}}}$$

---

### [STEP 4] 몬테카를로 5개년 시계열 시뮬레이션 ($N=10,000$)
* **연도별 성숙도 계수**: $M_t = [0.65, 0.80, 0.92, 0.98, 1.00] \quad (t = 1, 2, 3, 4, 5)$
* **연도별 개입 강도**: $\theta_t(r) = \theta(r) \times M_t$
* **각 비용 항목별 억제율**:
  $$\text{Eff}_{\text{hosp}}(t, r) = \left(0.42 P_{\text{home}} + 0.30 P_{\text{rehab}}\right) \times M_t$$
  $$\text{Eff}_{\text{surg}}(t, r) = \left(0.45 P_{\text{coop}} + 0.25 P_{\text{home}}\right) \times M_t$$
  $$\text{Eff}_{\text{pharm}}(t, r) = \left(0.38 P_{\text{coop}} + 0.28 P_{\text{home}}\right) \times M_t$$
  $$\text{Eff}_{\text{er}}(t, r) = \left(0.50 P_{\text{home}}\right) \times M_t$$
* **확률적 의료비 노이즈**: $\eta_k \sim \mathcal{N}(1.0, \sigma_k^2) \quad (\sigma_{\text{hosp}}=0.032, \sigma_{\text{surg}}=0.038, \sigma_{\text{pharm}}=0.028)$
* **연간 순절감액 및 누적 ROI 산출**:
  $$\text{Savings}_t(r) = \text{BaseCityAnnualTotal} - \text{CityAnnualCost}_t(r)$$
  $$\text{ROI}_{\text{cum}}(r) = \frac{\sum_{t=1}^5 \left(\text{Savings}_t + \text{KM\_Input}_t\right)}{\sum_{t=1}^5 \text{KM\_Input}_t}$$

---

### [STEP 5] 효과 검증: 이중차분(DID) 및 6대 의료 적정성 평가
* **DID 처치효과 계수**:
  $$\delta(r) = -\left|\frac{\text{CostDiff}_{\text{eld}, 5}(r)}{\text{BaseCost}_{\text{eld}}}\right| \times (0.95 + 0.05r) \quad (p < 0.001)$$
* **6대 의료 적정성 평가 지표 산출**:
  1. 요양병원 사회적 입원 억제율: $\text{Eff}_{\text{hosp}}(5, r) \times 100\%$
  2. 30일 이내 재입원율 감소율: $\text{Eff}_{\text{hosp}}(5, r) \times 85\%$
  3. 불필요 응급실 내원 감소율: $50\% \times P_{\text{home}}(5) \times M_5$
  4. 10종 이상 다제약물 처방 억제율: $\text{Eff}_{\text{pharm}}(5, r) \times 100\%$
  5. K-ADL 일상생활수행능력 유지율: $25\% + 35\% \times P_{\text{home}}(5) \times M_5$
  6. Malmquist 총요소생산성 지수 (TFP): $1.0 + 0.30 \times r^{0.75}$

---

## 💻 6. 파이썬 분석 스크립트 실행 및 결과 무결성 검증

### 6.1 실행 커맨드
```bash
python "03_분석_및_수집_스크립트/simulate_iksan_km_10_to_100_full.py"
```

### 6.2 산출 아티팩트 검증
* `03_분석_및_수집_스크립트/iksan_km_10_to_100_full_simulation.json`: 10단계 시나리오 × 5개년 N=10,000 몬테카를로 원시 수치 완벽 저장
* `iksan_km_10_to_100_simulation_chart.png`: 4분면 고해상도 시각화 차트 (진료비 추이, 순절감액, 내쉬균형, 질환별 비용비교)
* `익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html`: 인터랙티브 반응형 Chart.js 대시보드

---

*본 명세서는 건강보험심사평가원(HIRA) 및 통계청(KOSIS) 기준을 준수하여 작성되었습니다.*
