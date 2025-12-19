# 🚀 Railway 배포 가이드

## Railway란?
Railway는 웹 애플리케이션을 쉽게 배포할 수 있는 클라우드 플랫폼입니다.
- **무료 플랜**: 월 $5 크레딧 제공 (약 500시간 실행)
- **자동 배포**: Git push하면 자동으로 배포됨
- **환경변수 관리**: .env 파일 내용을 웹에서 설정 가능

---

## 📋 배포 전 준비사항

### 1. Railway 계정 생성
1. [Railway.app](https://railway.app) 접속
2. **"Start a New Project"** 또는 **"Login with GitHub"** 클릭
3. GitHub 계정으로 로그인

### 2. 필요한 정보 준비
다음 환경변수 값들을 준비해주세요:
- `GOOGLE_API_KEY`: Google Gemini AI API 키
- `TELEGRAM_TOKEN`: 텔레그램 봇 토큰
- `TELEGRAM_CHAT_ID`: 텔레그램 채팅 ID
- `DB_PASSWORD`: MySQL 데이터베이스 비밀번호

---

## 🚢 배포 방법

### 방법 1: GitHub 저장소 연결 (추천)

1. **GitHub에 코드 푸시**
   ```bash
   git add .
   git commit -m "Railway 배포 준비"
   git push origin main
   ```

2. **Railway 프로젝트 생성**
   - Railway 대시보드에서 **"New Project"** 클릭
   - **"Deploy from GitHub repo"** 선택
   - 저장소 선택 (이 프로젝트)

3. **환경변수 설정**
   - 프로젝트 대시보드에서 **"Variables"** 탭 클릭
   - 다음 환경변수들을 추가:
     ```
     GOOGLE_API_KEY=실제_API_키
     TELEGRAM_TOKEN=실제_봇_토큰
     TELEGRAM_CHAT_ID=실제_채팅_ID
     DB_PASSWORD=실제_DB_비밀번호
     ```

4. **배포 완료!**
   - Railway가 자동으로 빌드 및 배포 진행
   - 배포 완료 후 생성된 URL 확인 (예: `https://your-app.railway.app`)

### 방법 2: Railway CLI 사용

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
railway init

# 환경변수 설정
railway variables set GOOGLE_API_KEY="your_key"
railway variables set TELEGRAM_TOKEN="your_token"
railway variables set TELEGRAM_CHAT_ID="your_chat_id"
railway variables set DB_PASSWORD="your_password"

# 배포
railway up
```

---

## ⚙️ 배포 후 설정

### 1. 도메인 확인
- Railway 대시보드에서 **"Settings"** → **"Domains"** 확인
- 기본 제공되는 `*.railway.app` 도메인 사용 가능
- 커스텀 도메인 연결도 가능

### 2. 로그 확인
- Railway 대시보드에서 **"Deployments"** 탭
- 실시간 로그 확인 가능

### 3. 자동 배포 설정
- GitHub에 push하면 자동으로 재배포됨
- `main` 브랜치가 기본 배포 브랜치

---

## 🔧 주요 설정 파일 설명

### `Procfile`
Railway가 애플리케이션을 실행하는 방법을 정의
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### `runtime.txt`
사용할 Python 버전 지정
```
python-3.12.11
```

### `requirements.txt`
필요한 Python 패키지 목록

---

## 🐛 문제 해결

### 배포가 실패하는 경우
1. **로그 확인**: Railway 대시보드의 "Deployments" 탭에서 에러 로그 확인
2. **환경변수 확인**: 모든 필수 환경변수가 설정되었는지 확인
3. **데이터베이스 연결**: DB_PASSWORD가 정확한지 확인

### 애플리케이션이 시작되지 않는 경우
- Procfile의 명령어가 올바른지 확인
- requirements.txt에 모든 패키지가 포함되었는지 확인
- 포트 번호가 `$PORT` 환경변수를 사용하는지 확인

### 데이터베이스 연결 오류
- MySQL 서버가 외부 접속을 허용하는지 확인
- 방화벽 설정 확인
- Railway의 IP가 MySQL 서버에 접근 가능한지 확인

---

## 💡 유용한 팁

1. **무료 플랜 관리**
   - Railway는 월 $5 크레딧 제공
   - 사용량은 대시보드에서 확인 가능
   - 트래픽이 적으면 충분히 무료로 사용 가능

2. **자동 재배포**
   - GitHub에 push하면 자동으로 재배포
   - 개발이 매우 편리함

3. **로컬 테스트**
   ```bash
   # 로컬에서 Railway 환경과 동일하게 테스트
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## 📞 지원

- [Railway 공식 문서](https://docs.railway.app)
- [Railway Discord 커뮤니티](https://discord.gg/railway)
- [GitHub Issues](https://github.com/railwayapp/railway/issues)

---

## ✅ 체크리스트

배포 전 확인사항:
- [ ] GitHub 저장소에 코드 push 완료
- [ ] Railway 계정 생성 완료
- [ ] 모든 환경변수 준비 완료
- [ ] MySQL 데이터베이스 외부 접속 허용 확인
- [ ] Procfile, runtime.txt, requirements.txt 확인

배포 후 확인사항:
- [ ] Railway 배포 성공 확인
- [ ] 생성된 URL로 웹 접속 테스트
- [ ] 데이터베이스 연결 테스트
- [ ] 뉴스 스크래핑 기능 테스트 (/scrape)
- [ ] 텔레그램 알림 기능 테스트
