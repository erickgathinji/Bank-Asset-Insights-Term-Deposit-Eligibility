# Bank Asset Insights: Term Deposit Eligibility

## 1. Project Overview
This project addresses a **high-stakes Binary Classification problem** by predicting whether a client will subscribe to a bank term deposit following a direct marketing campaign. By identifying high-propensity customer profiles, financial institutions can move away from generalized mass marketing toward **data-driven precision**, optimizing resource allocation and reducing call fatigue.

### Strategic Business Value
*   **Precision Marketing**: Targets high-potential individuals, reducing operational overhead and preventing customer burnout.
*   **Liquidity Management**: Predictable growth in term deposits provides stable capital for long-term credit products like mortgages and SME loans.
*   **Competitive Differentiation**: Leverages predictive analytics to deliver the right product at the optimal time in a highly competitive savings environment.

## 2. Dataset Description
The model is trained on a comprehensive dataset from a Portuguese banking institution (UCI Machine Learning Repository).


| Dimension | Features | Strategic Insight |
| :--- | :--- | :--- |
| **Demographics** | age, job, marital, education | Defines customer segment and life-stage stability. |
| **Financial Health** | balance, default, housing, loan | Indicates disposable income and existing debt obligations. |
| **Current Campaign** | contact, day, month, duration, campaign | Captures the "how" and "when" of the marketing effort. |
| **Historical Context** | pdays, previous, poutcome | Leverages past behavior to predict future receptivity. |

**Target Variable (`y`)**: Whether the client subscribed to a term deposit (binary: "yes", "no").

## 3. Modeling and Performance
Several machine learning algorithms were evaluated, with **Ridge Regression** emerging as the top predictor.

*   **Top Model**: Ridge Regression (Kaggle Score/ROC AUC: **0.94654**).
*   **Other Models Evaluated**:
    *   XGBoost Classifier (0.90688).
    *   Random Forest Classifier (0.89447).
    *   Logistic Regression (0.8815).
    *   K-Neighbors Classifier (0.87578).

A hybrid resampling strategy was implemented to handle the significant **class imbalance** (where only 12% of customers typically subscribe).

## 4. Web Application Features
The project includes a functional **Streamlit application** for real-time decision-making.

*   **Single Profile Prediction**: A 6-step interactive questionnaire to analyze individual customer propensity.
*   **Bulk Analysis (Batch Mode)**: Allows stakeholders to upload a CSV and process up to **1,000 profiles** simultaneously.
*   **Instant Propensity Scores**: Provides immediate eligibility scores to drive real-time banking operations.
*   **Fallback Defaults**: Handles "unsure" inputs by utilizing training data means and modes (e.g., average age of 41, management job) to ensure continuous prediction.

## 5. Repository Structure
*   `analysis.ipynb`: Full exploratory data analysis (EDA), feature engineering, and model training workflow.
*   `bank_web_app/bank_app.py`: Main Streamlit application interface and navigation logic.
*   `bank_web_app/bank_app_logic.py`: Backend logic for feature engineering (e.g., payday proximity, engagement momentum) and model inference.
*   `bank_web_app/render_css.py`: Custom CSS styling for a professional "Precision Banking" UI theme.
*   `data/`: Contains `train.csv` and `test.csv` used for model development.

## 6. How to Use
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/erickgathinji/Bank-Asset-Insights-Term-Deposit-Eligibility.git
    ```
2.  **Install Dependencies**
3.  **Run the App**:
    ```bash
    streamlit run bank_web_app/bank_app.py
    ```

***
**Note**: The live web application may sleep when inactive; it typically takes 30–60 seconds to wake up and load the model.

[Live Web App](https://term-deposit-eligibility.streamlit.app/)
