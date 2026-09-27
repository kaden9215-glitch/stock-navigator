from concurrent.futures import ThreadPoolExecutor
import json
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests
import yfinance as yf

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
}

# 미국 시총 상위 100대 종목
US_TOP_100 = [
    ('AAPL', '애플'),
    ('MSFT', '마이크로소프트'),
    ('NVDA', '엔비디아'),
    ('GOOGL', '알파벳A'),
    ('AMZN', '아마존'),
    ('META', '메타'),
    ('TSLA', '테슬라'),
    ('BRK-B', '버크셔해서웨이'),
    ('AVGO', '브로드컴'),
    ('TSM', 'TSMC'),
    ('LLY', '일라이릴리'),
    ('WMT', '월마트'),
    ('JPM', 'JP모건'),
    ('V', '비자'),
    ('UNH', '유나이티드헬스'),
    ('XOM', '엑슨모빌'),
    ('ORCL', '오라클'),
    ('MA', '마스터카드'),
    ('HD', '홈디포'),
    ('PG', 'P&G'),
    ('COST', '코스트코'),
    ('JNJ', '존슨앤드존슨'),
    ('ABBV', '애브비'),
    ('BAC', '뱅크오브아메리카'),
    ('CRM', '세일즈포스'),
    ('NFLX', '넷플릭스'),
    ('KO', '코카콜라'),
    ('CVX', '쉐브론'),
    ('MRK', '머크'),
    ('AMD', 'AMD'),
    ('PEP', '펩시코'),
    ('TMO', '써모피셔'),
    ('LIN', '린데'),
    ('ADBE', '어도비'),
    ('WFC', '웰스파고'),
    ('ACN', '액센츄어'),
    ('MCD', '맥도날드'),
    ('CSCO', '시스코'),
    ('ABT', '애보트'),
    ('QCOM', '퀄컴'),
    ('GE', 'GE에어로스페이스'),
    ('INTU', '인튜이트'),
    ('IBM', 'IBM'),
    ('CAT', '캐터필러'),
    ('TXN', '텍사스인스트루먼트'),
    ('VZ', '버라이즌'),
    ('DHR', '다나허'),
    ('AMAT', '어플라이드머티어리얼즈'),
    ('NOW', '서비스나우'),
    ('ISRG', '인튜이티브서지컬'),
    ('PM', '필립모리스'),
    ('DIS', '디즈니'),
    ('SPGI', 'S&P글로벌'),
    ('PFE', '화이자'),
    ('GS', '골드만삭스'),
    ('HON', '허니웰'),
    ('UBER', '우버'),
    ('BKNG', '부킹홀딩스'),
    ('RTX', 'RTX(레이시온)'),
    ('LOW', '로우에스'),
    ('AMGN', '암젠'),
    ('UNP', '유니온퍼시픽'),
    ('COP', '코노코필립스'),
    ('MS', '모건스탠리'),
    ('PGR', '프로그레시브'),
    ('SYK', '스트라이커'),
    ('BA', '보잉'),
    ('BLK', '블랙록'),
    ('ELV', '엘레반스헬스'),
    ('MDT', '메드트로닉'),
    ('C', '씨티그룹'),
    ('VRTX', '버텍스'),
    ('LRCX', '램리서치'),
    ('TJX', 'TJX컴퍼니'),
    ('PANW', '팔로알토네트웍스'),
    ('PLTR', '팔란티어'),
    ('BSX', '보스턴사이언티픽'),
    ('ADP', '오토매틱데이터'),
    ('SCHW', '찰스슈왑'),
    ('ETN', '이튼'),
    ('DE', '디어앤컴퍼니'),
    ('CB', '처브'),
    ('ADI', '아날로그디바이스'),
    ('MMC', '마시앤맥레넌'),
    ('MDLZ', '몬델리즈'),
    ('CI', '시그나'),
    ('GILD', '길리어드'),
    ('FI', '파이서브'),
    ('BMY', 'BMS'),
    ('ZTS', '조에티스'),
    ('SO', '서던컴퍼니'),
    ('REGN', '리제네론'),
    ('LMT', '록히드마틴'),
    ('SHW', '셔윈윌리엄즈'),
    ('MO', '알트리아'),
    ('DUK', '듀크에너지'),
    ('CVS', 'CVS헬스'),
    ('SBUX', '스타벅스'),
    ('MU', '마이크론'),
    ('ICE', '인터컨티넨털'),
]


# RSI 계산 함수 (Wilder Smoothing)
def calculate_rsi(series, period=14):
  if len(series) < period + 1:
    return 50.0
  delta = series.diff()
  gain = delta.where(delta > 0, 0.0)
  loss = -delta.where(delta < 0, 0.0)
  avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
  avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()

  if avg_loss.iloc[-1] == 0:
    return 100.0 if avg_gain.iloc[-1] > 0 else 50.0
  rs = avg_gain / avg_loss
  rsi = 100.0 - (100.0 / (1.0 + rs))
  val = rsi.iloc[-1]
  return round(float(val), 1) if not pd.isna(val) else 50.0


# 네이버 금융에서 코스피/코스닥 상위 종목 목록 수집
def get_kr_top_stocks(sosok, market_name, limit=100):
  stocks = []
  page = 1
  suffix = '.KS' if market_name == 'KOSPI' else '.KQ'
  while len(stocks) < limit:
    url = f'https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}'
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table', {'class': 'type_2'})
    if not table:
      break
    for row in table.find_all('tr'):
      a_tag = row.find('a', {'class': 'tltle'})
      if a_tag:
        name = a_tag.text.strip()
        code = a_tag['href'].split('code=')[-1].strip()
        stocks.append({
            'ticker': f'{code}{suffix}',
            'name': name,
            'code': code,
            'sector': market_name,
        })
        if len(stocks) >= limit:
          break
    page += 1
    time.sleep(0.04)
  return stocks


# 공통 종목 데이터 처리 함수 (국내/미국 공통)
def fetch_stock_data(item):
  ticker = item['ticker']
  name = item['name']
  code = item['code']
  sector = item['sector']
  is_us = sector.startswith('US')

  try:
    stock = yf.Ticker(ticker)
    df = stock.history(period='2y', interval='1d')
    if df.empty or len(df) < 30:
      return None

    # RSI (일봉 / 주봉 / 월봉)
    rsi_day = calculate_rsi(df['Close'], 14)
    df_week = df['Close'].resample('W-FRI').last().dropna()
    rsi_week = calculate_rsi(df_week, 14)
    try:
      df_month = df['Close'].resample('ME').last().dropna()
    except ValueError:
      df_month = df['Close'].resample('M').last().dropna()
    rsi_month = calculate_rsi(df_month, 14)

    # 52주 최고점 대비 하락률 (MDD)
    recent_high = df['High'].iloc[-250:].max()
    current_close = df['Close'].iloc[-1]
    mdd = (
        round(((current_close - recent_high) / recent_high) * 100, 1)
        if recent_high > 0
        else 0.0
    )

    # 20일선 이동평균 및 이격도
    ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    disparity_20 = (
        round(((current_close - ma20) / ma20) * 100, 1) if ma20 > 0 else 0.0
    )

    # 거래량 및 전일 대비 급증 비율
    current_vol = int(df['Volume'].iloc[-1])
    prev_vol = df['Volume'].iloc[-2] if len(df) >= 2 else current_vol
    vol_ratio = (
        round((current_vol / prev_vol) * 100, 1) if prev_vol > 0 else 100.0
    )

    return {
        'name': name,
        'code': code,
        'sector': sector,
        'price': (
            round(float(current_close), 2) if is_us else int(current_close)
        ),
        'rsi': {'day': rsi_day, 'week': rsi_week, 'month': rsi_month},
        'mdd': mdd,
        'ma20': round(float(ma20), 2) if is_us else int(ma20),
        'disparity20': disparity_20,
        'volume': current_vol,
        'vol_ratio': vol_ratio,
    }
  except Exception:
    return None


if __name__ == '__main__':
  start_time = time.time()
  all_items = []

  # 1. 국내 코스피 100 + 코스닥 100
  print('🔍 국내 KOSPI/KOSDAQ 상위 종목 수집 중...')
  kr_kospi = get_kr_top_stocks(0, 'KOSPI', 100)
  kr_kosdaq = get_kr_top_stocks(1, 'KOSDAQ', 100)
  all_items.extend(kr_kospi)
  all_items.extend(kr_kosdaq)

  # 2. 미국 상위 100
  for ticker, name in US_TOP_100:
    all_items.append(
        {'ticker': ticker, 'name': name, 'code': ticker, 'sector': 'US (미국)'}
    )

  print(f'🚀 총 {len(all_items)}개 종목 yfinance 고속 데이터 연산 시작...')

  # 3. 멀티스레딩 고속 병렬 연산 (15개 동시 처리)
  results = []
  with ThreadPoolExecutor(max_workers=15) as executor:
    processed = executor.map(fetch_stock_data, all_items)
    for r in processed:
      if r:
        results.append(r)

  # stocks.json 저장
  with open('stocks.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

  print(
      f'🎉 연산 완료! 총 {len(results)}개 종목이 stocks.json에'
      f' 저장되었습니다. ({round(time.time() - start_time, 2)}초)'
  )
