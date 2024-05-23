# Import the necessary libraries.
from . import train
from flask import jsonify
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import os
from matplotlib import pyplot as plt
import seaborn as sns
from scipy.stats import norm
import re
import pickle
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import cross_val_score, KFold
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, BaggingRegressor, AdaBoostRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, mean_absolute_percentage_error

@train.route('/train_model', methods=['POST'])
def train_model():
    # Get the absolute path of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, 'cleaned_dataset.csv')

    # SECTION 1 ---> Read the data
    df = pd.read_csv(csv_file_path)
    
    # SECTION 2 --->  Separating independent variables and the target variable
    X = df.drop('tradein_value_dollars', axis=1)  # independent features
    y = df['tradein_value_dollars']  # the target features

    # SECTION 3 ---> Splitting the dataset into train and test datasets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=1)

    # SECTION 4 ---> Encoding the categorical columns before training
    # section 4.1 ---> Define ordinal encoding for 'condition_category' column
    ordinal_enc = OrdinalEncoder(categories=[['fair', 'good', 'excellent']])
    ordinal_cols = ['condition_category']

    # section 4.2 Define one-hot encoding for 'region' and 'device_category' columns
    one_hot_enc = OneHotEncoder(sparse_output=False)
    one_hot_cols = ['region', 'device_category']

    # SECTION 5 Define a column transformer for the preprocessing of the categorical cols
    preprocessor = ColumnTransformer([
        ('ordinal', ordinal_enc, ordinal_cols),
        ('onehot', one_hot_enc, one_hot_cols)
    ], remainder='passthrough')

    # SECTION 6 --->  Preprocess the training data
    X_train_processed = preprocessor.fit_transform(X_train)

    # SECTION 7 --->  Preprocess the testing data
    X_test_processed = preprocessor.transform(X_test)

    # SECTION 8 ---> Save the preprocessing steps (preprocessor) into a pickle file
    with open(os.path.join(current_dir, '2preprocessor.pkl'), 'wb') as file:
        pickle.dump(preprocessor, file)

    # SECTION 9 --->  Initializing the Decision Tree Regressor
    dt_regressor = DecisionTreeRegressor(random_state=1)

    # section 9.1 --- Fitting the model to the training dataset to train it
    dt_regressor.fit(X_train_processed, y_train)

    # SECTION 10 ---> Save the trained model into a pickle file
    with open(os.path.join(current_dir, '2model.pkl'), 'wb') as file:
        pickle.dump(dt_regressor, file)

    return jsonify({'message': 'Models created successfully!'})
