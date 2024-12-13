import os
import dotenv
import pandas as pd
import requests
import psycopg
from sqlalchemy import create_engine, text


class Stocks:
    def __init__(self):
        dotenv.load_dotenv()
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD")
        self.server, self.engine = self.connect_to_postgres(self.postgres_password, host="postgres", create_stocks=True)


    def connect_to_postgres(self, pw, user="postgres", host="localhost", port="5432", create_stocks=False):
        """
        Connect to PostgreSQL, creating the 'stocks' database if necessary.
        """
        dbserver = psycopg.connect(user=user, password=pw, host=host, port=port)
        dbserver.autocommit = True
        cursor = dbserver.cursor()

        if create_stocks:
            try:
                # Terminate existing connections to the 'stocks' database
                cursor.execute("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'stocks'
                AND pid <> pg_backend_pid();
                """)
                print("Terminated active connections to 'stocks'.")
                
                # Drop and recreate the database
                cursor.execute("DROP DATABASE IF EXISTS stocks")
                print("Dropped database 'stocks'.")
            except Exception as e:
                print(f"Error while dropping database 'stocks': {e}")
            
            cursor.execute("CREATE DATABASE stocks")
            print("Created database 'stocks'.")

        engine = create_engine(f"postgresql+psycopg://{user}:{pw}@{host}:{port}/stocks")
        return dbserver, engine
    
    '''def create_all_tables(self):
        """
        Create all necessary tables in the database.
        """
        stock_data_query = """
        CREATE TABLE IF NOT EXISTS stock_data (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR NOT NULL,
            date DATE NOT NULL,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume INT,
            UNIQUE (symbol, date) -- Composite unique constraint
        );
        """
        technical_indicators_query = """
        CREATE TABLE IF NOT EXISTS technical_indicators (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR NOT NULL,
            date DATE NOT NULL,
            ma_50 FLOAT,
            rsi FLOAT,
            bollinger_upper FLOAT,
            bollinger_lower FLOAT,
            FOREIGN KEY (symbol, date) REFERENCES stock_data (symbol, date) ON DELETE CASCADE
        );
        """
        fundamental_data_query = """
        CREATE TABLE IF NOT EXISTS fundamental_data (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR NOT NULL,
            report_date DATE NOT NULL,
            revenue FLOAT,
            earnings FLOAT,
            pe_ratio FLOAT,
            dividend_yield FLOAT,
            FOREIGN KEY (symbol) REFERENCES stock_data (symbol) ON DELETE CASCADE
        );
        """
        try:
            with self.engine.connect() as conn:
                # Create stock_data table
                conn.execute(text(stock_data_query))
                print("Ensured table 'stock_data' exists.")

                # Create technical_indicators table
                conn.execute(text(technical_indicators_query))
                print("Ensured table 'technical_indicators' exists.")

                # Create fundamental_data table
                conn.execute(text(fundamental_data_query))
                print("Ensured table 'fundamental_data' exists.")

        except Exception as e:
            print(f"Error creating tables: {e}")
            raise'''




    def fetch_stock_data(self, symbol):
        """
        Fetch historical stock data from Alpha Vantage.
        """
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={self.alpha_vantage_key}"
        response = requests.get(url)
        data = response.json()

        if "Time Series (Daily)" not in data:
            raise ValueError(f"API response does not contain 'Time Series (Daily)' data for {symbol}")

        records = [
            {
                "symbol": symbol,
                "date": date,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["6. volume"]),
            }
            for date, values in data["Time Series (Daily)"].items()
        ]
        return pd.DataFrame(records)

    def upload_stock_data(self, df):
        """
        Upload stock data to the database.
        """
        df.to_sql("stock_data", con=self.engine, index=False, if_exists="append")
        print(f"Uploaded {len(df)} rows to 'stock_data'.")

    def calculate_technical_indicators(self, symbol):
        """
        Calculate and upload technical indicators for a given stock symbol.
        """
        query = f"""
        SELECT date, close
        FROM stock_data
        WHERE symbol = '{symbol}'
        ORDER BY date;
        """
        df = pd.read_sql_query(query, con=self.engine)

        if df.empty:
            print(f"No stock data available for {symbol}. Cannot calculate indicators.")
            return

        df["ma_50"] = df["close"].rolling(window=50).mean()
        df["rsi"] = df["close"].diff().apply(lambda x: max(x, 0)).rolling(window=14).mean() / \
                    df["close"].diff().apply(abs).rolling(window=14).mean()
        rolling_mean = df["close"].rolling(window=20).mean()
        rolling_std = df["close"].rolling(window=20).std()
        df["bollinger_upper"] = rolling_mean + (rolling_std * 2)
        df["bollinger_lower"] = rolling_mean - (rolling_std * 2)

        indicators = df.dropna(subset=["ma_50", "rsi", "bollinger_upper", "bollinger_lower"])
        indicators["symbol"] = symbol

        indicators.to_sql("technical_indicators", con=self.engine, index=False, if_exists="append")
        print(f"Uploaded technical indicators for {symbol}.")

    def fetch_and_upload_fundamental_data(self, symbol):
        """
        Fetch and upload fundamental data for a given stock symbol.
        """
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={self.alpha_vantage_key}"
        response = requests.get(url)
        data = response.json()

        if not data:
            print(f"No fundamental data found for {symbol}.")
            return

        fundamental_data = {
            "symbol": symbol,
            "report_date": pd.Timestamp.now().date(),
            "revenue": float(data.get("RevenueTTM", 0)),
            "earnings": float(data.get("EPS", 0)),
            "pe_ratio": float(data.get("PERatio", 0)),
            "dividend_yield": float(data.get("DividendYield", 0)),
        }
        df = pd.DataFrame([fundamental_data])
        df.to_sql("fundamental_data", con=self.engine, index=False, if_exists="append")
        print(f"Uploaded fundamental data for {symbol}.")
