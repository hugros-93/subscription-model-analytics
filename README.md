# subscription-model-analytics
A dashboard to help you analyse subscription product data.

![screenshot](assets/screenshot.png)

### Dashboard overview

#### Load data
Using the `Load data` button, upload a csv filw with the following columns:
- `user_id`: the unique ID of a customer
- `subscription_id`: the unique ID of a subscription
- `start_date`: the start date of the subscription (format `YYYY-MM-DD`)
- `end_date`: the end date of the subscription (format `YYYY-MM-DD`, empty if the subscription is currently active)

#### KPIs
This section will show big picture indicators about currently active, new and churn users.

#### Growth
In this section, we will show the evolution of net number of active users over time, as well as the growth accounting (new, resurrected and churn).  

#### Retention
This section will show the number of active users over time split by cohort (based on the start date), as well as retention heatmaps.

#### Churn
Here we will focus on churn, with total number of churn by time period and churn as a percentage of active users at the end of previous period.

#### Data
This section will allow you to navigate into the input data. 

### Setup
To run the dashboard locally, follow the steps bellow:
1. Clone the repo
2. Open command line in the root folder
3. Create a virtual env: `python -m venv venv`
4. With virtual env activated, install requirements: `pip install -r requirements.txt` 
5. In the root folder, start the app: `python app.py`


## Project structure
- `app.py`: The app to run the dashboard.
- `pages/`: The different pages of the app.
- `utils/`: Some utility functions for the model, dash or to generate synthetic data.
- `data/`: Where the input data is stored once uploaded.
- `figures/`: Where charts figures are exported after data upload. When you re-run the app, the charts will be re-loaded from here, saving some computation time.
- `assets/`: The folder for app custom `.css`, plotly template, logos...