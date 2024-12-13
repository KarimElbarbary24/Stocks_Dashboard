from stocks import Stocks


stock_app = Stocks()


engine = stock_app.connect_to_postgres()


print("Creating schema...") 
stock_app.create_stocks_schema(engine)


print("Fetching and storing stock data for AAPL...")
stock_app.fetch_and_store_stock_data('AAPL', engine)

print("Stock data successfully stored!")
