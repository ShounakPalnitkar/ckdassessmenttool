from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import tensorflow as tf
import joblib
import lightgbm as lgb
from catboost import CatBoostClassifier
from sklearn.neural_network import MLPClassifier

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load models (adjust paths as needed)
lgbm_model = tf.keras.models.load_model('models/lgbm_model.h5')
catboost_model = CatBoostClassifier().load_model('models/catboost_model.cbm')
mlp_model = joblib.load('models/mlp_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Preprocess input to match your model's requirements
        features = preprocess_input(data)
        
        # Get predictions from each model
        lgbm_pred = lgbm_model.predict(np.array([features]))[0][0]
        catboost_pred = catboost_model.predict_proba([features])[0][1]
        mlp_pred = mlp_model.predict_proba([features])[0][1]
        
        # Hybrid weighted average
        hybrid_score = (0.4 * lgbm_pred) + (0.3 * catboost_pred) + (0.3 * mlp_pred)
        risk_score = int(hybrid_score * 100)
        
        # Determine risk level
        if hybrid_score >= 0.7:
            risk_level = "high"
        elif hybrid_score >= 0.4:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        return jsonify({
            "riskScore": risk_score,
            "riskLevel": risk_level,
            "riskPercentage": f"{risk_score}%",
            "modelContributions": {
                "lightgbm": float(lgbm_pred),
                "catboost": float(catboost_pred),
                "mlp": float(mlp_pred)
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def preprocess_input(data):
    """Convert frontend data to model input format"""
    # Example preprocessing - adjust based on your models' requirements
    return [
        data.get('age', 0),
        1 if data.get('sex') == 'male' else 0,
        data.get('bmi', 0),
        1 if data.get('hypertension') == 'yes' else 0,
        # Add all other features your models expect...
    ]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)