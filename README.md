# Cloud-Native API for Risk Analysis of Trading Strategies

![Project Banner](insert_link_here)

This project demonstrates the construction of a cloud-native API using multiple services across cloud providers. The API supports user-specifiable scaling and provides risk analysis for trading strategies. By combining specific trading signals with a Monte Carlo method, we calculate risk values and profitability metrics.

## Table of Contents

- [Cloud-Native API for Risk Analysis of Trading Strategies](#cloud-native-api-for-risk-analysis-of-trading-strategies)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Problem Statement](#problem-statement)
  - [Requirements](#requirements)
    - [Cloud Services](#cloud-services)
    - [API Design](#api-design)
    - [Initialization](#initialization)
    - [Risk Analysis](#risk-analysis)
    - [Output](#output)
    - [Audit Information](#audit-information)
  - [Getting Started](#getting-started)
  - [Endpoints](#endpoints)
  - [Directory Structure](#directory-structure)
  - [Usage](#usage)
  - [Screenshots (if applicable)](#screenshots-if-applicable)
  - [License](#license)

## Overview

Our goal is to build an API that allows users to analyze the risks and profitability of trading strategies. Users can input historical price data, trading decisions (buy or sell), and the desired time horizon for profit calculation. The API will generate risk values and provide insights into potential gains or losses.

## Problem Statement

Trading strategies require thorough risk analysis. Our API aims to address the following challenges:

1. **Risk Calculation**: Calculate 95% and 99% VaR (Value at Risk) values based on historical data.
2. **Profit/Loss Simulation**: Simulate profit or loss based on trading decisions.
3. **Scalability**: Implement scalable services for parallel analysis.
4. **Audit Information**: Maintain an audit log with execution time, costs, and other relevant data.

## Requirements

### Cloud Services

- **Google App Engine (GAE)**: Manages the API and collects average simulated risk values.
- **AWS Lambda**: Mediates communication between GAE and other AWS services.
- **Elastic Compute Cloud (EC2)**: For parallel analysis.

### API Design

- Offers a persistent API for user interaction.
- Scalable services generate simulated risk values.

### Initialization

- Users specify the scale-out factor (`r`) for parallel analysis.
- Implement a "warm-up" process for all scalable services.
- Provide endpoints for readiness checks, warm-up time, and cost estimation.

### Risk Analysis

- Input parameters:
  - `h`: Length of price history for mean and standard deviation calculation.
  - `d`: Number of data points for risk calculation.
  - `t`: Buy or sell (for separate analysis).
  - `p`: Number of days to check price difference for profit or loss.
- Calculate 95% and 99% VaR values.
- Simulate profit or loss based on trading decisions.

### Output

- Risk values per signal and average risk over signals.
- Profit/loss values related to each signal.
- Chart showing risk values.

### Audit Information

- Maintain an audit log with selections of parameters, total profit/loss, execution time, and costs.

## Getting Started

1. Clone this repository.
2. Set up your GAE project and AWS credentials.
3. Implement the API endpoints and risk analysis logic.
4. Deploy the API and monitor performance.

## Endpoints

- `/scaled_ready`: Check if scalable resources are ready.
- `/get_warmup_cost`: Estimate warm-up costs.
- `/get_endpoints`: Retrieve endpoints for direct testing.
- `/analyse`: Perform risk analysis (POST request).
- `/get_chart_url`: Generate a chart URL for risk values.
- `/get_audit`: View audit information.
- `/reset`: Reset resources.
- `/terminate`: Terminate resources.
- `/scaled_terminated`: Check if instances have been terminated.
- `/get_avg_vars9599`: Get average VaR values.
- `/get_sig_profit_loss`: Get significant profit/loss values.
- `/get_tot_profit_loss`: Get total profit/loss.
- `/get_time_cost`: Get execution time and cost.
- `/warmup`: Initialize resources for parallel analysis.
- `/get_sig_vars9599`: Get significant VaR values.

## Directory Structure

```bash
README.md
app.yaml # Google App Engine configuration
helper.py # Utility functions
lambda # AWS Lambda functions (reset.py & risk_analysis.py)
   |-- reset.py
   |-- risk_analysis.py
main.py # API endpoints and risk analysis logic
requirements.txt # Required packages
risk_analysis.py # Risk analysis logic - This was not used in the final implementation but was rather used to test the risk analysis logic, after which it was included in the user_data.sh script
static # Static files (css/style.css)
   |-- css
   |   |-- style.css
templates # HTML templates (index.html)
   |-- index.html
test.py # Original risk analysis logic using DataFrames
user_data.sh # User data script for EC2 instances
```

## Usage

1. Customize the API endpoints and risk analysis logic.
2. Deploy the API to GAE and set up AWS Lambda.
3. Monitor performance and adjust scaling as needed.

## Screenshots (if applicable)

Include relevant screenshots here.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
