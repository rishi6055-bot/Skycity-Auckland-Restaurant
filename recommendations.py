import pandas as pd
import numpy as np

def generate_restaurant_recommendations(restaurant: pd.Series, benchmark_df: pd.DataFrame = None) -> dict:
    """
    Generates data-driven business recommendations and operational diagnostics for a specific restaurant.
    Compares restaurant performance against dataset / subregion / cuisine benchmarks.
    """
    name = restaurant.get('RestaurantName', 'Unknown Restaurant')
    category = restaurant.get('StrategicCategory', 'MAINTAIN')
    score = restaurant.get('GrowthScore', 50.0)
    rev = restaurant.get('TotalRevenue', 0.0)
    profit = restaurant.get('TotalNetProfit', 0.0)
    margin = restaurant.get('ProfitMarginPct', 0.0)
    aov = restaurant.get('AOV', 0.0)
    cogs_rate = restaurant.get('COGSRate', 0.0) * 100.0
    opex_rate = restaurant.get('OPEXRate', 0.0) * 100.0
    comm_rate = restaurant.get('CommissionRate', 0.0) * 100.0
    growth = restaurant.get('GrowthFactor', 1.0)
    growth_pct = (growth - 1.0) * 100.0
    deliv_share = restaurant.get('DeliveryOrderShare', 0.0) * 100.0
    tp_share = restaurant.get('ThirdPartyShare', 0.0) * 100.0
    instore_profit = restaurant.get('InStoreNetProfit', 0.0)
    sd_profit = restaurant.get('SelfDeliveryNetProfit', 0.0)
    ue_profit = restaurant.get('UberEatsNetProfit', 0.0)
    dd_profit = restaurant.get('DoorDashNetProfit', 0.0)
    
    # Subregion & Cuisine Benchmarks if available
    subregion = restaurant.get('Subregion', '')
    cuisine = restaurant.get('CuisineType', '')
    
    if benchmark_df is not None:
        sub_bench = benchmark_df[benchmark_df['Subregion'] == subregion] if subregion in benchmark_df['Subregion'].values else benchmark_df
        avg_rev = sub_bench['TotalRevenue'].mean()
        avg_margin = sub_bench['ProfitMarginPct'].mean()
    else:
        avg_rev = 45000.0
        avg_margin = 10.0

    why_reasons = []
    strengths = []
    weaknesses = []
    action_items = []

    # Category Specific Core Rationale & Action Items
    if category == 'EXPAND AGGRESSIVELY':
        why_reasons.append(f"Exceptional Growth Score of {score:.1f}/100 with robust top-line monthly revenue (${rev:,.2f}).")
        why_reasons.append(f"Highly profitable with a net profit margin of {margin:.1f}% (${profit:,.2f}/month).")
        why_reasons.append(f"Strong expansion velocity (Growth factor: {growth:.2f}).")
        
        strengths.append(f"Top-tier profitability margin of {margin:.1f}%.")
        strengths.append(f"Strong average order value (${aov:.2f}).")
        
        action_items.append("Capitalize on strong brand equity by opening new subregion locations or franchising.")
        action_items.append("Increase local digital marketing budget by 15-20% to capture additional market share.")
        action_items.append("Establish centralized prep kitchens (ghost kitchens) to serve adjacent high-density subregions.")
        action_items.append("Standardize operational SOPs to maintain quality during rapid expansion.")

    elif category == 'INVEST SELECTIVELY':
        why_reasons.append(f"Solid Growth Score of {score:.1f}/100 showing strong consumer demand.")
        why_reasons.append(f"Healthy gross potential with monthly revenue of ${rev:,.2f} and {margin:.1f}% net margin.")
        
        strengths.append(f"Consistent order volume and steady customer growth (+{growth_pct:.1f}%).")
        if aov > 35:
            strengths.append(f"Solid Average Order Value (${aov:.2f}).")
            
        action_items.append("Target operational bottlenecks to convert sales into higher net margin.")
        action_items.append("Invest in customer loyalty programs and direct ordering channels to reduce platform commission reliance.")
        action_items.append("Evaluate targeted kitchen equipment upgrades to boost peak-hour throughput.")

    elif category == 'OPTIMIZE BEFORE EXPANSION':
        why_reasons.append(f"High order volume (${rev:,.2f} revenue), but profitability is compressed to {margin:.1f}%.")
        why_reasons.append(f"High operational overhead (COGS: {cogs_rate:.1f}%, OPEX: {opex_rate:.1f}%).")
        
        weaknesses.append(f"Margin compression: OPEX ({opex_rate:.1f}%) and COGS ({cogs_rate:.1f}%) consume majority of revenue.")
        if comm_rate > 28:
            weaknesses.append(f"Third-party commission fees ({comm_rate:.1f}%) eat heavily into delivery profits.")
            
        action_items.append("Renegotiate raw material vendor pricing and implement strict portion control to trim COGS by 3-5%.")
        action_items.append("Audit store staffing schedules to align labor cost with peak order hours.")
        action_items.append("Renegotiate third-party delivery commission contracts or promote self-delivery options.")
        action_items.append("Freeze physical location expansion until net profit margin exceeds 10%.")

    elif category == 'MAINTAIN':
        why_reasons.append(f"Stable, steady operational footprint with Moderate Growth Score ({score:.1f}/100).")
        why_reasons.append(f"Positive net profit (${profit:,.2f}/month) with steady market presence.")
        
        strengths.append(f"Low risk profile with consistent cash flow generation.")
        
        action_items.append("Maintain baseline operational efficiency and preserve cash flow.")
        action_items.append("Optimize menu engineering by promoting high-margin items.")
        action_items.append("Run seasonal promotional campaigns to boost Average Order Value.")

    else: # RESTRUCTURE / HIGH RISK
        why_reasons.append(f"Low Growth Potential Score ({score:.1f}/100) indicating operational drag.")
        if margin < 0:
            why_reasons.append(f"Operates at a net financial loss (${profit:,.2f}/month; {margin:.1f}% margin).")
        else:
            why_reasons.append(f"Weak bottom-line margin of {margin:.1f}%.")
            
        weaknesses.append(f"Severe profitability strain (${profit:,.2f} net profit).")
        weaknesses.append(f"Excessive cost structure (Combined COGS + OPEX: {cogs_rate + opex_rate:.1f}%).")
        
        action_items.append("Conduct an immediate operational audit of menu item profitability and cut non-performing items.")
        action_items.append("Implement aggressive cost reduction in OPEX and labor overhead.")
        action_items.append("Shift focus toward direct high-margin in-store sales and self-delivery to eliminate platform fee drag.")
        action_items.append("Consider restructuring business hours to eliminate unprofitable off-peak shifts.")

    # General Channel Specific Highlights
    if ue_profit < 0 or dd_profit < 0:
        weaknesses.append("Loss-making third-party delivery channels detected (UberEats/DoorDash net profit negative).")
        action_items.append("Adjust third-party delivery menu pricing upwards (10-15% markups) to cover platform commission rates.")

    if sd_profit > ue_profit and sd_profit > dd_profit and sd_profit > 0:
        strengths.append(f"Self-delivery channel is highly profitable (${sd_profit:,.2f} net profit).")
        action_items.append("Expand self-delivery delivery radius and market self-ordering directly to customers.")

    return {
        "restaurant_name": name,
        "strategic_category": category,
        "growth_score": round(score, 1),
        "why": why_reasons,
        "strengths": strengths if strengths else ["Stable baseline operations."],
        "weaknesses": weaknesses if weaknesses else ["Minor margin optimization opportunities."],
        "recommendations": action_items
    }
