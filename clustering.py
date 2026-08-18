import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

CLUSTER_FEATURES = [
    'TotalRevenue', 
    'TotalNetProfit', 
    'ProfitMargin', 
    'AOV', 
    'GrowthFactor', 
    'DeliveryOrderShare', 
    'CostEfficiency'
]

def evaluate_optimal_k(df: pd.DataFrame, feature_cols: list = None, k_range: range = range(2, 9)) -> tuple[dict, dict]:
    """
    Computes WCSS (Elbow method) and Silhouette Scores for a range of k values.
    """
    if feature_cols is None:
        feature_cols = CLUSTER_FEATURES
        
    X = StandardScaler().fit_transform(df[feature_cols])
    
    wcss = {}
    silhouette_scores = {}
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        wcss[k] = float(kmeans.inertia_)
        silhouette_scores[k] = float(silhouette_score(X, labels))
        
    return wcss, silhouette_scores

def assign_cluster_labels(cluster_df: pd.DataFrame, feature_cols: list) -> dict:
    """
    Dynamically maps numeric cluster IDs to meaningful domain-specific cluster names based on cluster centroids.
    """
    means = cluster_df.groupby('Cluster_ID')[feature_cols + ['GrowthScore']].mean()
    
    # Ranking metrics
    rev_rank = means['TotalRevenue'].rank(ascending=False)
    profit_rank = means['TotalNetProfit'].rank(ascending=False)
    margin_rank = means['ProfitMargin'].rank(ascending=False)
    score_rank = means['GrowthScore'].rank(ascending=False)
    deliv_rank = means['DeliveryOrderShare'].rank(ascending=False)
    
    cluster_names = {}
    used_names = set()
    
    candidate_names = [
        "Expansion Leaders",
        "Efficient Growth Performers",
        "Delivery Driven Powerhouses",
        "High Revenue / Low Margin Operators",
        "At-Risk / Low Margin Stores",
        "Stable Performers",
        "Moderate Potential Outlets"
    ]
    
    for c_id in means.index:
        c_score = means.loc[c_id, 'GrowthScore']
        c_margin = means.loc[c_id, 'ProfitMargin']
        c_rev = means.loc[c_id, 'TotalRevenue']
        c_deliv = means.loc[c_id, 'DeliveryOrderShare']
        c_profit = means.loc[c_id, 'TotalNetProfit']
        
        # Logic for naming based on centroids
        if c_score >= 65 and c_profit > means['TotalNetProfit'].median():
            name = "Expansion Leaders"
        elif c_deliv > means['DeliveryOrderShare'].median() and c_score >= 50:
            name = "Delivery Driven Powerhouses"
        elif c_margin > means['ProfitMargin'].median() and c_score >= 50:
            name = "Efficient Growth Performers"
        elif c_rev > means['TotalRevenue'].median() and c_margin <= means['ProfitMargin'].median():
            name = "High Revenue / Low Margin Operators"
        elif c_profit < means['TotalNetProfit'].median() or c_margin < 0:
            name = "At-Risk / Low Margin Stores"
        else:
            name = "Stable Performers"
            
        # Guarantee unique name per cluster ID
        if name in used_names:
            idx = 1
            alt_name = f"{name} ({idx})"
            while alt_name in used_names:
                idx += 1
                alt_name = f"{name} ({idx})"
            name = alt_name
            
        used_names.add(name)
        cluster_names[c_id] = name
        
    return cluster_names

def perform_clustering(df: pd.DataFrame, n_clusters: int = 5, feature_cols: list = None, method: str = 'kmeans') -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Performs K-Means or Hierarchical Clustering and PCA dimensionality reduction.
    Returns DataFrame with cluster assignments, cluster profiles, and summary dictionary.
    """
    if feature_cols is None:
        feature_cols = CLUSTER_FEATURES
        
    df_clust = df.copy()
    X = StandardScaler().fit_transform(df_clust[feature_cols])
    
    if method.lower() == 'hierarchical':
        model = AgglomerativeClustering(n_clusters=n_clusters)
        labels = model.fit_predict(X)
        sil_val = float(silhouette_score(X, labels))
    else:
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(X)
        sil_val = float(silhouette_score(X, labels))
        
    df_clust['Cluster_ID'] = labels
    
    # Assign cluster names
    cluster_names = assign_cluster_labels(df_clust, feature_cols)
    df_clust['Cluster'] = df_clust['Cluster_ID'].map(cluster_names)
    
    # Compute 2D & 3D PCA
    pca2 = PCA(n_components=2, random_state=42)
    pca3 = PCA(n_components=3, random_state=42)
    
    coords2 = pca2.fit_transform(X)
    coords3 = pca3.fit_transform(X)
    
    df_clust['PCA1'] = coords2[:, 0]
    df_clust['PCA2'] = coords2[:, 1]
    
    df_clust['PCA3D_1'] = coords3[:, 0]
    df_clust['PCA3D_2'] = coords3[:, 1]
    df_clust['PCA3D_3'] = coords3[:, 2]
    
    # Compute profile statistics per cluster
    profile_cols = feature_cols + ['GrowthScore', 'TotalRevenue', 'TotalNetProfit', 'ProfitMarginPct', 'AOV', 'MonthlyOrders']
    profile_cols = list(dict.fromkeys(profile_cols))
    cluster_profiles = df_clust.groupby(['Cluster_ID', 'Cluster'])[profile_cols].mean().round(2).reset_index()
    
    meta = {
        "n_clusters": n_clusters,
        "method": method,
        "silhouette_score": sil_val,
        "pca_variance_2d": list(pca2.explained_variance_ratio_),
        "pca_variance_3d": list(pca3.explained_variance_ratio_),
        "cluster_names": cluster_names,
        "cluster_counts": df_clust['Cluster'].value_counts().to_dict()
    }
    
    return df_clust, cluster_profiles, meta
