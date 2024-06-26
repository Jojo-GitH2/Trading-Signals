# Cloud-Native API for Risk Analysis of Trading Strategies

![Project Banner](./images/Cloud%20Platforms.png)

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
    - [Deploying Locally](#deploying-locally)
    - [Deploying on Google App Engine (GAE)](#deploying-on-google-app-engine-gae)
  - [Screenshots](#screenshots)
    - [Root Endpoint](#root-endpoint)
    - [Warmup Endpoint](#warmup-endpoint)
    - [Scale Ready Endpoint](#scale-ready-endpoint)
    - [Analyse Endpoint](#analyse-endpoint)
    - [Get Endpoints Endpoint](#get-endpoints-endpoint)
    - [Get Signals VaR (95% and 99%) Endpoint](#get-signals-var-95-and-99-endpoint)
    - [Get Average VaR (95% and 99%) Endpoint](#get-average-var-95-and-99-endpoint)
    - [Get Chart URL Endpoint](#get-chart-url-endpoint)
    - [Get Audit Endpoint](#get-audit-endpoint)
    - [Terminate Endpoint](#terminate-endpoint)
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
- `/get_sig_profit_loss`: Get each signals profit/loss values.
- `/get_tot_profit_loss`: Get total profit/loss.
- `/get_time_cost`: Get execution time and cost.
- `/warmup`: Initialize resources for parallel analysis.
- `/get_sig_vars9599`: Get each signals VaR values.

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

### Deploying Locally

1. **Clone the Repository**:

   ```bash
   git clone git@github.com:Jojo-GitH2/Trading-Signals.git
   cd Trading-Signals
   ```

2. **Set Up Virtual Environment (Optional)**:

   1. On Linux/macOS:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   2. On Windows:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   python main.py
   ```

5. **Access the API**:
   Open your web browser and navigate to `http://localhost:8080`.

### Deploying on Google App Engine (GAE)

1.  **Create a GAE Project**:

    - Set up a new project on Google Cloud Console.
    - Enable the App Engine API.

2.  **Configure `app.yaml`**:

    - Customize the `app.yaml` file to match your project settings.
    - Specify the runtime, handlers, and other configuration options.

3.  **Enable Secret Manager API**:

    - Access the Secret Manager API from the Google Cloud Console.
    - Select your project and enable the API.
    - Deploy AWS Credentials to Secret Manager.

      > **Note**: The AWS credentials are stored in the ~/.aws/credentials file. You can deploy them to Secret Manager using the following command:

      ```bash
      gcloud secrets create aws-credentials --data-file=~/.aws/credentials
      ```

    - Check the main.py file for information about this command.

4.  **Grant Permissions**:

    - Grant the necessary permissions to the App Engine service account.
    - Add the Secret Manager Admin role to the App Engine service account.
    - Enable the Cloud Build API.

5.  **Deploy to GAE**:

    ```bash
    gcloud app deploy
    ```

6.  **Access the Deployed API**:
    Visit the URL provided after successful deployment.

## Screenshots

### Root Endpoint

![Root Endpoint](./images/root.png)

### Warmup Endpoint

![Warmup Endpoint](./images/warmup.png)
**Provisioned EC2 instances and DynamoDB Table**
![Provisioned EC2 instances](./images/provisioned_instances.png)
![Provisioned DynamoDB Table](./images/dynamodb.png)

### Scale Ready Endpoint

![Scale Ready Endpoint](./images/scaled_ready.png)

### Analyse Endpoint

![Analyse Endpoint](./images/analyse.png)

### Get Endpoints Endpoint

![Get Endpoints Endpoint](./images/get_endpoints.png)
**Checking out a single endpoint**
![Get Endpoints Endpoint](./images/single_endpoint_1.png)
![Get Endpoints Endpoint](./images/single_endpoint_2.png)

> **Note**: The other endpoints can be accessed in a similar manner. Each ec2 instance produces a risk values at 95% and 99% confidence levels, profit and loss values, and a execution time.

### Get Signals VaR (95% and 99%) Endpoint

![Get Signals VaR Endpoint](./images/get_signal_vars.png)

### Get Average VaR (95% and 99%) Endpoint

![Get Average VaR Endpoint](./images/get_avg_vars.png)

> **Note**: The average VaR values are calculated by taking the average of the VaR values produced by each ec2 instance. The same applies to the profit and loss values.

### Get Chart URL Endpoint

![Get Chart URL Endpoint](./images/get_chart_url.png)
**Chart**
![Get Chart URL Endpoint](./images/chart.png)

### Get Audit Endpoint

![Get Audit Endpoint](./images/get_audit.png)

### Terminate Endpoint

![Terminate Endpoint](./images/terminate.png)
**Terminating EC2 instances**
![Terminate Endpoint](./images/terminate_2.png)

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
