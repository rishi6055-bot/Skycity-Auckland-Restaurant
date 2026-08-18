import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path

from data_processing import load_raw_data, clean_data
from feature_engineering import engineer_features
from scoring import calculate_growth_score
from clustering import perform_clustering, evaluate_optimal_k
from classification import classify_restaurants, train_and_evaluate_models
from feature_importance import compute_correlations, extract_tree_feature_importance, get_growth_drivers_ranking
from recommendations import generate_restaurant_recommendations

# Streamlit Page Config
st.set_page_config(
    page_title="Restaurant Growth Modeling & Strategic Classification",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-expand {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .badge-invest {
        background-color: #DBEAFE;
        color: #1D4ED8;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .badge-optimize {
        background-color: #FEF3C7;
        color: #B45309;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .badge-maintain {
        background-color: #F1F5F9;
        color: #475569;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .badge-risk {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_preprocess_data():
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "data" / "SkyCity Auckland Restaurants & Bars.csv"
    if not csv_path.exists():
        csv_path = base_dir / "SkyCity Auckland Restaurants & Bars.csv"
    df_raw = load_raw_data(str(csv_path))
    df_clean, meta = clean_data(df_raw)
    df_feat = engineer_features(df_clean)
    df_scored, score_meta = calculate_growth_score(df_feat)
    df_clust, profiles, clust_meta = perform_clustering(df_scored, n_clusters=5)
    df_final = classify_restaurants(df_clust)
    return df_final, meta, score_meta, profiles, clust_meta


@st.cache_resource
def get_ml_models(df):
    metrics_df, model_bundle = train_and_evaluate_models(df)
    return metrics_df, model_bundle


# Load Pipeline Data
df_all, data_meta, score_meta, cluster_profiles, clust_meta = load_and_preprocess_data()
metrics_df, model_bundle = get_ml_models(df_all)

# --- SIDEBAR FILTERS ---
st.sidebar.image("https://img.icons8.com/color/96/000000/restaurant-.png", width=64)
st.sidebar.title("System Controls")
st.sidebar.markdown("Filter options dynamically across all dashboard tabs:")

subregion_opts = sorted(list(df_all['Subregion'].unique()))
selected_subregions = st.sidebar.multiselect("Subregion", subregion_opts, default=subregion_opts)

cuisine_opts = sorted(list(df_all['CuisineType'].unique()))
selected_cuisines = st.sidebar.multiselect("Cuisine Type", cuisine_opts, default=cuisine_opts)

segment_opts = sorted(list(df_all['Segment'].unique()))
selected_segments = st.sidebar.multiselect("Segment", segment_opts, default=segment_opts)

category_opts = [
    'EXPAND AGGRESSIVELY',
    'INVEST SELECTIVELY',
    'OPTIMIZE BEFORE EXPANSION',
    'MAINTAIN',
    'RESTRUCTURE / HIGH RISK'
]
selected_categories = st.sidebar.multiselect("Strategic Category", category_opts, default=category_opts)

cluster_opts = sorted(list(df_all['Cluster'].unique()))
selected_clusters = st.sidebar.multiselect("Cluster", cluster_opts, default=cluster_opts)

min_score, max_score = float(df_all['GrowthScore'].min()), float(df_all['GrowthScore'].max())
score_range = st.sidebar.slider("Growth Potential Score Range", min_score, max_score, (min_score, max_score))

# Apply Sidebar Filters
df_filtered = df_all[
    (df_all['Subregion'].isin(selected_subregions)) &
    (df_all['CuisineType'].isin(selected_cuisines)) &
    (df_all['Segment'].isin(selected_segments)) &
    (df_all['StrategicCategory'].isin(selected_categories)) &
    (df_all['Cluster'].isin(selected_clusters)) &
    (df_all['GrowthScore'] >= score_range[0]) &
    (df_all['GrowthScore'] <= score_range[1])
]

st.sidebar.markdown("---")
st.sidebar.metric("Filtered Records", f"{len(df_filtered):,} / {len(df_all):,}")
st.sidebar.caption("SkyCity Auckland Analytics Engine v2.0")

# --- HEADER SECTION ---
st.markdown("<div class='main-header'>Restaurant Growth Potential Modeling & Strategic Classification System</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Data-driven framework for restaurant portfolio expansion, clustering, financial scoring, and strategic resource allocation.</div>", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Executive Overview",
    "🗺️ Cluster Explorer & Map",
    "🎯 Growth Scorecards",
    "📈 Feature Drivers",
    "💡 Strategy Recommendations",
    "⚖️ Restaurant Comparison",
    "🤖 ML Model Evaluation"
])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW
# ==========================================
with tab1:
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    tot_rest = len(df_filtered)
    avg_score = df_filtered['GrowthScore'].mean() if tot_rest > 0 else 0
    high_pot_cnt = len(df_filtered[df_filtered['GrowthScore'] >= 65])
    avg_rev = df_filtered['TotalRevenue'].mean() if tot_rest > 0 else 0
    avg_prof = df_filtered['TotalNetProfit'].mean() if tot_rest > 0 else 0
    avg_margin = df_filtered['ProfitMarginPct'].mean() if tot_rest > 0 else 0
    
    col1.metric("Total Restaurants", f"{tot_rest:,}")
    col2.metric("Avg Growth Score", f"{avg_score:.1f} / 100")
    col3.metric("High Potential", f"{high_pot_cnt:,}", f"{high_pot_cnt/tot_rest*100:.1f}%" if tot_rest>0 else "0%")
    col4.metric("Avg Monthly Rev", f"${avg_rev:,.0f}")
    col5.metric("Avg Net Profit", f"${avg_prof:,.0f}")
    col6.metric("Avg Profit Margin", f"{avg_margin:.1f}%")
    
    st.markdown("---")
    
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.subheader("Strategic Classification Distribution")
        cat_counts = df_filtered['StrategicCategory'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        
        color_map = {
            'EXPAND AGGRESSIVELY': '#10B981',
            'INVEST SELECTIVELY': '#3B82F6',
            'OPTIMIZE BEFORE EXPANSION': '#F59E0B',
            'MAINTAIN': '#64748B',
            'RESTRUCTURE / HIGH RISK': '#EF4444'
        }
        
        fig_cat = px.pie(
            cat_counts, 
            names='Category', 
            values='Count',
            color='Category',
            color_discrete_map=color_map,
            hole=0.4,
            title="Restaurants by Strategic Category"
        )
        fig_cat.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with row1_col2:
        st.subheader("Cluster Distribution")
        clust_counts = df_filtered['Cluster'].value_counts().reset_index()
        clust_counts.columns = ['Cluster', 'Count']
        
        fig_clust = px.bar(
            clust_counts,
            x='Count',
            y='Cluster',
            orientation='h',
            color='Cluster',
            title="Restaurants by Operational Cluster",
            text_auto=True
        )
        fig_clust.update_layout(showlegend=False)
        st.plotly_chart(fig_clust, use_container_width=True)
        
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.subheader("Revenue & Net Profit by Subregion")
        sub_agg = df_filtered.groupby('Subregion')[['TotalRevenue', 'TotalNetProfit']].mean().reset_index()
        
        fig_sub = go.Figure()
        fig_sub.add_trace(go.Bar(x=sub_agg['Subregion'], y=sub_agg['TotalRevenue'], name='Avg Revenue', marker_color='#3B82F6'))
        fig_sub.add_trace(go.Bar(x=sub_agg['Subregion'], y=sub_agg['TotalNetProfit'], name='Avg Net Profit', marker_color='#10B981'))
        fig_sub.update_layout(barmode='group', title="Financial Overview by Subregion ($)")
        st.plotly_chart(fig_sub, use_container_width=True)
        
    with row2_col2:
        st.subheader("Growth Potential Score Distribution")
        fig_hist = px.histogram(
            df_filtered, 
            x='GrowthScore', 
            color='StrategicCategory',
            color_discrete_map=color_map,
            nbins=30,
            title="Score Distribution across Portfolio"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# ==========================================
# TAB 2: CLUSTER MAP & PCA EXPLORER
# ==========================================
with tab2:
    st.subheader("Operational Clustering & Dimensionality Reduction (PCA)")
    st.markdown("Unsupervised K-Means clustering reduces high-dimensional financial/channel variables into 5 distinct operational profiles.")
    
    pca_dim = st.radio("PCA Visualization Mode", ["2D PCA Scatter", "3D PCA Scatter"], horizontal=True)
    
    if pca_dim == "2D PCA Scatter":
        fig_pca = px.scatter(
            df_filtered,
            x='PCA1',
            y='PCA2',
            color='Cluster',
            hover_name='RestaurantName',
            hover_data=['RestaurantID', 'Subregion', 'CuisineType', 'Segment', 'GrowthScore', 'TotalRevenue', 'TotalNetProfit', 'ProfitMarginPct'],
            title=f"2D PCA Projection of Restaurant Clusters (Explained Variance: {clust_meta['pca_variance_2d'][0]*100:.1f}% + {clust_meta['pca_variance_2d'][1]*100:.1f}%)"
        )
        fig_pca.update_traces(marker=dict(size=8, opacity=0.85))
        st.plotly_chart(fig_pca, use_container_width=True)
    else:
        fig_pca3 = px.scatter_3d(
            df_filtered,
            x='PCA3D_1',
            y='PCA3D_2',
            z='PCA3D_3',
            color='Cluster',
            hover_name='RestaurantName',
            hover_data=['Subregion', 'GrowthScore', 'TotalRevenue', 'TotalNetProfit'],
            title="3D PCA Dimensionality Projection"
        )
        fig_pca3.update_traces(marker=dict(size=5, opacity=0.8))
        st.plotly_chart(fig_pca3, use_container_width=True)
        
    st.subheader("Cluster Benchmark Centroids & Characteristics")
    st.dataframe(cluster_profiles, use_container_width=True)
    
    col_wcss, col_sil = st.columns(2)
    with col_wcss:
        st.caption("WCSS (Elbow Curve) & Silhouette Scores")
        k_wcss, k_sil = evaluate_optimal_k(df_filtered)
        elbow_df = pd.DataFrame({"k": list(k_wcss.keys()), "WCSS": list(k_wcss.values()), "Silhouette": list(k_sil.values())})
        fig_elbow = px.line(elbow_df, x='k', y='Silhouette', markers=True, title="Silhouette Score by Number of Clusters (k)")
        st.plotly_chart(fig_elbow, use_container_width=True)

# ==========================================
# TAB 3: GROWTH SCORECARDS
# ==========================================
with tab3:
    st.subheader("Individual Restaurant Growth Scorecard")
    
    rest_list = sorted(list(df_filtered['RestaurantName'].unique())) if len(df_filtered) > 0 else sorted(list(df_all['RestaurantName'].unique()))
    selected_rest_name = st.selectbox("Select Restaurant", rest_list)
    
    selected_row = df_all[df_all['RestaurantName'] == selected_rest_name].iloc[0]
    
    sc_col1, sc_col2, sc_col3 = st.columns([1, 2, 2])
    
    with sc_col1:
        st.markdown(f"### {selected_row['RestaurantName']}")
        st.caption(f"ID: #{selected_row['RestaurantID']} | {selected_row['CuisineType']} | {selected_row['Segment']} | {selected_row['Subregion']}")
        
        score_val = selected_row['GrowthScore']
        cat_val = selected_row['StrategicCategory']
        clust_val = selected_row['Cluster']
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score_val,
            title={'text': "Growth Potential Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1E293B"},
                'steps': [
                    {'range': [0, 35], 'color': "#FEE2E2"},
                    {'range': [35, 50], 'color': "#FEF3C7"},
                    {'range': [50, 65], 'color': "#E0F2FE"},
                    {'range': [65, 80], 'color': "#DBEAFE"},
                    {'range': [80, 100], 'color': "#DCFCE7"}
                ]
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.markdown(f"**Strategic Category**: `{cat_val}`")
        st.markdown(f"**Cluster Assignment**: `{clust_val}`")
        
    with sc_col2:
        st.markdown("#### Operational & Financial Stats")
        f_col1, f_col2 = st.columns(2)
        f_col1.metric("Total Monthly Rev", f"${selected_row['TotalRevenue']:,.2f}")
        f_col1.metric("Total Net Profit", f"${selected_row['TotalNetProfit']:,.2f}")
        f_col1.metric("Net Profit Margin", f"{selected_row['ProfitMarginPct']:.1f}%")
        
        f_col2.metric("Monthly Orders", f"{selected_row['MonthlyOrders']:,}")
        f_col2.metric("Average Order Value (AOV)", f"${selected_row['AOV']:.2f}")
        f_col2.metric("Growth Factor", f"{selected_row['GrowthFactor']:.2f}")
        
    with sc_col3:
        st.markdown("#### Performance vs Cuisine Benchmarks")
        cuisine_avg = df_all[df_all['CuisineType'] == selected_row['CuisineType']]
        
        categories_radar = ['GrowthScore', 'ProfitMarginPct', 'CostEfficiency', 'AOV', 'DeliveryOrderShare']
        
        rest_vals = [
            selected_row['GrowthScore'],
            min(selected_row['ProfitMarginPct'] * 2, 100), # scaled
            selected_row['CostEfficiency'] * 100,
            min(selected_row['AOV'] * 2, 100),
            selected_row['DeliveryOrderShare'] * 100
        ]
        
        cuisine_vals = [
            cuisine_avg['GrowthScore'].mean(),
            min(cuisine_avg['ProfitMarginPct'].mean() * 2, 100),
            cuisine_avg['CostEfficiency'].mean() * 100,
            min(cuisine_avg['AOV'].mean() * 2, 100),
            cuisine_avg['DeliveryOrderShare'].mean() * 100
        ]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=rest_vals, theta=categories_radar, fill='toself', name=selected_rest_name))
        fig_radar.add_trace(go.Scatterpolar(r=cuisine_vals, theta=categories_radar, fill='toself', name=f"Avg {selected_row['CuisineType']}"))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=280)
        st.plotly_chart(fig_radar, use_container_width=True)

# ==========================================
# TAB 4: FEATURE DRIVERS
# ==========================================
with tab4:
    st.subheader("Growth Drivers & Feature Contribution Analysis")
    st.markdown("Identification of top features driving restaurant expansion potential using Pearson correlation and Supervised Tree Feature Importances.")
    
    col_feat1, col_feat2 = st.columns(2)
    
    with col_feat1:
        st.markdown("#### Machine Learning Feature Importances (Gini Impurity)")
        rf_model = model_bundle['fitted_models']['Random Forest']
        feat_imp_df = extract_tree_feature_importance(rf_model, model_bundle['feature_cols'])
        
        fig_imp = px.bar(
            feat_imp_df,
            x='Importance_Pct',
            y='Feature',
            orientation='h',
            title="Random Forest Feature Importance (%)",
            text_auto='.1f'
        )
        fig_imp.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_imp, use_container_width=True)
        
    with col_feat2:
        st.markdown("#### Feature Correlations with Growth Potential Score")
        corr_df = compute_correlations(df_filtered, 'GrowthScore')
        
        fig_corr = px.bar(
            corr_df.head(10),
            x='Pearson Correlation',
            y='Feature',
            orientation='h',
            title="Top 10 Pearson Correlations with Growth Score",
            color='Pearson Correlation',
            color_continuous_scale='Blues'
        )
        fig_corr.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_corr, use_container_width=True)
        
    st.subheader("Combined Driver Ranking Table")
    driver_ranking = get_growth_drivers_ranking(df_filtered, rf_model, model_bundle['feature_cols'])
    st.dataframe(driver_ranking, use_container_width=True)

# ==========================================
# TAB 5: STRATEGY RECOMMENDATIONS
# ==========================================
with tab5:
    st.subheader("Data-Driven Prescriptive Strategy Engine")
    
    rec_rest_name = st.selectbox("Select Restaurant for Business Advice", rest_list, key="rec_select")
    rec_row = df_all[df_all['RestaurantName'] == rec_rest_name].iloc[0]
    
    recs_out = generate_restaurant_recommendations(rec_row, df_all)
    
    rec_c1, rec_c2 = st.columns([1, 2])
    
    with rec_c1:
        st.markdown(f"### {recs_out['restaurant_name']}")
        st.markdown(f"**Strategic Classification**: `{recs_out['strategic_category']}`")
        st.markdown(f"**Growth Potential Score**: `{recs_out['growth_score']} / 100`")
        
        st.markdown("#### Key Strengths")
        for s in recs_out['strengths']:
            st.markdown(f"✅ {s}")
            
        st.markdown("#### Operational Bottlenecks / Risks")
        for w in recs_out['weaknesses']:
            st.markdown(f"⚠️ {w}")
            
    with rec_c2:
        st.markdown("#### Strategic Rationale (WHY)")
        for r in recs_out['why']:
            st.info(r)
            
        st.markdown("#### Recommended Action Plan")
        for idx, item in enumerate(recs_out['recommendations'], 1):
            st.success(f"**Step {idx}**: {item}")

# ==========================================
# TAB 6: RESTAURANT COMPARISON
# ==========================================
with tab6:
    st.subheader("Multi-Restaurant Side-by-Side Comparison")
    
    default_select = rest_list[:3] if len(rest_list) >= 3 else rest_list
    selected_comp_rests = st.multiselect("Select 2 to 5 Restaurants to Compare", rest_list, default=default_select)
    
    if len(selected_comp_rests) >= 2:
        comp_df = df_all[df_all['RestaurantName'].isin(selected_comp_rests)]
        
        comp_metrics = [
            'RestaurantName', 'Subregion', 'CuisineType', 'Segment', 'GrowthScore',
            'StrategicCategory', 'Cluster', 'TotalRevenue', 'TotalNetProfit',
            'ProfitMarginPct', 'AOV', 'MonthlyOrders', 'DeliveryOrderShare', 'CostEfficiency'
        ]
        
        st.markdown("#### Comparative Metrics Table")
        st.dataframe(comp_df[comp_metrics].reset_index(drop=True), use_container_width=True)
        
        comp_c1, comp_c2 = st.columns(2)
        
        with comp_c1:
            fig_comp_rev = px.bar(comp_df, x='RestaurantName', y='TotalRevenue', color='StrategicCategory', title="Monthly Revenue Comparison ($)")
            st.plotly_chart(fig_comp_rev, use_container_width=True)
            
        with comp_c2:
            fig_comp_profit = px.bar(comp_df, x='RestaurantName', y='TotalNetProfit', color='StrategicCategory', title="Net Profit Comparison ($)")
            st.plotly_chart(fig_comp_profit, use_container_width=True)
    else:
        st.warning("Please select at least 2 restaurants to compare.")

# ==========================================
# TAB 7: ML MODEL EVALUATION
# ==========================================
with tab7:
    st.subheader("Supervised Machine Learning Model Performance")
    st.markdown("Evaluation of classification models predicting Strategic Category using 80/20 train-test split.")
    
    st.markdown("#### Model Performance Leaderboard")
    st.dataframe(metrics_df, use_container_width=True)
    
    selected_eval_model = st.selectbox("Select Model for Confusion Matrix Inspection", metrics_df['Model'].tolist())
    
    eval_bundle = model_bundle['eval_results'][selected_eval_model]
    cm_matrix = eval_bundle['confusion_matrix']
    class_labels = eval_bundle['classes']
    
    fig_cm = px.imshow(
        cm_matrix,
        x=class_labels,
        y=class_labels,
        text_auto=True,
        color_continuous_scale='Blues',
        title=f"Confusion Matrix: {selected_eval_model}",
        labels=dict(x="Predicted Category", y="Actual Category")
    )
    st.plotly_chart(fig_cm, use_container_width=True)
