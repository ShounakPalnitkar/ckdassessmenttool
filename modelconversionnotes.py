# Example conversion script (run once to create backend-compatible models)
import tensorflow as tf
from tensorflowjs.converters import load_keras_model

# Convert TFJS to Keras
lgbm_model = load_keras_model('lgbm_model.json')
lgbm_model.save('models/lgbm_model.h5')

# For CatBoost/MLP (save in native formats)
catboost_model.save_model('models/catboost_model.cbm')
joblib.dump(mlp_model, 'models/mlp_model.pkl')