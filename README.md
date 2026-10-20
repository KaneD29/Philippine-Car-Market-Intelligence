# Philippine Used Car Market Analytics Pipeline & Dashboard

An end-to-end data pipeline and analytics platform designed to scrape, clean, detect deceptive pricing, analyze market trends, and report on used vehicle valuations across the Philippine automotive marketplace.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Project Architecture & File Structure](#project-architecture--file-structure)
3. [Technology Stack & Dependencies](#technology-stack--dependencies)
4. [Installation & Setup](#installation--setup)
5. [How to Run the Pipeline](#how-to-run-the-pipeline)
6. [Data Engineering & Dashboard Logic](#data-engineering--dashboard-logic)
7. [AI Usage Template](#ai-usage-template)
8. [License](#license)

---

## Project Overview

The Philippine online used car marketplace frequently suffers from low-ball "All-In Downpayment / Promo" listings that mask full vehicle prices, skewing market averages and complicating valuation analysis. 

This repository provides:
- A multi-tiered Python scraper and market analysis engine that filters out low-ball promotional listings using dynamic quantile clustering and category price floor matrices.
- An automated bargain-hunting module that flags verified full-price listings significantly below true market average.
- An executive-grade Power BI report interface to track inventory trends, payment listing distributions, and high-value deal opportunities.

---

## Project Architecture & File Structure

```
Philippine-Car-Market-Intelligence/
|-- dashboard/
|   `-- Philkotse Scraped Data Dashboard.pbix   # Power BI report interface
|-- data/
|   |-- car_models.json                         # Single Source of Truth (SSOT) target taxonomy
|   |-- master_philippine_cars.csv              # Processed dataset with price_type and flags
|   `-- top_deals.csv                           # Filtered bargain listings output
|-- src/
|   |-- deal_finder.py                          # Automated bargain isolation module
|   |-- main.py                                 # Pipeline execution and runtime profiler
|   |-- scraper.py                              # Rate-limited WAF-compliant HTTP scraper
|   `-- utils.py                                # Data processing, clustering & median math
|-- .gitignore                                  # Git ignore rules
|-- LICENSE                                     # License agreement
`-- README.md                                   # Project documentation
```

---

## Technology Stack & Dependencies

### Core Languages & Execution
- Python 3.9+
- Power Query M & DAX (Power BI Desktop)

### Python Libraries
- `pandas` - Data manipulation and statistical analysis
- `numpy` - Vectorized quantile calculation and array operations
- `requests` - Network HTTP interaction
- `beautifulsoup4` - HTML DOM parsing
- `json` - SSOT model config management

---

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/ph-used-car-analytics.git
   cd ph-used-car-analytics
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run the Pipeline

### 1. Execute Python Data Pipeline
Run the orchestrator script to fetch, clean, and process marketplace data:

```bash
python src/main.py
```

Pipeline steps executed automatically:
1. Scraping targeted makes/models using standard rate delays (~15 RPM).
2. Categorization using the 4-Tier explicit price matrix in `car_models.json`.
3. Outlier filtration (60% to 150% group median filtering).
4. Generating output files `cleaned_market_data.csv` and `top_deals.csv`.

### 2. Load Power BI Dashboard
1. Open Power BI Desktop.
2. Open `reports/Market_Analytics.pbix` or import `data/top_deals.csv` into a new report.
3. Refresh data connections to pull the latest generated CSV files.

---

## Data Engineering & Dashboard Logic

### Price Type Tagging Matrix
To strip away misleading downpayment listings:
- **Tier 1 (Luxury / Premium):** 2020+ Floor = PHP 1,200,000
- **Tier 2 (Mid/Full SUVs, Pickups):** 2022+ Floor = PHP 850,000
- **Tier 3 (MPVs, Compact Crossovers):** 2022+ Floor = PHP 600,000
- **Tier 4 (Economy Sedans):** 2022+ Floor = PHP 400,000

### Dynamic Quantile Filtering
For custom pools without hardcoded category rules, dynamic filtering utilizes the 75th percentile ($P_{75}$) of prices per model-year cluster:
$$\text{Price Floor} = 0.45 \times P_{75}$$

### Derived Market Median Metric (Power Query M / DAX)
Reconstructs baseline market price from relative variance flags:

**Power Query M:**
```powerquery
[price] / (1 + [market_avg_comparison])
```

**DAX Measure:**
```dax
Market Median Price = 
DIVIDE(
    'top_deals'[price],
    1 + 'top_deals'[market_avg_comparison],
    'top_deals'[price]
)
```

---

## AI Usage Template

> **Note for Collaborators:** Edit this section to detail how generative AI tools were integrated into the development lifecycle of this project.

### AI Assistance Declaration

Gemini was utilized strictly as a secondary coding assistant for syntax verification, DAX/M formatting, and generating markdown templates. All project architecture, data cleaning rules, price floor thresholds, and analytical logic were independently designed, implemented, and verified by Aaron Kane Dungca.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Author:** Aaron Kane Dungca  
**Project Link:** [https://github.com/KaneD29/Philippine-Car-Market-Intelligence](https://github.com/KaneD29/Philippine-Car-Market-Intelligence)