import pymysql
import requests
import os
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# 1. 환경변수 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') # 관리자 테스트용
DB_PASSWORD = os.getenv('DB_PASSWORD')

# 2. AI 설정
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 3. DB 설정
DB_CONFIG = {
    'host': 'bitnmeta2.synology.me',
    'user': 'iyrc',
    'passwd': DB_PASSWORD,
    'db': 'gemini_ai',
    'charset': 'utf8',
    'port': 3307,
    'cursorclass': pymysql.cursors.DictCursor
}

# 분석 결과 저장 파일명
TREND_FILE = "latest_trend.txt"

# ---------------------------------------------------------
# [기능 1] DB 및 텔레그램 도우미 함수들
# ---------------------------------------------------------
def is_link_exist(link):
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ai_news WHERE link=%s", (link,))
        return cursor.fetchone() is not None
    except:
        return False
    finally:
        if conn: conn.close()

def save_news(title, link, summary):
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = "INSERT IGNORE INTO ai_news (title, link, summary, created_at) VALUES (%s, %s, %s, NOW())"
        cursor.execute(sql, (title, link, summary))
        conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        if conn: conn.close()

# (단일 발송용 - 관리자 테스트 등)
def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ 텔레그램 설정(토큰/ID)이 누락되었습니다.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": text, 
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            print(f"❌ 텔레그램 전송 실패: {response.text}")
    except Exception as e:
        print(f"❌ 텔레그램 연결 에러: {e}")

# (구독자 전체 발송용)
def send_telegram_to_all(text):
    if not TELEGRAM_TOKEN:
        print("⚠️ 텔레그램 토큰이 없습니다.")
        return

    conn = None
    try:
        # 1. 구독자 목록 가져오기
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT nickname, chat_id FROM subscribers")
        subscribers = cursor.fetchall()
        
        if not subscribers:
            print("⚠️ 발송할 구독자가 없습니다.")
            return

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        # 2. 한 명씩 순서대로 전송
        print(f"📨 총 {len(subscribers)}명에게 발송 시작...")
        
        for sub in subscribers:
            chat_id = sub['chat_id']
            payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            
            try:
                resp = requests.post(url, data=payload, timeout=5)
                if resp.status_code == 200:
                    print(f" - {sub['nickname']}님 전송 성공")
                else:
                    print(f" - {sub['nickname']}님 전송 실패: {resp.text}")
            except Exception as e:
                print(f" - 전송 에러 ({sub['nickname']}): {e}")
            
            # 너무 빨리 보내면 텔레그램이 차단할 수 있으므로 약간 대기
            time.sleep(0.5)

    except Exception as e:
        print(f"DB 접속 에러: {e}")
    finally:
        if conn: conn.close()

# ---------------------------------------------------------
# [기능 2] AI 요약 및 분석 함수
# ---------------------------------------------------------
def summarize_news_with_ai(title, content):
    try:
        # 내용이 너무 짧으면 제목을 내용으로 사용
        if len(content) < 20:
            actual_content = f"제목: {title}"
        else:
            actual_content = content

        prompt = f"""
        너는 IT 뉴스 브리핑 봇이야. 아래 뉴스에 대해 한국어로 2~3줄 요약을 작성해.
        
        [지침]
        1. '내용'이 충분하지 않거나 비어있다면, '제목'만 보고 어떤 뉴스인지 추론해서 작성해.
        2. 절대 '내용을 분석할 수 없습니다'라고 말하지 마.
        3. 문장은 "~함", "~임", "~것으로 보임" 같은 명사형 어미로 끝내.
        
        [제목]: {title}
        [내용]: {actual_content}
        """
        
        # 안전 설정 (필터링 기준을 낮춰서 뉴스가 차단되지 않게 함)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        # 응답 텍스트가 있는지 확인
        if response.text:
            return response.text
        else:
            return f"{title} (상세 내용 확인 필요)"

    except Exception as e:
        print(f"⚠️ AI 호출 에러: {e}")
        # AI가 실패하면 그냥 제목이라도 깔끔하게 반환 (분석 불가 메시지 제거)
        return f"주요 뉴스: {title}"

def generate_trend_analysis(news_data_list):
    try:
        # 뉴스 제목 리스트 생성
        combined_titles = "\n".join([f"- {news['title']}" for news in news_data_list])
        
        prompt = f"""
        아래는 현재 수집된 주요 AI 관련 뉴스 제목들이다. (총 {len(news_data_list)}건)
        이 뉴스들을 바탕으로 'AI 산업 뉴스 브리핑'을 작성해줘. 
        뉴스가 10개 미만이어도 있는 정보만으로 분석해라.

        [작성 규칙]
        1. 텔레그램 메시지로 보낼 것이므로 가독성 좋게 작성할 것.
        2. HTML 태그 <b> (볼드체)만 사용 가능 (마크다운 ** 사용 금지).
        3. 아래 형식을 반드시 따를 것:

        <b>[📅 오늘의 AI 뉴스 브리핑]</b>
        
        <b>1. 핵심 키워드</b>
        : (키워드 3개 추출)

        <b>2. 주요 동향 요약</b>
        : (전체적인 흐름을 3~5줄로 요약)

        <b>3. 주요 헤드라인</b>
        : (가장 중요한 뉴스 제목 3개만 나열)

        [뉴스 목록]:
        {combined_titles}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ 종합 분석 실패: {e}")
        return "종합 분석을 생성하지 못했습니다."

# ---------------------------------------------------------
# [기능 3] 메인 로직 (스크래핑 -> 요약 -> DB -> 종합분석 -> 구독자 전원 전송)
# ---------------------------------------------------------
def scrape_and_process():
    url = "https://news.google.com/rss/search?q=AI+인공지능&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        print("🚀 스크래핑 시작...")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.findAll('item')
        
        processed_list = []
        new_count = 0
        
        target_items = items[:10]
        
        for item in target_items:
            title = item.title.text
            link = item.link.text
            
            # description 처리 강화
            raw_desc = item.description.text if item.description else ""
            soup_desc = BeautifulSoup(raw_desc, "html.parser")
            cleaned_text = soup_desc.get_text(separator=" ", strip=True)
            
            # [핵심 수정] 내용이 너무 짧으면 제목을 내용으로 간주 (구글 뉴스는 본문이 없는 경우가 많음)
            if len(cleaned_text) < 10:
                context = f"기사 제목: {title}. (본문 미리보기가 제공되지 않는 기사입니다.)"
            else:
                context = cleaned_text

            processed_list.append({'title': title}) 

            if is_link_exist(link):
                print(f"PASS (중복): {title[:10]}...")
                continue 

            # 요약 함수 호출
            summary = summarize_news_with_ai(title, context)
            
            save_news(title, link, summary)
            new_count += 1
            
            print(f"✅ DB 저장 완료: {title[:10]}...")
            time.sleep(1)

        if processed_list:
            print(f"📊 총 {len(processed_list)}건의 뉴스로 트렌드 분석 중...")
            trend_report = generate_trend_analysis(processed_list)
            
            with open(TREND_FILE, "w", encoding="utf-8") as f:
                f.write(trend_report)
            
            send_telegram_to_all(trend_report)
            print("📨 텔레그램 종합 브리핑 전송 완료")
        else:
            print("⚠️ 처리할 뉴스가 없습니다.")
                
        return new_count        
    except Exception as e:
        print(f"❌ 전체 프로세스 에러: {e}")
        return 0
# ---------------------------------------------------------
# API 엔드포인트
# ---------------------------------------------------------
@app.get("/")
def read_root(request: Request):
    conn = None
    news_list = []
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ai_news ORDER BY id DESC LIMIT 10")
        news_list = cursor.fetchall()
    except Exception as e:
        print(f"DB Read Error: {e}")
    finally:
        if conn: conn.close()
    
    trend_report = "아직 분석된 데이터가 없습니다. '뉴스 분석 시작' 버튼을 눌러주세요."
    if os.path.exists(TREND_FILE):
        with open(TREND_FILE, "r", encoding="utf-8") as f:
            trend_report = f.read()
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "news_list": news_list,
        "trend_report": trend_report
    })

@app.get("/scrape")
def trigger_scrape():
    print("🔔 /scrape 요청 받음")
    count = scrape_and_process()
    return {"status": "success", "message": f"{count}건 신규 수집 및 구독자 발송 완료!"}

# ---------------------------------------------------------
# [기능 추가] 구독 신청 API
# ---------------------------------------------------------
@app.post("/subscribe")
def subscribe_user(nickname: str = Form(...), chat_id: str = Form(...)):
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 중복 방지 (이미 등록된 Chat ID면 무시)
        # DB에 subscribers 테이블이 생성되어 있어야 함
        sql = "INSERT IGNORE INTO subscribers (nickname, chat_id) VALUES (%s, %s)"
        cursor.execute(sql, (nickname, chat_id))
        conn.commit()
        
        print(f"🔔 신규 구독자 등록: {nickname} ({chat_id})")
    except Exception as e:
        print(f"구독 에러: {e}")
    finally:
        if conn: conn.close()
    
    # 등록 후 다시 메인 페이지로 이동
    return RedirectResponse(url="/", status_code=303)