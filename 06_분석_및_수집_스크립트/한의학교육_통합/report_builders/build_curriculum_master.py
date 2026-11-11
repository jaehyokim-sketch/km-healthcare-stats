import json
import pandas as pd

# Load parsed catalog contexts
with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\catalog_contexts.json", "r", encoding="utf-8") as f:
    contexts = json.load(f)

# Let's inspect pages 17 to 26 and map out every course cleanly
# We know the official structure of Wonkwang Univ College of Korean Medicine:
# Pre-med (예과 1, 2) and Main (본과 1, 2, 3, 4)

# Let's write a parser that maps each course code to its exact details
courses = [
    # 예과 1학년 1학기
    {"year": "예과1", "sem": "1학기", "code": "001111", "type": "교필", "name": "종교와원불교", "credit": 3, "theory": 3, "lab": 0, "category": "교양/인문"},
    {"year": "예과1", "sem": "1학기", "code": "001252", "type": "교필", "name": "대학생활과자기혁신", "credit": 2, "theory": 2, "lab": 0, "category": "교양/인문"},
    {"year": "예과1", "sem": "1학기", "code": "221050", "type": "전필", "name": "의학용어1", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "예과1", "sem": "1학기", "code": "221263", "type": "전필", "name": "한의학기초이론1", "credit": 2, "theory": 3, "lab": 0, "category": "기초한의학(원전/이론)"},
    {"year": "예과1", "sem": "1학기", "code": "221264", "type": "전필", "name": "한의학개론", "credit": 2, "theory": 3, "lab": 0, "category": "기초한의학(원전/이론)"},
    {"year": "예과1", "sem": "1학기", "code": "221296", "type": "전필", "name": "일반생물학1", "credit": 2, "theory": 2, "lab": 0, "category": "기초과학"},
    {"year": "예과1", "sem": "1학기", "code": "221295", "type": "전필", "name": "일반화학1", "credit": 2, "theory": 2, "lab": 0, "category": "기초과학"},
    {"year": "예과1", "sem": "1학기", "code": "221291", "type": "전선", "name": "기초중국어", "credit": 2, "theory": 2, "lab": 0, "category": "어학/교양"},
    {"year": "예과1", "sem": "1학기", "code": "221292", "type": "전선", "name": "심리학개론", "credit": 2, "theory": 2, "lab": 0, "category": "인문사회"},

    # 예과 1학년 2학기
    {"year": "예과1", "sem": "2학기", "code": "221051", "type": "전필", "name": "의학용어2", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "예과1", "sem": "2학기", "code": "221269", "type": "전필", "name": "한의학기초이론2", "credit": 2, "theory": 3, "lab": 0, "category": "기초한의학(원전/이론)"},
    {"year": "예과1", "sem": "2학기", "code": "221270", "type": "전필", "name": "한의학의역사와현대사회", "credit": 2, "theory": 3, "lab": 0, "category": "기초한의학(역사/인문)"},
    {"year": "예과1", "sem": "2학기", "code": "221297", "type": "전필", "name": "일반화학2", "credit": 2, "theory": 2, "lab": 0, "category": "기초과학"},
    {"year": "예과1", "sem": "2학기", "code": "221298", "type": "전필", "name": "일반생물학2", "credit": 2, "theory": 2, "lab": 0, "category": "기초과학"},
    {"year": "예과1", "sem": "2학기", "code": "221299", "type": "전필", "name": "한의학한문", "credit": 1, "theory": 2, "lab": 0, "category": "어학/원전문헌"},
    {"year": "예과1", "sem": "2학기", "code": "221300", "type": "전필", "name": "인체의구조와기능1(해부생리)", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "예과1", "sem": "2학기", "code": "221293", "type": "전선", "name": "약용식물학", "credit": 2, "theory": 2, "lab": 0, "category": "기초한의학(본초)"},
    {"year": "예과1", "sem": "2학기", "code": "221294", "type": "전선", "name": "의료데이터사이언스", "credit": 2, "theory": 2, "lab": 0, "category": "정보/AI/데이터"},

    # 예과 2학년 1학기
    {"year": "예과2", "sem": "1학기", "code": "221258", "type": "전필", "name": "본초학총론", "credit": 1, "theory": 2, "lab": 0, "category": "기초한의학(본초)"},
    {"year": "예과2", "sem": "1학기", "code": "221259", "type": "전필", "name": "원전학1", "credit": 3, "theory": 4, "lab": 0, "category": "기초한의학(원전/이론)"},
    {"year": "예과2", "sem": "1학기", "code": "221278", "type": "전필", "name": "의철학", "credit": 1, "theory": 2, "lab": 0, "category": "인문사회"},
    {"year": "예과2", "sem": "1학기", "code": "221280", "type": "전필", "name": "인체의구조와기능실습1(해부실습)", "credit": 1, "theory": 0, "lab": 2, "category": "기초의학실습"},
    {"year": "예과2", "sem": "1학기", "code": "221281", "type": "전필", "name": "분자와세포의학1(생화학/세포)", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "예과2", "sem": "1학기", "code": "222701", "type": "전필", "name": "생리학1(한방생리)", "credit": 3, "theory": 4, "lab": 0, "category": "기초한의학"},
    {"year": "예과2", "sem": "1학기", "code": "221301", "type": "전필", "name": "인체의구조와기능2(해부학)", "credit": 3, "theory": 4, "lab": 0, "category": "기초의학"},
    {"year": "예과2", "sem": "1학기", "code": "221305", "type": "전필", "name": "분자와세포의학2", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "예과2", "sem": "1학기", "code": "221276", "type": "전선", "name": "의학중국어", "credit": 2, "theory": 2, "lab": 0, "category": "어학/교양"},
    {"year": "예과2", "sem": "1학기", "code": "221277", "type": "전선", "name": "경서강독", "credit": 2, "theory": 2, "lab": 0, "category": "원전문헌"},

    # 예과 2학년 2학기
    {"year": "예과2", "sem": "2학기", "code": "221271", "type": "전필", "name": "원전학2", "credit": 3, "theory": 4, "lab": 0, "category": "기초한의학(원전/이론)"},
    {"year": "예과2", "sem": "2학기", "code": "221282", "type": "전필", "name": "인체의구조와기능실습2(해부실습)", "credit": 1, "theory": 0, "lab": 2, "category": "기초의학실습"},
    {"year": "예과2", "sem": "2학기", "code": "221283", "type": "전필", "name": "의학통계학", "credit": 2, "theory": 2, "lab": 0, "category": "의과학/통계"},
    {"year": "예과2", "sem": "2학기", "code": "221285", "type": "전필", "name": "기초의과학실습1", "credit": 1, "theory": 0, "lab": 2, "category": "기초의학실습"},
    {"year": "예과2", "sem": "2학기", "code": "221286", "type": "전필", "name": "한의과학기초실습", "credit": 1, "theory": 0, "lab": 2, "category": "기초한의학실습"},
    {"year": "예과2", "sem": "2학기", "code": "222702", "type": "전필", "name": "생리학2", "credit": 3, "theory": 4, "lab": 0, "category": "기초한의학"},
    {"year": "예과2", "sem": "2학기", "code": "221302", "type": "전필", "name": "인체의구조와기능3(조직/해부)", "credit": 3, "theory": 4, "lab": 0, "category": "기초의학"},
    {"year": "예과2", "sem": "2학기", "code": "221306", "type": "전필", "name": "분자와세포의학3", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "예과2", "sem": "2학기", "code": "221284", "type": "전선", "name": "의료교육학", "credit": 2, "theory": 2, "lab": 0, "category": "인문사회"},

    # 본과 1학년 1학기
    {"year": "본과1", "sem": "1학기", "code": "222125", "type": "전필", "name": "본초학실습1", "credit": 1, "theory": 0, "lab": 2, "category": "기초한의학실습"},
    {"year": "본과1", "sem": "1학기", "code": "222812", "type": "전필", "name": "경혈학1", "credit": 2, "theory": 3, "lab": 0, "category": "침구/경혈"},
    {"year": "본과1", "sem": "1학기", "code": "222813", "type": "전필", "name": "경혈학실습1", "credit": 1, "theory": 0, "lab": 2, "category": "침구/경혈실습"},
    {"year": "본과1", "sem": "1학기", "code": "222814", "type": "전필", "name": "본초학1", "credit": 3, "theory": 5, "lab": 0, "category": "기초한의학(본초)"},
    {"year": "본과1", "sem": "1학기", "code": "222815", "type": "전필", "name": "질병의원리와반응1(미생물/면역)", "credit": 2, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "본과1", "sem": "1학기", "code": "222816", "type": "전필", "name": "질병의원리와반응실습1", "credit": 1, "theory": 0, "lab": 2, "category": "기초의학실습"},
    {"year": "본과1", "sem": "1학기", "code": "222817", "type": "전필", "name": "상한론1", "credit": 2, "theory": 3, "lab": 0, "category": "기초한의학(원전/임상기초)"},
    {"year": "본과1", "sem": "1학기", "code": "222818", "type": "전필", "name": "의료윤리", "credit": 1, "theory": 2, "lab": 0, "category": "의료인문학"},
    {"year": "본과1", "sem": "1학기", "code": "222819", "type": "전선", "name": "한의학과경제", "credit": 1, "theory": 2, "lab": 0, "category": "인문사회"},
    {"year": "본과1", "sem": "1학기", "code": "222820", "type": "전선", "name": "의학기상학", "credit": 1, "theory": 2, "lab": 0, "category": "기초한의학"},

    # 본과 1학년 2학기
    {"year": "본과1", "sem": "2학기", "code": "222824", "type": "전필", "name": "임상본초학실습", "credit": 1, "theory": 0, "lab": 2, "category": "기초한의학실습"},
    {"year": "본과1", "sem": "2학기", "code": "222825", "type": "전필", "name": "임상본초학", "credit": 2, "theory": 3, "lab": 0, "category": "기초한의학(본초)"},
    {"year": "본과1", "sem": "2학기", "code": "222826", "type": "전필", "name": "경혈학2", "credit": 2, "theory": 3, "lab": 0, "category": "침구/경혈"},
    {"year": "본과1", "sem": "2학기", "code": "222827", "type": "전필", "name": "경혈학실습2", "credit": 1, "theory": 0, "lab": 2, "category": "침구/경혈실습"},
    {"year": "본과1", "sem": "2학기", "code": "222828", "type": "전필", "name": "질병의원리와반응2(양방병리)", "credit": 2, "theory": 3, "lab": 0, "category": "기초의학"},
    {"year": "본과1", "sem": "2학기", "code": "222829", "type": "전필", "name": "질병의원리와반응실습2", "credit": 1, "theory": 0, "lab": 2, "category": "기초의학실습"},
    {"year": "본과1", "sem": "2학기", "code": "222830", "type": "전필", "name": "상한론2", "credit": 2, "theory": 3, "lab": 0, "category": "기초한의학(원전/임상기초)"},
    {"year": "본과1", "sem": "2학기", "code": "222831", "type": "전필", "name": "의료정보학", "credit": 1, "theory": 2, "lab": 0, "category": "정보/AI/데이터"},
    {"year": "본과1", "sem": "2학기", "code": "222832", "type": "전필", "name": "방제학1", "credit": 3, "theory": 4, "lab": 0, "category": "기초한의학(방제)"},
    {"year": "본과1", "sem": "2학기", "code": "222833", "type": "전선", "name": "원전학3", "credit": 2, "theory": 2, "lab": 0, "category": "원전문헌"},
    {"year": "본과1", "sem": "2학기", "code": "222834", "type": "전선", "name": "뇌신경연구", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},

    # 본과 2학년 1학기
    {"year": "본과2", "sem": "1학기", "code": "222430", "type": "전필", "name": "한방병리학실습1", "credit": 1, "theory": 0, "lab": 2, "category": "기초한의학실습"},
    {"year": "본과2", "sem": "1학기", "code": "222636", "type": "전필", "name": "방제학실습", "credit": 1, "theory": 0, "lab": 2, "category": "기초한의학실습"},
    {"year": "본과2", "sem": "1학기", "code": "222637", "type": "전필", "name": "방제학2", "credit": 3, "theory": 4, "lab": 0, "category": "기초한의학(방제)"},
    {"year": "본과2", "sem": "1학기", "code": "222703", "type": "전필", "name": "병리학1(한방병리)", "credit": 3, "theory": 5, "lab": 0, "category": "기초한의학"},
    {"year": "본과2", "sem": "1학기", "code": "222704", "type": "전필", "name": "양방병리학1", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "본과2", "sem": "1학기", "code": "222728", "type": "전필", "name": "약리학1(양방약리)", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "본과2", "sem": "1학기", "code": "222729", "type": "전필", "name": "약리학실습1", "credit": 1, "theory": 0, "lab": 2, "category": "기초의학실습"},
    {"year": "본과2", "sem": "1학기", "code": "222731", "type": "전필", "name": "경혈학3", "credit": 1, "theory": 2, "lab": 0, "category": "침구/경혈"},
    {"year": "본과2", "sem": "1학기", "code": "222732", "type": "전필", "name": "질병의예방과관리1(예방의학)", "credit": 2, "theory": 2, "lab": 0, "category": "예방의학/보건"},
    {"year": "본과2", "sem": "1학기", "code": "222808", "type": "전선", "name": "한의산업학", "credit": 1, "theory": 2, "lab": 0, "category": "인문사회/산업"},

    # 본과 2학년 2학기
    {"year": "본과2", "sem": "2학기", "code": "222436", "type": "전필", "name": "한방병리학실습2", "credit": 1, "theory": 0, "lab": 2, "category": "기초한의학실습"},
    {"year": "본과2", "sem": "2학기", "code": "222445", "type": "전필", "name": "응급의학", "credit": 1, "theory": 2, "lab": 0, "category": "임상의학"},
    {"year": "본과2", "sem": "2학기", "code": "222645", "type": "전필", "name": "방제학3(처방구성)", "credit": 3, "theory": 4, "lab": 0, "category": "기초한의학(방제)"},
    {"year": "본과2", "sem": "2학기", "code": "222646", "type": "전필", "name": "영상의학", "credit": 1, "theory": 2, "lab": 0, "category": "임상의학(영상)"},
    {"year": "본과2", "sem": "2학기", "code": "222653", "type": "전필", "name": "온병학", "credit": 1, "theory": 2, "lab": 0, "category": "기초한의학(원전)"},
    {"year": "본과2", "sem": "2학기", "code": "222705", "type": "전필", "name": "병리학2(한방병리)", "credit": 3, "theory": 5, "lab": 0, "category": "기초한의학"},
    {"year": "본과2", "sem": "2학기", "code": "222706", "type": "전필", "name": "양방병리학2", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "본과2", "sem": "2학기", "code": "222730", "type": "전필", "name": "약리학2(양방약리)", "credit": 1, "theory": 2, "lab": 0, "category": "기초의학"},
    {"year": "본과2", "sem": "2학기", "code": "222731", "type": "전필", "name": "약리학실습2", "credit": 1, "theory": 0, "lab": 2, "category": "기초의학실습"},
    {"year": "본과2", "sem": "2학기", "code": "222733", "type": "전필", "name": "진단학1(한방진단)", "credit": 2, "theory": 3, "lab": 0, "category": "임상진단"},
    {"year": "본과2", "sem": "2학기", "code": "222734", "type": "전필", "name": "침구의학1", "credit": 2, "theory": 3, "lab": 0, "category": "임상침구"},
    {"year": "본과2", "sem": "2학기", "code": "222735", "type": "전필", "name": "사상체질의학1", "credit": 1, "theory": 2, "lab": 0, "category": "사상의학"},
    {"year": "본과2", "sem": "2학기", "code": "222736", "type": "전필", "name": "한방재활의학1", "credit": 1, "theory": 2, "lab": 0, "category": "임상한의학(재활)"},
    {"year": "본과2", "sem": "2학기", "code": "222502", "type": "전선", "name": "법의학", "credit": 1, "theory": 2, "lab": 0, "category": "의료인문/법의학"},
    {"year": "본과2", "sem": "2학기", "code": "222809", "type": "전선", "name": "한의약연구방법론", "credit": 1, "theory": 2, "lab": 0, "category": "연구/통계"},

    # 본과 3학년 1학기
    {"year": "본과3", "sem": "1학기", "code": "222685", "type": "전필", "name": "진단검사의학1", "credit": 1, "theory": 2, "lab": 0, "category": "임상의학(검사)"},
    {"year": "본과3", "sem": "1학기", "code": "222796", "type": "전필", "name": "진단학2", "credit": 1, "theory": 2, "lab": 0, "category": "임상진단"},
    {"year": "본과3", "sem": "1학기", "code": "222738", "type": "전필", "name": "진단학실습", "credit": 1, "theory": 0, "lab": 2, "category": "임상진단실습"},
    {"year": "본과3", "sem": "1학기", "code": "222739", "type": "전필", "name": "침구의학2", "credit": 3, "theory": 4, "lab": 0, "category": "임상침구"},
    {"year": "본과3", "sem": "1학기", "code": "222740", "type": "전필", "name": "사상체질의학2", "credit": 1.5, "theory": 3, "lab": 0, "category": "사상의학"},
    {"year": "본과3", "sem": "1학기", "code": "222741", "type": "전필", "name": "한방재활의학2", "credit": 1.5, "theory": 3, "lab": 0, "category": "임상한의학(재활)"},
    {"year": "본과3", "sem": "1학기", "code": "222742", "type": "전필", "name": "간계내과학1", "credit": 1, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "1학기", "code": "222743", "type": "전필", "name": "심계내과학1", "credit": 1, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "1학기", "code": "222744", "type": "전필", "name": "비계내과학1", "credit": 1, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "1학기", "code": "222745", "type": "전필", "name": "폐계내과학1", "credit": 1, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "1학기", "code": "222746", "type": "전필", "name": "신계내과학1", "credit": 1, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "1학기", "code": "222747", "type": "전필", "name": "한방소아과학1", "credit": 1, "theory": 2, "lab": 0, "category": "임상소아"},
    {"year": "본과3", "sem": "1학기", "code": "222748", "type": "전필", "name": "한방부인과학1", "credit": 3, "theory": 4, "lab": 0, "category": "임상부인"},
    {"year": "본과3", "sem": "1학기", "code": "222749", "type": "전필", "name": "한방안이비인후피부과학1", "credit": 2, "theory": 3, "lab": 0, "category": "임상안이비피부"},
    {"year": "본과3", "sem": "1학기", "code": "222750", "type": "전필", "name": "한방신경정신과학1", "credit": 1, "theory": 2, "lab": 0, "category": "임상정신"},
    {"year": "본과3", "sem": "1학기", "code": "222794", "type": "전필", "name": "추나의학", "credit": 1, "theory": 2, "lab": 0, "category": "임상추나"},

    # 본과 3학년 2학기
    {"year": "본과3", "sem": "2학기", "code": "222659", "type": "전필", "name": "양방진단학", "credit": 1.5, "theory": 2, "lab": 0, "category": "임상의학(진단)"},
    {"year": "본과3", "sem": "2학기", "code": "222699", "type": "전필", "name": "진단검사의학2", "credit": 1, "theory": 2, "lab": 0, "category": "임상의학(검사)"},
    {"year": "본과3", "sem": "2학기", "code": "222751", "type": "전필", "name": "침구의학3", "credit": 3, "theory": 6, "lab": 0, "category": "임상침구"},
    {"year": "본과3", "sem": "2학기", "code": "222752", "type": "전필", "name": "간계내과학2", "credit": 1.5, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "2학기", "code": "222753", "type": "전필", "name": "심계내과학2", "credit": 1.5, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "2학기", "code": "222754", "type": "전필", "name": "비계내과학2", "credit": 1.5, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "2학기", "code": "222755", "type": "전필", "name": "폐계내과학2", "credit": 1.5, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "2학기", "code": "222756", "type": "전필", "name": "신계내과학2", "credit": 1.5, "theory": 2, "lab": 0, "category": "임상내과"},
    {"year": "본과3", "sem": "2학기", "code": "222757", "type": "전필", "name": "한방소아과학2", "credit": 2, "theory": 3, "lab": 0, "category": "임상소아"},
    {"year": "본과3", "sem": "2학기", "code": "222758", "type": "전필", "name": "한방부인과학2", "credit": 2, "theory": 3, "lab": 0, "category": "임상부인"},
    {"year": "본과3", "sem": "2학기", "code": "222759", "type": "전필", "name": "한방안이비인후피부과학2", "credit": 2, "theory": 3, "lab": 0, "category": "임상안이비피부"},
    {"year": "본과3", "sem": "2학기", "code": "222760", "type": "전필", "name": "한방신경정신과학2", "credit": 2, "theory": 3, "lab": 0, "category": "임상정신"},
    {"year": "본과3", "sem": "2학기", "code": "222795", "type": "전필", "name": "추나의학실습", "credit": 1, "theory": 0, "lab": 2, "category": "임상추나실습"},
    {"year": "본과3", "sem": "2학기", "code": "222810", "type": "전필", "name": "임상술기실습1", "credit": 1.5, "theory": 0, "lab": 3, "category": "임상술기실습"},

    # 본과 4학년 1학기
    {"year": "본과4", "sem": "1학기", "code": "222798", "type": "전필", "name": "원외실습1", "credit": 3.5, "theory": 0, "lab": 7.5, "category": "원외임상실습"},
    {"year": "본과4", "sem": "1학기", "code": "222799", "type": "전필", "name": "임상각과실습A-1", "credit": 5, "theory": 0, "lab": 10, "category": "병원임상실습"},
    {"year": "본과4", "sem": "1학기", "code": "222800", "type": "전필", "name": "임상각과실습B-1", "credit": 5, "theory": 0, "lab": 10, "category": "병원임상실습"},
    {"year": "본과4", "sem": "1학기", "code": "222801", "type": "전필", "name": "임상각과실습C-1", "credit": 5, "theory": 0, "lab": 10, "category": "병원임상실습"},
    {"year": "본과4", "sem": "1학기", "code": "001175", "type": "전필", "name": "졸업논문", "credit": 0, "theory": 0, "lab": 0, "category": "논문"},

    # 본과 4학년 2학기
    {"year": "본과4", "sem": "2학기", "code": "222811", "type": "전필", "name": "임상술기실습2", "credit": 3.5, "theory": 0, "lab": 7, "category": "임상술기실습"},
    {"year": "본과4", "sem": "2학기", "code": "222803", "type": "전필", "name": "원외실습2", "credit": 1.5, "theory": 0, "lab": 2.5, "category": "원외임상실습"},
    {"year": "본과4", "sem": "2학기", "code": "222804", "type": "전필", "name": "임상각과실습A-2", "credit": 5, "theory": 0, "lab": 10, "category": "병원임상실습"},
    {"year": "본과4", "sem": "2학기", "code": "222805", "type": "전필", "name": "임상각과실습B-2", "credit": 5, "theory": 0, "lab": 10, "category": "병원임상실습"},
    {"year": "본과4", "sem": "2학기", "code": "222806", "type": "전필", "name": "임상각과실습C-2", "credit": 5, "theory": 0, "lab": 10, "category": "병원임상실습"}
]

df_curriculum = pd.DataFrame(courses)
df_curriculum.to_excel(r"d:\행정\한의학 교육과 의료 통합\01_교육과정_혁신로드맵\분석자료\wonkwang_curriculum_master.xlsx", index=False)
print(f"Master curriculum created with {len(df_curriculum)} courses.")
print(df_curriculum.groupby("category")[["credit", "theory", "lab"]].sum())
