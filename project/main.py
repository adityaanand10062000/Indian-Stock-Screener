import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import seaborn as sns
import numpy as np
import math
import time
import mplfinance as mpf
from datetime import datetime, timedelta

# Setup output folder
output_dir = "stock_graphs"
os.makedirs(output_dir, exist_ok=True)

# Load ticker list
tickers_df = pd.read_csv("nifty_500_list.csv")
tickers = tickers_df["Symbol"].tolist()

def fetch_data(ticker, period="1y", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        return data
    except:
        return None

#------------------------------------------------------------------------------------------------------------------------------------------------------------
#  1st 5 Y high 1 Y low

def strong_5y_weak_1y():
    try:
        min_5y_return = float(input("Enter minimum 5-Year return % (e.g., 50): "))
        max_1y_return = float(input("Enter maximum 1-Year return % (e.g., -5 for negative return): "))
        results = []

        # Create subfolder for this module inside 'stock_graphs'
        output_dir = os.path.join("stock_graphs", "strong_5y_weak_1y")
        os.makedirs(output_dir, exist_ok=True)

        for ticker in tickers:
            try:
                data_5y = fetch_data(ticker, period="5y")
                data_1y = fetch_data(ticker, period="1y")

                if data_5y is None or data_1y is None or data_5y.empty or data_1y.empty:
                    continue

                start_5y = data_5y["Close"].iloc[0].item()
                end_5y = data_5y["Close"].iloc[-1].item()
                start_1y = data_1y["Close"].iloc[0].item()
                end_1y = data_1y["Close"].iloc[-1].item()

                if start_5y == 0 or start_1y == 0:
                    continue

                ret_5y = ((end_5y - start_5y) / start_5y) * 100
                ret_1y = ((end_1y - start_1y) / start_1y) * 100

                if ret_5y >= min_5y_return and ret_1y >= max_1y_return:
                    results.append({
                        "Ticker": ticker,
                        "5Y Return": round(ret_5y, 2),
                        "1Y Return": round(ret_1y, 2)
                    })

                    plt.figure(figsize=(10, 5))
                    data_5y["Close"].plot(title=f"{ticker} - 5Y Close\n5Y: {round(ret_5y, 2)}%, 1Y: {round(ret_1y, 2)}%", color='blue')
                    plt.xlabel("Date")
                    plt.ylabel("Close Price")
                    plt.tight_layout()

                    graph_path = os.path.join(output_dir, f"{ticker}_5y_return_graph.png")
                    plt.savefig(graph_path)
                    plt.close()
                    print(f"📈 Saved graph for {ticker}: {graph_path}")

            except Exception as e:
                print(f"⚠️ Skipped {ticker} due to error: {e}")

        if results:
            df = pd.DataFrame(results)
            print("\n🎯 Stocks matching the criteria:\n")
            print(df)
        else:
            print("❌ No stocks matched the given return filters.")

    except KeyboardInterrupt:
        print("\n❗ Process interrupted by user (Ctrl+C). Exiting module.")

        
#------------------------------------------------------------------------------------------------------------------------------------------------------------
#   2nd Top movers

def top_daily_movers(tickers):
    results = []
    
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="2d", interval="1d", progress=False, auto_adjust=False)
            closes = data['Close']
            if len(closes) < 2:
                continue

            prev_close = closes.iloc[-2].item()
            today_close = closes.iloc[-1].item()
            change_pct = ((today_close - prev_close) / prev_close) * 100
            results.append((ticker, prev_close, today_close, change_pct))
        except Exception as e:
            print(f"⚠️ Error with {ticker}: {e}")
            continue

    if not results:
        print("❌ No valid stock data found.")
        return

    try:
        top_n = int(input("Enter number of top stocks to show (e.g., 10): "))
        direction = input("Enter 1 for Top Gainers or 2 for Top Losers: ")
    except ValueError:
        print("❌ Invalid input.")
        return

    sorted_results = sorted(results, key=lambda x: x[3], reverse=(direction == "1"))
    selected = sorted_results[:top_n]

    print("\n📈 Top Gainers:" if direction == "1" else "\n📉 Top Losers:")
    for ticker, prev_close, today_close, change_pct in selected:
        print(f"{ticker} | Prev Close: {prev_close} | Today Close: {today_close} | Change: {round(change_pct, 2)}%")

    # Create subfolder for this module
    output_dir = os.path.join("stock_graphs", "top_daily_movers")
    os.makedirs(output_dir, exist_ok=True)

    for ticker, _, _, change_pct in selected:
        try:
            intraday = yf.download(ticker, period="1d", interval="5m", progress=False, auto_adjust=False)
            if intraday.empty:
                print(f"⚠️ No intraday data for {ticker}")
                continue

            if intraday.index.tz is None:
                intraday.index = intraday.index.tz_localize('UTC')
            intraday.index = intraday.index.tz_convert('Asia/Kolkata')

            plt.figure(figsize=(10, 5))
            plt.plot(intraday.index, intraday['Close'], label='Close Price', color='blue')
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=intraday.index.tz))
            plt.gcf().autofmt_xdate()

            date_str = intraday.index[-1].strftime("%Y-%m-%d")
            plt.title(f"{ticker} Intraday ({date_str}) - Change: {round(change_pct, 2)}%")
            plt.xlabel("Time (IST)")
            plt.ylabel("Price (INR)")
            plt.grid(True)
            plt.tight_layout()

            filename = os.path.join(output_dir, f"{ticker}_intraday.png")
            plt.savefig(filename)
            plt.close()
            print(f"📊 Chart saved: {filename}")
        except Exception as e:
            print(f"⚠️ Couldn't plot {ticker}: {e}")



#------------------------------------------------------------------------------------------------------------------------------------------------------------
#   3rd Heatmap


def generate_nifty500_weekly_heatmap(tickers):
    print("📥 Fetching weekly price change data...")
    heatmap_data = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="7d", interval="1d", progress=False, auto_adjust=True)

            if df is None or df.empty or not isinstance(df, pd.DataFrame):
                print(f"⚠️ {ticker} skipped: Empty or invalid DataFrame")
                continue

            if 'Close' not in df.columns:
                print(f"⚠️ {ticker} skipped: 'Close' column missing")
                continue

            close_prices = df['Close'].dropna()
            if len(close_prices) < 2:
                print(f"⚠️ {ticker} skipped: Not enough valid close data")
                continue

            prev_close = close_prices.iloc[0].item()
            latest_close = close_prices.iloc[-1].item()


            if prev_close == 0 or pd.isna(prev_close) or pd.isna(latest_close):
                print(f"⚠️ {ticker} skipped: Invalid price data")
                continue

            change_pct = ((latest_close - prev_close) / prev_close) * 100
            heatmap_data.append({'Ticker': ticker, '% Change': change_pct})

        except Exception as e:
            print(f"⚠️ {ticker} skipped due to error: {e}")
            continue

    df = pd.DataFrame(heatmap_data)

    if df.empty or df['% Change'].isna().all():
        print("❌ All % Change values were NaN. Heatmap aborted.")
        return

    df = df.dropna(subset=['% Change']).sort_values(by='% Change', ascending=False).reset_index(drop=True)

    # 🧮 Create square-like matrix
    size = int(math.ceil(math.sqrt(len(df))))
    matrix = np.full((size, size), np.nan)
    labels = np.full((size, size), '', dtype=object)

    for i, row in df.iterrows():
        r, c = divmod(i, size)
        matrix[r][c] = row['% Change']
        labels[r][c] = f"{row['Ticker']}\n{row['% Change']:.2f}%"

    plt.figure(figsize=(16, 10))
    cmap = sns.diverging_palette(20, 220, as_cmap=True)
    sns.heatmap(matrix, annot=labels, fmt='', cmap=cmap, center=0, linewidths=0.5, cbar_kws={'label': '% Change'})

    plt.title("📊 Nifty 500 Weekly % Change Heatmap")
    plt.tight_layout()

    os.makedirs("stock_graphs", exist_ok=True)
    filename = "stock_graphs/nifty500_weekly_heatmap.png"
    plt.savefig(filename)
    plt.close()
    print(f"✅ Heatmap saved to {filename}")

#------------------------------------------------------------------------------------------------------------------------------------------------------------
# 4th 52 Week High/Low

def screen_52_week_high(tickers):
    print("\n📊 Scanning for stocks at 52-week HIGH...")

    os.makedirs("stock_graphs/52_week_high", exist_ok=True)
    found_any = False

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
            if df.empty or 'Close' not in df.columns or df['Close'].dropna().empty:
                print(f"⚠️ {ticker} skipped: No valid 'Close' data")
                continue

            close_prices = df['Close'].dropna()
            latest_close = df['Close'].iloc[-1].item()
            high_52w = df['Close'].max().item()


            # Fix: Ensure scalar comparison
            if np.isclose(latest_close, high_52w, atol=0.01):
                print(f"✅ {ticker} is at 52-week HIGH ({latest_close:.2f})")
                found_any = True

                # Save graph
                plt.figure(figsize=(10, 5))
                plt.plot(close_prices.index, close_prices.values, label='Close Price')
                plt.title(f"{ticker} - 1Y Chart (52W High)")
                plt.xlabel("Date")
                plt.ylabel("Price")
                plt.grid(True)
                plt.legend()
                plt.tight_layout()

                filename = f"stock_graphs/52_week/{ticker}_52whigh_chart.png"
                plt.savefig(filename)
                plt.close()

        except Exception as e:
            print(f"⚠️ {ticker} skipped due to error: {e}")

    if not found_any:
        print("❌ No stocks currently at 52-week high.")
    else:
        print("📁 Charts saved in 'stock_graphs/52_week/'")


#------------------------------------------------------------------------------------------------------------------------------------------------------------
# 5th 52 Week Low

def screen_52_week_low(tickers):
    print("\n📉 Scanning for stocks at 52-week LOW...")

    os.makedirs("stock_graphs/52_week_low", exist_ok=True)
    found_any = False

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
            if df.empty or 'Close' not in df.columns or df['Close'].dropna().empty:
                print(f"⚠️ {ticker} skipped: No valid 'Close' data")
                continue

            close_prices = df['Close'].dropna()
            latest_close = df['Close'].iloc[-1].item()
            low_52w = df['Close'].min().item()

            # Fix: Ensure scalar comparison
            if np.isclose(latest_close, low_52w, atol=0.01):
                print(f"✅ {ticker} is at 52-week LOW ({latest_close:.2f})")
                found_any = True

                # Save graph
                plt.figure(figsize=(10, 5))
                plt.plot(close_prices.index, close_prices.values, label='Close Price', color='red')
                plt.title(f"{ticker} - 1Y Chart (52W Low)")
                plt.xlabel("Date")
                plt.ylabel("Price")
                plt.grid(True)
                plt.legend()
                plt.tight_layout()

                filename = f"stock_graphs/52_week/{ticker}_52wlow_chart.png"
                plt.savefig(filename)
                plt.close()

        except Exception as e:
            print(f"⚠️ {ticker} skipped due to error: {e}")

    if not found_any:
        print("❌ No stocks currently at 52-week low.")
    else:
        print("📁 Charts saved in 'stock_graphs/52_week/'")
        
        
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# 6 RSI

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def screen_rsi_stocks(tickers, mode):
    if mode not in ['low', 'high']:
        print("❌ Invalid mode. Use 'low' for RSI<30 or 'high' for RSI>70.")
        return

    print(f"\n📊 Scanning for stocks with RSI {'< 30' if mode == 'low' else '> 70'}...")

    folder = f"stock_graphs/rsi_{mode}"
    os.makedirs(folder, exist_ok=True)
    found_any = False

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="3mo", interval="1d", progress=False, auto_adjust=True)

            if df.empty or 'Close' not in df.columns or df['Close'].dropna().empty:
                print(f"⚠️ {ticker} skipped: No valid 'Close' data")
                continue

            rsi = calculate_rsi(df['Close']).dropna()
            if rsi.empty:
                print(f"⚠️ {ticker} skipped: RSI is all NaN")
                continue

            latest_rsi = rsi.iloc[-1]
            if isinstance(latest_rsi, pd.Series):  # extra safety check
                latest_rsi = latest_rsi.item()

            # Now safe to compare
            if (mode == 'low' and latest_rsi < 30) or (mode == 'high' and latest_rsi > 70):
                print(f"✅ {ticker} has RSI = {latest_rsi:.2f} ({'Oversold' if mode == 'low' else 'Overbought'})")
                found_any = True

                plt.figure(figsize=(10, 5))
                plt.plot(df['Close'], label='Close Price', color='blue')
                plt.title(f"{ticker} - Close Price (RSI {mode.upper()})")
                plt.xlabel("Date")
                plt.ylabel("Price")
                plt.grid(True)
                plt.legend()
                plt.tight_layout()

                filename = f"{folder}/{ticker}_rsi_{mode}.png"
                plt.savefig(filename)
                plt.close()

        except Exception as e:
            print(f"⚠️ {ticker} skipped due to error: {e}")

    if not found_any:
        print("❌ No stocks found matching RSI criteria.")
    else:
        print(f"📁 Charts saved in '{folder}/'")

#------------------------------------------------------------------------------------------------------------------------------------------------------------
# 7 Gap up/down

def screen_gap_up_down(tickers, gap_threshold=2.0, user_choice="1"):
    mode = 'gap_up' if user_choice == "1" else 'gap_down'
    print(f"\n📊 Scanning for {'Gap Up' if mode == 'gap_up' else 'Gap Down'} stocks (Gap {'>' if mode == 'gap_up' else '<'} {gap_threshold}%)...")

    folder = f"stock_graphs/{mode}"
    os.makedirs(folder, exist_ok=True)
    found_any = False

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="15d", interval="1d", progress=False, auto_adjust=False)

            # Flatten multi-index if needed
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if df is None or df.empty or len(df) < 2:
                print(f"⚠️ {ticker} skipped: Not enough data.")
                continue

            required_cols = ['Open', 'Close', 'High', 'Low', 'Volume']
            if not set(required_cols).issubset(df.columns):
                print(f"⚠️ {ticker} skipped: Missing OHLCV columns.")
                continue

            prev_close_val = df['Close'].iloc[-2]
            today_open_val = df['Open'].iloc[-1]

            if pd.isna(prev_close_val) or pd.isna(today_open_val):
                print(f"⚠️ {ticker} skipped: Invalid Open/Close values.")
                continue

            gap_percent = ((today_open_val - prev_close_val) / prev_close_val) * 100

            if (mode == 'gap_up' and gap_percent > gap_threshold) or \
               (mode == 'gap_down' and gap_percent < -gap_threshold):

                print(f"✅ {ticker}: Gap = {gap_percent:.2f}%")
                found_any = True

                plot_df = df[required_cols].copy().tail(10)
                plot_df.dropna(inplace=True)
                plot_df = plot_df[plot_df['Volume'] > 0]
                if len(plot_df) < 2:
                    print(f"⚠️ {ticker} skipped: Not enough clean data.")
                    continue

                if not isinstance(plot_df.index, pd.DatetimeIndex):
                    try:
                        plot_df.index = pd.to_datetime(plot_df.index)
                    except Exception as e:
                        print(f"⚠️ {ticker} skipped: Invalid datetime index. {e}")
                        continue

                for col in required_cols:
                    plot_df[col] = pd.to_numeric(plot_df[col], errors='coerce')
                plot_df.dropna(inplace=True)

                try:
                    plot_df = plot_df.astype({
                        'Open': float,
                        'High': float,
                        'Low': float,
                        'Close': float,
                        'Volume': int
                    })
                except Exception as e:
                    print(f"⚠️ {ticker} skipped during type casting: {e}")
                    continue

                try:
                    # Custom plotting to show all dates
                    fig, axlist = mpf.plot(
                        plot_df,
                        type='candle',
                        style='yahoo',
                        title=f"{ticker} ({'Gap Up' if mode == 'gap_up' else 'Gap Down'})",
                        ylabel='Price',
                        volume=True,
                        returnfig=True
                    )

                    ax = axlist[0]  # Main price chart
                    ax.set_xticks(range(len(plot_df)))
                    ax.set_xticklabels(
                        [d.strftime('%b-%d') for d in plot_df.index],
                        rotation=20,
                        ha='right'
                    )

                    fig.subplots_adjust(bottom=0.2)  # Add more spacing at the bottom for date labels

                    fig.savefig(f"{folder}/{ticker}_gap_{mode}.png")
                    plt.close(fig)

                except Exception as e:
                    print(f"⚠️ {ticker} skipped during plotting: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ {ticker} skipped due to error: {e}")
            continue

    if not found_any:
        print("❌ No stocks matched the gap criteria.")
    else:
        print(f"📁 Charts saved in '{folder}/'")
        
        
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# 8 macd crossover

def screen_macd_crossover(tickers, user_choice="bullish", save_charts=True):
    crossover_type = "bullish" if user_choice.lower() == "bullish" else "bearish"
    print(f"\n📊 Scanning for {crossover_type.title()} MACD Crossovers...")

    folder = f"stock_graphs/macd_{crossover_type}"
    if save_charts:
        os.makedirs(folder, exist_ok=True)

    found_any = False

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="3mo", interval="1d", auto_adjust=True, progress=False)

            if df.empty or len(df) < 35:
                print(f"⚠️ {ticker} skipped: Not enough data.")
                continue

            # Calculate MACD and Signal Line
            df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA12'] - df['EMA26']
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

            # Detect crossover (today vs yesterday)
            macd_today = df['MACD'].iloc[-1]
            signal_today = df['Signal'].iloc[-1]
            macd_yesterday = df['MACD'].iloc[-2]
            signal_yesterday = df['Signal'].iloc[-2]

            bullish = macd_yesterday < signal_yesterday and macd_today > signal_today
            bearish = macd_yesterday > signal_yesterday and macd_today < signal_today

            if (crossover_type == "bullish" and bullish) or (crossover_type == "bearish" and bearish):
                print(f"✅ {ticker}: {crossover_type.title()} Crossover")
                found_any = True

                if save_charts:
                    plot_df = df[['Close', 'MACD', 'Signal']].tail(60)

                    plt.figure(figsize=(10, 6))
                    plt.plot(plot_df.index, plot_df['MACD'], label='MACD Line', color='blue')
                    plt.plot(plot_df.index, plot_df['Signal'], label='Signal Line', color='red')
                    plt.title(f"{ticker} - MACD {crossover_type.title()} Crossover")
                    plt.xlabel("Date")
                    plt.ylabel("MACD")
                    plt.legend()
                    plt.grid(True)
                    plt.tight_layout()
                    plt.savefig(f"{folder}/{ticker}_macd_{crossover_type}.png")
                    plt.close()

        except Exception as e:
            print(f"⚠️ {ticker} skipped due to error: {e}")

    if not found_any:
        print("❌ No stocks matched the MACD crossover criteria.")
    else:
        print(f"📁 Charts saved in '{folder}/'")
        
        
#------------------------------------------------------------------------------------------------------------------------------------------------------------

# return over n years

def plot_return_over_n_years(tickers):
    try:
        n_years = int(input("Enter number of years (e.g., 3 for 3-year return): ").strip())
        if n_years <= 0:
            print("❌ Enter a valid number of years (>0).")
            return
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return

    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * n_years)

    folder = f"stock_graphs/returns_over_{n_years}y"
    os.makedirs(folder, exist_ok=True)

    print(f"\n📊 Generating {n_years}-Year Return Line Charts...\n")

    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)


            if df is None or df.empty or 'Close' not in df.columns:
                print(f"⚠️ {ticker} skipped: No valid data.")
                continue

            df = df[['Close']].dropna()
            if df.empty or len(df) < 2:
                print(f"⚠️ {ticker} skipped: Not enough price history.")
                continue

            initial_price = df['Close'].iloc[0].item()
            final_price = df['Close'].iloc[-1].item()
            return_pct = ((final_price - initial_price) / initial_price) * 100


            plt.figure(figsize=(10, 5))
            plt.plot(df.index, df['Close'], label='Close Price')
            plt.title(f"{ticker} - {n_years}Y Return: {return_pct:.2f}%")
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            plt.savefig(f"{folder}/{ticker}_return_{n_years}y.png")
            plt.close()
            print(f"✅ {ticker}: Return = {return_pct:.2f}%")

        except Exception as e:
            print(f"⚠️ {ticker} skipped due to error: {e}")

    print(f"\n📁 All charts saved in '{folder}/'")


                
                
#------------------------------------------------------------------------------------------------------------------------------------------------------------

def show_menu():
    print("\n📊 STOCK SCREENER MENU 📊")
    print("1. Strong 5Y Return + Weak 1Y (Drawdown) Filter")
    print("2. Top Daily Gainers/Losers")
    print("3. Heatmap ")
    print("4. 52 Week High")
    print("5. 52 Week Low")
    print("6. RSI Screen (Low/High)")
    print("7. Gap Up/Down Screen")
    print("8. MACD Crossover Screen")
    print("9. Return Over N Years")
    print("10. Exit")

while True:
    show_menu()
    choice = input("Enter your choice (1-10): ").strip()

    if choice == "1":
        strong_5y_weak_1y()

    elif choice == "2":
        top_daily_movers(tickers)

    elif choice == "3":
        generate_nifty500_weekly_heatmap(tickers)

    elif choice == "4":
        screen_52_week_high(tickers)
        
    elif choice == "5":
        screen_52_week_low(tickers)
        
    elif choice == "6":
        mode = input("Enter mode ('low' for RSI<30 or 'high' for RSI>70): ").strip().lower()
        if mode in ['low', 'high']:
            screen_rsi_stocks(tickers, mode)
        else:
            print("Invalid mode. Try again.")
            
    elif choice == "7":
        print("\n📈 Gap Screener:")
        print("1. Gap Up")
        print("2. Gap Down")
        sub_choice = input("Enter 1 for Gap Up or 2 for Gap Down: ").strip()

        if sub_choice not in ["1", "2"]:
            print("❌ Invalid choice for gap mode.")
            continue

        try:
            gap_threshold = float(input("Enter gap threshold percentage (default 2): ").strip())
        except ValueError:
            print("❌ Invalid threshold. Using default 2%.")
            gap_threshold = 2.0

        screen_gap_up_down(tickers, gap_threshold, sub_choice)
        
    elif choice == "8":
        print("\n📉 MACD Crossover Screener:")
        print("1. Bullish Crossover")
        print("2. Bearish Crossover")
        mode_choice = input("Enter 1 for Bullish or 2 for Bearish: ").strip()

        if mode_choice == "1":
            screen_macd_crossover(tickers, user_choice="bullish")
        elif mode_choice == "2":
            screen_macd_crossover(tickers, user_choice="bearish")
        else:
            print("❌ Invalid input. Please enter 1 or 2.")
            
    
    elif choice == "9":
        plot_return_over_n_years(tickers)



    elif choice == "10":
        print("👋 Goodbye!")
        break

    else:
        print("❌ Invalid choice, please try again.")

