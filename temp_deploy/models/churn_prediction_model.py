#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Churn Prediction Model Implementation
This module provides a class for bank customer churn prediction.
It handles data preprocessing, model training, evaluation, and prediction.
"""

import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Configuration of plot style
sns.set_theme(style="whitegrid")

class ChurnPredictionModel:
    """Bank Customer Churn Prediction Model.
    
    This class implements a machine learning pipeline for predicting customer churn,
    including data preprocessing, model training, evaluation, and prediction for new customers.
    """
    
    def __init__(self, data_path=None, output_dir="output"):
        """Initialize the ChurnPredictionModel instance.
        
        Args:
            data_path (str, optional): Path to the dataset CSV file. Defaults to None.
            output_dir (str, optional): Directory to save model artifacts. Defaults to "output".
        """
        self.data_path = data_path
        self.output_dir = output_dir
        self.df = None
        self.df_encoded = None
        self.data_balanced = None
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.results = {}
        
        # Creation of output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def load_data(self, data_path=None):
        """Load and preprocess the churn dataset.
        
        Args:
            data_path (str, optional): Path to the dataset CSV file.
                If None, uses the path provided during initialization.
                
        Returns:
            pandas.DataFrame: The loaded and preprocessed dataframe.
        """
        if data_path:
            self.data_path = data_path
        
        if not self.data_path:
            raise ValueError("Data path must be provided either during initialization or when calling load_data().")
        
        print(f"Loading data from: {self.data_path}")
        self.df = pd.read_csv(self.data_path)
        
        # Initial data cleaning
        if 'RowNumber' in self.df.columns:
            self.df = self.df.drop(['RowNumber', 'CustomerId', 'Surname'], axis=1)
        
        print(f"Dataset shape: {self.df.shape}")
        return self.df
    
    def preprocess_data(self):
        """Clean, preprocess, and prepare the data for modeling.
        
        This method handles missing values, encodes categorical variables,
        and balances the dataset through oversampling.
        
        Returns:
            tuple: (X_train, X_test, y_train, y_test) - Split and preprocessed data.
        """
        if self.df is None:
            raise ValueError("Data must be loaded before preprocessing. Call load_data() first.")
        
        # Checking and handling missing values
        missing_values = self.df.isnull().sum()
        print("Missing Values Before Filling:\n", missing_values[missing_values > 0])
        
        # Dropping of duplicates
        self.df = self.df.drop_duplicates()
        
        # Handling missing values
        self.df['HasCrCard'] = self.df['HasCrCard'].fillna(method='ffill')
        self.df['IsActiveMember'] = self.df['IsActiveMember'].fillna(method='ffill')
        
        geography_mode = self.df['Geography'].mode()[0]
        self.df['Geography'].fillna(geography_mode, inplace=True)
        
        age_median = self.df['Age'].median()
        self.df['Age'].fillna(age_median, inplace=True)
        
        # Encoding categorical variables
        self.df_encoded = pd.get_dummies(self.df, columns=['Geography'])
        self.df_encoded['Gender'] = self.df_encoded['Gender'].map({'Male': 0, 'Female': 1})
        
        # Handling class imbalance through oversampling
        majority_class = self.df_encoded[self.df_encoded['Exited'] == 0]
        minority_class = self.df_encoded[self.df_encoded['Exited'] == 1]
        
        # Oversampling the minority class
        minority_oversampled = resample(
            minority_class,
            replace=True,
            n_samples=len(majority_class),
            random_state=42
        )
        
        # Combining the majority class with the oversampled minority class
        self.data_balanced = pd.concat([majority_class, minority_oversampled])
        
        # Preparing features and target
        X = self.data_balanced.drop('Exited', axis=1)
        y = self.data_balanced['Exited']
        
        # Saving feature columns for future prediction
        self.feature_columns = X.columns.tolist()
        
        # Splitting data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scaling features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"Training set: {X_train.shape}, Testing set: {X_test.shape}")
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def initialize_models(self):
        """Initialize various machine learning models for comparison.
        
        Returns:
            dict: Dictionary of initialized model instances.
        """
        self.models = {
            "Logistic Regression": LogisticRegression(random_state=42),
            "SVM": SVC(probability=True, random_state=42),
            "Decision Tree": DecisionTreeClassifier(random_state=42),
            "Random Forest": RandomForestClassifier(random_state=42),
            "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
        }
        print("Models initialized:", list(self.models.keys()))
        return self.models
    
    def train_and_evaluate(self, X_train, X_test, y_train, y_test, visualize=True):
        """Train all models and evaluate their performance.
        
        Args:
            X_train (numpy.ndarray): Training features.
            X_test (numpy.ndarray): Testing features.
            y_train (numpy.ndarray): Training target.
            y_test (numpy.ndarray): Testing target.
            visualize (bool, optional): Whether to generate visualization plots. Defaults to True.
            
        Returns:
            dict: Dictionary with model names as keys and accuracy scores as values.
        """
        if not self.models:
            self.initialize_models()
        
        self.results = {}
        
        for name, model in self.models.items():
            print(f"\nTraining {name}...")
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            self.results[name] = accuracy
            
            print(f"\nModel: {name}")
            print(classification_report(y_test, y_pred))
            
            if visualize:
                cm = confusion_matrix(y_test, y_pred)
                plt.figure(figsize=(6, 4))
                sns.heatmap(cm, annot=True, cmap='Greens', fmt='g')
                plt.title(f'Confusion Matrix - {name}')
                plt.xlabel('Predicted')
                plt.ylabel('Actual')
                plt.savefig(os.path.join(self.output_dir, f"confusion_matrix_{name.replace(' ', '_')}.png"))
                plt.close()
        
        print("\nModel Accuracies:")
        for model, accuracy in self.results.items():
            print(f"{model}: {accuracy:.4f}")
        
        # Identifying the best model
        self.best_model_name = max(self.results, key=self.results.get)
        self.best_model = self.models[self.best_model_name]
        best_accuracy = self.results[self.best_model_name]
        
        print(f"\nBest Model: {self.best_model_name} with Accuracy: {best_accuracy:.4f}")
        
        # Cross-validation for the best model
        cv_scores = cross_val_score(self.best_model, X_train, y_train, cv=5, scoring='accuracy')
        print(f"Cross-Validation Scores: {cv_scores}")
        print(f"Mean CV Accuracy: {np.mean(cv_scores):.4f}")
        
        return self.results
    
    def analyze_feature_importance(self):
        """Analyze and visualize feature importance for the best model.
        
        Returns:
            pandas.DataFrame: DataFrame containing feature importance information.
        """
        if self.best_model is None:
            raise ValueError("No best model available. Train models first using train_and_evaluate().")
        
        if not hasattr(self.best_model, 'feature_importances_'):
            print(f"Feature importance visualization not available for {self.best_model_name}")
            return None
        
        feature_importances = self.best_model.feature_importances_
        
        feature_importance_df = pd.DataFrame({
            'Feature': self.feature_columns,
            'Importance': feature_importances
        }).sort_values(by='Importance', ascending=False)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Importance', y='Feature', data=feature_importance_df, palette='viridis')
        plt.title(f'Feature Importances - {self.best_model_name}', fontsize=16)
        plt.xlabel('Importance Score')
        plt.ylabel('Feature')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "feature_importance.png"))
        plt.close()
        
        return feature_importance_df
    
    def save_model(self, model_name=None):
        """Save the best model or specified model to disk.
        
        Args:
            model_name (str, optional): Name of the model to save. If None, saves the best model.
                
        Returns:
            str: Path to the saved model file.
        """
        if model_name and model_name in self.models:
            model_to_save = self.models[model_name]
            name_to_save = model_name
        elif self.best_model is not None:
            model_to_save = self.best_model
            name_to_save = self.best_model_name
        else:
            raise ValueError("No model available to save.")
        
        # Saving model
        model_path = os.path.join(self.output_dir, f"{name_to_save.replace(' ', '_')}_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model_to_save, f)
        
        # Saving scaler
        scaler_path = os.path.join(self.output_dir, "scaler.pkl")
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Saving feature columns
        feature_path = os.path.join(self.output_dir, "feature_columns.pkl")
        with open(feature_path, 'wb') as f:
            pickle.dump(self.feature_columns, f)
            
        print(f"Model saved to {model_path}")
        return model_path
    
    def load_model(self, model_path, scaler_path=None, feature_path=None):
        """Load a saved model from disk.
        
        Args:
            model_path (str): Path to the saved model file.
            scaler_path (str, optional): Path to the saved scaler file.
            feature_path (str, optional): Path to the saved feature columns file.
                
        Returns:
            object: Loaded model.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        if scaler_path and os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
                
        if feature_path and os.path.exists(feature_path):
            with open(feature_path, 'rb') as f:
                self.feature_columns = pickle.load(f)
        
        return model
    
    def predict_new_customer(self, customer_data, model=None):
        """Predict churn probability for a new customer.
        
        Args:
            customer_data (pandas.DataFrame or dict): New customer data.
            model (object, optional): Model to use for prediction. If None, uses the best model.
                
        Returns:
            dict: Dictionary containing prediction results.
        """
        if isinstance(customer_data, dict):
            customer_data = pd.DataFrame([customer_data])
        
        # Using the provided model or the best model
        if model is None:
            if self.best_model is None:
                raise ValueError("No model available for prediction. Train or load a model first.")
            model = self.best_model
        
        # Preprocessing the customer data same as training data
        for col in ['RowNumber', 'CustomerId', 'Surname']:
            if col in customer_data.columns:
                customer_data.drop(col, axis=1, inplace=True)
        
        # Handling missing values
        customer_data['HasCrCard'] = customer_data['HasCrCard'].fillna(1)  # Mode value
        customer_data['IsActiveMember'] = customer_data['IsActiveMember'].fillna(1)  # Mode value
        
        if 'Geography' in customer_data.columns:
            # Get mode from the training data if available, otherwise use the first geography
            default_geography = customer_data['Geography'].iloc[0]
            if hasattr(self, 'df') and self.df is not None:
                geography_mode = self.df['Geography'].mode()[0]
            else:
                geography_mode = default_geography
            customer_data['Geography'].fillna(geography_mode, inplace=True)
        
        if 'Age' in customer_data.columns:
            # Get median from the training data if available, otherwise use 35 as a reasonable default
            if hasattr(self, 'df') and self.df is not None:
                age_median = self.df['Age'].median()
            else:
                age_median = 35
            customer_data['Age'].fillna(age_median, inplace=True)
        
        # Encoding categorical variables
        if 'Gender' in customer_data.columns:
            customer_data['Gender'] = customer_data['Gender'].map({'Male': 0, 'Female': 1})
        
        # One-hot encode Geography
        if 'Geography' in customer_data.columns:
            customer_data_encoded = pd.get_dummies(customer_data, columns=['Geography'])
            
            # Ensuring all expected Geography columns are present
            if self.feature_columns:
                geography_cols = [col for col in self.feature_columns if col.startswith('Geography_')]
                for col in geography_cols:
                    if col not in customer_data_encoded.columns:
                        customer_data_encoded[col] = 0
                
                # Ensuring customer data has the same columns in the same order as training data
                customer_data_encoded = customer_data_encoded[self.feature_columns]
        else:
            customer_data_encoded = customer_data
        
        # Scaling the features
        X_customer_scaled = self.scaler.transform(customer_data_encoded)
        
        # Making prediction
        churn_probability = model.predict_proba(X_customer_scaled)[0]
        churn_prediction = int(churn_probability[1] > 0.5)  # 1 if probability > 0.5, 0 otherwise
        
        result = {
            'stay_probability': churn_probability[0],
            'churn_probability': churn_probability[1],
            'prediction': churn_prediction
        }
        
        print(f"→ Probability customer will STAY  (Exited=0): {churn_probability[0]:.2%}")
        print(f"→ Probability customer will CHURN (Exited=1): {churn_probability[1]:.2%}")
        print(f"→ Final Output (0 = Stay, 1 = Churn): {churn_prediction}")
        
        return result
    
    def visualize_data(self):
        """Generate exploratory data visualizations.
        
        This method creates key visualizations to understand the dataset
        and how different features relate to customer churn.
        """
        if self.df is None:
            raise ValueError("Data must be loaded before visualization. Call load_data() first.")
        
        # 1. Churn Distribution
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        exited_counts = self.df['Exited'].value_counts()
        sns.barplot(x=exited_counts.index, y=exited_counts, palette='Set2')
        plt.title('Exited Distribution (Churn)')
        plt.ylabel('Count')
        
        for p in plt.gca().patches:
            plt.annotate(f'{int(p.get_height())}', 
                       (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha='center', va='center', xytext=(0, 10), 
                       textcoords='offset points')
            
        plt.subplot(1, 2, 2)
        exited_percentage = self.df['Exited'].value_counts(normalize=True) * 100
        plt.pie(exited_percentage, labels=exited_percentage.index, autopct='%1.1f%%',
                colors=sns.color_palette('Set2'))
        plt.title('Percentage Distribution of Churn (Exited)')
        plt.legend(['Stayed (0)', 'Churned (1)'])
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "churn_distribution.png"))
        plt.close()
        
        # 2. Geography Distribution
        plt.figure(figsize=(10, 6))
        sns.countplot(y='Geography', data=self.df, palette='Set2')
        plt.title('Distribution of Geography')
        plt.savefig(os.path.join(self.output_dir, "geography_distribution.png"))
        plt.close()
        
        # 3. Age Distribution by Churn Status
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.df, x='Age', hue='Exited', kde=True, fill=True, palette='Set2')
        plt.title('Age Distribution by Churn Status')
        plt.xlabel('Age')
        plt.ylabel('Count')
        plt.legend(title='Churn Status', labels=['Stayed (0)', 'Churned (1)'])
        plt.savefig(os.path.join(self.output_dir, "age_distribution.png"))
        plt.close()
        
        # 4. Balance Distribution by Churn Status
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.df, x='Balance', hue='Exited', kde=True, fill=True, palette='Set2')
        plt.title('Balance Distribution by Churn Status')
        plt.xlabel('Balance')
        plt.ylabel('Count')
        plt.legend(title='Churn Status', labels=['Stayed (0)', 'Churned (1)'])
        plt.savefig(os.path.join(self.output_dir, "balance_distribution.png"))
        plt.close()
        
        # 5. Correlation Heatmap (after preprocessing)
        if self.data_balanced is not None:
            plt.figure(figsize=(12, 8))
            correlation_matrix = self.data_balanced.corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
            plt.title('Correlation Matrix Heatmap', fontsize=16)
            plt.savefig(os.path.join(self.output_dir, "correlation_heatmap.png"))
            plt.close()
    
    def run_pipeline(self, data_path=None, visualize=True):
        """Run the entire modeling pipeline from data loading to model evaluation.
        
        Args:
            data_path (str, optional): Path to the dataset CSV file.
            visualize (bool, optional): Whether to generate visualization plots. Defaults to True.
                
        Returns:
            dict: Dictionary with model names as keys and accuracy scores as values.
        """
        # Loading and preprocessing data
        self.load_data(data_path)
        
        if visualize:
            self.visualize_data()
        
        # Preprocessing data
        X_train, X_test, y_train, y_test = self.preprocess_data()
        
        # Initializing models
        self.initialize_models()
        
        # Training and evaluating models
        results = self.train_and_evaluate(X_train, X_test, y_train, y_test, visualize=visualize)
        
        # Analyzing feature importance
        if self.best_model_name:
            self.analyze_feature_importance()
            
        # Saving the best model
        self.save_model()
        
        return results


def main():
    """Main function to demonstrate the ChurnPredictionModel class."""
    print("Bank Customer Churn Prediction Model")
    print("===================================")
    
    data_path = "d:/Dev/hackathon/techm-hackathon/data/csv-files/Churn_Modelling_1.csv"
    output_dir = "d:/Dev/hackathon/techm-hackathon/models/output"
    
    # Creating model instance
    model = ChurnPredictionModel(data_path=data_path, output_dir=output_dir)
    
    # Running the entire pipeline
    results = model.run_pipeline(visualize=True)
    
    # Example of how to predict for a new customer
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
    
    print("\nPredicting for a new customer:")
    prediction = model.predict_new_customer(new_customer)
    
    return 0


if __name__ == "__main__":
    main()