
import pandas as pd  # Reused
from sklearn.model_selection import train_test_split  # Reused
from sklearn.ensemble import GradientBoostingRegressor  # Improvised: GBM for stock price prediction
from sklearn.metrics import mean_squared_error  # Reused
import joblib  # Reused: For saving/loading models
from stocks import Stocks  # Improvised: Leverage Stocks class for data

class StockMLModel:
    def __init__(self):
        self.stocks = Stocks()  # Improvised: Use the Stocks class for data retrieval
        self.model = None  # Improvised: Placeholder for the ML model

    def prepare_data(self, symbol):
        """
        Prepare data for modeling, including feature engineering and train-test split.
        """
        # Inspired: Query and preprocess data from stocks.py
        df = self.stocks.get_stock_data(symbol)
        df = self.stocks.calculate_moving_average(df)  # Reused: Feature engineering
        df = self.stocks.calculate_bollinger_bands(df)  # Reused

        # Improvised: Create features and labels
        df["target"] = df["close"].shift(-1)  # Predict next day's close price
        df.dropna(inplace=True)  # Reused: Handle missing values

        features = ["close", "ma_50", "bollinger_upper", "bollinger_lower"]
        X = df[features]
        y = df["target"]

        # Reused: Split into training and testing sets
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, symbol):
        """
        Train a Gradient Boosting model on the stock data.
        """
        X_train, X_test, y_train, y_test = self.prepare_data(symbol)

        # Improvised: Train a Gradient Boosting Regressor
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        # Improvised: Evaluate the model
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Model trained. Test MSE: {mse:.4f}")

        # Improvised: Save the model
        joblib.dump(self.model, f"{symbol}_model.pkl")

    def load_model(self, model_path):
        """
        Load a pre-trained model.
        """
        # Reused: Use joblib to load models
        self.model = joblib.load(model_path)

    def predict(self, features):
        """
        Predict stock prices using the trained model.
        """
        if not self.model:
            raise ValueError("Model is not trained or loaded.")
        # Reused: Predict using the loaded model
        return self.model.predict(features)
