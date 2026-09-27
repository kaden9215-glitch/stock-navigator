from concurrent.futures import ThreadPoolExecutor
import json
import time
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd
import requests
import yfinance as yf

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
}

# 1. 미국 시가총액 상위 대표 100대 종목 티커 리스트
US_TOP_100 = [
    (
        'AAPL',
        '애플',
    ),
    (
        'MSFT',
        '마이크로소프트',
    ),
    (
        'NVDA',
        '엔비디아',
    ),
    (
        'GOOGL',
        '알파벳A',
    ),
    (
        'AMZN',
        '아마존',
    ),
    (
        'META',
        '메타',
    ),
    (
        'TSLA',
        '테슬라',
    ),
    (
        'BRK-B',
        '버크셔해서웨이',
    ),
    (
        'AVGO',
        '브로드컴',
    ),
    (
        'TSM',
        'TSMC',
    ),
    (
        'LLY',
        '일라이릴리',
    ),
    (
        'WMT',
        '월마트',
    ),
    (
        'JPM',
        'JP모건',
    ),
    (
        'V',
        '비자',
    ),
    (
        'UNH',
        '유나이티드헬스',
    ),
    (
        'XOM',
        '엑슨모빌',
    ),
    (
        'ORCL',
        '오라클',
    ),
    (
        'MA',
        '마스터카드',
    ),
    (
        'HD',
        '홈디포',
    ),
    (
        'PG',
        'P&G',
    ),
    (
        'COST',
        '코스트코',
    ),
    (
        'JNJ',
        '존슨앤드존슨',
    ),
    (
        'ABBV',
        '애브비',
    ),
    (
        'BAC',
        '뱅크오브아메리카',
    ),
    (
        'CRM',
        '세일즈포스',
    ),
    (
        'NFLX',
        '넷플릭스',
    ),
    (
        'KO',
        '코카콜라',
    ),
    (
        'CVX',
        '쉐브론',
    ),
    (
        'MRK',
        '머크',
    ),
    (
        'AMD',
        'AMD',
    ),
    (
        'PEP',
        '펩시코',
    ),
    (
        'TMO',
        '써모피셔',
    ),
    (
        'LIN',
        '린데',
    ),
    (
        'ADBE',
        '어도비',
    ),
    (
        'WFC',
        '웰스파고',
    ),
    (
        'ACN',
        '액센츄어',
    ),
    (
        'MCD',
        '맥도날드',
    ),
    (
        'CSCO',
        '시스코',
    ),
    (
        'ABT',
        '애보트',
    ),
    (
        'QCOM',
        '퀄컴',
    ),
    (
        'GE',
        'GE에어로스페이스',
    ),
    (
        'INTU',
        '인튜이트',
    ),
    (
        'IBM',
        'IBM',
    ),
    (
        'CAT',
        '캐터필러',
    ),
    (
        'TXN',
        '텍사스인스트루먼트',
    ),
    (
        'VZ',
        '버라이즌',
    ),
    (
        'DHR',
        '다나허',
    ),
    (
        'AMAT',
        '어플라이드머티어리얼즈',
    ),
    (
        'NOW',
        '서비스나우',
    ),
    (
        'ISRG',
        '인튜이티브서지컬',
    ),
    (
        'PM',
        '필립모리스',
    ),
    (
        'DIS',
        '디즈니',
    ),
    (
        'SPGI',
        'S&P글로벌',
    ),
    (
        'PFE',
        '화이자',
    ),
    (
        'GS',
        '골드만삭스',
    ),
    (
        'HON',
        '허니웰',
    ),
    (
        'UBER',
        '우버',
    ),
    (
        'BKNG',
        '부킹홀딩스',
    ),
    (
        'RTX',
        'RTX(레이시온)',
    ),
    (
        'LOW',
        '로우에스',
    ),
    (
        'AMGN',
        '암젠',
    ),
    (
        'UNP',
        '유니온퍼시픽',
    ),
    (
        'COP',
        '코노코필립스',
    ),
    (
        'MS',
        '모건스탠리',
    ),
    (
        'PGR',
        '프로그레시브',
    ),
    (
        'SYK',
        '스트라이커',
    ),
    (
        'BA',
        '보잉',
    ),
    (
        'BLK',
        '블랙록',
    ),
    (
        'ELV',
        '엘레반스헬스',
    ),
    (
        'MDT',
        '메드트로닉',
    ),
    (
        'C',
        '씨티그룹',
    ),
    (
        'VRTX',
        '버텍스',
    ),
    (
        'LRCX',
        '램리서치',
    ),
    (
        'TJX',
        'TJX컴퍼니',
    ),
    (
        'PANW',
        '팔로알토네트웍스',
    ),
    (
        'PLTR',
        '팔란티어',
    ),
    (
        'BSX',
        '보스턴사이언티픽',
    ),
    (
        'ADP',
        '오토매틱데이터',
    ),
    (
        'SCHW',
        '찰스슈왑',
    ),
    (
        'ETN',
        '이튼',
    ),
    (
        'DE',
        '디어앤컴퍼니',
    ),
    (
        'CB',
        '처브',
    ),
    (
        'ADI',
        '아날로그디바이스',
    ),
    (
        'MMC',
        '마시앤맥레넌',
    ),
    (
        'MDLZ',
        '몬델리즈',
    ),
    (
        'CI',
        '시그나',
    ),
    (
        'GILD',
        '길리어드',
    ),
    (
        'FI',
        '파이서브',
    ),
    (
        'BMY',
        'BMS',
    ),
    (
        'ZTS',
        '조에티스',
    ),
    (
        'SO',
        '서던컴퍼니',
    ),
    (
        'REGN',
        '리제네론',
    ),
    (
        'LMT',
        '록히드마틴',
    ),
    (
        'SHW',
        '셔윈윌리엄즈',
    ),
    (
        'MO',
        '알트리아',
    ),
    (
        'DUK',
        '듀크에너지',
    ),
    (
        'CVS',
        'CVS헬스',
    ),
    (
        'SBUX',
        '스타벅스',
    ),
    (
        'MU',
        '마이크론',
    ),
    (
        'ICE',
        '인터컨티넨털',
    ),
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


# 국내 종목 목록 크롤링 (코스피/코스닥)
def get_kr_top_stocks(sosok, market_name, limit=100):
  stocks = []
  page = 1
  print(f'🔍 {market_name} 상위 {limit}개 크롤링...')
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
        stocks.append({'name': name, 'code': code, 'sector': market_name})
        if len(stocks) >= limit:
          break
    page += 1
    time.sleep(0.04)
  return stocks


# 국내 종목 수집 및 지표(RSI, 거래량, 20일선 이격도) 계산
def process_kr_stock(stock):
  code = stock['code']
  try:
    url = f'https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count=600&requestType=0'
    res = requests.get(url, headers=HEADERS, timeout=10)
    root = ET.fromstring(res.content)
    items = root.findall('.//item')
    if not items or len(items) < 30:
      return None

    dates, closes, highs, volumes = [], [], [], []
    for item in items:
      parts = item.attrib['data'].split('|')
      dates.append(parts[0])
      highs.append(float(parts[2]))
      closes.append(float(parts[4]))
      volumes.append(float(parts[5]))

    df = pd.DataFrame(
        {'date': dates, 'close': closes, 'high': highs, 'volume': volumes}
    )
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df = df.sort_values('date').set_index('date')

    # RSI
    rsi_day = calculate_rsi(df['close'], 14)
    df_week = df['close'].resample('W-FRI').last().dropna()
    rsi_week = calculate_rsi(df_week, 14)
    try:
      df_month = df['close'].resample('ME').last().dropna()
    except ValueError:
      df_month = df['close'].resample('M').last().dropna()
    rsi_month = calculate_rsi(df_month, 14)

    # MDD (최근 52주 고점대비)
    recent_high = (
        df['high'].iloc[-250:].max()
        if len(df) >= 250
        else df['high'].max()
    )
    current_close = df['close'].iloc[-1]
    mdd = (
        round(((current_close - recent_high) / recent_high) * 100, 1)
        if recent_high > 0
        else 0.0
    )

    # 이동평균선(20일선) & 이격도 계산
    ma20 = df['close'].rolling(window=20).mean().iloc[-1]
    disparity_20 = (
        round(((current_close - ma20) / ma20) * 100, 1) if ma20 > 0 else 0.0
    )

    # 거래량 및 거래량 급증률 (전일 대비)
    current_vol = int(df['volume'].iloc[-1])
    prev_vol = df['volume'].iloc[-2] if len(df) >= 2 else current_vol
    vol_ratio = (
        round((current_vol / prev_vol) * 100, 1) if prev_vol > 0 else 100.0
    )

    return {
        'name': stock['name'],
        'code': code,
        'sector': stock['sector'],
        'price': int(current_close),
        'rsi': {'day': rsi_day, 'week': rsi_week, 'month': rsi_month},
        'mdd': mdd,
        'ma20': int(ma20),
        'disparity20': disparity_20,
        'volume': current_vol,
        'vol_ratio': vol_ratio,
    }
  except Exception:
    return None


# 미국 종목 수집 및 지표 계산 (yfinance 활용)
def process_us_stock(item):
  ticker, name = item
  try:
    stock = yf.Ticker(ticker)
    df = stock.history(period='2y', interval='1d')
    if df.empty or len(df) < 30:
      return None

    # RSI
    rsi_day = calculate_rsi(df['Close'], 14)
    df_week = df['Close'].resample('W-FRI').last().dropna()
    rsi_week = calculate_rsi(df_week, 14)
    try:
      df_month = df['Close'].resample('ME').last().dropna()
    except ValueError:
      df_month = df['Close'].resample('M').last().dropna()
    rsi_month = calculate_rsi(df_month, 14)

    # MDD
    recent_high = df['High'].iloc[-250:].max()
    current_close = df['Close'].iloc[-1]
    mdd = (
        round(((current_close - recent_high) / recent_high) * 100, 1)
        if recent_high > 0
        else 0.0
    )

    # 이동평균선(20일선) & 이격도
    ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    disparity_20 = (
        round(((current_close - ma20) / ma20) * 100, 1) if ma20 > 0 else 0.0
    )

    # 거래량
    current_vol = int(df['Volume'].iloc[-1])
    prev_vol = df['Volume'].iloc[-2] if len(df) >= 2 else current_vol
    vol_ratio = (
        round((current_vol / prev_vol) * 100, 1) if prev_vol > 0 else 100.0
    )

    return {
        'name': name,
        'code': ticker,
        'sector': 'US (미국)',
        'price': round(float(current_close), 2),
        'rsi': {'day': rsi_day, 'week': rsi_week, 'month': rsi_month},
        'mdd': mdd,
        'ma20': round(float(ma20), 2),
        'disparity20': disparity_20,
        'volume': current_vol,
        'vol_ratio': vol_ratio,
    }
  except Exception:
    return None


if __name__ == '__main__':
  start_time = time.time()
  results = []

  # 1. 국내 코스피 + 코스닥 (200개)
  kr_targets = get_kr_top_stocks(0, 'KOSPI', 100) + get_kr_top_stocks(
      1, 'KOSDAQ', 100
  )
  print('📊 국내 200개 종목 고속 연산 시작...')
  with ThreadPoolExecutor(max_workers=10) as executor:
    kr_res = executor.map(process_kr_stock, kr_targets)
    for r in kr_res:
      if r:
        results.append(r)

  # 2. 미국 상위 100개
  print('🇺🇸 미국 시총 상위 100개 종목 연산 시작...')
  with ThreadPoolExecutor(max_workers=10) as executor:
    us_res = executor.map(process_us_stock, US_TOP_100)
    for r in us_res:
      if r:
        results.append(r)

  # stocks.json 저장
  with open('stocks.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

  print(
      f'🎉 연산 완료! 총 {len(results)}개 종목이 stocks.json에'
      f' 저장되었습니다. ({round(time.time() - start_time, 2)}초)'
  )
