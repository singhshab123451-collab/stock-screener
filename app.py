import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Set up the page configuration
st.set_page_config(page_title="Stock Screener", layout="wide")

st.title("📈 Stock Screener")
st.markdown("Filter stocks by Price, P/E Ratio, and Dividend Yield.")

# 2. Sidebar for User Inputs
st.sidebar.header("Filter Criteria")

# Input for Stock Tickers (Comma separated)
ticker_input = st.sidebar.text_area(
    "Enter Stock Tickers (e.g., AAPL, MSFT, TSLA)", 
    "AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, JPM, JNJ, PG, KO"
)

# Filter Inputs
min_price = st.sidebar.number_input("Minimum Price", value=0)
max_pe = st.sidebar.number_input("Max P/E Ratio", value=50.0)
min_div_yield = st.sidebar.number_input("Min Dividend Yield (%)", value=0.0)

# 3. Function to fetch data
def get_stock_data(tickers):
    if not tickers:
        return pd.DataFrame()
    
    # Clean up input
    tickers = [t.strip().upper() for t in tickers.split(',')]
    
    data = []
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(tickers):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract relevant fields
            row = {
                'Ticker': ticker,
                'Company Name': info.get('shortName', 'N/A'),
                'Current Price': info.get('currentPrice', 0),
                'P/E Ratio': info.get('trailingPE', None),
                'Dividend Yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'Market Cap': info.get('marketCap', 0),
                'Sector': info.get('sector', 'N/A')
            }
            data.append(row)
        except:
            pass
        
        # Update progress
        progress_bar.progress((i + 1) / len(tickers))
            
    return pd.DataFrame(data)

# 4. Main Logic
if st.button("🔍 Search Stocks"):
    with st.spinner('Fetching data from Yahoo Finance...'):
        df = get_stock_data(ticker_input)
        
        if not df.empty:
            # Apply Filters
            filtered_df = df[
                (df['Current Price'] >= min_price) &
                (df['P/E Ratio'] <= max_pe) &
                (df['Dividend Yield'] >= min_div_yield)
            ].sort_values(by='P/E Ratio')
            
            st.success(f"Found {len(filtered_df)} matching stocks!")
            
            # Display Metrics
            st.dataframe(
                filtered_df.style.format({
                    'Current Price': "${:.2f}",
                    'P/E Ratio': "{:.2f}",
                    'Dividend Yield': "{:.2f}%",
                    'Market Cap': "${:,.0f}"
                }), 
                use_container_width=True
            )
            
            # Chart for top result
            if not filtered_df.empty:
                st.write("---")
                st.write(f"### 📊 Price History: {filtered_df.iloc[0]['Ticker']}")
                first_ticker = filtered_df.iloc[0]['Ticker']
                hist = yf.Ticker(first_ticker).history(period="3mo")
                st.line_chart(hist['Close'])
                
        else:
            st.warning("No data found. Check your ticker symbols.")
