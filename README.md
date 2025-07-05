# Indian-Stock-Screener
📊 A Python-based Nifty 500 stock screener with 9 modules including RSI, MACD, gap up/down, 52-week high/low, multi-year returns, and more. Uses yfinance, pandas, and mplfinance for data, filtering, and plotting. Ideal for investors, analysts, and learners.


# 🎯 Objective:
To develop a comprehensive and user-friendly stock screener using Python that allows users to analyze Nifty 500 stocks based on various technical and return-based indicators, and generate automated graphs to visually assist in decision-making. The tool uses yfinance, pandas, numpy, matplotlib and provides multiple stock filtering strategies for traders, analysts, and investors.


# 📋 Description of Modules

### 1. Strong 5Y Return + Weak 1Y Return (Drawdown) Filter

Purpose: Identify fundamentally strong stocks that have performed well over the last 5 years but are currently in a short-term drawdown. This helps spot potential buying opportunities.

Logic:

Filter stocks where 5Y return ≥ user-defined %
AND 1Y return ≤ user-defined % (e.g., negative or weak return)

![360ONE NS_5y_return_graph](https://github.com/user-attachments/assets/e52d11da-947e-47de-80bd-827edcf87315) 
![ANGELONE NS_5y_return_graph](https://github.com/user-attachments/assets/3424e5cd-0398-4130-b144-b7202a89ea64)

------------------------------------------------------

### 2. Top Daily Gainers/Losers

Purpose: Quickly identify the top performers and worst-performing stocks of the day based on daily price percentage changes.

Logic:

Download past 2 days' close prices
Compute % change
Show top N gainers or losers
Plot intraday 5-minute chart for each selected stock
![BPCL NS_intraday](https://github.com/user-attachments/assets/7cb7cd7c-ecb0-46f2-817e-185c60ec8b17)
![SAPPHIRE NS_intraday](https://github.com/user-attachments/assets/b3a880b4-7602-4ee8-a056-e8c5e751c5c5)


-----------------------------------------------------

### 3. Heatmap

Purpose: Provide a color-coded view of how all Nifty 500 stocks performed during the week.

Logic:

Compute % change from previous close
Display as color-coded heatmap grouped by sector or alphabet

![nifty500_weekly_heatmap](https://github.com/user-attachments/assets/419e6cc5-bec2-464c-ba7e-00b66538d2c1)

-----------------------------------------------------

### 4. 52-Week High/Low Screener

Purpose: Detect stocks that have touched their 52-week highest or lowest price today.

Logic:

Download 1-year daily data
If today's closing price ≈ 52-week high or low (within ±0.01), flag it
Plot 1-year close price line chart

![ASAHIINDIA NS_52whigh_chart](https://github.com/user-attachments/assets/c4822ae6-55eb-4c80-9d0a-419b50a74194)
![ULTRACEMCO NS_52whigh_chart](https://github.com/user-attachments/assets/17b74272-8eaf-4131-9491-1f6f36ff03b4)

-----------------------------------------------------

### 5. RSI Screener (Overbought/Oversold)

Purpose: Identify stocks that are potentially overbought (RSI > 70) or oversold (RSI < 30), based on Relative Strength Index.

Logic:

Calculate 14-day RSI
Filter based on user preference (overbought or oversold)

![SBICARD NS_rsi_low](https://github.com/user-attachments/assets/726bd3db-4b34-4831-8a8d-61242a27df70)
![HINDZINC NS_rsi_low](https://github.com/user-attachments/assets/b02c8bb4-3921-4d00-82be-36bc00296e0c)

-----------------------------------------------------

### 6. Gap Up/Down Screener

Purpose: Detect stocks that opened significantly higher or lower than their previous day’s close.

Logic:

Compare today’s opening price to yesterday’s close
Flag stocks with large upward/downward gap

![BAJFINANCE NS_gap_gap_up](https://github.com/user-attachments/assets/55cbb3e2-eca1-4c46-bb80-70d80b905ec5)

![BANDHANBNK NS_gap_gap_down](https://github.com/user-attachments/assets/fca5a086-db4c-43d5-baf3-25d6d45600bd)


---------------------------------------------------

### 7. MACD Crossover Screener

Purpose: Spot bullish or bearish momentum changes using Moving Average Convergence Divergence crossovers.

Logic:

Calculate MACD and Signal Line
Flag bullish crossover (MACD crosses above signal) or bearish (crosses below)


![TATAMOTORS NS_macd_bullish](https://github.com/user-attachments/assets/00cd8192-e1cb-49b4-81b7-ab99a4fb5497)
![HYUNDAI NS_macd_bearish](https://github.com/user-attachments/assets/88fe13ee-6330-4b57-84ad-b5f70ebd39c3)


--------------------------------------------------

### 8. Return Over N Years Module

Purpose: Visualize the return % over a custom number of years (e.g., 2Y, 3Y, 7Y) for every stock.

Logic:

Take input of N years
Fetch data
Calculate % return
Plot N-year performance line chart

![360ONE NS_return_5y](https://github.com/user-attachments/assets/9164e691-fc14-4fcf-a1c3-d7a038f48f1c)
![AAVAS NS_return_5y](https://github.com/user-attachments/assets/46877a21-8e22-468f-9391-33fbf710e0dc)


--------------------------------------------------


#  Conclusion
The development of this Nifty 500 Stock Screener project marks a significant step toward the practical application of financial data analysis using Python. This project not only consolidates various technical and return-based indicators into a single, user-friendly tool but also provides visual insights through automated charts, making it a valuable resource for both novice investors and seasoned analysts.

Throughout the project, we leveraged Python’s robust data science libraries such as yfinance, pandas, numpy, and matplotlib to fetch, clean, analyze, and visualize stock market data efficiently. The screener was built to cover a comprehensive range of modules—from long-term performance filters like "Strong 5Y Return + Weak 1Y Drawdown" to short-term technical setups such as "MACD Crossovers" and "RSI Extremes." Additionally, features like "Top Daily Gainers/Losers" and the "Gap Up/Down Screener" provide users with real-time momentum-based filtering capabilities.

One of the unique strengths of this tool lies in its visual output generation. For every matching stock in a module, the program automatically generates high-quality graphs and stores them in neatly organized directories. This visual representation greatly enhances the decision-making process, helping users identify trends, patterns, and key price levels at a glance.

Moreover, the project reflects a balanced integration of fundamental return-based metrics and technical indicators, which is essential for developing a well-rounded investment strategy. The modular architecture also makes the tool highly scalable—new features such as Bollinger Bands, PE ratio filters, or volume analysis can be easily added without disrupting existing functionality.

From a technical standpoint, this project improved our understanding of API data extraction, error handling in real-world financial datasets, user interaction through console inputs, and dynamic visualization techniques. It also emphasized the importance of data integrity, directory management, and exception handling to ensure a smooth and error-free user experience.

In conclusion, this stock screener serves as a practical example of how programming and financial analysis can intersect to build intelligent, data-driven tools. It not only reinforces key programming concepts but also enhances analytical thinking from a finance perspective. The flexibility, automation, and depth of insights offered by this tool can empower users to make informed decisions in the ever-evolving stock market. With further refinements and the potential addition of a GUI or web interface, this project can evolve into a full-scale market analytics platform.



