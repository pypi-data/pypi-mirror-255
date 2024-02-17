import pandas as pd
import numpy as np

def stat_summary(data, campaign_id, start_date, end_date):
    """Return statistics summary of metrics.
    
    Return a pandas dataframe presenting the statistics summary of the four metric, where the metrics are:
            1. New to return rate
            2. Conversion rate
            3. Total transaction revenue
            4. Average transaction revenue

    Parameters
    ----------
    data : dataframe
        Dataframe containing information from google analytics.
    campaign_id : int
        The unique id of the campaign.
    start_date : int
        The campaign start date.
    end_date : int
        The campaign end date.
    
    Returns
    -------
    summary_table : pd.DataFrame
        A pandas dataframe contains the mean, median and standard deviation of the four metrics of each day.
        Four metrics:
            1. New to return rate
            2. Conversion rate
            3. Total transaction revenue
            4. Average transaction revenue 
    
    Example
    -------
    >>> summary = stat_summary(data, 11111111, 20170817, 20170820)
    >>> print(summary)
                    return   conversion   ttl_revenue   avg_revenue
        Mean         0.01        0.05         250           100
        Median       0.02        0.04         238           120
        SD           1.43        0.66         1.62          0.77
    """

    # declare functions which calculate return and conversion rates and to use in the "groupby -> aggregate" later.
    def get_return_rate(data):
        return data['totals.newVisits'].fillna(0.0).mean()
    def get_conversion(data):
        if sum(data['totals.visits'] != 0):
            return sum(data['totals.transactions'].fillna(0.0)) / sum(data['totals.visits'])
        else:
            return 0
    
    # Check the input type to prevent incorrect inputs
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input data type should be pandas.DataFrame")
    
    # Filter data according to the specified condition: dates and campaign_id.
    data = data[(data['trafficSource.adwordsClickInfo.campaignId'] == campaign_id) & (data['date'] >= start_date) & (data['date'] <= end_date)]

    return_rates = data.groupby(['date'])[['date', 'totals.newVisits']].apply(get_return_rate).reset_index()[0]
    conversion_rates = data.groupby(['date'])[['date', 'totals.transactions', 'totals.visits']].apply(get_conversion).reset_index()[0]
    ttl_transac_revenues = data.fillna(0.0).groupby(['date'])['totals.transactionRevenue'].sum().reset_index().iloc[:, 1]
    avg_transac_revenues = data.fillna(0.0).groupby(['date'])['totals.transactionRevenue'].mean().reset_index().iloc[:, 1]

    # Calculate the mean, median, and standard deviation of the aggregate values, 
    # and transform then into a pandas dataframe as the final output.
    output = pd.DataFrame(
                {
                    'return_rate': [return_rates.mean(), return_rates.median(), np.std(return_rates)],
                    'conversion_rate': [conversion_rates.mean(), conversion_rates.median(), np.std(conversion_rates, ddof=1)],
                    'ttl_revenue': [ttl_transac_revenues.mean(), ttl_transac_revenues.median(), np.std(ttl_transac_revenues, ddof=1)],
                    'avg_revenue': [avg_transac_revenues.mean(), avg_transac_revenues.median(), np.std(avg_transac_revenues, ddof=1)]
                },
                index = ['Mean', 'Median', 'Standard Deviation']
            )
    return output
