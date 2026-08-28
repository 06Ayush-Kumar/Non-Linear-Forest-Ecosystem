import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

MODEL_PATH = "ml_model.pkl"

def extract_features(cell):
    state = np.array(cell["state"])
    return [
        cell["ndvi"],
        cell["disturbance"],
        state[0], state[1], state[2],
        state[2] / max(state[0], 1.0),  # invasion pressure
        cell["biodiversity_index"]
    ]

def train_model(simulation_result):
    X, y = [], []

    for row in simulation_result["cells"]:
        for cell in row:
            X.append(extract_features(cell))
            y.append(cell["class_code"])

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    return "Model trained"

def predict_cell(cell):
    model = joblib.load(MODEL_PATH)
    features = np.array([extract_features(cell)])
    return int(model.predict(features)[0])