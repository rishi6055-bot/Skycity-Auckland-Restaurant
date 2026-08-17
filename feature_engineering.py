import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineers holistic financial, operational, growth, cost, and delivery metrics.
    """
    df_feat = df.copy()
    
    # 1. Total Financial Aggregates
    df_feat['TotalRevenue'] = (
        df_feat['InStoreRevenue'] + 
        df_feat['UberEatsRevenue'] + 
        df_feat['DoorDashRevenue'] + 
        df_feat['SelfDeliveryRevenue']
    )
    
    df_feat['TotalNetProfit'] = (
        df_feat['InStoreNetProfit'] + 
        df_feat['UberEatsNetProfit'] + 
        df_feat['DoorDashNetProfit'] + 
        df_feat['SelfDeliveryNetProfit']
    )
    
    # Avoid divide-by-zero
    rev_safe = np.where(df_feat['TotalRevenue'] == 0, 1e-5, df_feat['TotalRevenue'])
    orders_safe = np.where(df_feat['MonthlyOrders'] == 0, 1e-5, df_feat['MonthlyOrders'])
    
    # 2. Profitability & Margins
    df_feat['ProfitMargin'] = df_feat['TotalNetProfit'] / rev_safe
    df_feat['ProfitMarginPct'] = df_feat['ProfitMargin'] * 100.0
    
    # 3. Delivery Metrics
    df_feat['DeliveryOrders'] = (
        df_feat['UberEatsOrders'] + 
        df_feat['DoorDashOrders'] + 
        df_feat['SelfDeliveryOrders']
    )
    
    df_feat['DeliveryRevenue'] = (
        df_feat['UberEatsRevenue'] + 
        df_feat['DoorDashRevenue'] + 
        df_feat['SelfDeliveryRevenue']
    )
    
    df_feat['DeliveryNetProfit'] = (
        df_feat['UberEatsNetProfit'] + 
        df_feat['DoorDashNetProfit'] + 
        df_feat['SelfDeliveryNetProfit']
    )
    
    df_feat['DeliveryOrderShare'] = df_feat['DeliveryOrders'] / orders_safe
    df_feat['DeliveryRevenueShare'] = df_feat['DeliveryRevenue'] / rev_safe
    
    # 4. Third-Party Platform vs Self-Delivery Breakdown
    df_feat['ThirdPartyRevenue'] = df_feat['UberEatsRevenue'] + df_feat['DoorDashRevenue']
    df_feat['ThirdPartyOrders'] = df_feat['UberEatsOrders'] + df_feat['DoorDashOrders']
    df_feat['ThirdPartyShare'] = df_feat['ThirdPartyRevenue'] / rev_safe
    
    # 5. Cost Breakdown & Efficiency
    df_feat['TotalCOGS'] = df_feat['TotalRevenue'] * df_feat['COGSRate']
    df_feat['TotalOPEX'] = df_feat['TotalRevenue'] * df_feat['OPEXRate']
    df_feat['ThirdPartyCommissionCost'] = df_feat['ThirdPartyRevenue'] * df_feat['CommissionRate']
    df_feat['TotalDeliveryCost'] = df_feat['SD_DeliveryTotalCost']
    
    # Cost Efficiency Ratio: 1 - (COGS % + OPEX %)
    df_feat['CostEfficiency'] = 1.0 - (df_feat['COGSRate'] + df_feat['OPEXRate'])
    
    # 6. Growth & Per-Order Metrics
    df_feat['GrowthRatePct'] = (df_feat['GrowthFactor'] - 1.0) * 100.0
    df_feat['ProfitPerOrder'] = df_feat['TotalNetProfit'] / orders_safe
    df_feat['RevenuePerOrder'] = df_feat['TotalRevenue'] / orders_safe
    
    # 7. Channel Margin Differentials
    in_store_rev_safe = np.where(df_feat['InStoreRevenue'] == 0, 1e-5, df_feat['InStoreRevenue'])
    delivery_rev_safe = np.where(df_feat['DeliveryRevenue'] == 0, 1e-5, df_feat['DeliveryRevenue'])
    
    df_feat['InStoreMargin'] = df_feat['InStoreNetProfit'] / in_store_rev_safe
    df_feat['DeliveryMargin'] = df_feat['DeliveryNetProfit'] / delivery_rev_safe
    
    return df_feat
