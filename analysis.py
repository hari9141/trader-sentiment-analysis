#!/usr/bin/env python3
"""
Trader Behavior & Market Sentiment Analysis
Complete Analysis Pipeline
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*100)
print("TRADER BEHAVIOR & MARKET SENTIMENT ANALYSIS - COMPLETE EXECUTION")
print("="*100 + "\n")

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("[STEP 1] Loading datasets...\n")

try:
    fear_greed = pd.read_csv('data/fear_greed_index.csv')
    print("✓ Fear & Greed Index loaded successfully")
    print(f"  Shape: {fear_greed.shape}")
except Exception as e:
    print(f"✗ ERROR loading fear_greed_index.csv: {e}")
    exit()

try:
    trader_data = pd.read_csv('data/historical_data.csv', low_memory=False)
    print("✓ Historical trader data loaded successfully")
    print(f"  Shape: {trader_data.shape}")
except Exception as e:
    print(f"✗ ERROR loading historical_data.csv: {e}")
    exit()

# ============================================================================
# STEP 2: EXPLORE DATA STRUCTURE
# ============================================================================
print("\n[STEP 2] Exploring data structure...\n")

print("FEAR & GREED INDEX COLUMNS:")
print(f"  {fear_greed.columns.tolist()}\n")

print("TRADER DATA COLUMNS:")
for i, col in enumerate(trader_data.columns, 1):
    print(f"  {i}. {col}")

print(f"\nTrader data preview:")
print(trader_data.head(2))

# ============================================================================
# STEP 3: DATA CLEANING & PREPARATION
# ============================================================================
print("\n[STEP 3] Cleaning and preparing data...\n")

# Convert fear_greed dates
fear_greed['date'] = pd.to_datetime(fear_greed['date'])
print(f"✓ Fear & Greed dates converted")

# Identify and convert trader timestamp
timestamp_col = 'Timestamp'  # This is the millisecond timestamp from your image
if timestamp_col in trader_data.columns:
    trader_data['datetime'] = pd.to_datetime(trader_data[timestamp_col], unit='ms')
    print(f"✓ Trader timestamps converted from milliseconds")
else:
    print(f"⚠ Column '{timestamp_col}' not found. Available: {trader_data.columns.tolist()}")
    # Use the last column (usually timestamp)
    last_col = trader_data.columns[-1]
    trader_data['datetime'] = pd.to_datetime(trader_data[last_col], unit='ms', errors='coerce')
    print(f"✓ Used alternative column: {last_col}")

# Extract date
trader_data['date'] = trader_data['datetime'].dt.date
trader_data['date'] = pd.to_datetime(trader_data['date'])

print(f"✓ Date extracted from timestamps")
print(f"  Trader data date range: {trader_data['date'].min()} to {trader_data['date'].max()}")

# Remove duplicates
trader_data_before = len(trader_data)
trader_data = trader_data.drop_duplicates(subset=['Transaction Hash'], keep='first')
print(f"✓ Duplicates removed: {trader_data_before - len(trader_data)} records")

# Handle Closed PnL column
pnl_col = 'Closed PnL'
if pnl_col not in trader_data.columns:
    # Find it by partial name
    pnl_candidates = [col for col in trader_data.columns if 'pnl' in col.lower()]
    if pnl_candidates:
        pnl_col = pnl_candidates[0]
        print(f"⚠ Remapped PnL column to: {pnl_col}")
    else:
        print("✗ ERROR: Could not find PnL column")
        exit()

# Remove NaN from PnL
trader_data = trader_data.dropna(subset=[pnl_col])
print(f"✓ Removed rows with missing PnL")

# Remove extreme outliers (keep 1st-99th percentile)
q1 = trader_data[pnl_col].quantile(0.01)
q99 = trader_data[pnl_col].quantile(0.99)
trader_data_before = len(trader_data)
trader_data = trader_data[(trader_data[pnl_col] >= q1) & (trader_data[pnl_col] <= q99)]
print(f"✓ Outliers removed (1st-99th percentile): {trader_data_before - len(trader_data)} records")
print(f"  Remaining trades: {len(trader_data):,}")

# ============================================================================
# STEP 4: MERGE DATASETS
# ============================================================================
print("\n[STEP 4] Merging sentiment data with trader data...\n")

merged = trader_data.merge(
    fear_greed[['date', 'classification', 'value']], 
    on='date', 
    how='left'
)

print(f"Before removing NaN sentiment: {len(merged):,} trades")
merged = merged.dropna(subset=['classification'])
print(f"After removing NaN sentiment: {len(merged):,} trades")
print(f"✓ Merge complete")

# ============================================================================
# STEP 5: FEATURE ENGINEERING
# ============================================================================
print("\n[STEP 5] Engineering features...\n")

# Trade classification
merged['profitable'] = merged[pnl_col] > 0
merged['pnl_abs'] = merged[pnl_col].abs()

print(f"✓ Created 'profitable' feature")

# Sentiment numeric encoding
sentiment_map = {
    'Extreme Fear': 1,
    'Fear': 2,
    'Neutral': 3,
    'Greed': 4,
    'Extreme Greed': 5
}
merged['sentiment_numeric'] = merged['classification'].map(sentiment_map)
print(f"✓ Created 'sentiment_numeric' feature")

# Direction features
dir_col = 'Direction'
if dir_col in merged.columns:
    merged['is_buy'] = (merged[dir_col] == 'Buy').astype(int)
    print(f"✓ Created 'is_buy' feature from Direction column")
else:
    print(f"⚠ Direction column not found")
    merged['is_buy'] = np.nan

# Time features
merged['hour'] = merged['datetime'].dt.hour
merged['day_of_week'] = merged['datetime'].dt.day_name()
merged['month'] = merged['datetime'].dt.month
print(f"✓ Created time-based features")

print("\n" + "="*100)
print("ANALYSIS RESULTS")
print("="*100 + "\n")

# ============================================================================
# ANALYSIS 1: OVERALL STATISTICS
# ============================================================================
print("[ANALYSIS 1] OVERALL STATISTICS\n")

print(f"Total Trades Analyzed:        {len(merged):,}")
print(f"Date Range:                   {merged['date'].min().date()} to {merged['date'].max().date()}")
print(f"Overall Win Rate:             {(merged['profitable'].mean() * 100):.2f}%")
print(f"Average PnL per Trade:        ${merged[pnl_col].mean():.2f}")
print(f"Median PnL per Trade:         ${merged[pnl_col].median():.2f}")
print(f"Total PnL (All Trades):       ${merged[pnl_col].sum():.2f}")
print(f"Std Dev of PnL:               ${merged[pnl_col].std():.2f}")
print(f"Max Single Trade PnL:         ${merged[pnl_col].max():.2f}")
print(f"Min Single Trade PnL:         ${merged[pnl_col].min():.2f}")
print(f"Profitable Trades:            {merged['profitable'].sum():,}")
print(f"Losing Trades:                {(~merged['profitable']).sum():,}")

# ============================================================================
# ANALYSIS 2: PERFORMANCE BY SENTIMENT
# ============================================================================
print("\n" + "-"*100)
print("[ANALYSIS 2] PERFORMANCE BY SENTIMENT\n")

sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']

print(f"{'Sentiment':<15} {'Trades':>10} {'Win Rate':>12} {'Avg PnL':>12} {'Total PnL':>15} {'Profitable':>12}")
print("-"*100)

for sentiment in sentiment_order:
    subset = merged[merged['classification'] == sentiment]
    if len(subset) > 0:
        win_rate = (subset['profitable'].sum() / len(subset) * 100)
        avg_pnl = subset[pnl_col].mean()
        total_pnl = subset[pnl_col].sum()
        profitable_count = subset['profitable'].sum()
        
        print(f"{sentiment:<15} {len(subset):>10,} {win_rate:>11.2f}% ${avg_pnl:>11.2f} ${total_pnl:>14.2f} {profitable_count:>12,}")

# ============================================================================
# ANALYSIS 3: EXTREME SENTIMENT DEEP DIVE
# ============================================================================
print("\n" + "-"*100)
print("[ANALYSIS 3] EXTREME SENTIMENT COMPARISON\n")

extreme_fear = merged[merged['classification'] == 'Extreme Fear']
extreme_greed = merged[merged['classification'] == 'Extreme Greed']
neutral = merged[merged['classification'] == 'Neutral']

print("EXTREME FEAR:")
print(f"  Number of trades:         {len(extreme_fear):,}")
print(f"  Win rate:                 {(extreme_fear['profitable'].mean() * 100):.2f}%")
print(f"  Average PnL:              ${extreme_fear[pnl_col].mean():.2f}")
print(f"  Total PnL:                ${extreme_fear[pnl_col].sum():.2f}")
print(f"  Avg Loss per trade:       ${extreme_fear[pnl_col].std():.2f}")

print("\nEXTREME GREED:")
print(f"  Number of trades:         {len(extreme_greed):,}")
print(f"  Win rate:                 {(extreme_greed['profitable'].mean() * 100):.2f}%")
print(f"  Average PnL:              ${extreme_greed[pnl_col].mean():.2f}")
print(f"  Total PnL:                ${extreme_greed[pnl_col].sum():.2f}")
print(f"  Avg Loss per trade:       ${extreme_greed[pnl_col].std():.2f}")

print("\nNEUTRAL:")
print(f"  Number of trades:         {len(neutral):,}")
print(f"  Win rate:                 {(neutral['profitable'].mean() * 100):.2f}%")
print(f"  Average PnL:              ${neutral[pnl_col].mean():.2f}")
print(f"  Total PnL:                ${neutral[pnl_col].sum():.2f}")
print(f"  Avg Loss per trade:       ${neutral[pnl_col].std():.2f}")

# ============================================================================
# ANALYSIS 4: STATISTICAL TESTS
# ============================================================================
print("\n" + "-"*100)
print("[ANALYSIS 4] STATISTICAL SIGNIFICANCE TESTS\n")

# T-test: Extreme Fear vs Extreme Greed
if len(extreme_fear) > 1 and len(extreme_greed) > 1:
    t_stat, p_value_t = stats.ttest_ind(
        extreme_fear[pnl_col].dropna(),
        extreme_greed[pnl_col].dropna()
    )
    
    print("T-TEST: Extreme Fear vs Extreme Greed")
    print(f"  t-statistic:              {t_stat:.6f}")
    print(f"  p-value:                  {p_value_t:.10f}")
    print(f"  Significant (p<0.05):     {'YES ✓✓✓ HIGHLY SIGNIFICANT' if p_value_t < 0.05 else 'NO'}")
else:
    print("⚠ Insufficient data for t-test")

# ANOVA: All sentiment groups
print("\nANOVA: All Sentiment Groups")
sentiment_groups = [
    group[pnl_col].dropna().values 
    for name, group in merged.groupby('classification') 
    if len(group) > 0
]

if len(sentiment_groups) > 1:
    f_stat, p_value_anova = stats.f_oneway(*sentiment_groups)
    
    print(f"  f-statistic:              {f_stat:.6f}")
    print(f"  p-value:                  {p_value_anova:.10f}")
    print(f"  Significant (p<0.05):     {'YES ✓✓✓ HIGHLY SIGNIFICANT' if p_value_anova < 0.05 else 'NO'}")
    print(f"\n  Interpretation: Sentiment {'DOES' if p_value_anova < 0.05 else 'DOES NOT'} significantly affect trading performance")
else:
    print("⚠ Insufficient sentiment groups for ANOVA")

# ============================================================================
# ANALYSIS 5: BUY vs SELL PERFORMANCE
# ============================================================================
print("\n" + "-"*100)
print("[ANALYSIS 5] BUY vs SELL PERFORMANCE BY SENTIMENT\n")

if 'is_buy' in merged.columns and merged['is_buy'].notna().any():
    print(f"{'Sentiment':<15} {'Buy Trades':>12} {'Buy Win%':>12} {'Buy Avg$':>15} {'Sell Trades':>12} {'Sell Win%':>12} {'Sell Avg$':>15}")
    print("-"*100)
    
    for sentiment in sentiment_order:
        subset = merged[merged['classification'] == sentiment]
        buy_trades = subset[subset['is_buy'] == 1]
        sell_trades = subset[subset['is_buy'] == 0]
        
        buy_win = (buy_trades['profitable'].mean() * 100) if len(buy_trades) > 0 else 0
        buy_avg = buy_trades[pnl_col].mean() if len(buy_trades) > 0 else 0
        
        sell_win = (sell_trades['profitable'].mean() * 100) if len(sell_trades) > 0 else 0
        sell_avg = sell_trades[pnl_col].mean() if len(sell_trades) > 0 else 0
        
        print(f"{sentiment:<15} {len(buy_trades):>12,} {buy_win:>11.2f}% ${buy_avg:>14.2f} {len(sell_trades):>12,} {sell_win:>11.2f}% ${sell_avg:>14.2f}")
else:
    print("⚠ Buy/Sell data not available")

# ============================================================================
# ANALYSIS 6: DAILY AGGREGATION
# ============================================================================
print("\n" + "-"*100)
print("[ANALYSIS 6] DAILY STATISTICS BY SENTIMENT\n")

daily_stats = merged.groupby(['date', 'classification']).agg({
    pnl_col: ['sum', 'mean', 'count'],
    'profitable': ['sum', 'mean']
}).round(2)

daily_stats.columns = ['daily_total_pnl', 'daily_avg_pnl', 'trade_count', 'profitable_count', 'win_rate']
daily_stats = daily_stats.reset_index()
daily_stats['win_rate'] = (daily_stats['win_rate'] * 100).round(2)

print("Sample Daily Statistics (first 10 days):")
print(daily_stats.head(10).to_string())

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n" + "-"*100)
print("[SAVING RESULTS]\n")

# Save daily stats
daily_stats.to_csv('outputs/daily_statistics.csv', index=False)
print("✓ Saved: outputs/daily_statistics.csv")

# Save merged data for visualization
merged.to_csv('outputs/merged_data.csv', index=False)
print("✓ Saved: outputs/merged_data.csv")

# ============================================================================
# CREATE VISUALIZATIONS
# ============================================================================
print("\n[CREATING VISUALIZATIONS]\n")

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# FIGURE 1: Performance Dashboard
print("Creating Figure 1: Performance Dashboard...")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Trader Performance by Market Sentiment', fontsize=18, fontweight='bold', y=0.995)

# Convert classification to ordered category
merged['classification_cat'] = pd.Categorical(merged['classification'], 
                                              categories=sentiment_order, 
                                              ordered=True)

# Subplot 1: Box plot of PnL
ax1 = axes[0, 0]
box_data = [merged[merged['classification'] == sent][pnl_col].values for sent in sentiment_order]
bp = ax1.boxplot(box_data, labels=sentiment_order, patch_artist=True)
for patch, color in zip(bp['boxes'], plt.cm.RdYlGn(np.linspace(0, 1, 5))):
    patch.set_facecolor(color)
ax1.set_title('PnL Distribution by Sentiment', fontsize=12, fontweight='bold')
ax1.set_ylabel('PnL ($)', fontsize=11)
ax1.set_xlabel('Sentiment Classification', fontsize=11)
ax1.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax1.grid(True, alpha=0.3)
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Subplot 2: Win Rate by Sentiment
ax2 = axes[0, 1]
win_rates = [merged[merged['classification'] == sent]['profitable'].mean() * 100 for sent in sentiment_order]
colors = plt.cm.RdYlGn(np.linspace(0, 1, 5))
bars = ax2.bar(range(len(sentiment_order)), win_rates, color=colors, edgecolor='black', linewidth=1.5)
ax2.set_xticks(range(len(sentiment_order)))
ax2.set_xticklabels(sentiment_order, rotation=45, ha='right')
ax2.set_title('Win Rate by Sentiment', fontsize=12, fontweight='bold')
ax2.set_ylabel('Win Rate (%)', fontsize=11)
ax2.axhline(y=50, color='red', linestyle='--', linewidth=2, alpha=0.7, label='50% (Breakeven)')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')
for bar, wr in zip(bars, win_rates):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{wr:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Subplot 3: Average PnL by Sentiment
ax3 = axes[1, 0]
avg_pnls = [merged[merged['classification'] == sent][pnl_col].mean() for sent in sentiment_order]
colors_pnl = ['red' if x < 0 else 'green' for x in avg_pnls]
bars = ax3.bar(range(len(sentiment_order)), avg_pnls, color=colors_pnl, edgecolor='black', linewidth=1.5, alpha=0.7)
ax3.set_xticks(range(len(sentiment_order)))
ax3.set_xticklabels(sentiment_order, rotation=45, ha='right')
ax3.set_title('Average PnL by Sentiment', fontsize=12, fontweight='bold')
ax3.set_ylabel('Average PnL ($)', fontsize=11)
ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax3.grid(True, alpha=0.3, axis='y')
for bar, pnl in zip(bars, avg_pnls):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'${pnl:.2f}', ha='center', va='bottom' if pnl >= 0 else 'top', fontsize=10, fontweight='bold')

# Subplot 4: Trade Count by Sentiment
ax4 = axes[1, 1]
trade_counts = [len(merged[merged['classification'] == sent]) for sent in sentiment_order]
bars = ax4.bar(range(len(sentiment_order)), trade_counts, color=colors, edgecolor='black', linewidth=1.5)
ax4.set_xticks(range(len(sentiment_order)))
ax4.set_xticklabels(sentiment_order, rotation=45, ha='right')
ax4.set_title('Trading Activity by Sentiment', fontsize=12, fontweight='bold')
ax4.set_ylabel('Number of Trades', fontsize=11)
ax4.grid(True, alpha=0.3, axis='y')
for bar, tc in zip(bars, trade_counts):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(tc):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/01_sentiment_performance.png', dpi=300, bbox_inches='tight')
print("✓ Saved: outputs/01_sentiment_performance.png")
plt.close()

# FIGURE 2: Buy vs Sell Analysis
if 'is_buy' in merged.columns and merged['is_buy'].notna().any():
    print("Creating Figure 2: Buy vs Sell Analysis...")
    fig, ax = plt.subplots(figsize=(14, 7))
    
    buy_avg_pnls = [merged[(merged['classification'] == sent) & (merged['is_buy'] == 1)][pnl_col].mean() 
                    for sent in sentiment_order]
    sell_avg_pnls = [merged[(merged['classification'] == sent) & (merged['is_buy'] == 0)][pnl_col].mean() 
                     for sent in sentiment_order]
    
    x = np.arange(len(sentiment_order))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, buy_avg_pnls, width, label='BUY', color='lightblue', edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, sell_avg_pnls, width, label='SELL', color='lightcoral', edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Sentiment Classification', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average PnL ($)', fontsize=12, fontweight='bold')
    ax.set_title('Buy vs Sell Performance by Sentiment', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(sentiment_order, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.2f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('outputs/02_buy_sell_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: outputs/02_buy_sell_analysis.png")
    plt.close()

# FIGURE 3: Time Series Analysis
print("Creating Figure 3: Time Series Analysis...")
fig, axes = plt.subplots(2, 1, figsize=(16, 10))

# Daily cumulative PnL
daily_pnl = merged.groupby('date')[pnl_col].sum().cumsum()
axes[0].plot(daily_pnl.index, daily_pnl.values, linewidth=2, color='navy', marker='o', markersize=2, alpha=0.7)
axes[0].fill_between(daily_pnl.index, daily_pnl.values, alpha=0.3, color='navy')
axes[0].set_title('Cumulative PnL Over Time', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Cumulative PnL ($)', fontsize=11)
axes[0].axhline(y=0, color='red', linestyle='--', linewidth=1)
axes[0].grid(True, alpha=0.3)

# Daily sentiment value
daily_sentiment = merged.groupby('date')['value'].mean()
axes[1].plot(daily_sentiment.index, daily_sentiment.values, linewidth=2, color='orange', marker='o', markersize=2)
axes[1].fill_between(daily_sentiment.index, daily_sentiment.values, alpha=0.3, color='orange')
axes[1].set_title('Fear & Greed Index Over Time', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Index Value (0-100)', fontsize=11)
axes[1].set_xlabel('Date', fontsize=11)
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim([0, 100])

# Add sentiment zones
axes[1].axhspan(0, 25, alpha=0.1, color='red', label='Extreme Fear')
axes[1].axhspan(25, 45, alpha=0.1, color='orange', label='Fear')
axes[1].axhspan(45, 55, alpha=0.1, color='yellow', label='Neutral')
axes[1].axhspan(55, 75, alpha=0.1, color='lightgreen', label='Greed')
axes[1].axhspan(75, 100, alpha=0.1, color='green', label='Extreme Greed')

plt.tight_layout()
plt.savefig('outputs/03_time_series_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: outputs/03_time_series_analysis.png")
plt.close()

# FIGURE 4: Correlation Heatmap
print("Creating Figure 4: Correlation Heatmap...")
fig, ax = plt.subplots(figsize=(10, 8))

correlation_data = merged[[pnl_col, 'sentiment_numeric', 'profitable']].corr()
sns.heatmap(correlation_data, annot=True, fmt='.3f', cmap='coolwarm', center=0, 
            square=True, ax=ax, cbar_kws={'label': 'Correlation'}, linewidths=2)
ax.set_title('Correlation: Sentiment, PnL, and Profitability', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/04_correlation_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ Saved: outputs/04_correlation_heatmap.png")
plt.close()

print("\n" + "="*100)
print("✓ ANALYSIS COMPLETE!")
print("="*100)
print("\nGenerated Files:")
print("  - outputs/01_sentiment_performance.png")
print("  - outputs/02_buy_sell_analysis.png")
print("  - outputs/03_time_series_analysis.png")
print("  - outputs/04_correlation_heatmap.png")
print("  - outputs/daily_statistics.csv")
print("  - outputs/merged_data.csv")

print("\n" + "="*100)
print("NEXT STEPS:")
print("="*100)
print("\n1. Review the generated PNG files to understand the patterns")
print("2. Extract key findings from the numbers printed above")
print("3. Create ANALYSIS_REPORT.md with your findings")
print("4. Create GitHub repository")
print("5. Submit email with GitHub link and resume")
print("\n" + "="*100 + "\n")
