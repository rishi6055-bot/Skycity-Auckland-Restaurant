import pandas as pd
import numpy as np
from sklearn.inspection import permutation_importance
from sklearn.ensemble import RandomForestClassifier

def compute_correlations(df: pd.DataFrame, target_col: str = 'GrowthScore') -> pd.DataFrame:
    """
    Computes Pearson and Spearman correlation coefficients of all numerical variables with the target column.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    if target_col not in numeric_df.columns:
        return pd.DataFrame()
        
    pearson = numeric_df.corr(method='pearson')[target_col].drop(target_col)
    spearman = numeric_df.corr(method='spearman')[target_col].drop(target_col)
    
    corr_df = pd.DataFrame({
        'Feature': pearson.index,
        'Pearson Correlation': pearson.values.round(4),
        'Spearman Correlation': spearman.values.round(4),
        'Absolute Pearson': pearson.abs().values.round(4)
    }).sort_values(by='Absolute Pearson', ascending=False).reset_index(drop=True)
    
    return corr_df

def extract_tree_feature_importance(model, feature_names: list) -> pd.DataFrame:
    """
    Extracts Gini feature importances from a fitted tree model (RandomForest/GradientBoosting).
    """
    if not hasattr(model, 'feature_importances_'):
        return pd.DataFrame()
        
    importances = model.feature_importances_
    df_imp = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False).reset_index(drop=True)
    
    df_imp['Importance_Pct'] = (df_imp['Importance'] * 100.0).round(2)
    return df_imp

def compute_permutation_importance(model, X_val, y_val, feature_names: list, n_repeats: int = 5) -> pd.DataFrame:
    """
    Computes permutation importance on validation dataset.
    """
    result = permutation_importance(model, X_val, y_val, n_repeats=n_repeats, random_state=42)
    
    df_perm = pd.DataFrame({
        'Feature': feature_names,
        'Mean Importance Loss': result.importances_mean.round(4),
        'Std Dev': result.importances_std.round(4)
    }).sort_values(by='Mean Importance Loss', ascending=False).reset_index(drop=True)
    
    return df_perm

def get_growth_drivers_ranking(df: pd.DataFrame, rf_model=None, feature_cols: list = None) -> pd.DataFrame:
    """
    Combines correlation and model feature importances to rank top growth drivers.
    """
    corr_df = compute_correlations(df, target_col='GrowthScore')
    
    if rf_model is not None and feature_cols is not None:
        tree_imp = extract_tree_feature_importance(rf_model, feature_cols)
        merged = pd.merge(corr_df, tree_imp, on='Feature', how='outer').fillna(0)
        merged = merged.sort_values(by=['Importance', 'Absolute Pearson'], ascending=False).reset_index(drop=True)
        return merged
    else:
        return corr_df
