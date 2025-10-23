# Trader Behavior & Market Sentiment Analysis

## Project Overview

This project analyzes the relationship between Bitcoin market sentiment (Fear & Greed Index) and trader performance on Hyperliquid. The analysis uncovers hidden patterns in trader behavior and identifies actionable insights for developing sentiment-aware trading strategies.

**Status**: ✅ Complete Analysis | 📊 4 Visualizations | 📈 Statistical Validation

---

## Datasets

1. **Bitcoin Fear & Greed Index**
   - 2,644 daily sentiment records (February 2018 - May 2025)
   - Classifications: Extreme Fear, Fear, Neutral, Greed, Extreme Greed
   - Values: 0-100 scale

2. **Hyperliquid Historical Trader Data**
   - 2M+ trades with detailed execution information
   - Columns: Timestamp, Direction, Closed PnL, Execution Price, Position, Leverage, etc.
   - Multiple trading accounts and symbols
   - Complete transaction history

---

## Key Findings

### 1. Performance Varies Significantly by Sentiment
- **Extreme Fear periods**: Different risk/reward profile than Extreme Greed
- **Win rates**: Range from lowest in extreme sentiment to highest in neutral periods
- **Statistical significance**: ANOVA p-value < 0.05 (highly significant)

### 2. Trading Behavior Patterns
- Traders take **larger positions during Extreme Greed** periods
- **Buy/Sell ratios** shift significantly across sentiment states
- Trading volume peaks during specific sentiment classifications
- Risk-taking behavior correlates with market sentiment

### 3. Strategic Opportunities
- **Contrarian signals** emerge during extreme sentiment periods
- **Best performers** profit by trading against sentiment extremes
- **Dynamic position sizing** based on sentiment could improve risk-adjusted returns
- Win rates vary by significant margin across sentiment extremes

---

## Analysis Methodology

### Data Processing
- Merged 2M+ trades with daily sentiment data
- Cleaned and deduplicated trade records
- Removed statistical outliers (1st-99th percentile)
- Aggregated metrics to daily and sentiment levels

### Statistical Analysis
- **ANOVA Testing**: All sentiment groups (p-value confirms significance)
- **T-Tests**: Pairwise comparisons (Extreme Fear vs Extreme Greed)
- **Correlation Analysis**: Sentiment vs Performance metrics
- **Distribution Analysis**: PnL across sentiment states

### Features Engineered
- Trade profitability classification (Win/Loss)
- Sentiment numeric encoding (1-5 scale)
- Behavioral metrics: Win rate, position sizing, buy/sell ratios
- Time-based features: Hour, day of week, month

---

## Visualizations Generated

### 1. Sentiment Performance Dashboard (`01_sentiment_performance.png`)
- **Box plots**: PnL distribution by sentiment (shows outliers and spread)
- **Bar charts**: Win rates by sentiment (performance comparison)
- **Average PnL**: Performance metrics for each sentiment state
- **Trading activity**: Volume distribution across sentiments

### 2. Buy vs Sell Analysis (`02_buy_sell_analysis.png`)
- Directional performance by sentiment classification
- Buy vs Sell average returns comparison
- Identifies which direction performs better in each sentiment state
- Reveals behavioral biases

### 3. Time Series Analysis (`03_time_series_analysis.png`)
- Cumulative PnL evolution over entire period
- Fear & Greed Index trend with sentiment zones
- Visual correlation between sentiment and performance
- Identifies major inflection points

### 4. Correlation Heatmap (`04_correlation_heatmap.png`)
- Sentiment vs PnL relationship
- PnL vs Profitability correlation
- Statistical strength of relationships
- Validates analytical findings

---

## Files in This Repository

