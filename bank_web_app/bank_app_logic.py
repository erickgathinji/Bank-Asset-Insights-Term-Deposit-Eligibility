# imports
import pandas as pd
import numpy as np
import re
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import Ridge
import streamlit as st 
import pickle
import joblib

# load model
# model_columns = joblib.load('pickles/model_columns.pkl')
model_columns = joblib.load('bank_web_app/pickles/model_columns.pkl')
back_asset_insights_model = joblib.load('bank_web_app/pickles/back_asset_insights_model.pkl')
# back_asset_insights_model = joblib.load('pickles/back_asset_insights_model.pkl')

def render_single_prediction_logic(df):          
    # feature engineering
    df['is_new_customer'] = (df['pdays'] == -1).astype(int)    
    df['has_debt'] = ((df['housing'] == 1) | (df['loan'] == 1)).astype(int)
    df['is_exhausted'] = (df['campaign'] > 3).astype(int)
        
    df['is_senior'] = (df['age'] > 60).astype(int)
    df['is_youth'] = (df['age'] < 25).astype(int)
    
    payday_days = [1, 2, 3, 4, 5, 15, 16, 17, 18, 19, 20]
    df['is_payday_prox'] = df['day'].isin(payday_days).astype(int)
        
    # Reciprocal of pdays (Momentum); handles -1 naturally by returning 0
    df['engagement_momentum'] = df['pdays'].apply(lambda x: 1/(x+1) if x > 0 else 0)
    
    # Log Transforms (Fixed Offset) - value used during training
    # balance_offset = abs(train['balance'].min()) + 1
    balance_offset = 8020
    df['log_balance'] = np.log1p(df['balance'] + balance_offset)
    df['log_duration'] = np.log1p(df['duration'])
    df['conversion_intent'] = df['log_balance'] * df['log_duration']

    # Relative Liquidity 
    # stats obtained from train
    # edu_stats = train.groupby('education')['balance'].agg(['mean', 'std'])
    edu_stats = pd.DataFrame(
        {'mean': {'primary': 1175.984152346498,
        'secondary': 1005.0104510273027,
        'tertiary': 1543.667128188899,
        'unknown': 1461.858819662895},
        'std': {'primary': 2843.4064791393607,
        'secondary': 2397.7889936431766,
        'tertiary': 3441.4449027941396,
        'unknown': 2911.0589652896}
        }
    )
    mean_map = edu_stats['mean'].to_dict()
    std_map = edu_stats['std'].to_dict()

    # Apply to df using the TRAIN maps        
    df['rel_liquidity'] = (df['balance'] - df['education'].map(mean_map)) / \
                        (df['education'].map(std_map) + 1)
                          
    # encoding                    #   
    binary_cols = ['default', 'housing', 'loan']
    for col in binary_cols:       
        df[col] = df[col].map({'no': 0, 'yes': 1}) 

    nominal_cols = ['poutcome', 'month', 'job', 'contact', 'marital']
    df = pd.get_dummies(df, columns=nominal_cols, drop_first=True)
    
    # Ordinal mapping (if hierarchy is assumed)    
    education_map = {'unknown': 0, 'primary': 1, 'secondary': 2, 'tertiary': 3}
    df['education'] = df['education'].map(education_map)

    
    # Reindex - adds missing columns as 0s and removes any extras not in training
    df = df.reindex(columns=model_columns, fill_value=0)
    
    result=back_asset_insights_model.predict(df)

    # clip
    probability = np.clip(result, 0, 1)
    
    # Convert to Binary (0 or 1) if the score >= 0.5, it becomes 1 (Eligible)
    input_prediction = (probability >= 0.5).astype(int)
  
    return input_prediction[0]

def render_batch_prediction_logic(df):          
    # Standardize text 
    df.columns = df.columns.str.lower()
    df.drop(columns="id", errors='ignore', inplace=True)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.lower()

    # Binary mapping
    binary_cols = ['default', 'housing', 'loan']
    for col in binary_cols:       
        df[col] = df[col].map({'no': 0, 'yes': 1}) 

    # Feature engineering
    df['is_new_customer'] = (df['pdays'] == -1).astype(int)    
    df['has_debt'] = ((df['housing'] == 1) | (df['loan'] == 1)).astype(int)
    df['is_exhausted'] = (df['campaign'] > 3).astype(int)
    df['is_senior'] = (df['age'] > 60).astype(int)
    df['is_youth'] = (df['age'] < 25).astype(int)
    
    payday_days = [1, 2, 3, 4, 5, 15, 16, 17, 18, 19, 20]
    df['is_payday_prox'] = df['day'].isin(payday_days).astype(int)
    df['engagement_momentum'] = df['pdays'].apply(lambda x: 1/(x+1) if x > 0 else 0)
    
    # Transforms
    balance_offset = 8020
    df['log_balance'] = np.log1p(df['balance'] + balance_offset)
    df['log_duration'] = np.log1p(df['duration'])
    df['conversion_intent'] = df['log_balance'] * df['log_duration']

    # Relative Liquidity using fixed stats
    edu_stats = {
        'mean': {'primary': 1175.98, 'secondary': 1005.01, 'tertiary': 1543.67, 'unknown': 1461.86},
        'std': {'primary': 2843.41, 'secondary': 2397.79, 'tertiary': 3441.44, 'unknown': 2911.06}
    }
    df['rel_liquidity'] = (df['balance'] - df['education'].map(edu_stats['mean'])) / \
                          (df['education'].map(edu_stats['std']) + 1)

    # Dummy Encoding & Ordinal Mapping
    nominal_cols = ['poutcome', 'month', 'job', 'contact', 'marital']
    df = pd.get_dummies(df, columns=nominal_cols, drop_first=True)
    
    education_map = {'unknown': 0, 'primary': 1, 'secondary': 2, 'tertiary': 3}
    df['education'] = df['education'].map(education_map)

    # Alignment & Prediction
    df = df.reindex(columns=model_columns, fill_value=0)
    result = back_asset_insights_model.predict(df)

    # return the whole array for Batch Mode
    probability = np.clip(result, 0, 1)
    input_prediction = (probability >= 0.5).astype(int)
  
    return input_prediction # an array [1, 0, 1...]


def validate_batch_data(df):
    """
    Validates data types and categorical values for the 16 features.
    """
    
    if len(df) <= 1:
        return False, "This prediction mode is for **Bulk Analysis**. If you only have one client profile, please use the **Single Prediction** mode (uncheck the box above)."
    
    # clean the job column which has 'admin.' instead of 'admin'
    df['job'] = df['job'].str.replace('admin.', 'admin', regex=False)
    
    VALID_CATEGORIES = {
        'contact': ['cellular', 'telephone', 'unknown'],
        'month': ['apr', 'aug', 'dec', 'feb', 'jan', 'jul', 'jun', 'mar', 'may', 'nov', 'oct', 'sep'],
        'default': ['no', 'yes'],
        'poutcome': ['failure', 'other', 'success', 'unknown'],
        'loan': ['no', 'yes'],
        'marital': ['divorced', 'married', 'single'],
        'housing': ['no', 'yes'],
        'education': ['primary', 'secondary', 'tertiary', 'unknown'],
        'job': ['admin', 'blue-collar', 'entrepreneur', 'housemaid', 'management', 'retired', 'self-employed', 'services', 'student', 'technician', 'unemployed', 'unknown']
    }
    
    # Standardize strings (handles case sensitivity and accidental spaces)
    for col in VALID_CATEGORIES.keys():
        df[col] = df[col].astype(str).str.lower().str.strip()

    # Validate Categorical Content
    for col, allowed in VALID_CATEGORIES.items():
        invalid_values = df[~df[col].isin(allowed)][col].unique()
        if len(invalid_values) > 0:
            return False, f"Invalid entries in **{col}**: {list(invalid_values)}. Allowed: {allowed}"

    # Validate Numeric Integrity
    numeric_cols = ['age', 'balance', 'day', 'duration', 'campaign', 'pdays', 'previous']
    for col in numeric_cols:
        # Check if column is numeric or can be converted without error
        try:
            pd.to_numeric(df[col])
        except Exception:
            return False, f"Column **{col}** contains non-numeric data that the model cannot process."

    return True, "Success"



       
       
       
       
       
       
       
       
       
       
       
       
       
       
            
    # result=model.predict(encoded_input[predictors])

    # if result[0] == 1:    
    #     st.error("Result: **Warning!** Patient is at a **higher risk** for heart disease.")
    # else:
    #     st.success("Result: **Low Risk**, heart health looks strong.")
    




