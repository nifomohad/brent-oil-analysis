# Task 1: Laying the Foundation for Analysis

## Planned Analysis Document (1-2 Pages Equivalent)

**Project Title:** Bayesian Change Point Analysis of Brent Oil Prices and Association with Geopolitical/OPEC Events (1987–2022)

**Date:** February 07, 2026

## 1. Defining the Data Analysis Workflow

The workflow is structured for reproducibility and insight generation using the provided dataset (BrentOilPrices.csv, 9,011 daily observations from May 20, 1987, to November 14, 2022):

### **Data Loading and Preparation**

- Load the CSV.
- Parse `Date` column to datetime (handling formats like `dd-mmm-yy` and quoted `Month dd, yyyy`).
- Sort chronologically, index by date, and handle any missing values (none detected).

### **Exploratory Data Analysis (EDA)**

- Visualize price series (cycles, peaks ~$144 in 2008, lows ~$9 in 2020, 2022 spike).
- Compute and plot log returns for stationarity and volatility insights.

### **Event Research and Compilation**

Curate 15+ events aligned with visible shifts (e.g., 1990 invasion, 2008 crisis, 2014 glut, 2020 COVID, 2022 Ukraine invasion).

### **Time Series Property Investigation**

- Confirm non-stationary prices.
- Confirm stationary returns.
- Assess volatility clustering.

### **Bayesian Change Point Modeling (Core)**

- Use PyMC: single change point on prices (or log prices), recursive for multiples.
- MCMC sampling with convergence checks.

### **Interpretation and Event Association**

- Extract posterior change points.
- Overlay with events.
- Quantify mean shifts probabilistically.

### **Insight Generation and Validation**

- Highlight key impacts with uncertainty.
- Emphasize causality limitations.

### **Communication and Visualization**

- Interactive dashboard (Plotly/Streamlit).
- Report with visuals.

## 2. Structured Event Dataset

| Date       | Event Description                             | Category              | Observed Impact in Data             |
| ---------- | --------------------------------------------- | --------------------- | ----------------------------------- |
| 1990-08-02 | Iraqi invasion of Kuwait                      | Geopolitical conflict | Rapid spike from ~$18 to ~$40       |
| 2008-07-11 | Global Financial Crisis peak; demand collapse | Economic shock        | Peak ~$144, then crash to ~$40      |
| 2011-02-15 | Arab Spring/Libyan disruption                 | Geopolitical unrest   | Spike to ~$120                      |
| 2014-11-27 | OPEC no-cut decision amid shale glut          | OPEC policy           | Crash from ~$110 to ~$30 (2016 low) |
| 2016-11-30 | OPEC production cuts agreed                   | OPEC policy           | Recovery from lows                  |
| 2018-05-08 | US Iran sanctions reimposed                   | Sanctions             | Rise toward ~$80                    |
| 2019-09-14 | Drone attacks on Saudi Aramco                 | Geopolitical attack   | Temporary spike ~15–20%             |
| 2020-03-09 | OPEC+ talks collapse; price war + COVID shock | OPEC+/Pandemic        | Crash to ~$9 (April 2020)           |
| 2020-04-12 | Record OPEC+ cuts agreed                      | OPEC+ policy          | Floor + recovery                    |
| 2022-02-24 | Russia invades Ukraine; sanctions             | Geopolitical conflict | Spike to ~$130 (March 2022)         |

## 3. Assumptions and Limitations

### **Assumptions**

- Abrupt mean shifts capture primary event impacts.
- Short-lag event effects on prices.
- Data complete (9,011 rows, no missings post-parsing).

### **Limitations**

- Misses gradual trends or variance-only changes.
- Recursive single change points approximate multiples.
- No confounders (e.g., inventories, USD).

### **Correlation vs. Causation**

Change points show temporal alignment (correlation), but causation requires isolating effects—difficult in observational data with confounders.

## 4. Communication Channels

- **Primary:** Interactive dashboard for event/price exploration.
- **Secondary:** PDF report with visuals and quantified insights.
- **Tertiary:** Slides for policymakers; notebook for analysts.

## 5. Understanding the Model and Data

### **Review of Key References**

- PyMC Bayesian change point examples (switchpoint model).
- Hamilton on oil shocks; literature on regime shifts.

### **Analyze Time Series Properties (Based on Dataset)**

#### **Trend**

- Multi-decade cycles: low ~$18–20 (1987–2000), boom to $144 (2008 peak), busts (2014–2016 ~$30, 2020 $9.12), recovery/spike 2022 ~$130+.

#### **Stationarity**

- Prices non-stationary (ADF statistic -1.99, p=0.289 > 0.05).
- Log returns stationary (ADF statistic -16.43, p < 1e-28).

#### **Volatility Patterns**

- Clustering (std log returns 2.55%, extremes like -64% in 2020).
- High-volatility regimes during crises.

### **Modeling Implications**

- Non-stationary prices favor change point models on price levels.
- Stationary returns suitable for volatility modeling.

### **Explain Change Point Models**

Detect structural breaks (e.g., mean shifts from events). Bayesian approach uses priors (uniform on τ), MCMC for posteriors—quantifying uncertainty.

### **Expected Outputs and Limitations**

- Posterior of τ (break dates with uncertainty).
- Pre/post regime means.
- Visualizations of identified breaks.
- Limitations: abrupt shift assumption; single change point requires recursion.
