import streamlit as st
import pandas as pd
import datetime
import FinanceDataReader as fdr
import yfinance as yf
import xlsxwriter
from io import BytesIO

@st.cache_data
def get_stock_info():
    base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"    
    method = "download"
    url = "{0}?method={1}".format(base_url, method)   
    df = pd.read_html(url, encoding='cp949', header=0)[0]
    df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")     
    df = df[['회사명','종목코드']]
    return df

def get_ticker_symbol(company_name):     
    df = get_stock_info()
    code = df[df['회사명']==company_name]['종목코드'].values    
    if len(code) > 0:
        ticker_symbol = code[0]
        return ticker_symbol
    else:
        return None
    
st.header("무슨 주식을 사야 부자가 되려나...")
# Using object notation
st.sidebar.header("회사 이름과 기간을 입력하세요")
stock_name = st.sidebar.text_input('회사 이름', ('삼성전자'))
date_range = st.sidebar.date_input('시작일 - 종료일',
                                    (datetime.date(2019, 1, 1), 
                                    datetime.date(2023, 12, 31)))

if st.sidebar.button('추가 데이터 입력'):
    ticker_symbol = get_ticker_symbol(stock_name)
    if ticker_symbol:
        start_p = date_range[0]
        end_p = date_range[1] + datetime.timedelta(days=1)
        df = fdr.DataReader(ticker_symbol, start_p, end_p, exchange="KRX")
        df.index = df.index.date
        st.subheader(f"[{stock_name}] Stock Price Data")
        st.dataframe(df.head())
        st.line_chart(df)
        col1, col2 = st.columns(2)
        
        output = BytesIO() # 파일을 바이너리로 변환
        workbook = xlsxwriter.Workbook(output, {'in_memory': True}) # 바이너리 파일을 엑셀 파일로 변환
        worksheet = workbook.add_worksheet()
        # worksheet.write('A1', 'Hello')
        workbook.close()

        with col1:
            st.download_button(
                label="CSV 파일 다운로드",
                data=df.to_csv(),
                file_name='app_df.csv',
                mime='text/csv'
            )

        with col2:
            st.download_button(
                label="엑셀 파일 다운로드",
                data=output.getvalue(),
                file_name="workbook.xlsx",
                mime="application/vnd.ms-excel"
            )
        col1, col2 = st.columns([1,1])
    else:
        st.warning(f"Stock code not found for {stock_name}")