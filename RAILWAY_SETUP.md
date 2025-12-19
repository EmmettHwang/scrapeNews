# 🚂 Railway 배포 - 단계별 실행 가이드

이 가이드를 따라하시면 5-10분 안에 배포를 완료하실 수 있습니다!

---

## 📋 배포 전 체크리스트

배포하기 전에 다음 정보를 준비해주세요:

### 필수 환경변수 값
```
GOOGLE_API_KEY=실제_구글_API_키
TELEGRAM_TOKEN=실제_텔레그램_봇_토큰
TELEGRAM_CHAT_ID=실제_채팅_ID
DB_PASSWORD=실제_데이터베이스_비밀번호
```

⚠️ **중요**: 이 값들은 `.env` 파일에 있거나, 현재 사용 중인 값들입니다.

---

## 🚀 Step 1: Railway 계정 생성 (1분)

1. **Railway 웹사이트 접속**
   - 브라우저에서 [https://railway.app](https://railway.app) 열기

2. **GitHub로 로그인**
   - 우측 상단 **"Login"** 버튼 클릭
   - **"Login with GitHub"** 선택
   - GitHub 계정으로 인증

3. **Railway 권한 승인**
   - GitHub에서 Railway 접근 권한 요청이 나타나면 **"Authorize Railway"** 클릭

---

## 🎯 Step 2: 프로젝트 생성 (2분)

1. **새 프로젝트 시작**
   - Railway 대시보드에서 **"New Project"** 버튼 클릭
   - 또는 **"Start a New Project"** 클릭

2. **GitHub 저장소 연결**
   - **"Deploy from GitHub repo"** 선택
   - 저장소 목록에서 **`EmmettHwang/scrapeNews`** 찾아서 선택
   
   > 💡 저장소가 보이지 않는 경우:
   > - **"Configure GitHub App"** 클릭
   > - Railway가 저장소에 접근할 수 있도록 권한 부여
   > - `scrapeNews` 저장소 선택 후 저장

3. **배포 시작**
   - 저장소 선택 후 자동으로 배포가 시작됩니다
   - 빌드 로그를 확인할 수 있습니다

---

## ⚙️ Step 3: 환경변수 설정 (3분)

이 단계가 가장 중요합니다! ⚠️

1. **Variables 탭 열기**
   - 프로젝트 대시보드에서 왼쪽 사이드바의 프로젝트 이름 클릭
   - 상단 탭에서 **"Variables"** 클릭

2. **환경변수 추가하기**
   
   각 변수를 하나씩 추가합니다:
   
   **a) GOOGLE_API_KEY 추가**
   - **"New Variable"** 버튼 클릭
   - Variable name: `GOOGLE_API_KEY`
   - Variable value: `실제_구글_API_키_값`
   - **"Add"** 클릭

   **b) TELEGRAM_TOKEN 추가**
   - **"New Variable"** 버튼 클릭
   - Variable name: `TELEGRAM_TOKEN`
   - Variable value: `실제_텔레그램_봇_토큰`
   - **"Add"** 클릭

   **c) TELEGRAM_CHAT_ID 추가**
   - **"New Variable"** 버튼 클릭
   - Variable name: `TELEGRAM_CHAT_ID`
   - Variable value: `실제_채팅_ID`
   - **"Add"** 클릭

   **d) DB_PASSWORD 추가**
   - **"New Variable"** 버튼 클릭
   - Variable name: `DB_PASSWORD`
   - Variable value: `실제_데이터베이스_비밀번호`
   - **"Add"** 클릭

3. **자동 재배포**
   - 환경변수를 추가하면 자동으로 재배포가 시작됩니다
   - 약 1-2분 정도 소요됩니다

---

## 🌐 Step 4: 도메인 설정 및 접속 (1분)

1. **Settings 탭으로 이동**
   - 상단 탭에서 **"Settings"** 클릭

2. **Public Networking 섹션 찾기**
   - 아래로 스크롤하여 **"Networking"** 섹션 찾기

3. **도메인 생성**
   - **"Generate Domain"** 버튼 클릭
   - Railway가 자동으로 도메인 생성 (예: `scrapnews-production.up.railway.app`)

4. **웹사이트 접속**
   - 생성된 도메인 URL을 클릭하여 웹사이트 확인!
   - 🎉 배포 완료!

---

## ✅ Step 5: 배포 확인 및 테스트 (2분)

### 1. 웹사이트 접속 테스트
- 생성된 Railway URL로 접속
- 메인 페이지가 정상적으로 로드되는지 확인

### 2. 데이터베이스 연결 확인
- 페이지에 기존 뉴스 목록이 표시되는지 확인
- 만약 표시되지 않으면 **"뉴스 분석 시작"** 버튼 클릭

### 3. 스크래핑 기능 테스트
- **"뉴스 분석 시작"** 버튼 클릭
- 새로운 뉴스가 수집되는지 확인
- 텔레그램으로 알림이 오는지 확인

### 4. 로그 확인 (문제 발생 시)
- Railway 대시보드의 **"Deployments"** 탭 클릭
- 최신 배포를 클릭하여 로그 확인
- 에러 메시지가 있는지 확인

---

## 🐛 문제 해결

### 문제 1: 배포가 실패하는 경우
**증상**: Build failed 또는 Deploy failed

**해결 방법**:
1. **"Deployments"** 탭에서 에러 로그 확인
2. 가장 흔한 원인:
   - `requirements.txt` 패키지 설치 실패
   - Python 버전 불일치
3. 로그에서 에러 메시지 확인 후 재배포

### 문제 2: 웹사이트가 열리지 않는 경우
**증상**: 도메인 접속 시 "Application failed to respond" 또는 502 에러

**해결 방법**:
1. 환경변수가 모두 설정되었는지 확인
2. **"Deployments"** 탭에서 최신 배포 상태 확인
3. 로그에서 `Uvicorn running on` 메시지가 있는지 확인
4. 재배포: **"Deployments"** → **"Redeploy"** 버튼 클릭

### 문제 3: 데이터베이스 연결 오류
**증상**: 페이지는 열리지만 뉴스가 표시되지 않음, 로그에 DB 에러

**해결 방법**:
1. `DB_PASSWORD` 환경변수가 올바른지 확인
2. MySQL 서버(`bitnmeta2.synology.me:3307`)가 외부 접속을 허용하는지 확인
3. 방화벽에서 Railway의 IP를 허용해야 할 수 있음

### 문제 4: 환경변수가 적용되지 않는 경우
**증상**: 환경변수를 추가했는데도 앱이 인식하지 못함

**해결 방법**:
1. 변수 이름에 오타가 없는지 확인 (대소문자 구분!)
2. 변수 값에 공백이나 따옴표가 불필요하게 포함되지 않았는지 확인
3. 환경변수 추가 후 **자동 재배포 대기** (1-2분)
4. 수동 재배포: **"Deployments"** → **"Redeploy"**

---

## 💡 유용한 팁

### 1. 실시간 로그 확인
```
Railway 대시보드 → 프로젝트 선택 → Deployments 탭 → 최신 배포 클릭
```
- 실시간으로 앱 로그를 확인할 수 있습니다
- 에러 디버깅에 매우 유용합니다

### 2. 자동 재배포 비활성화
개발 중에 GitHub에 push할 때마다 재배포되는 것이 싫다면:
```
Settings 탭 → Deploy Triggers → "Watch Paths" 설정
```

### 3. 커스텀 도메인 연결
Railway 기본 도메인 대신 자신의 도메인을 사용하려면:
```
Settings 탭 → Networking → Custom Domain → 도메인 추가
```

### 4. 무료 플랜 사용량 확인
```
Account Settings → Usage → 현재 월 사용량 확인
```
- 월 $5 크레딧 제공
- 약 500시간 실행 가능
- 트래픽이 적으면 충분히 무료로 사용 가능

### 5. 앱 중지 (비용 절약)
사용하지 않을 때 앱을 중지하려면:
```
프로젝트 대시보드 → Settings → Danger → "Remove Service"
```
⚠️ 주의: 완전히 삭제되므로, 재배포 필요 시 처음부터 설정해야 함

---

## 📊 배포 후 모니터링

### 1. 앱 상태 확인
- Railway 대시보드에서 실시간으로 상태 확인 가능
- 초록색: 정상 실행 중
- 빨간색: 에러 발생

### 2. 리소스 사용량
- CPU, 메모리 사용량 그래프 제공
- 과도한 사용 시 알림

### 3. 배포 히스토리
- 모든 배포 기록 저장
- 이전 버전으로 롤백 가능

---

## 🎓 다음 단계

배포가 완료되었다면:

1. ✅ **URL 공유**: 생성된 Railway URL을 친구들과 공유
2. ✅ **자동화 설정**: GitHub Actions로 정기적인 스크래핑 자동화
3. ✅ **모니터링 추가**: UptimeRobot으로 앱 상태 모니터링
4. ✅ **커스텀 도메인**: 자신만의 도메인 연결

---

## 📞 도움이 필요하신가요?

- [Railway 공식 문서](https://docs.railway.app)
- [Railway Discord 커뮤니티](https://discord.gg/railway)
- [Railway 서포트](https://railway.app/help)

---

## 🎉 축하합니다!

Railway 배포가 완료되었습니다! 

**배포된 URL**: `https://your-app-name.up.railway.app`

이제 전 세계 어디서나 당신의 AI 뉴스 스크래핑 앱에 접속할 수 있습니다! 🚀
