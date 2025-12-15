## 프로그램 개발 순서 
<img width="728" height="265" alt="image" src="https://github.com/user-attachments/assets/cd8da887-e1be-4ab8-9353-5dd0031c9782" />
순서의 차이는 있으나 제일 중요하다고 보는것이 의외로 hello 인점

## 프로그램 실행 방법
FastAPI 프로그램(main.py)을 단순히 python main.py로 실행하지 않고 **uvicorn**이라는 명령어로 실행하는 이유와 방법을 요약해 드립니다.

1. 왜 Uvicorn을 쓰나요? (이유)
   쉽게 비유하자면 **FastAPI는 '요리사'**이고, **Uvicorn은 '지배인(서버)'**입니다.   

   통역사 역할 (Server): 작성하신 파이썬 코드는 스스로 웹 브라우저(Chrome 등)와 대화할 수 없습니다.   
   Uvicorn이 브라우저의 요청(HTTP)을 받아서 파이썬이 이해할 수 있게 통역해 주는 역할을 합니다.   

   비동기 처리 (Speed): FastAPI는 **"엄청나게 빠른 속도(Asynchronous)"**가 장점입니다.   
   Uvicorn은 이 비동기 처리를 완벽하게 지원하는 ASGI(Asynchronous Server Gateway Interface)   
   서버라서, 수많은 요청이 동시에 들어와도 멈추지 않고 빠르게 처리해 줍니다.   

   개발 편의성 (Reload): 코드를 수정하고 저장할 때마다 서버를 껐다 켜는 건 귀찮은 일입니다. 
   Uvicorn의 --reload 옵션은 파일이 저장되는 순간 알아서 서버를 새로고침 해줍니다.   

2. 실행 방법 (요약)
   터미널에서 다음 명령어를 입력합니다.   
   uvicorn main:app --reload   

3. 명령어 뜯어보기 (해석)
   uvicorn: 서버 프로그램을 실행하라는 명령어.   

   main: 실행할 파이썬 파일의 이름 (main.py에서 .py를 뺀 것).   

   :: 파일 이름과 내부 객체를 연결하는 구분자.   

   app: main.py 코드 안에서 만든 FastAPI 객체 변수 이름 (app = FastAPI()).   

   --reload: (개발용 옵션) 코드를 수정하고 저장(Ctrl+S)하면, 서버를 자동으로 재시작하라는 뜻. 
   (실제 서비스 배포 시에는 뺍니다.)

   
