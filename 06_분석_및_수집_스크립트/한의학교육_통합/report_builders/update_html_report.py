import html

html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>한의학 교육과정 및 임상 의료서비스 실태 교차분석과 AI 기반 교육과정 혁신 방안</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0f4c81;
            --primary-dark: #0a2540;
            --primary-light: #e8f1f8;
            --accent: #008080;
            --accent-light: #e0f2f1;
            --secondary: #6366f1;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --border-color: #e2e8f0;
            --danger: #ef4444;
            --warning: #f59e0b;
            --success: #10b981;
            --info: #3b82f6;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --radius-md: 12px;
            --radius-lg: 16px;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-main);
            line-height: 1.7;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            max-width: 1240px;
            margin: 0 auto;
            padding: 40px 24px;
        }

        /* Hero Header */
        header.report-header {
            background: linear-gradient(135deg, #0a2540 0%, #0f4c81 50%, #008080 100%);
            color: #ffffff;
            padding: 48px 40px;
            border-radius: var(--radius-lg);
            margin-bottom: 36px;
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }

        header.report-header::after {
            content: "";
            position: absolute;
            top: -50%;
            right: -10%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 70%);
            border-radius: 50%;
        }

        .badge-tag {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            color: #ffffff;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 16px;
            backdrop-filter: blur(8px);
        }

        .report-title {
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 16px;
            letter-spacing: -0.5px;
        }

        .report-subtitle {
            font-size: 1.05rem;
            opacity: 0.9;
            font-weight: 400;
            max-width: 960px;
            line-height: 1.6;
        }

        .header-meta {
            margin-top: 24px;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            font-size: 0.9rem;
            opacity: 0.85;
            border-top: 1px solid rgba(255,255,255,0.15);
            padding-top: 16px;
        }

        /* KPI Cards Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px;
            margin-bottom: 36px;
        }

        .kpi-card {
            background: var(--bg-card);
            padding: 24px;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .kpi-title {
            font-size: 0.88rem;
            color: var(--text-muted);
            font-weight: 600;
            margin-bottom: 8px;
        }

        .kpi-value {
            font-size: 1.9rem;
            font-weight: 800;
            color: var(--primary);
            font-family: 'Outfit', sans-serif;
            margin-bottom: 4px;
        }

        .kpi-sub {
            font-size: 0.82rem;
            color: var(--text-muted);
        }

        .kpi-change.positive { color: var(--danger); font-weight: 600; }
        .kpi-change.highlight { color: var(--accent); font-weight: 600; }
        .kpi-change.reduction { color: var(--secondary); font-weight: 600; }

        /* Content Sections */
        .section-card {
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-color);
            padding: 36px;
            margin-bottom: 32px;
            box-shadow: var(--shadow-sm);
        }

        .section-header {
            display: flex;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid var(--primary-light);
        }

        .section-num {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 38px;
            height: 38px;
            background: var(--primary);
            color: white;
            font-weight: 700;
            border-radius: 10px;
            margin-right: 14px;
            font-size: 1.1rem;
            font-family: 'Outfit', sans-serif;
        }

        .section-title {
            font-size: 1.45rem;
            font-weight: 700;
            color: var(--primary-dark);
            letter-spacing: -0.3px;
        }

        h3 {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-main);
            margin: 24px 0 12px 0;
            display: flex;
            align-items: center;
        }

        h3::before {
            content: "";
            display: inline-block;
            width: 6px;
            height: 18px;
            background: var(--accent);
            border-radius: 3px;
            margin-right: 10px;
        }

        p {
            margin-bottom: 14px;
            color: #334155;
            font-size: 0.98rem;
        }

        /* Callout Box */
        .callout {
            background: var(--primary-light);
            border-left: 4px solid var(--primary);
            padding: 18px 20px;
            border-radius: 0 8px 8px 0;
            margin: 20px 0;
            font-size: 0.95rem;
        }

        .callout.alert {
            background: #fef2f2;
            border-left-color: var(--danger);
        }

        .callout.success {
            background: #f0fdf4;
            border-left-color: var(--success);
        }

        .callout.law {
            background: #eff6ff;
            border-left-color: #3b82f6;
        }

        /* Tables */
        .table-responsive {
            overflow-x: auto;
            margin: 20px 0 28px 0;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            text-align: left;
        }

        th {
            background: #f1f5f9;
            color: #334155;
            font-weight: 700;
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }

        td {
            padding: 12px 14px;
            border-bottom: 1px solid #f1f5f9;
            color: #334155;
            vertical-align: middle;
        }

        tr:last-child td { border-bottom: none; }
        tr:hover td { background-color: #f8fafc; }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 700;
            text-align: center;
        }

        .badge-a { background: #dcfce7; color: #166534; }
        .badge-b { background: #e0e7ff; color: #3730a3; }
        .badge-c { background: #fef3c7; color: #92400e; }
        .badge-red { background: #fee2e2; color: #991b1b; }
        .badge-blue { background: #e0f2fe; color: #075985; }

        /* Grid Comparison */
        .compare-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 24px 0;
        }

        .compare-box {
            padding: 22px;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
        }

        .compare-box.weak {
            background: #fffafa;
            border-color: #fecaca;
        }

        .compare-box.need {
            background: #f0fdfa;
            border-color: #99f6e4;
        }

        .compare-title {
            font-weight: 700;
            font-size: 1.05rem;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .compare-title.weak { color: #b91c1c; }
        .compare-title.need { color: #0f766e; }

        ul.styled-list {
            padding-left: 20px;
            margin-bottom: 12px;
        }

        ul.styled-list li {
            margin-bottom: 8px;
            font-size: 0.94rem;
        }

        footer.report-footer {
            text-align: center;
            padding: 32px 0;
            color: var(--text-muted);
            font-size: 0.88rem;
            border-top: 1px solid var(--border-color);
            margin-top: 40px;
        }

        @media print {
            body { background: white; }
            .container { max-width: 100%; padding: 0; }
            .section-card { border: none; box-shadow: none; padding: 16px 0; page-break-inside: avoid; }
            header.report-header { box-shadow: none; border-radius: 0; }
        }

        @media (max-width: 768px) {
            .compare-grid { grid-template-columns: 1fr; }
            .report-title { font-size: 1.7rem; }
            .section-card { padding: 20px; }
        }
    </style>
</head>
<body>

<div class="container">

    <!-- Header -->
    <header class="report-header">
        <div class="badge-tag">2026 최신 법령·평가인증·보건의료 빅데이터 융합 분석 보고서</div>
        <h1 class="report-title">한의학 교육과정 및 임상 의료서비스 실태 교차분석과<br>AI 기반 교육과정 혁신 방안</h1>
        <p class="report-subtitle">원광대 교육과정 전수 분석 × HIRA 10개년 빅데이터 × 2026 개정 시체해부법령(대통령령 제36725호) × 한평원(KAS2022) 평가기준 개선안</p>
        <div class="header-meta">
            <span><strong>분석 대상:</strong> 원광대 한의과대학 교육과정(123과목), KAS2022 편람, 시체해부법령 제21107호, WFCMS 중의표준</span>
            <span><strong>데이터 출처:</strong> 건강보험심사평가원(HIRA), 통계청(KOSIS), 한국한의학교육평가원(IKKOME)</span>
            <span><strong>작성 기준일:</strong> 2026. 10. 07</span>
        </div>
    </header>

    <!-- Key Metrics Summary -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">임상 다빈도 질환 편중도</div>
            <div class="kpi-value">78.4%</div>
            <div class="kpi-sub">외래 진료 근골격계·염좌 질환 집중 <span class="kpi-change highlight">(1위 등통증/요통)</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">2026 개정 시체해부법령</div>
            <div class="kpi-value">실정법 보장</div>
            <div class="kpi-sub">한의대 <strong>'교육목적 시체제공기관'</strong> 인가 <span class="kpi-change positive">(독자적 카데바 수급)</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">자동차보험 한의 점유율</div>
            <div class="kpi-value">58.4%</div>
            <div class="kpi-sub">2014년 19.0% → 2023년 1.49조 원 <span class="kpi-change positive">(의과 추월 1위)</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">AI 대체 기반 학점 순절감</div>
            <div class="kpi-value">-29.5학점</div>
            <div class="kpi-sub">주당 48시간 절감 → <span class="kpi-change reduction">초음파/카데바 실습 재배치</span></div>
        </div>
    </div>

    <!-- Section 1: Overview -->
    <section class="section-card">
        <div class="section-header">
            <div class="section-num">1</div>
            <h2 class="section-title">2026년 보건의료 및 법령 환경의 대전환</h2>
        </div>
        <p>대한민국 보건의료체계는 2025~2026년 초고령사회(65세 이상 20% 초과) 진입, 만성 복합질환 급증, 그리고 사법부·입법부의 획기적인 법률 개정이라는 거대한 3대 전환기를 맞이하고 있습니다.</p>
        
        <div class="callout law">
            <strong>2026 개정 시체해부법령의 역사적 의의:</strong>
            2026년 5월 시행된 「시체해부법」(법률 제21107호) 및 2026년 9월 29일 시행된 동법 시행령(대통령령 제36725호)은 법 제1조와 제2조에서 <strong>'의학(한의학 포함)', '의과대학(한의과대학 포함)'</strong>을 명문화하고, 한의과대학이 <strong>'교육목적 시체제공기관'(영 제3조 및 별표 1)</strong> 허가를 받아 독자적으로 카데바를 수집·보존·제공할 수 있는 완전무결한 실정법적 해부 교육권을 확립하였습니다.
        </div>
    </section>

    <!-- Section 2: Wonkwang Curriculum -->
    <section class="section-card">
        <div class="section-header">
            <div class="section-num">2</div>
            <h2 class="section-title">원광대학교 한의과대학 교육과정 현황 및 구조적 결함</h2>
        </div>
        <p>원광대학교 한의과대학 교육과정(2024학년도)은 <strong>총 6년(예과 2년 + 본과 4년), 123개 강좌, 248.5학점(주당 약 320시간 분량)</strong>으로 운영되고 있으나, 교육 내용이 임상 수요 및 개정 법령 인프라와 심각하게 미스매치되어 있습니다.</p>

        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>영역 구분</th>
                        <th>교과목 수</th>
                        <th>총 학점</th>
                        <th>비중(%)</th>
                        <th>구조적 문제점 및 교육 결함</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>기초한의학 (원전·이론·본초·방제)</strong></td>
                        <td>38개</td>
                        <td>80.0학점</td>
                        <td><strong>32.2%</strong></td>
                        <td>원전문헌군 21학점(주 28h), 본초/방제 16학점 등 <strong>훈고학적 자구 번역 및 단순 암기 과밀</strong></td>
                    </tr>
                    <tr>
                        <td><strong>기초의생명과학</strong></td>
                        <td>25개</td>
                        <td>55.0학점</td>
                        <td><strong>22.1%</strong></td>
                        <td>해부실습(2학점)이 단순 구조 확인에 그쳐 <strong>경혈 층차(Layer 1~5) 신경해부 및 초음파 연계 결여</strong></td>
                    </tr>
                    <tr>
                        <td><strong>임상한의학 이론</strong></td>
                        <td>24개</td>
                        <td>50.5학점</td>
                        <td><strong>20.3%</strong></td>
                        <td>간/심/비/폐/신계 내과학(10과목 12.5학점)으로 <strong>5대 장부 파편화 및 유사 이론 중복</strong></td>
                    </tr>
                    <tr>
                        <td><strong>임상실습 및 술기</strong></td>
                        <td>16개</td>
                        <td>45.0학점</td>
                        <td><strong>18.1%</strong></td>
                        <td>본4 병원 로테이션 실습 위주이며, <strong>초음파 유도하 약침/침도 등 능동적 정밀 술기 실습 부족</strong></td>
                    </tr>
                    <tr>
                        <td><strong>의료정보학 / 데이터 / AI</strong></td>
                        <td>4개</td>
                        <td>3.0학점</td>
                        <td><strong>1.2%</strong></td>
                        <td>의료데이터사이언스(전선 2학점), 의료정보학(전필 1학점)에 불과하여 <strong>절대적 부족</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>

    <!-- Section 3: 10-Year HIRA Trends & CPG -->
    <section class="section-card">
        <div class="section-header">
            <div class="section-num">3</div>
            <h2 class="section-title">HIRA 10개년 빅데이터 분석 및 15대 다빈도 상병 CPG 매트릭스</h2>
        </div>
        <p>HIRA·KOSIS 10개년(2014~2024) 분석 결과, 한의 외래 이용의 <strong>78.4%가 근골격계 및 염좌 질환</strong>에 집중되어 있습니다.</p>

        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>순위</th>
                        <th>상병명 (KCD 코드)</th>
                        <th>질환군</th>
                        <th>환자 비중</th>
                        <th>CPG 핵심 권고 중재술</th>
                        <th>CPG 권고등급</th>
                        <th>현행 건강보험 급여 현황</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td><strong>등 통증 / 요통 (M54)</strong></td>
                        <td>근골격계</td>
                        <td>25.4%</td>
                        <td>침, 전침, 추나요법, 약침, 첩약</td>
                        <td><span class="badge badge-a">침 (A)</span> <span class="badge badge-a">추나 (A)</span> <span class="badge badge-b">약침 (B)</span></td>
                        <td>침/구/부항/추나(급여), 약침(비급여)</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td><strong>요추·골반 염좌 (S33)</strong></td>
                        <td>근골격/외상</td>
                        <td>14.8%</td>
                        <td>침, 사혈부항, 약침, 추나, 첩약</td>
                        <td><span class="badge badge-a">침 (A)</span> <span class="badge badge-a">부항 (A)</span> <span class="badge badge-b">약침 (B)</span></td>
                        <td>침/구/부항/추나(급여), 약침(비급여)</td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td><strong>연조직 장애 / 근막통 (M79)</strong></td>
                        <td>근골격계</td>
                        <td>10.2%</td>
                        <td>침, 전침, 약침, 도인안교</td>
                        <td><span class="badge badge-a">침 (A)</span> <span class="badge badge-a">전침 (A)</span> <span class="badge badge-b">약침 (B)</span></td>
                        <td>침/구/부항(급여), 약침(비급여)</td>
                    </tr>
                    <tr>
                        <td>4</td>
                        <td><strong>어깨 병변 / 오십견 (M75)</strong></td>
                        <td>근골격계</td>
                        <td>8.6%</td>
                        <td>침, 전침, 관절가동추나, 약침</td>
                        <td><span class="badge badge-a">침 (A)</span> <span class="badge badge-b">추나 (B)</span> <span class="badge badge-b">약침 (B)</span></td>
                        <td>침/구/부항/추나(급여), 약침(비급여)</td>
                    </tr>
                    <tr>
                        <td>5</td>
                        <td><strong>경추 염좌 및 긴장 (S13)</strong></td>
                        <td>근골격/외상</td>
                        <td>7.5%</td>
                        <td>침, 전침, 경추추나, 약침, 부항</td>
                        <td><span class="badge badge-a">침 (A)</span> <span class="badge badge-a">추나 (A)</span> <span class="badge badge-b">약침 (B)</span></td>
                        <td>침/구/부항/추나(급여), 약침(비급여)</td>
                    </tr>
                    <tr>
                        <td>6</td>
                        <td><strong>추간판탈출증 (디스크 M50/51)</strong></td>
                        <td>근골격/신경</td>
                        <td>4.2%</td>
                        <td>침, 복잡추나, 약침, 첩약</td>
                        <td><span class="badge badge-a">침 (A)</span> <span class="badge badge-a">추나 (A)</span> <span class="badge badge-b">첩약 (B)</span></td>
                        <td>첩약 건보 시범사업 2단계 급여</td>
                    </tr>
                    <tr>
                        <td>7</td>
                        <td><strong>안면신경마비 (벨마비 G51)</strong></td>
                        <td>신경계</td>
                        <td>1.8%</td>
                        <td>침, 전침, 첩약, 약침, 매선</td>
                        <td><span class="badge badge-a">침 (A)</span> <span class="badge badge-a">전침 (A)</span> <span class="badge badge-a">첩약 (A)</span></td>
                        <td>첩약 건보 시범사업 1·2단계 급여</td>
                    </tr>
                    <tr>
                        <td>8</td>
                        <td><strong>기능성 소화불량 (K30)</strong></td>
                        <td>소화기계</td>
                        <td>1.7%</td>
                        <td>침, 뜸, 첩약, 평위산 등 한약제제</td>
                        <td><span class="badge badge-a">침 (A)</span> <span class="badge badge-a">뜸 (A)</span> <span class="badge badge-a">첩약 (A)</span></td>
                        <td>첩약 건보 시범사업 2단계 급여</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>

    <!-- Section 4: Anatomy Act & Legal Integration -->
    <section class="section-card">
        <div class="section-header">
            <div class="section-num">4</div>
            <h2 class="section-title">2026 개정 시체해부법령과 한의학 교육권의 융합</h2>
        </div>
        <p>2026년 9월 29일 시행된 대통령령 제36725호는 한의과대학의 해부학 실습을 질적으로 고도화할 수 있는 법적 기반을 완비하였습니다.</p>

        <div class="compare-grid">
            <div class="compare-box need">
                <div class="compare-title need">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
                    시체해부법령 개정에 따른 교육과정 혁신 효과
                </div>
                <ul class="styled-list">
                    <li><strong>교육목적 시체제공기관 인가:</strong> 전국 12개 한의대가 독자적 카데바 수급 체계 구축 및 수급 불안정 완전 해소.</li>
                    <li><strong>경혈 층차(Layer 1~5) 신경해부 실습:</strong> 경혈점의 신경·혈관 주행 및 근막경선(Myofascial) 구조를 카데바에서 직접 박리·확인.</li>
                    <li><strong>초음파 유도하 약침·침도 카데바 실습:</strong> 초음파를 실시간 보며 자침하여 신경포착(Entrapment) 해소 훈련.</li>
                </ul>
            </div>

            <div class="compare-box weak">
                <div class="compare-title weak">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
                    한평원 KAS2022 평가기준의 구조적 한계 (개선 대상)
                </div>
                <ul class="styled-list">
                    <li><strong>14개 분과교실 단위 교원 정원(P5.1.2) 강제:</strong> 대학의 자율적 과목 통폐합을 원천 차단하는 기득권 병목.</li>
                    <li><strong>현대 진단기기 필수기준 결여:</strong> 대법원 판결 및 개정 법령에도 불구하고 초음파 실습 필수기준 전무.</li>
                    <li><strong>WFCMS 국제표준 대비 암기 상한선(Cap) 부재:</strong> 200학점 이상의 이론 강의 과밀을 방조.</li>
                </ul>
            </div>
        </div>
    </section>

    <!-- Section 5: AI-Based Reform Model -->
    <section class="section-card">
        <div class="section-header">
            <div class="section-num">5</div>
            <h2 class="section-title">[교육과정 혁신안] AI 대체 분석 및 학점·시수 개편 실행 모델</h2>
        </div>
        <p>AI 기술로 대체 가능한 훈고학적 문헌 및 암기 과목에서 <strong>순수 29.5학점 / 주당 48시간을 감축</strong>하고, 이를 <strong>초음파 진단 실습, 초음파 유도 카데바 중재술, 1차 진단검사 실습으로 100% 재배치</strong>합니다.</p>

        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>구분</th>
                        <th>현행 대상 교과목군</th>
                        <th>현행 학점(시수)</th>
                        <th>개편 통합 교과목명</th>
                        <th>개편 학점(시수)</th>
                        <th>학점 변동</th>
                        <th>시수 변동</th>
                        <th>AI 대체 및 교육과정 혁신 근거</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><span class="badge badge-red">대폭 축소</span></td>
                        <td><strong>한문·원전문헌군 (8과목)</strong><br>한의학한문, 중국어, 경서강독, 원전학 1~3, 상한론 1~2, 온병학</td>
                        <td>21.0학점 (28h)</td>
                        <td><strong>통합 원전·의사학 및 AI 문헌데이터분석</strong></td>
                        <td>4.0학점 (4h)</td>
                        <td><strong>-17.0</strong></td>
                        <td><strong>-24.0h</strong></td>
                        <td>LLM 실시간 원문 번역·주석 대체로 단순 자구 해석 수업 폐지, AI 문헌 탐색 실습으로 압축</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-red">대폭 축소</span></td>
                        <td><strong>기초이론군 (3과목)</strong><br>한의학개론, 한의학기초이론 1·2</td>
                        <td>6.0학점 (9h)</td>
                        <td><strong>통합 한의학 원리와 현대 생체조절론</strong></td>
                        <td>3.0학점 (3h)</td>
                        <td><strong>-3.0</strong></td>
                        <td><strong>-6.0h</strong></td>
                        <td>개념 이론 강의를 AI Flipped Learning으로 축소, 신경내분비 면역학적 기전과 통합</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-red">대폭 축소</span></td>
                        <td><strong>본초·방제 암기군 (6과목)</strong><br>본초학총론/1, 임상본초학, 방제학 1~3</td>
                        <td>16.0학점 (24h)</td>
                        <td><strong>통합 본초·방제학 및 임상약리학(DDI)</strong></td>
                        <td>6.0학점 (8h)</td>
                        <td><strong>-10.0</strong></td>
                        <td><strong>-16.0h</strong></td>
                        <td>500종 본초/방제 단순 암기는 AI CDSS 검색 대체, 양·한약 상호작용 및 안전성 평가 집중</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-red">대폭 축소</span></td>
                        <td><strong>장부 파편형 내과군 (10과목)</strong><br>간/심/비/폐/신계 내과학 1·2</td>
                        <td>12.5학점 (20h)</td>
                        <td><strong>통합 한방내과학 (계통별·증례별 PBL)</strong></td>
                        <td>6.0학점 (8h)</td>
                        <td><strong>-6.5</strong></td>
                        <td><strong>-12.0h</strong></td>
                        <td>5대 장부 중복 강의를 소화/호흡/대사/순환 계통별 임상 증례 중심 문제해결 학습으로 통합</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-a">신규 강화</span></td>
                        <td><strong>영상의학 및 초음파</strong><br>영상의학</td>
                        <td>1.0학점 (2h)</td>
                        <td><strong>임상 초음파 진단학 및 영상의학 실습</strong></td>
                        <td>4.0학점 (6h)</td>
                        <td><strong>+3.0</strong></td>
                        <td><strong>+4.0h</strong></td>
                        <td><strong>대법원 판결 대응 필수 역량:</strong> 근골격계/복부 초음파 핸즈온 실습 및 AI 영상 판독</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-a">신규 강화</span></td>
                        <td><strong>카데바 연계 정밀 중재술</strong><br>추나의학/실습, 침구실습 1·2</td>
                        <td>4.0학점 (6h)</td>
                        <td><strong>초음파유도 카데바 중재술 및 척추관절 골상실습</strong></td>
                        <td>6.0학점 (10h)</td>
                        <td><strong>+2.0</strong></td>
                        <td><strong>+4.0h</strong></td>
                        <td><strong>2026 개정 시체해부법령 및 환자 78% 대응:</strong> 카데바 기반 초음파 유도 약침/침도/추나 집중 훈련</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-a">신규 강화</span></td>
                        <td><strong>진단검사의학 및 임상병리</strong><br>진단검사의학 1·2</td>
                        <td>2.0학점 (4h)</td>
                        <td><strong>1차 의료 임상병리 및 검사해석 실습</strong></td>
                        <td>3.0학점 (4h)</td>
                        <td><strong>+1.0</strong></td>
                        <td><strong>0.0h</strong></td>
                        <td>혈액·소변검사기 실습 및 간/신장기능 모니터링 실무 역량 배양</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-a">신규 강화</span></td>
                        <td><strong>CPG 기반 임상 & 의료 AI</strong><br>의료데이터사이언스, 의료정보학</td>
                        <td>3.0학점 (4h)</td>
                        <td><strong>CPG 기반 AI-CDSS 임상의사결정 및 보험실무</strong></td>
                        <td>4.0학점 (4h)</td>
                        <td><strong>+1.0</strong></td>
                        <td><strong>+2.0h</strong></td>
                        <td>국가 CPG 연계 진료, AI EMR 활용, 건강보험 청구 및 SOAP 차팅 실무 교육</td>
                    </tr>
                    <tr style="background: #f1f5f9; font-weight: bold;">
                        <td><strong>합 계</strong></td>
                        <td><strong>총 33개 대상 과목</strong></td>
                        <td><strong>65.5학점 (97h)</strong></td>
                        <td><strong>8개 핵심 통합 모듈</strong></td>
                        <td><strong>36.0학점 (49h)</strong></td>
                        <td><strong style="color: var(--danger);">-29.5학점</strong></td>
                        <td><strong style="color: var(--danger);">-48.0시간</strong></td>
                        <td><strong>순절감된 29.5학점은 병원 임상실습 및 서브인턴십으로 100% 재배치</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>

    <!-- Section 6: Action Plan & Policy -->
    <section class="section-card">
        <div class="section-header">
            <div class="section-num">6</div>
            <h2 class="section-title">결론 및 종합 정책 로드맵</h2>
        </div>
        <p>1. <strong>2026 개정 시체해부법령 인프라 구축:</strong> 전국 12개 한의과대학은 2026~2027년 질병관리청 <strong>'교육목적 시체제공기관' 인가</strong>를 완료하고 BL2 실습실을 구축하여 <strong>카데바-초음파 연계 정밀 실습</strong>을 핵심 과정으로 안착시켜야 합니다.</p>
        <p>2. <strong>한평원 KAS2022 평가기준 즉각 개정:</strong> 14개 분과교실 단위 교원 정원제를 폐지하고 <strong>5대 통합모듈 교원제 및 초음파 실습(60h) 필수기준(E)</strong>을 신설해야 합니다.</p>
        <p>3. <strong>초고령사회 대응 1차 통합의료인 육성:</strong> AI 기반 지식 암기 29.5학점 감축과 초음파·카데바·진단검사·CPG 실습 강화를 통해 대한민국 한의사를 <strong>1차 통합의료 전문가</strong>로 완성해야 합니다.</p>
    </section>

    <footer class="report-footer">
        <p>© 2026 한의학 교육과 의료 통합 정책 연구 분과. All rights reserved.</p>
        <p>본 문서는 시체해부법(법률 제21107호/대통령령 제36725호), 한평원 KAS2022, HIRA 빅데이터 및 원광대학교 교육과정에 기반하여 작성되었습니다.</p>
    </footer>

</div>

</body>
</html>
"""

with open(r"d:\행정\한의학 교육과 의료 통합\01_교육과정_혁신로드맵\한의학교육_의료통합_상세보고서.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Updated HTML report successfully.")
