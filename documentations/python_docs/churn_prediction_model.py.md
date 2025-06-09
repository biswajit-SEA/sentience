# `churn_prediction_model.py` Documentation

## Overview
This file implements the core machine learning functionality for the Customer Churn Prediction System. It provides a comprehensive pipeline for loading customer data, preprocessing it, training multiple machine learning models, evaluating their performance, and making predictions. The module is designed to handle the entire lifecycle of a machine learning model from data ingestion to deployment.

## Class: `ChurnPredictionModel`

A complete implementation for bank customer churn prediction that includes:
- Data loading and preprocessing
- Feature engineering
- Model training with multiple algorithms
- Model evaluation and comparison
- Feature importance analysis
- Model persistence (saving/loading)
- Visualization of data and results
- Prediction for new customers

## Dependencies
- **pandas & numpy**: For data manipulation and numerical operations
- **matplotlib & seaborn**: For data visualization
- **scikit-learn**: For machine learning models, preprocessing, and evaluation
- **XGBoost**: For gradient boosting implementation

## Class Attributes

- `data_path`: Path to the dataset CSV file
- `output_dir`: Directory to save model artifacts
- `df`: Original dataframe
- `df_encoded`: Dataframe after encoding categorical variables
- `data_balanced`: Dataframe after handling class imbalance
- `models`: Dictionary of machine learning models
- `best_model`: The model with the highest accuracy
- `best_model_name`: Name of the best model
- `scaler`: StandardScaler for feature normalization
- `feature_columns`: List of feature column names
- `results`: Dictionary of model evaluation results

## Methods

### Initialization and Data Preparation

#### `__init__(data_path=None, output_dir="output")`
Initializes the model with optional data path and output directory.

#### `load_data(data_path=None)`
Loads the dataset from a CSV file and performs initial cleaning.
```python
self.df = pd.read_csv(self.data_path)
# Initial data cleaning
if 'RowNumber' in self.df.columns:
    self.df = self.df.drop(['RowNumber', 'CustomerId', 'Surname'], axis=1)
```

#### `preprocess_data()`
Performs comprehensive data preprocessing including:
- Handling missing values
- Encoding categorical variables (one-hot encoding for Geography, binary encoding for Gender)
- Balancing classes using oversampling
- Splitting data into training and testing sets
- Scaling features using StandardScaler

```python
# Encoding categorical variables
self.df_encoded = pd.get_dummies(self.df, columns=['Geography'])
self.df_encoded['Gender'] = self.df_encoded['Gender'].map({'Male': 0, 'Female': 1})

# Handling class imbalance through oversampling
majority_class = self.df_encoded[self.df_encoded['Exited'] == 0]
minority_class = self.df_encoded[self.df_encoded['Exited'] == 1]
minority_oversampled = resample(minority_class, replace=True, n_samples=len(majority_class), random_state=42)
self.data_balanced = pd.concat([majority_class, minority_oversampled])
```

### Model Training and Evaluation

#### `initialize_models()`
Creates instances of multiple machine learning models for comparison:
- Logistic Regression
- Support Vector Machine (SVM)
- Decision Tree
- Random Forest
- XGBoost

#### `train_and_evaluate(X_train, X_test, y_train, y_test, visualize=True)`
Trains all models and evaluates their performance using:
- Accuracy score
- Classification report
- Confusion matrix
```python
for name, model in self.models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    self.results[name] = accuracy
```

### Feature Analysis and Visualization

#### `analyze_feature_importance()`
Analyzes and visualizes feature importance for tree-based models.
```python
feature_importances = self.best_model.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': self.feature_columns,
    'Importance': feature_importances
}).sort_values(by='Importance', ascending=False)
```

#### `visualize_data()`
Generates exploratory data visualizations:
- Churn distribution (count and percentage)
- Geography distribution
- Age distribution by churn status
- Balance distribution by churn status
- Correlation heatmap

### Model Persistence

#### `save_model(model_name=None)`
Saves the model, scaler, and feature columns to disk.
```python
model_path = os.path.join(self.output_dir, f"{name_to_save.replace(' ', '_')}_model.pkl")
with open(model_path, 'wb') as f:
    pickle.dump(model_to_save, f)
```

#### `load_model(model_path, scaler_path=None, feature_path=None)`
Loads a saved model, scaler, and feature columns from disk.

### Prediction

#### `predict_new_customer(customer_data, model=None)`
Predicts churn probability for a new customer.
```python
# Making prediction
churn_probability = model.predict_proba(X_customer_scaled)[0]
churn_prediction = int(churn_probability[1] > 0.5)  # 1 if probability > 0.5, 0 otherwise

result = {
    'stay_probability': churn_probability[0],
    'churn_probability': churn_probability[1],
    'prediction': churn_prediction
}
```

### Full Pipeline

#### `run_pipeline(data_path=None, visualize=True)`
Runs the entire modeling pipeline from data loading to model evaluation.
1. Loads and visualizes the data
2. Preprocesses the data
3. Initializes, trains, and evaluates models
4. Analyzes feature importance
5. Saves the best model

## Example Usage

```python
# Create model instance
model = ChurnPredictionModel(data_path="data/Churn_Modelling.csv", output_dir="output")

# Run the entire pipeline
results = model.run_pipeline(visualize=True)

# Predict for a new customer
new_customer = {
    'CreditScore': 650,
    'Geography': 'France',
    'Gender': 'Female',
    'Age': 35,
    'Tenure': 5,
    'Balance': 100000,
    'NumOfProducts': 2,
    'HasCrCard': 1,
    'IsActiveMember': 1,
    'EstimatedSalary': 50000
}
prediction = model.predict_new_customer(new_customer)
```

## Integration with the Application

This model is integrated with the main Flask application through the `process_data_files()` function, which:
1. Loads the trained model from disk
2. Processes uploaded customer data files
3. Makes predictions for each customer in the files
4. Returns the predictions to be displayed and emailed to the user