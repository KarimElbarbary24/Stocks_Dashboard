from stocks import Stocks

# Initialize the Stocks class
stock_app = Stocks()

# Connect to the database
engine = stock_app.connect_to_postgres()

# Step 1: Create the schema
print("Creating schema...") 
stock_app.create_stocks_schema(engine)

# Step 2: Fetch and store stock data
print("Fetching and storing stock data for AAPL...")
stock_app.fetch_and_store_stock_data('AAPL', engine)

print("Stock data successfully stored!")
