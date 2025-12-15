import pymysql
import requests
import os
import time
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import google.generativeai as genai

# 1. 환경변수 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# 2. AI 설정 (중요: 모델명 수정됨 gemini-1.5-flash)
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
# [기능 1] DB 도우미 함수들
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

def send_telegram_message(text):
    # 아직 미처리 되었음 TELEGRAM_TOKEN 이 없으면 패스
    if not TELEGRAM_TOKEN:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
            data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        )
    except:
        pass

# ---------------------------------------------------------
# [기능 2] AI 요약 및 분석 함수
# ---------------------------------------------------------
def summarize_news_with_ai(title, content):
    try:
        prompt = f"""
        너는 IT 뉴스 전문 분석가야. 아래 기사를 한국어로 상세히 요약해줘.
        
        [규칙]
        1. 본문 내용이 부족하면 '제목'을 보고 내용을 추론해서 작성할 것.
        2. '- ' 글머리 기호를 사용해 5~7줄 내외로 작성.
        
        [제목]: {title}
        [내용]: {content}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ 개별 요약 실패: {e}")
        return "내용을 분석할 수 없습니다."

def generate_trend_analysis(news_data_list):
    try:
        combined_titles = "\n".join([f"- {news['title']}" for news in news_data_list])
        prompt = f"""
        아래는 오늘 수집된 주요 AI 관련 뉴스 10개의 제목들이다.
        이 뉴스들을 바탕으로 '오늘의 AI 산업 동향'을 종합적으로 분석해줘.
        
        [작성 규칙]
        1. 전체적인 트렌드나 공통된 키워드를 찾아서 설명할 것.
        2. '오늘의 핵심 키워드: OOO, OOO' 형식을 포함할 것.
        3. 서술형으로 5줄 내외로 요약할 것.
        
        [뉴스 목록]:
        {combined_titles}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ 종합 분석 실패: {e}")
        return "종합 분석을 생성하지 못했습니다."

# ---------------------------------------------------------
# [기능 3] 메인 로직 (스크래핑 -> 요약 -> DB -> 텔레그램 -> 종합분석)
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
        
        # 10개 처리
        for item in items[:10]:
            title = item.title.text
            link = item.link.text
            raw_desc = item.description.text if item.description else ""
            
            # 태그 제거
            soup_desc = BeautifulSoup(raw_desc, "html.parser")
            cleaned_text = soup_desc.get_text(separator=" ", strip=True)
            
            # 중복 체크
            if is_link_exist(link):
                print(f"PASS: {title[:10]}...")
                processed_list.append({'title': title}) 
                continue

            # AI 요약
            context = cleaned_text if len(cleaned_text) > 10 else f"본문 내용 없음. 제목({title}) 기반으로 분석 필요."
            summary = summarize_news_with_ai(title, context)
            
            # DB 저장 및 텔레그램 전송
            save_news(title, link, summary)
            new_count += 1
            processed_list.append({'title': title})
            
            msg = f"<b>📰 {title}</b>\n\n{summary}\n\n🔗 <a href='{link}'>원문 보기</a>"
            send_telegram_message(msg)
            
            print(f"✅ 처리 완료: {title[:10]}...")
            time.sleep(1)

        # 종합 분석
        if processed_list:
            print("📊 종합 트렌드 분석 중...")
            trend_report = generate_trend_analysis(processed_list)
            with open(TREND_FILE, "w", encoding="utf-8") as f:
                f.write(trend_report)
                
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
    return {"status": "success", "message": f"{count}건 신규 수집 및 종합 분석 완료!"}