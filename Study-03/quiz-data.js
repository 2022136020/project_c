const QUIZ_DATA = [
  // ===== 한국사 =====
  {
    id: 'KH-001', category: '한국사', difficulty: '쉬움',
    question: '훈민정음을 창제한 조선의 왕은?',
    choices: ['태종', '세종대왕', '성종', '중종'],
    answer: 1,
    explanation: '세종대왕은 1443년 훈민정음을 창제하고 1446년 반포하였습니다.'
  },
  {
    id: 'KH-002', category: '한국사', difficulty: '쉬움',
    question: '고려를 건국한 인물은?',
    choices: ['이성계', '왕건', '궁예', '견훤'],
    answer: 1,
    explanation: '왕건은 918년 고려를 건국하고 초대 태조가 되었습니다.'
  },
  {
    id: 'KH-003', category: '한국사', difficulty: '쉬움',
    question: '3·1 운동이 일어난 연도는?',
    choices: ['1910년', '1919년', '1945년', '1905년'],
    answer: 1,
    explanation: '3·1 운동은 1919년 3월 1일 일제 강점기에 일어난 독립운동입니다.'
  },
  {
    id: 'KH-004', category: '한국사', difficulty: '보통',
    question: '임진왜란이 발생한 연도는?',
    choices: ['1510년', '1592년', '1627년', '1636년'],
    answer: 1,
    explanation: '임진왜란은 1592년 일본의 조선 침략으로 시작된 7년 전쟁입니다.'
  },
  {
    id: 'KH-005', category: '한국사', difficulty: '보통',
    question: '조선이 건국된 연도는?',
    choices: ['1388년', '1392년', '1400년', '1418년'],
    answer: 1,
    explanation: '이성계는 1392년 조선을 건국하고 태조가 되었습니다.'
  },
  {
    id: 'KH-006', category: '한국사', difficulty: '보통',
    question: '대한민국 임시정부가 처음 수립된 도시는?',
    choices: ['베이징', '도쿄', '상하이', '충칭'],
    answer: 2,
    explanation: '대한민국 임시정부는 1919년 4월 중국 상하이에서 수립되었습니다.'
  },
  {
    id: 'KH-007', category: '한국사', difficulty: '보통',
    question: '을사늑약이 체결된 연도는?',
    choices: ['1895년', '1905년', '1910년', '1919년'],
    answer: 1,
    explanation: '을사늑약은 1905년 일제가 대한제국의 외교권을 박탈하기 위해 강제 체결한 조약입니다.'
  },
  {
    id: 'KH-008', category: '한국사', difficulty: '어려움',
    question: '고구려에 불교를 공식 수용한 왕은?',
    choices: ['장수왕', '광개토대왕', '소수림왕', '미천왕'],
    answer: 2,
    explanation: '소수림왕은 372년 전진(前秦)으로부터 불교를 공식 수용하였습니다.'
  },
  {
    id: 'KH-009', category: '한국사', difficulty: '어려움',
    question: '신라가 삼국 통일을 완성한 연도는?',
    choices: ['660년', '668년', '676년', '698년'],
    answer: 2,
    explanation: '신라는 676년 당나라 군대를 매소성·기벌포 전투에서 격파하고 삼국 통일을 완성하였습니다.'
  },
  {
    id: 'KH-010', category: '한국사', difficulty: '어려움',
    question: '조선 시대 최초로 설립된 서원으로, 경상북도 영주에 위치한 곳은?',
    choices: ['도산서원', '병산서원', '소수서원', '옥산서원'],
    answer: 2,
    explanation: '소수서원(백운동서원)은 1543년 풍기 군수 주세붕이 설립한 조선 최초의 서원입니다.'
  },

  // ===== 과학 =====
  {
    id: 'SC-001', category: '과학', difficulty: '쉬움',
    question: '물의 화학식은?',
    choices: ['CO₂', 'H₂O', 'NaCl', 'O₂'],
    answer: 1,
    explanation: '물은 수소 원자 2개와 산소 원자 1개로 이루어진 H₂O입니다.'
  },
  {
    id: 'SC-002', category: '과학', difficulty: '쉬움',
    question: '진공 중 빛의 속도는 약 몇 km/s인가?',
    choices: ['약 3만 km/s', '약 30만 km/s', '약 300만 km/s', '약 3,000만 km/s'],
    answer: 1,
    explanation: '진공 중 빛의 속도는 약 299,792 km/s로, 흔히 약 30만 km/s로 표현합니다.'
  },
  {
    id: 'SC-003', category: '과학', difficulty: '쉬움',
    question: '주기율표에서 원자번호 1번 원소는?',
    choices: ['헬륨(He)', '수소(H)', '리튬(Li)', '탄소(C)'],
    answer: 1,
    explanation: '원자번호 1번은 수소(H)로, 우주에서 가장 풍부한 원소입니다.'
  },
  {
    id: 'SC-004', category: '과학', difficulty: '보통',
    question: 'DNA의 이중나선 구조를 처음 규명한 과학자들은?',
    choices: ['아인슈타인과 보어', '왓슨과 크릭', '퀴리와 다윈', '뉴턴과 갈릴레이'],
    answer: 1,
    explanation: '제임스 왓슨과 프랜시스 크릭은 1953년 DNA의 이중나선 구조를 규명하였습니다.'
  },
  {
    id: 'SC-005', category: '과학', difficulty: '보통',
    question: '뉴턴의 운동 제3법칙은?',
    choices: ['관성의 법칙', '가속도의 법칙', '작용·반작용의 법칙', '만유인력의 법칙'],
    answer: 2,
    explanation: '뉴턴의 운동 제3법칙은 작용·반작용의 법칙으로, 두 물체 사이의 힘은 크기가 같고 방향이 반대입니다.'
  },
  {
    id: 'SC-006', category: '과학', difficulty: '보통',
    question: '원자핵을 구성하는 두 입자는?',
    choices: ['전자와 양성자', '양성자와 중성자', '중성자와 전자', '쿼크와 렙톤'],
    answer: 1,
    explanation: '원자핵은 양성자(+)와 중성자(전하 없음)로 구성되며, 전자는 핵 바깥을 돌고 있습니다.'
  },
  {
    id: 'SC-007', category: '과학', difficulty: '보통',
    question: '전자기파 중 파장이 가장 짧은 것은?',
    choices: ['라디오파', '가시광선', '자외선', '감마선'],
    answer: 3,
    explanation: '감마선은 전자기파 중 파장이 가장 짧고 에너지가 가장 높습니다.'
  },
  {
    id: 'SC-008', category: '과학', difficulty: '어려움',
    question: '20°C 공기 중에서 소리의 속도는 약 몇 m/s인가?',
    choices: ['약 240 m/s', '약 343 m/s', '약 500 m/s', '약 1,220 m/s'],
    answer: 1,
    explanation: '20°C 공기 중 소리의 속도는 약 343 m/s입니다. 온도가 높아질수록 소리의 속도도 빨라집니다.'
  },
  {
    id: 'SC-009', category: '과학', difficulty: '어려움',
    question: '태양계에서 행성의 수는? (2006년 국제천문연맹 결의 기준)',
    choices: ['7개', '8개', '9개', '10개'],
    answer: 1,
    explanation: '2006년 IAU(국제천문연맹)는 명왕성을 왜소행성으로 재분류하여 태양계 행성을 8개로 정했습니다.'
  },
  {
    id: 'SC-010', category: '과학', difficulty: '어려움',
    question: '국제단위계(SI)에서 전기 저항의 단위는?',
    choices: ['볼트(V)', '암페어(A)', '와트(W)', '옴(Ω)'],
    answer: 3,
    explanation: '전기 저항의 SI 단위는 옴(Ω)으로, 독일 물리학자 게오르크 옴의 이름에서 유래하였습니다.'
  },

  // ===== 지리 =====
  {
    id: 'GE-001', category: '지리', difficulty: '쉬움',
    question: '국토 면적 기준 세계에서 가장 넓은 나라는? (2024년 기준)',
    choices: ['캐나다', '미국', '러시아', '중국'],
    answer: 2,
    explanation: '러시아는 약 1,710만 km²로 국토 면적 기준 세계에서 가장 넓은 나라입니다. (2024년 기준)'
  },
  {
    id: 'GE-002', category: '지리', difficulty: '쉬움',
    question: '인구 기준 세계에서 가장 많은 나라는? (2024년 기준)',
    choices: ['중국', '인도', '미국', '인도네시아'],
    answer: 1,
    explanation: '인도는 2024년 기준 약 14억 4천만 명으로 세계에서 인구가 가장 많은 나라입니다.'
  },
  {
    id: 'GE-003', category: '지리', difficulty: '쉬움',
    question: '해발고도 기준 세계에서 가장 높은 산은?',
    choices: ['K2', '에베레스트산', '칸첸중가', '로체'],
    answer: 1,
    explanation: '에베레스트산(해발 8,849m)은 해발고도 기준 세계에서 가장 높은 산입니다.'
  },
  {
    id: 'GE-004', category: '지리', difficulty: '쉬움',
    question: '아마존강이 위치한 대륙은?',
    choices: ['아프리카', '아시아', '북아메리카', '남아메리카'],
    answer: 3,
    explanation: '아마존강은 남아메리카에 위치하며, 유량 기준 세계 최대의 강입니다.'
  },
  {
    id: 'GE-005', category: '지리', difficulty: '보통',
    question: '길이 기준 아프리카에서 가장 긴 강은?',
    choices: ['콩고강', '나일강', '니제르강', '잠베지강'],
    answer: 1,
    explanation: '나일강은 약 6,650km로 길이 기준 아프리카에서 가장 긴 강입니다.'
  },
  {
    id: 'GE-006', category: '지리', difficulty: '보통',
    question: '태평양과 대서양을 잇는 파나마 운하가 위치한 나라는?',
    choices: ['콜롬비아', '코스타리카', '파나마', '니카라과'],
    answer: 2,
    explanation: '파나마 운하는 중앙아메리카의 파나마에 위치하며 태평양과 대서양을 연결합니다.'
  },
  {
    id: 'GE-007', category: '지리', difficulty: '보통',
    question: '면적 기준 세계에서 가장 넓은 대양은?',
    choices: ['대서양', '인도양', '태평양', '북극해'],
    answer: 2,
    explanation: '태평양은 약 1억 6,525만 km²로 세계에서 가장 넓은 대양입니다.'
  },
  {
    id: 'GE-008', category: '지리', difficulty: '보통',
    question: '한국에서 면적이 가장 넓은 도(道)는? (2024년 기준)',
    choices: ['전라남도', '경상남도', '강원도', '경상북도'],
    answer: 3,
    explanation: '경상북도는 약 19,030 km²로 대한민국에서 면적이 가장 넓은 도입니다. (2024년 기준)'
  },
  {
    id: 'GE-009', category: '지리', difficulty: '어려움',
    question: '한반도에서 길이가 가장 긴 강은?',
    choices: ['한강', '낙동강', '압록강', '두만강'],
    answer: 2,
    explanation: '압록강은 약 803km로 한반도에서 가장 긴 강입니다.'
  },
  {
    id: 'GE-010', category: '지리', difficulty: '어려움',
    question: '세계에서 수심이 가장 깊은 호수는?',
    choices: ['카스피해', '슈피리어호', '바이칼호', '탕가니카호'],
    answer: 2,
    explanation: '러시아의 바이칼호는 최대 수심 약 1,642m로 세계에서 수심이 가장 깊은 호수입니다.'
  },

  // ===== 일반상식 =====
  {
    id: 'GK-001', category: '일반상식', difficulty: '쉬움',
    question: '하계 올림픽은 몇 년마다 열리는가?',
    choices: ['2년', '4년', '5년', '8년'],
    answer: 1,
    explanation: '하계 올림픽은 4년마다 개최됩니다.'
  },
  {
    id: 'GK-002', category: '일반상식', difficulty: '쉬움',
    question: '유엔(UN)의 본부가 위치한 도시는?',
    choices: ['워싱턴 D.C.', '제네바', '뉴욕', '파리'],
    answer: 2,
    explanation: '유엔(UN) 본부는 미국 뉴욕에 위치합니다.'
  },
  {
    id: 'GK-003', category: '일반상식', difficulty: '쉬움',
    question: 'FIFA 축구 월드컵은 몇 년마다 열리는가?',
    choices: ['2년', '3년', '4년', '5년'],
    answer: 2,
    explanation: 'FIFA 월드컵은 4년마다 개최됩니다.'
  },
  {
    id: 'GK-004', category: '일반상식', difficulty: '보통',
    question: '표준 피아노 건반의 총 개수는?',
    choices: ['76개', '80개', '84개', '88개'],
    answer: 3,
    explanation: '표준 피아노는 총 88개의 건반(흰건반 52개, 검은건반 36개)으로 구성됩니다.'
  },
  {
    id: 'GK-005', category: '일반상식', difficulty: '보통',
    question: '빛의 삼원색을 모두 합치면 어떤 색이 되는가?',
    choices: ['검정', '회색', '흰색', '노란색'],
    answer: 2,
    explanation: '빛의 삼원색(빨강·초록·파랑)을 모두 합치면 흰색이 됩니다.'
  },
  {
    id: 'GK-006', category: '일반상식', difficulty: '보통',
    question: '노벨 평화상 시상식이 열리는 도시는?',
    choices: ['스톡홀름', '코펜하겐', '헬싱키', '오슬로'],
    answer: 3,
    explanation: '노벨 평화상은 노르웨이 오슬로에서 시상됩니다. 다른 노벨상은 스웨덴 스톡홀름에서 시상됩니다.'
  },
  {
    id: 'GK-007', category: '일반상식', difficulty: '보통',
    question: '세계 최초의 인공위성 이름은?',
    choices: ['아폴로 1호', '스푸트니크 1호', '보스토크 1호', '익스플로러 1호'],
    answer: 1,
    explanation: '스푸트니크 1호는 1957년 소련이 발사한 세계 최초의 인공위성입니다.'
  },
  {
    id: 'GK-008', category: '일반상식', difficulty: '보통',
    question: '인터넷 국가 도메인 \'.jp\'는 어느 나라의 도메인인가?',
    choices: ['자메이카', '요르단', '일본', '인도네시아'],
    answer: 2,
    explanation: '.jp는 일본(Japan)의 국가 코드 최상위 도메인입니다.'
  },
  {
    id: 'GK-009', category: '일반상식', difficulty: '어려움',
    question: '세계 최초로 여성에게 국가 선거권을 부여한 나라는?',
    choices: ['미국', '영국', '뉴질랜드', '프랑스'],
    answer: 2,
    explanation: '뉴질랜드는 1893년 세계 최초로 여성에게 국가 선거권(참정권)을 부여하였습니다.'
  },
  {
    id: 'GK-010', category: '일반상식', difficulty: '어려움',
    question: '인체 내부 장기 중 질량 기준 가장 큰 장기는?',
    choices: ['심장', '간', '폐', '뇌'],
    answer: 1,
    explanation: '간(肝)은 성인 기준 약 1.2~1.5kg으로 인체 내부 장기 중 질량 기준 가장 큰 장기입니다.'
  }
];
