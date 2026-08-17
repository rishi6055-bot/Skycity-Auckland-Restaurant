# Restaurant Growth Potential Modeling & Strategic Classification System

An end-to-end statistical, machine-learning, and interactive decision-support system designed to evaluate restaurant growth readiness, cluster operational profiles, classify strategic expansion tiers, and provide data-driven business recommendations.

---

## 📌 Project Overview & Objective

In the competitive food service and hospitality industry, decision-makers are inundated with multi-channel data across physical dining, third-party delivery platforms (UberEats, DoorDash), self-delivery logistics, cost rates (COGS, OPEX, Commissions), and growth metrics. However, converting raw operational numbers into actionable expansion capital allocation strategies remains challenging.

### Objectives:
1. **Holistic Growth Assessment**: Develop an explainable 0–100 **Growth Potential Score** combining top-line revenue, growth velocity, net profit, margin quality, ticket size (AOV), cost efficiency, and channel performance.
2. **Operational Clustering**: Group 1,696 restaurants into 5 meaningful operational profiles using unsupervised learning (K-Means & Hierarchical Clustering) validated via Silhouette scoring and PCA.
3. **Strategic Taxonomy & Classification**: Categorize restaurants into 5 actionable business classes (`EXPAND AGGRESSIVELY`, `INVEST SELECTIVELY`, `OPTIMIZE BEFORE EXPANSION`, `MAINTAIN`, `RESTRUCTURE / HIGH RISK`) using a transparent rule engine and predictive Supervised Machine Learning models.
4. **Feature Contribution Analysis**: Extract top growth drivers using Pearson/Spearman correlation and Gini/Permutation feature importance.
5. **Interactive Streamlit Dashboard**: Provide executives and operational leaders with an interactive 7-tab dashboard for portfolio exploration, individual restaurant scorecards, scenario recommendations, and multi-restaurant comparative analyses.

---

## 📂 Project Structure

```
restaurant_growth_project/
│
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
│
├── data/
│   └── SkyCity Auckland Restaurants & Bars.csv   # Raw dataset (1,696 records x 30 columns)
│
├── src/
│   ├── __init__.py             # Package marker
│   ├── data_processing.py      # Cleaning, validation, & feature scaling
│   ├── feature_engineering.py  # Revenue, profit, channel, cost, & growth metrics
│   ├── scoring.py              # Explainable 0-100 Growth Potential Score model
│   ├── clustering.py           # K-Means, Silhouette analysis, & PCA projections
│   ├── classification.py       # Strategic classification & supervised ML models
│   ├── feature_importance.py   # Correlation, tree importances, & driver rankings
│   └── recommendations.py      # Data-driven strategy recommendation engine
│
└── outputs/                    # Output directory for exported models/data
```

---

## 📊 Dataset Description

The analysis is based on the **SkyCity Auckland Restaurants & Bars** dataset containing **1,696 restaurant records** across 30 original variables:
- **Descriptors**: `RestaurantID`, `RestaurantName`, `Subregion` (CBD, North Shore, South Auckland, West Auckland), `CuisineType` (8 cuisines), `Segment` (Cafe, QSR, Ghost Kitchen, Full-service).
- **Order & Channel Financials**: `InStoreOrders`, `UberEatsOrders`, `DoorDashOrders`, `SelfDeliveryOrders`, `InStoreRevenue`, `UberEatsRevenue`, `DoorDashRevenue`, `SelfDeliveryRevenue`, `InStoreNetProfit`, `UberEatsNetProfit`, `DoorDashNetProfit`, `SelfDeliveryNetProfit`.
- **Cost Structure & Logistics**: `COGSRate`, `OPEXRate`, `CommissionRate`, `DeliveryRadiusKM`, `DeliveryCostPerOrder`, `SD_DeliveryTotalCost`.
- **Growth & Performance**: `GrowthFactor` (0.99 to 1.05), `AOV` (Average Order Value).

---

## 🔬 Data Science Methodology

### 1. Data Cleaning & Preprocessing
- **Missing Values**: Verified zero null values across all 1,696 records.
- **Duplicates**: Verified zero duplicate `RestaurantID` rows.
- **Boundary Validation**: Non-negative order and revenue bounds enforced; rates restricted to valid $[0, 1]$ fractions.
- **Scaling**: `MinMaxScaler` applied for composite scoring and `StandardScaler` applied for distance-based clustering and ML classification.

### 2. Feature Engineering
- **`TotalRevenue`**: $Revenue_{InStore} + Revenue_{UberEats} + Revenue_{DoorDash} + Revenue_{SelfDelivery}$
- **`TotalNetProfit`**: $Profit_{InStore} + Profit_{UberEats} + Profit_{DoorDash} + Profit_{SelfDelivery}$
- **`ProfitMarginPct`**: $\left(\frac{TotalNetProfit}{TotalRevenue}\right) \times 100\%$
- **`DeliveryOrderShare`**: $\frac{Orders_{Delivery}}{MonthlyOrders}$
- **`CostEfficiency`**: $1.0 - (\text{COGSRate} + \text{OPEXRate})$
- **`ThirdPartyShare`**: $\frac{Revenue_{UberEats} + Revenue_{DoorDash}}{TotalRevenue}$
- **`GrowthRatePct`**: $(\text{GrowthFactor} - 1.0) \times 100\%$

### 3. Growth Potential Score (0–100)
Multi-criteria decision analysis (MCDA) combining 7 normalized dimensions:

$$\text{GrowthScore} = 100 \times \sum_{i=1}^n \left( w_i \times \text{MinMax}(X_i) \right)$$

| Dimension | Weight | Business Rationale |
| :--- | :--- | :--- |
| **Growth Factor** | **20%** | Measures top-line expansion momentum |
| **Total Net Profit** | **20%** | Absolute bottom-line cash generation |
| **Profit Margin %** | **15%** | Earnings quality and unit economic health |
| **Total Revenue** | **15%** | Scale and market demand volume |
| **Average Order Value (AOV)** | **10%** | Ticket size pricing power |
| **Cost Efficiency** | **10%** | Operational efficiency ($1 - \text{COGS}\% - \text{OPEX}\%$) |
| **Delivery Margin** | **10%** | Logistics channel optimization |

#### Score Tiers:
- **Very High Growth Potential**: $\ge 80.0$
- **High Growth Potential**: $65.0 - 79.9$
- **Moderate Growth Potential**: $50.0 - 64.9$
- **Low Growth Potential**: $35.0 - 49.9$
- **Very Low Growth Potential**: $< 35.0$

### 4. Operational Clustering
K-Means clustering evaluated across $k \in [2, 8]$:
- **Optimal $k=5$** selected via Silhouette score and Elbow Curve (WCSS).
- **PCA 2D & 3D**: Captures $>65\%$ of total feature variance for interactive visualization.
- **Cluster Profiles**:
  1. *Expansion Leaders*: High revenue, high profit margin, top growth score.
  2. *Efficient Growth Performers*: Strong margins, moderate revenue, lean cost structures.
  3. *Delivery Driven Powerhouses*: High delivery order share ($>85\%$), high revenue.
  4. *High Revenue / Low Margin Operators*: Strong top-line volume compressed by high OPEX/COGS.
  5. *At-Risk / Low Margin Stores*: Low growth score, compressed or negative net profit margins.

### 5. Strategic Classification & Supervised Machine Learning
Restaurants are classified into 5 strategic action categories:
- **`EXPAND AGGRESSIVELY`**: Growth Score $\ge 70$, Profit Margin $\ge 10\%$, Net Profit $> \$5,000$.
- **`INVEST SELECTIVELY`**: Growth Score $55 - 70$, Profit Margin $\ge 7.5\%$.
- **`OPTIMIZE BEFORE EXPANSION`**: High Revenue ($> \$40,000$) but compressed margin ($< 7.5\%$).
- **`MAINTAIN`**: Growth Score $42 - 55$, positive cash flow.
- **`RESTRUCTURE / HIGH RISK`**: Growth Score $< 42$ or negative net margin.

#### Supervised ML Benchmark Results (80/20 Train-Test Split):
| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **93.24%** | **93.30%** | **93.24%** | **0.9324** | **0.9952** |
| **Gradient Boosting** | **92.65%** | **92.67%** | **92.65%** | **0.9257** | **0.9932** |
| **Random Forest** | **87.94%** | **88.00%** | **87.94%** | **0.8759** | **0.9837** |
| **Decision Tree** | **86.76%** | **86.65%** | **86.76%** | **0.8659** | **0.9448** |

---

## 🖥️ Streamlit Interactive Dashboard Features

The dashboard includes 7 interactive tabs with dynamic sidebar filtering (Subregion, Cuisine, Segment, Category, Cluster, Growth Score):

1. **Executive Overview**: Executive KPI metrics cards, Strategic Category donut chart, Cluster breakdown bar chart, Subregion revenue/profit comparison, and Score distribution histogram.
2. **Cluster Explorer & Map**: Interactive 2D and 3D PCA scatter plots with hover tooltips, Elbow/Silhouette curves, and centroid benchmark table.
3. **Growth Scorecards**: Restaurant search & selection, 0–100 score gauge, operational metrics, and radar chart comparing restaurant vs. cuisine average.
4. **Feature Drivers**: Random Forest Gini feature importances, Pearson/Spearman correlation heatmaps, and driver ranking tables.
5. **Strategy Recommendations**: Automated data-driven business advice generating custom action plans across Marketing, Delivery Mix, Cost Control, and Expansion.
6. **Restaurant Comparison**: Side-by-side metric comparison table and comparative bar charts across 2–5 selected restaurants.
7. **ML Model Evaluation**: Model performance metrics summary and interactive confusion matrix heatmap.

---

## 🚀 Installation & Operating Guide

### Prerequisites
- Python 3.9+ installed on Windows / macOS / Linux.

### Setup Instructions

1. **Clone or Open Project Directory**:
   ```bash
   cd restaurant_growth_project
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch Streamlit Dashboard**:
   ```bash
   streamlit run app.py
   ```

4. Access the running app in your browser at `http://localhost:8501`.

---

## 📈 Key Business Findings & Strategic Insights

1. **Profitability Over Volume**: High revenue does not guarantee expansion readiness. High Revenue / Low Margin stores suffer from OPEX rates exceeding $40\%$, highlighting the need for cost optimization before capital deployment.
2. **Third-Party Platform Fee Drag**: Third-party commissions ($27\% - 33\%$) compress delivery margins compared to self-delivery. Encouraging direct self-delivery ordering significantly improves net profit margins.
3. **Subregion Performance Variance**: Stores located in high-density areas (CBD and North Shore) demonstrate higher average order volumes but require strict portion and labor controls due to elevated overhead.

---

## 🔮 Limitations & Future Scope

- **Geographic Data**: Current dataset provides subregion categories rather than latitude/longitude GPS points. Integrating street-level coordinates will enable geospatial routing maps.
- **Time-Series Dynamics**: Incorporating multi-month historical trends will enable predictive time-series forecasting (ARIMA / LSTM) for seasonal revenue predictions.

---

*System developed for MSc Statistics Academic Submission & Executive Decision Support.*
