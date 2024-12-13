
import pandas as pd  
from sklearn.model_selection import train_test_split  
from sklearn.ensemble import GradientBoostingRegressor 
from sklearn.metrics import mean_squared_error 
import joblib  
from stocks import Stocks 

class StockMLModel:
    def __init__(self):
        self.stocks = Stocks() 
        self.model = None  

    def prepare_data(self, symbol):

        df = self.stocks.get_stock_data(symbol)
        df = self.stocks.calculate_moving_average(df)
        df = self.stocks.calculate_bollinger_bands(df)

      
        df["target"] = df["close"].shift(-1)  
        df.dropna(inplace=True) 

        features = ["close", "ma_50", "bollinger_upper", "bollinger_lower"]
        X = df[features]
        y = df["target"]


        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, symbol):

        X_train, X_test, y_train, y_test = self.prepare_data(symbol)


        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)


        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Model trained. Test MSE: {mse:.4f}")


        joblib.dump(self.model, f"{symbol}_model.pkl")

    def load_model(self, model_path):
        """
        Load a pre-trained model.
        """

        self.model = joblib.load(model_path)

    def predict(self, features):
        """
        Predict stock prices using the trained model.
        """
        if not self.model:
            raise ValueError("Model is not trained or loaded.")

        return self.model.predict(features)
