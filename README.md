# Gmail 이메일 분류 및 통계 프로그램

Gmail API를 사용하여 이메일을 자동으로 분류하고 통계를 생성하는 프로그램입니다.

**두 가지 사용 방법을 제공합니다:**
1. **웹 애플리케이션** ⭐ - 구글 로그인 후 브라우저에서 실시간 통계 확인 (권장)
2. **CLI (명령줄 도구)** - 터미널에서 직접 실행하여 CSV 및 차트 생성

## 주요 기능

- 구글 OAuth 로그인 (웹 버전)
- Gmail 이메일 자동 가져오기
- 라벨 기반 이메일 분류
- 발신자 도메인별 통계
- 읽음/읽지않음 상태 분석
- 중요/별표 표시 이메일 통계
- 실시간 인터랙티브 대시보드 (웹 버전)
- 차트 및 그래프 시각화
- CSV 파일로 결과 저장 (CLI 버전)

## 설치 방법

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Google Cloud 프로젝트 설정

#### 웹 애플리케이션을 사용하는 경우 (권장)

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 (또는 기존 프로젝트 선택)
3. **Gmail API 활성화**:
   - 좌측 메뉴 > API 및 서비스 > 라이브러리
   - "Gmail API" 검색 및 활성화

4. **OAuth 2.0 클라이언트 ID 생성 (웹 애플리케이션)**:
   - 좌측 메뉴 > API 및 서비스 > 사용자 인증 정보
   - "사용자 인증 정보 만들기" > "OAuth 클라이언트 ID"
   - 애플리케이션 유형: **웹 애플리케이션**
   - 이름 입력
   - **승인된 리디렉션 URI** 추가:
     - `http://localhost:5000/authorize`
   - 생성 후 클라이언트 ID와 클라이언트 보안 비밀번호 복사

5. **환경 변수 설정**:
   ```bash
   cp .env.example .env
   ```

   `.env` 파일을 편집하여 다음 정보를 입력:
   ```
   FLASK_SECRET_KEY=your-secret-key-here
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   APP_URL=http://localhost:5000
   ```

#### CLI를 사용하는 경우

1~3번은 동일
4. **OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)**:
   - 애플리케이션 유형: **데스크톱 앱**
   - JSON 파일 다운로드

5. **다운로드한 JSON 파일을 `credentials.json`으로 저장**
   ```bash
   mv ~/Downloads/client_secret_*.json credentials.json
   ```

---

## 사용법

## 방법 1: 웹 애플리케이션 (권장)

### 실행

```bash
python app.py
```

서버가 시작되면 브라우저에서 `http://localhost:5000`으로 접속합니다.

### 사용 방법

1. **홈페이지**에서 "Google 계정으로 로그인" 버튼 클릭
2. Google 계정 선택 및 권한 승인
3. **대시보드**로 자동 리디렉션
4. 분석 옵션 설정:
   - 분석할 이메일 개수 선택 (50, 100, 200, 500)
   - 선택적으로 Gmail 검색 쿼리 입력
5. "분석 시작" 버튼 클릭
6. 실시간으로 통계 및 차트 확인

### 웹 대시보드 기능

- **상태 요약 카드**: 총 이메일, 받은편지함, 읽지않음, 중요, 별표 개수
- **라벨별 통계 테이블**: 각 라벨의 세부 통계
- **인터랙티브 차트**:
  - 상위 10개 라벨 막대 차트
  - 읽음/읽지않음 도넛 차트
- **도메인 통계**: 발신자 도메인별 이메일 개수
- **라벨 목록**: Gmail의 모든 라벨 확인

---

## 방법 2: CLI (명령줄 도구)

### 기본 사용

```bash
python gmail_main.py
```

기본적으로 최근 100개의 이메일을 분석합니다.

### 고급 옵션

```bash
# 최대 200개 이메일 분석
python gmail_main.py --max 200

# 읽지 않은 이메일만 분석
python gmail_main.py --query "is:unread"

# 특정 발신자의 이메일만 분석
python gmail_main.py --query "from:example@gmail.com"

# 여러 조건 조합
python gmail_main.py --query "is:unread after:2024/01/01" --max 150

# 결과를 다른 폴더에 저장
python gmail_main.py --output results

# 시각화 차트 생성 안 함
python gmail_main.py --no-visualize

# CSV 파일 저장 안 함
python gmail_main.py --no-csv

# Gmail 라벨 목록만 출력
python gmail_main.py --list-labels
```

### Gmail 검색 쿼리 예제

| 쿼리 | 설명 |
|------|------|
| `is:unread` | 읽지 않은 이메일 |
| `is:starred` | 별표 표시된 이메일 |
| `is:important` | 중요 표시된 이메일 |
| `from:user@example.com` | 특정 발신자 |
| `to:me` | 나에게 온 이메일 |
| `subject:회의` | 제목에 '회의' 포함 |
| `has:attachment` | 첨부파일 있는 이메일 |
| `after:2024/01/01` | 2024년 1월 1일 이후 |
| `before:2024/12/31` | 2024년 12월 31일 이전 |
| `label:inbox` | 받은편지함의 이메일 |

쿼리는 AND, OR, NOT 연산자로 조합할 수 있습니다:
```bash
python gmail_main.py --query "from:boss@company.com is:unread"
python gmail_main.py --query "(from:alice@example.com OR from:bob@example.com)"
```

### CLI 출력 결과

프로그램 실행 후 `output/` 폴더에 다음 파일들이 생성됩니다:

**CSV 파일**
- `emails_list.csv`: 전체 이메일 목록
- `label_statistics.csv`: 라벨별 통계
- `domain_statistics.csv`: 도메인별 통계

**시각화 차트 (PNG)**
- `label_distribution.png`: 라벨별 이메일 분포
- `read_status.png`: 읽음/읽지않음 비율
- `domain_distribution.png`: 발신자 도메인 분포
- `status_summary.png`: 이메일 상태 요약

---

## 통계 항목

프로그램은 다음과 같은 통계를 제공합니다:

1. **이메일 상태 요약**
   - 총 이메일 수
   - 받은편지함, 읽지않음, 중요, 별표 개수
   - 읽지않음 비율

2. **라벨별 통계**
   - 각 라벨의 이메일 개수
   - 읽지않음/중요/별표 표시된 이메일 개수
   - 읽음 비율

3. **발신자 도메인 통계**
   - 도메인별 이메일 개수 (상위 20개)
   - 각 도메인의 읽지않음 이메일 개수

---

## 문제 해결

### 웹 애플리케이션 관련

#### "GOOGLE_CLIENT_ID가 설정되지 않았습니다" 오류

`.env` 파일이 올바르게 설정되었는지 확인하세요. `.env.example`을 참고하여 필요한 환경 변수를 모두 설정해야 합니다.

#### 로그인 후 "Redirect URI mismatch" 오류

Google Cloud Console에서 승인된 리디렉션 URI에 `http://localhost:5000/authorize`를 정확히 추가했는지 확인하세요.

#### 포트 변경

기본 포트는 5000입니다. 다른 포트를 사용하려면 `.env` 파일에서 `PORT` 환경 변수를 설정하고, Google Cloud Console의 리디렉션 URI도 함께 변경하세요.

### CLI 관련

#### "credentials.json 파일을 찾을 수 없습니다" 오류

Google Cloud Console에서 OAuth 2.0 클라이언트 ID (데스크톱 앱)를 생성하고 JSON 파일을 다운로드했는지 확인하세요.

#### 첫 실행 시 브라우저 로그인 창

첫 실행 시 Google 계정 로그인이 필요합니다. 로그인 후 `token.json` 파일이 생성되며, 이후 실행에서는 자동으로 인증됩니다.

### 공통

#### API 할당량 초과

Gmail API는 일일 할당량이 있습니다. 너무 많은 이메일을 한 번에 가져오면 할당량을 초과할 수 있습니다. 분석할 이메일 개수를 줄여보세요.

---

## 프로젝트 구조

```
.
├── app.py                  # Flask 웹 애플리케이션
├── web_gmail_classifier.py # 웹용 Gmail API 모듈
├── gmail_main.py           # CLI 메인 실행 파일
├── gmail_classifier.py     # CLI용 Gmail API 모듈
├── email_statistics.py     # 통계 계산 및 시각화 모듈
├── requirements.txt        # 필수 패키지 목록
├── .env.example            # 환경 변수 예제
├── .gitignore              # Git 무시 파일 목록
├── credentials.json        # OAuth 2.0 클라이언트 ID (CLI용, 직접 생성)
├── token.json              # CLI 인증 토큰 (자동 생성)
├── templates/              # HTML 템플릿
│   ├── base.html
│   ├── index.html
│   └── dashboard.html
├── static/                 # 정적 파일
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
└── output/                 # CLI 결과 출력 폴더 (자동 생성)
    ├── emails_list.csv
    ├── label_statistics.csv
    ├── domain_statistics.csv
    └── *.png
```

---

## 보안 주의사항

- `.env` 파일과 `credentials.json` 파일은 절대 Git에 커밋하지 마세요
- `FLASK_SECRET_KEY`는 프로덕션 환경에서 반드시 강력한 랜덤 값으로 변경하세요
- 프로덕션 환경에서는 HTTPS를 사용하세요
- Google Cloud Console에서 승인된 리디렉션 URI를 정확히 설정하세요

---

## 라이선스

MIT License

## 참고 자료

- [Gmail API 문서](https://developers.google.com/gmail/api)
- [Gmail API Python 퀵스타트](https://developers.google.com/gmail/api/quickstart/python)
- [Gmail 검색 연산자](https://support.google.com/mail/answer/7190)
- [Flask 문서](https://flask.palletsprojects.com/)
- [Chart.js 문서](https://www.chartjs.org/)
