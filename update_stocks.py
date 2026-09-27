from concurrent.futures import ThreadPoolExecutor
import json
import time
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd
import requests

# 네이버 금융 크롤링용 헤더
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
}


# 1. 네이버 금융 시가총액 상위 종목 크롤링 함수 (코스피: sosok=0 / 코스닥: sosok=1)
def get_top_stocks(sosok, market_name, limit=100):
  stocks = []
  page = 1
  print(f'🔍 {market_name} 시가총액 상위 {limit}개 종목 목록 수집 중...')

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
    time.sleep(0.05)

  return stocks


# 2. 정밀 RSI 계산 함수 (월더스 지수평활 방식 적용)
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


# 3. 개별 종목 주가 데이터 수집 및 RSI/MDD 연산
def process_stock(stock):
  code = stock['code']
  name = stock['name']

  try:
    # 네이버 시세 차트 API (최근 600영업일 일봉 데이터 요청)
    url = f'https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count=600&requestType=0'
    res = requests.get(url, headers=HEADERS, timeout=10)
    root = ET.fromstring(res.content)

    items = root.findall('.//item')
    if not items or len(items) < 20:
      return None

    dates, closes, highs = [], [], []
    for item in items:
      parts = item.attrib['data'].split('|')
      dates.append(parts[0])
      highs.append(float(parts[2]))
      closes.append(float(parts[4]))

    # 판다스 시계열 데이터프레임 생성
    df = pd.DataFrame({'date': dates, 'close': closes, 'high': highs})
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df = df.sort_values('date').set_index('date')

    # 1) 일봉 RSI (14일)
    rsi_day = calculate_rsi(df['close'], 14)

    # 2) 주봉 리샘플링 & RSI (14주)
    df_week = df['close'].resample('W-FRI').last().dropna()
    rsi_week = calculate_rsi(df_week, 14)

    # 3) 월봉 리샘플링 & RSI (14개월)
    try:
      df_month = df['close'].resample('ME').last().dropna()
    except ValueError:
      df_month = df['close'].resample('M').last().dropna()
    rsi_month = calculate_rsi(df_month, 14)

    # 4) 최근 52주(약 250영업일) 최고점 대비 하락률 (MDD)
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

    return {
        'name': name,
        'code': code,
        'sector': stock['sector'],
        'rsi': {'day': rsi_day, 'week': rsi_week, 'month': rsi_month},
        'mdd': mdd,
    }

  except Exception as e:
    return None


# 메인 실행부
if __name__ == '__main__':
  start_time = time.time()

  # 코스피 100개 + 코스닥 100개 종목 리스트 수집
  kospi_stocks = get_top_stocks(sosok=0, market_name='KOSPI', limit=100)
  kosdaq_stocks = get_top_stocks(sosok=1, market_name='KOSDAQ', limit=100)
  all_targets = kospi_stocks + kosdaq_stocks

  print(
      f'총 {len(all_targets)}개 종목 (코스피 100 + 코스닥 100) RSI 고속 연산'
      ' 시작...'
  )

  # 병렬 고속 처리 (10개 스레드로 동시 요청)
  results = []
  with ThreadPoolExecutor(max_workers=10) as executor:
    processed = executor.map(process_stock, all_targets)
    for res in processed:
      if res:
        results.append(res)

  # stocks.json 파일 저장
  with open('stocks.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

  elapsed = round(time.time() - start_time, 2)
  print(
      f'🎉 연산 완료! 총 {len(results)}개 종목의 데이터가 stocks.json에'
      f' 저장되었습니다. (소요시간: {elapsed}초)'
  )
