import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

DEFAULT_WEIGHTS = {
    'GrowthFactor': 0.20,
    'TotalNetProfit': 0.20,
    'ProfitMargin': 0.15,
    'TotalRevenue': 0.15,
    'AOV': 0.10,
    'CostEfficiency': 0.10,
    'DeliveryMargin': 0.10
}

def calculate_growth_score(df: pd.DataFrame, custom_weights: dict = None) -> tuple[pd.DataFrame, dict]:
    """
    Calculates an explainable 0-100 Growth Potential Score for each restaurant using multi-criteria decision analysis (MCDA).
    Normalizes key features using MinMaxScaler before applying weights.
    
    Returns:
    - DataFrame with 'GrowthScore' and 'GrowthTier'
    - Dictionary with score methodology details and weights used
    """
    weights = custom_weights if custom_weights else DEFAULT_WEIGHTS
    
    # Normalize weights so they sum to 1.0
    total_w = sum(weights.values())
    norm_weights = {k: v / total_w for k, v in weights.items()}
    
    df_score = df.copy()
    scaler = MinMaxScaler()
    
    # Extract components
    score_cols = list(norm_weights.keys())
    
    # Handle missing score columns if any
    for col in score_cols:
        if col not in df_score.columns:
            raise KeyError(f"Required scoring feature '{col}' not found in DataFrame.")
            
    # Scaled matrix in [0, 1]
    scaled_mat = scaler.fit_transform(df_score[score_cols])
    scaled_df = pd.DataFrame(scaled_mat, columns=[f"{c}_norm" for c in score_cols], index=df_score.index)
    
    # Calculate composite score (0 to 100)
    raw_score = np.zeros(len(df_score))
    sub_scores = {}
    
    for col, w in norm_weights.items():
        contrib = scaled_df[f"{col}_norm"] * w * 100.0
        raw_score += contrib
        sub_scores[f"{col}_score_contrib"] = contrib
        
    df_score['GrowthScore'] = np.clip(raw_score, 0.0, 100.0).round(2)
    
    # Score component breakdown stored for transparency
    for k, v in sub_scores.items():
        df_score[k] = v.round(2)
        
    # Classify into 5 Growth Tiers
    tiers = []
    for score in df_score['GrowthScore']:
        if score >= 80.0:
            tiers.append('Very High Growth Potential')
        elif score >= 65.0:
            tiers.append('High Growth Potential')
        elif score >= 50.0:
            tiers.append('Moderate Growth Potential')
        elif score >= 35.0:
            tiers.append('Low Growth Potential')
        else:
            tiers.append('Very Low Growth Potential')
            
    df_score['GrowthTier'] = tiers
    
    score_meta = {
        "weights": norm_weights,
        "features": score_cols,
        "mean_score": float(df_score['GrowthScore'].mean()),
        "median_score": float(df_score['GrowthScore'].median()),
        "max_score": float(df_score['GrowthScore'].max()),
        "min_score": float(df_score['GrowthScore'].min()),
        "tier_counts": df_score['GrowthTier'].value_counts().to_dict()
    }
    
    return df_score, score_meta
