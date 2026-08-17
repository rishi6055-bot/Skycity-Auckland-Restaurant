import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

def load_raw_data(filepath: str) -> pd.DataFrame:
    """
    Loads raw CSV data from the specified file path.
    """
    df = pd.read_csv(filepath)
    return df

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Performs complete data cleaning on the input DataFrame:
    - Checks missing values
    - Removes duplicate records based on RestaurantID
    - Validates numeric datatypes and value boundaries
    - Returns cleaned DataFrame and metadata dictionary
    """
    initial_shape = df.shape
    missing_before = df.isnull().sum().sum()
    
    # Drop exact duplicate rows or duplicate RestaurantIDs if any
    duplicates_count = df.duplicated(subset=['RestaurantID']).sum()
    df_cleaned = df.drop_duplicates(subset=['RestaurantID']).copy()
    
    # Fill missing values if any exist (numeric -> median, cat -> mode)
    for col in df_cleaned.columns:
        if df_cleaned[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
            else:
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mode()[0])
                
    # Datatype casting and boundary validation
    numeric_cols = [
        'GrowthFactor', 'AOV', 'MonthlyOrders', 'InStoreOrders', 'InStoreRevenue',
        'UberEatsOrders', 'DoorDashOrders', 'SelfDeliveryOrders',
        'UberEatsRevenue', 'DoorDashRevenue', 'SelfDeliveryRevenue',
        'COGSRate', 'OPEXRate', 'CommissionRate', 'DeliveryRadiusKM',
        'DeliveryCostPerOrder', 'SD_DeliveryTotalCost', 'InStoreNetProfit',
        'UberEatsNetProfit', 'DoorDashNetProfit', 'SelfDeliveryNetProfit',
        'InStoreShare', 'UE_share', 'DD_share', 'SD_share'
    ]
    
    for col in numeric_cols:
        if col in df_cleaned.columns:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
            
    # Clip negative order values to zero if any corrupted entries exist
    order_cols = ['MonthlyOrders', 'InStoreOrders', 'UberEatsOrders', 'DoorDashOrders', 'SelfDeliveryOrders']
    for col in order_cols:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].clip(lower=0)
            
    summary_meta = {
        "initial_rows": initial_shape[0],
        "initial_cols": initial_shape[1],
        "missing_values": missing_before,
        "duplicates_removed": duplicates_count,
        "final_rows": df_cleaned.shape[0],
        "final_cols": df_cleaned.shape[1]
    }
    
    return df_cleaned, summary_meta

def scale_features(df: pd.DataFrame, feature_cols: list, method: str = 'minmax') -> tuple[pd.DataFrame, object]:
    """
    Scales specified numerical features using MinMaxScaler or StandardScaler.
    Returns scaled dataframe copy and scaler object.
    """
    df_scaled = df.copy()
    if method == 'minmax':
        scaler = MinMaxScaler()
    else:
        scaler = StandardScaler()
        
    df_scaled[feature_cols] = scaler.fit_transform(df[feature_cols])
    return df_scaled, scaler
