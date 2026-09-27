from concurrent.futures import ThreadPoolExecutor
import json
import time
import pandas as pd
import yfinance as yf

# 1. 한/미 대표 우량주 150개 명단 완벽 고정 탑재 (한국 100개 + 미국 50개)
# KOSPI는 .KS, KOSDAQ은 .KQ를 티커 뒤에 붙여 yfinance가 다이렉트로 읽게 합니다.
STOCK_DATABASE = [
    # [코스피 대표 70개]
    {"ticker": "005930.KS", "name": "삼성전자", "code": "005930", "sector": "KOSPI"},
    {"ticker": "000660.KS", "name": "SK하이닉스", "code": "000660", "sector": "KOSPI"},
    {"ticker": "373220.KS", "name": "LG에너지솔루션", "code": "373220", "sector": "KOSPI"},
    {"ticker": "207940.KS", "name": "삼성바이오로직스", "code": "207940", "sector": "KOSPI"},
    {"ticker": "005380.KS", "name": "현대차", "code": "005380", "sector": "KOSPI"},
    {"ticker": "005490.KS", "name": "POSCO홀딩스", "code": "005490", "sector": "KOSPI"},
    {"ticker": "000270.KS", "name": "기아", "code": "000270", "sector": "KOSPI"},
    {"ticker": "035420.KS", "name": "NAVER", "code": "035420", "sector": "KOSPI"},
    {"ticker": "051910.KS", "name": "LG화학", "code": "051910", "sector": "KOSPI"},
    {"ticker": "006400.KS", "name": "삼성SDI", "code": "006400", "sector": "KOSPI"},
    {"ticker": "068270.KS", "name": "셀트리온", "code": "068270", "sector": "KOSPI"},
    {"ticker": "035720.KS", "name": "카카오", "code": "035720", "sector": "KOSPI"},
    {"ticker": "003670.KS", "name": "포스코퓨처엠", "code": "003670", "sector": "KOSPI"},
    {"ticker": "012330.KS", "name": "현대모비스", "code": "012330", "sector": "KOSPI"},
    {"ticker": "028260.KS", "name": "삼성물산", "code": "028260", "sector": "KOSPI"},
    {"ticker": "105560.KS", "name": "KB금융", "code": "105560", "sector": "KOSPI"},
    {"ticker": "055550.KS", "name": "신한지주", "code": "055550", "sector": "KOSPI"},
    {"ticker": "066570.KS", "name": "LG전자", "code": "066570", "sector": "KOSPI"},
    {"ticker": "003550.KS", "name": "LG", "code": "003550", "sector": "KOSPI"},
    {"ticker": "034730.KS", "name": "SK", "code": "034730", "sector": "KOSPI"},
    {"ticker": "015760.KS", "name": "한국전력", "code": "015760", "sector": "KOSPI"},
    {"ticker": "032830.KS", "name": "삼성생명", "code": "032830", "sector": "KOSPI"},
    {"ticker": "086790.KS", "name": "하나금융지주", "code": "086790", "sector": "KOSPI"},
    {"ticker": "017670.KS", "name": "SK텔레콤", "code": "017670", "sector": "KOSPI"},
    {"ticker": "018260.KS", "name": "삼성에스디에스", "code": "018260", "sector": "KOSPI"},
    {"ticker": "009150.KS", "name": "삼성전기", "code": "009150", "sector": "KOSPI"},
    {"ticker": "323410.KS", "name": "카카오뱅크", "code": "323410", "sector": "KOSPI"},
    {"ticker": "011200.KS", "name": "HMM", "code": "011200", "sector": "KOSPI"},
    {"ticker": "010950.KS", "name": "S-Oil", "code": "010950", "sector": "KOSPI"},
    {"ticker": "000810.KS", "name": "삼성화재", "code": "000810", "sector": "KOSPI"},
    {"ticker": "033780.KS", "name": "KT&G", "code": "033780", "sector": "KOSPI"},
    {"ticker": "316140.KS", "name": "우리금융지주", "code": "316140", "sector": "KOSPI"},
    {"ticker": "352820.KS", "name": "하이브", "code": "352820", "sector": "KOSPI"},
    {"ticker": "005935.KS", "name": "삼성전자우", "code": "005935", "sector": "KOSPI"},
    {"ticker": "010130.KS", "name": "고려아연", "code": "010130", "sector": "KOSPI"},
    {"ticker": "011170.KS", "name": "롯데케미칼", "code": "011170", "sector": "KOSPI"},
    {"ticker": "009540.KS", "name": "HD현대중공업", "code": "009540", "sector": "KOSPI"},
    {"ticker": "259960.KS", "name": "크래프톤", "code": "259960", "sector": "KOSPI"},
    {"ticker": "010140.KS", "name": "삼성중공업", "code": "010140", "sector": "KOSPI"},
    {"ticker": "004020.KS", "name": "현대제철", "code": "004020", "sector": "KOSPI"},
    {"ticker": "024110.KS", "name": "기업은행", "code": "024110", "sector": "KOSPI"},
    {"ticker": "036570.KS", "name": "엔씨소프트", "code": "036570", "sector": "KOSPI"},
    {"ticker": "011070.KS", "name": "LG이노텍", "code": "011070", "sector": "KOSPI"},
    {"ticker": "097950.KS", "name": "CJ제일제당", "code": "097950", "sector": "KOSPI"},
    {"ticker": "028050.KS", "name": "삼성엔지니어링", "code": "028050", "sector": "KOSPI"},
    {"ticker": "307900.KS", "name": "한화에어로스페이스", "code": "307900", "sector": "KOSPI"},
    {"ticker": "000100.KS", "name": "유한양행", "code": "000100", "sector": "KOSPI"},
    {"ticker": "006260.KS", "name": "LS", "code": "006260", "sector": "KOSPI"},
    {"ticker": "012450.KS", "name": "한화에어로", "code": "012450", "sector": "KOSPI"},
    {"ticker": "138040.KS", "name": "메리츠금융지주", "code": "138040", "sector": "KOSPI"},
    {"ticker": "047050.KS", "name": "포스코인터내셔널", "code": "047050", "sector": "KOSPI"},
    {"ticker": "001040.KS", "name": "CJ", "code": "001040", "sector": "KOSPI"},
    {"ticker": "018880.KS", "name": "한온시스템", "code": "018880", "sector": "KOSPI"},
    {"ticker": "000120.KS", "name": "CJ대한통운", "code": "000120", "sector": "KOSPI"},
    {"ticker": "016360.KS", "name": "삼성증권", "code": "016360", "sector": "KOSPI"},
    {"ticker": "000080.KS", "name": "하이트진로", "code": "000080", "sector": "KOSPI"},
    {"ticker": "008770.KS", "name": "호텔신라", "code": "008770", "sector": "KOSPI"},
    {"ticker": "180640.KS", "name": "한진칼", "code": "180640", "sector": "KOSPI"},
    {"ticker": "014680.KS", "name": "한솔케미칼", "code": "014680", "sector": "KOSPI"},
    {"ticker": "078930.KS", "name": "GS", "code": "078930", "sector": "KOSPI"},
    {"ticker": "007070.KS", "name": "GS리테일", "code": "007070", "sector": "KOSPI"},
    {"ticker": "009900.KS", "name": "한화솔루션", "code": "009900", "sector": "KOSPI"},
    {"ticker": "020150.KS", "name": "일진머티리얼즈", "code": "020150", "sector": "KOSPI"},
    {"ticker": "001450.KS", "name": "현대해상", "code": "001450", "sector": "KOSPI"},
    {"ticker": "000720.KS", "name": "현대건설", "code": "000720", "sector": "KOSPI"},
    {"ticker": "005940.KS", "name": "NH투자증권", "code": "005940", "sector": "KOSPI"},
    {"ticker": "001800.KS", "name": "오리온", "code": "001800", "sector": "KOSPI"},
    {"ticker": "161390.KS", "name": "한국타이어앤테크놀로지", "code": "161390", "sector": "KOSPI"},
    {"ticker": "008930.KS", "name": "한미약품", "code": "008930", "sector": "KOSPI"},
    {"ticker": "004000.KS", "name": "롯데정밀화학", "code": "004000", "sector": "KOSPI"},

    # [코스닥 우량주 30개]
    {"ticker": "086520.KQ", "name": "에코프로", "code": "086520", "sector": "KOSDAQ"},
    {"ticker": "247540.KQ", "name": "에코프로비엠", "code": "247540", "sector": "KOSDAQ"},
    {"ticker": "293490.KQ", "name": "카카오게임즈", "code": "293490", "sector": "KOSDAQ"},
    {"ticker": "035900.KQ", "name": "JYP Ent.", "code": "035900", "sector": "KOSDAQ"},
    {"ticker": "253450.KQ", "name": "스튜디오드래곤", "code": "253450", "sector": "KOSDAQ"},
    {"ticker": "039840.KQ", "name": "디오", "code": "039840", "sector": "KOSDAQ"},
    {"ticker": "192080.KQ", "name": "더블유게임즈", "code": "192080", "sector": "KOSDAQ"},
    {"ticker": "066970.KQ", "name": "엘앤에프", "code": "066970", "sector": "KOSDAQ"},
    {"ticker": "145020.KQ", "name": "휴젤", "code": "145020", "sector": "KOSDAQ"},
    {"ticker": "025900.KQ", "name": "동화기업", "code": "025900", "sector": "KOSDAQ"},
    {"ticker": "058470.KQ", "name": "리노공업", "code": "058470", "sector": "KOSDAQ"},
    {"ticker": "086900.KQ", "name": "메디톡스", "code": "086900", "sector": "KOSDAQ"},
    {"ticker": "214150.KQ", "name": "클래시스", "code": "214150", "sector": "KOSDAQ"},
    {"ticker": "036830.KQ", "name": "솔브레인", "code": "036830", "sector": "KOSDAQ"},
    {"ticker": "091950.KQ", "name": "셀트리온제약", "code": "091950", "sector": "KOSDAQ"},
    {"ticker": "214310.KQ", "name": "세경하이테크", "code": "214310", "sector": "KOSDAQ"},
    {"ticker": "041515.KQ", "name": "SM", "code": "041515", "sector": "KOSDAQ"},
    {"ticker": "022410.KQ", "name": "엑세스바이오", "code": "022410", "sector": "KOSDAQ"},
    {"ticker": "112040.KQ", "name": "위메이드", "code": "112040", "sector": "KOSDAQ"},
    {"ticker": "298020.KQ", "name": "효성티앤씨", "code": "298020", "sector": "KOSDAQ"},
    {"ticker": "393890.KQ", "name": "천보", "code": "393890", "sector": "KOSDAQ"},
    {"ticker": "036490.KQ", "name": "어서테크", "code": "036490", "sector": "KOSDAQ"},
    {"ticker": "060230.KQ", "name": "영원무역홀딩스", "code": "060230", "sector": "KOSDAQ"},
    {"ticker": "034230.KQ", "name": "파라다이스", "code": "034230", "sector": "KOSDAQ"},
    {"ticker": "041960.KQ", "name": "코미팜", "code": "041960", "sector": "KOSDAQ"},
    {"ticker": "046890.KQ", "name": "서울반도체", "code": "046890", "sector": "KOSDAQ"},
    {"ticker": "131970.KQ", "name": "테스나", "code": "131970", "sector": "KOSDAQ"},
    {"ticker": "039200.KQ", "name": "오스템임플란트", "code": "039200", "sector": "KOSDAQ"},
    {"ticker": "067160.KQ", "name": "아프리카TV", "code": "067160", "sector": "KOSDAQ"},
    {"ticker": "122640.KQ", "name": "예스티", "code": "122640", "sector": "KOSDAQ"},

    # [미국 우량주 대표 50개]
    {"ticker": "AAPL", "name": "애플", "code": "AAPL", "sector": "US (미국)"},
    {"ticker": "MSFT", "name": "마이크로소프트", "code": "MSFT", "sector": "US (미국)"},
    {"ticker": "NVDA", "name": "엔비디아", "code": "NVDA", "sector": "US (미국)"},
    {"ticker": "GOOGL", "name": "알파벳A", "code": "GOOGL", "sector": "US (미국)"},
    {"ticker": "AMZN", "name": "아마존", "code": "AMZN", "sector": "US (미국)"},
    {"ticker": "META", "name": "메타", "code": "META", "sector": "US (미국)"},
    {"ticker": "TSLA", "name": "테슬라", "code": "TSLA", "sector": "US (미국)"},
    {"ticker": "BRK-B", "name": "버크셔해서웨이", "code": "BRK-B", "sector": "US (미국)"},
    {"ticker": "AVGO", "name": "브로드컴", "code": "AVGO", "sector": "US (미국)"},
    {"ticker": "TSM", "name": "TSMC", "code": "TSM", "sector": "US (미국)"},
    {"ticker": "LLY", "name": "일라이릴리", "code": "LLY", "sector": "US (미국)"},
    {"ticker": "WMT", "name": "월마트", "code": "WMT", "sector": "US (미국)"},
    {"ticker": "JPM", "name": "JP모건", "code": "JPM", "sector": "US (미국)"},
    {"ticker": "V", "name": "비자", "code": "V", "sector": "US (미국)"},
    {"ticker": "UNH", "name": "유나이티드헬스", "code": "UNH", "sector": "US (미국)"},
    {"ticker": "XOM", "name": "엑슨모빌", "code": "XOM", "sector": "US (미국)"},
    {"ticker": "ORCL", "name": "오라클", "code": "ORCL", "sector": "US (미국)"},
    {"ticker": "MA", "name": "마스터카드", "code": "MA", "sector": "US (미국)"},
    {"ticker": "HD", "name": "홈디포", "code": "HD", "sector": "US (미국)"},
    {"ticker": "PG", "name": "P&G", "code": "PG", "sector": "US (미국)"},
    {"ticker": "COST", "name": "코스트코", "code": "COST", "sector": "US (미국)"},
    {"ticker": "JNJ", "name": "존슨앤드존슨", "code": "JNJ", "sector": "US (미국)"},
    {"ticker": "ABBV", "name": "애브비", "code": "ABBV", "sector": "US (미국)"},
    {"ticker": "BAC", "name": "뱅크오브아메리카", "code": "BAC", "sector": "US (미국)"},
    {"ticker": "CRM", "name": "세일즈포스", "code": "CRM", "sector": "US (미국)"},
    {"ticker": "NFLX", "name": "넷플릭스", "code": "NFLX", "sector": "US (미국)"},
    {"ticker": "KO", "name": "코카콜라", "code": "KO", "sector": "US (미국)"},
    {"ticker": "CVX", "name": "쉐브론", "code": "CVX", "sector": "US (미국)"},
    {"ticker": "MRK", "name": "머크", "code": "MRK", "sector": "US (미국)"},
    {"ticker": "AMD", "name": "AMD", "code": "AMD", "sector": "US (미국)"},
    {"ticker": "PEP", "name": "펩시코", "code": "PEP", "sector": "US (미국)"},
    {"ticker": "TMO", "name": "써모피셔", "code": "TMO", "sector": "US (미국)"},
    {"ticker": "ADBE", "name": "어도비", "code": "ADBE", "sector": "US (미국)"},
    {"ticker": "WFC", "name": "웰스파고", "code": "WFC", "sector": "US (미국)"},
    {"ticker": "ACN", "name": "액센츄어", "code": "ACN", "sector": "US (미국)"},
    {"ticker": "MCD", "name": "맥도날드", "code": "MCD", "sector": "US (미국)"},
    {"ticker": "CSCO", "name": "시스코", "code": "CSCO", "sector": "US (미국)"},
    {"ticker": "QCOM", "name": "퀄컴", "code": "QCOM", "sector": "US (미국)"},
    {"ticker": "GE", "name": "GE에어로스페이스", "code": "GE", "sector": "US (미국)"},
    {"ticker": "IBM", "name": "IBM", "code": "IBM", "sector": "US (미국)"},
    {"ticker": "CAT", "name": "캐터필러", "code": "CAT", "sector": "US (미국)"},
    {"ticker": "INTU", "name": "인튜이트", "code": "INTU", "sector": "US (미국)"},
    {"ticker": "TXN", "name": "텍사스인스트루먼트", "code": "TXN", "sector": "US (미국)"},
    {"ticker": "VZ", "name": "버라이즌", "code": "VZ", "sector": "US (미국)"},
    {"ticker": "AMAT", "name": "어플라이드머티어리얼즈", "code": "AMAT", "sector": "US (미국)"},
    {"ticker": "NOW", "name": "서비스나우", "code": "NOW", "sector": "US (미국)"},
    {"ticker": "ISRG", "name": "인튜이티브서지컬", "code": "ISRG", "sector": "US (미국)"},
    {"ticker": "DIS", "name": "디즈니", "code": "DIS", "sector": "US (미국)"},
    {"ticker": "SBUX", "name": "스타벅스", "code": "SBUX", "sector": "US (미국)"},
    {"ticker": "MU", "name": "마이크론", "code": "MU", "sector": "US (미국)"}
]

# RSI 계산 함수 (Wilder Smoothing)
def calculate_rsi(series, period=14):
    if len(series) < period + 1:
        return 50.0
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()

    if avg_loss.iloc[-1] == 0:
        return 100.0 if avg_gain.iloc[-1] > 0 else 50.0
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    val = rsi.iloc[-1]
    return round(float(val), 1) if not pd.isna(val) else 50.0

# 종목 데이터 수집 및 지표 계산 함수 (야후 파이낸스 직접 동기화)
def fetch_stock_data(item):
    ticker = item["ticker"]
    name = item["name"]
    code = item["code"]
    sector = item["sector"]
    is_us = sector.startswith("US")

    try:
        stock = yf.Ticker(ticker)
        # 안정적인 2년 데이터 확보 (RSI 월봉 계산을 위해 중요)
        df = stock.history(period="2y", interval="1d")
        if df.empty or len(df) < 30:
            return None

        # 1. RSI 계산
        rsi_day = calculate_rsi(df["Close"], 14)
        df_week = df["Close"].resample("W-FRI").last().dropna()
        rsi_week = calculate_rsi(df_week, 14)
        try:
            df_month = df["Close"].resample("ME").last().dropna()
        except ValueError:
            df_month = df["Close"].resample("M").last().dropna()
        rsi_month = calculate_rsi(df_month, 14)

        # 2. 52주 최고점 대비 하락률 (MDD)
        recent_high = df["High"].iloc[-250:].max()
        current_close = df["Close"].iloc[-1]
        mdd = round(((current_close - recent_high) / recent_high) * 100, 1) if recent_high > 0 else 0.0

        # 3. 20일선 이동평균선 & 이격도
        ma20 = df["Close"].rolling(window=20).mean().iloc[-1]
        disparity_20 = round(((current_close - ma20) / ma20) * 100, 1) if ma20 > 0 else 0.0

        # 4. 거래량 및 전일 대비 거래량 비율
        current_vol = int(df["Volume"].iloc[-1])
        prev_vol = df["Volume"].iloc[-2] if len(df) >= 2 else current_vol
        vol_ratio = round((current_vol / prev_vol) * 100, 1) if prev_vol > 0 else 100.0

        return {
            "name": name,
            "code": code,
            "sector": sector,
            "price": round(float(current_close), 2) if is_us else int(current_close),
            "rsi": {"day": rsi_day, "week": rsi_week, "month": rsi_month},
            "mdd": mdd,
            "ma20": round(float(ma20), 2) if is_us else int(ma20),
            "disparity20": disparity_20,
            "volume": current_vol,
            "vol_ratio": vol_ratio
        }
    except Exception as e:
        print(f"❌ {name}({ticker}) 처리 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    start_time = time.time()
    
    print(f"🚀 총 {len(STOCK_DATABASE)}개 정예 글로벌 종목 yfinance 병렬 데이터 계산 시작...")

    # 멀티스레딩 고속 병렬 연산 (15개 채널로 10초 컷)
    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        processed = executor.map(fetch_stock_data, STOCK_DATABASE)
        for r in processed:
            if r:
                results.append(r)

    # stocks.json 저장
    with open("stocks.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"🎉 모든 수치 계산 완료! 총 {len(results)}개 종목이 stocks.json에 안전하게 이식되었습니다. (소요시간: {round(time.time() - start_time, 2)}초)")
