import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

CATEGORIES = [
    'EXPAND AGGRESSIVELY',
    'INVEST SELECTIVELY',
    'OPTIMIZE BEFORE EXPANSION',
    'MAINTAIN',
    'RESTRUCTURE / HIGH RISK'
]

def assign_strategic_category(row: pd.Series) -> str:
    """
    Data-driven rule engine to assign Strategic Category based on GrowthScore, ProfitMarginPct, TotalNetProfit, and OPEX/COGS efficiency.
    """
    score = row.get('GrowthScore', 0)
    margin = row.get('ProfitMarginPct', 0)
    profit = row.get('TotalNetProfit', 0)
    rev = row.get('TotalRevenue', 0)
    growth = row.get('GrowthFactor', 1.0)
    cost_eff = row.get('CostEfficiency', 0.4)
    
    if score >= 70.0 and margin >= 10.0 and profit > 5000:
        return 'EXPAND AGGRESSIVELY'
    elif score >= 55.0 and margin >= 7.5:
        return 'INVEST SELECTIVELY'
    elif rev >= 40000 and margin < 7.5:
        return 'OPTIMIZE BEFORE EXPANSION'
    elif score >= 42.0 and profit >= 0:
        return 'MAINTAIN'
    else:
        return 'RESTRUCTURE / HIGH RISK'

def classify_restaurants(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies strategic classification rule engine to the dataset.
    """
    df_classified = df.copy()
    df_classified['StrategicCategory'] = df_classified.apply(assign_strategic_category, axis=1)
    return df_classified

def train_and_evaluate_models(df: pd.DataFrame, feature_cols: list = None) -> tuple[pd.DataFrame, dict, dict]:
    """
    Trains multiple supervised ML classification models to predict Strategic Category.
    Returns:
    - Model comparison metrics DataFrame
    - Dictionary of fitted models & scalers
    - Dictionary of evaluation confusion matrices & test data
    """
    if feature_cols is None:
        feature_cols = [
            'TotalRevenue', 'TotalNetProfit', 'ProfitMargin', 'AOV',
            'MonthlyOrders', 'GrowthFactor', 'COGSRate', 'OPEXRate',
            'CommissionRate', 'DeliveryOrderShare', 'CostEfficiency',
            'ThirdPartyShare', 'DeliveryRadiusKM'
        ]
        
    df_ml = df.copy()
    if 'StrategicCategory' not in df_ml.columns:
        df_ml = classify_restaurants(df_ml)
        
    X = df_ml[feature_cols]
    y = df_ml['StrategicCategory']
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.20, random_state=42, stratify=y_encoded
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=6, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    }
    
    metrics_list = []
    fitted_models = {}
    eval_results = {}
    
    for name, model in models.items():
        # Scale for linear models, raw for tree models
        if name == 'Logistic Regression':
            model.fit(X_train_scaled, y_train)
            preds = model.predict(X_test_scaled)
            probs = model.predict_proba(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)
            
        fitted_models[name] = model
        
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, average='weighted', zero_division=0)
        rec = recall_score(y_test, preds, average='weighted', zero_division=0)
        f1 = f1_score(y_test, preds, average='weighted', zero_division=0)
        
        try:
            auc = roc_auc_score(y_test, probs, multi_class='ovr', average='weighted')
        except Exception:
            auc = np.nan
            
        cm = confusion_matrix(y_test, preds)
        
        metrics_list.append({
            'Model': name,
            'Accuracy': round(acc, 4),
            'Precision': round(prec, 4),
            'Recall': round(rec, 4),
            'F1 Score': round(f1, 4),
            'ROC-AUC': round(auc, 4) if not np.isnan(auc) else 'N/A'
        })
        
        eval_results[name] = {
            'confusion_matrix': cm,
            'y_test': y_test,
            'preds': preds,
            'classes': le.classes_
        }
        
    metrics_df = pd.DataFrame(metrics_list).sort_values(by='F1 Score', ascending=False).reset_index(drop=True)
    
    model_bundle = {
        'fitted_models': fitted_models,
        'scaler': scaler,
        'label_encoder': le,
        'feature_cols': feature_cols,
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'eval_results': eval_results
    }
    
    return metrics_df, model_bundle
