
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Load dataset
df = pd.read_csv("realistic_fitness_data.csv")

# Features and target
X = df[["Steps", "Sleep", "Calories", "HeartRate", "Height", "Weight", "BMI"]]
y = df["FitnessScore"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model n_estimators=100, random_state=42
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"✅ Model trained.\n📉 MSE: {mse:.2f}\n📈 R² Score: {r2:.2f}")


def predict_fitness(steps, sleep, calories, hr, height, weight, bmi):
    input_data = pd.DataFrame([{
        "Steps": steps,
        "Sleep": sleep,
        "Calories": calories,
        "HeartRate": hr,
        "Height": height,
        "Weight": weight,
        "BMI": bmi
    }])
    score = model.predict(input_data)[0]
    score = round(score, 2)
 

    return score
