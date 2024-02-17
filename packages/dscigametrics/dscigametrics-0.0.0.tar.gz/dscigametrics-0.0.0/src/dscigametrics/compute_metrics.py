
import pandas as pd

def compute_metrics(data, campaign_id, start_date, end_date):
    """Computes the key metrics.

    Computes four metrics from Google Analytics data: 
        1. Ratio of new to returning visitors: measures the ratio of new users to returning users
           of each campaign in certain period.
        2. Conversion rate: measures the percentage of users who complete a specific desired action 
           of each campaign in certain period.
        3. Total transaction revenue: measures total transaction revenue of each campaign in certain period.
        4. Average transaction revenue: measures average transaction revenue of each campaign in certain period.

    Parameters
    ----------
    data : pandas dataframe
        dataframe containing information from google analytics
    campaign_id : int
        The campaign ID of the campaign in question
    start_date : int
        Date when campaign started
    end_date : int
        Date when campaign ended

    Returns
    -------
    dict
        A dictionary containing the four computed metrics

    Example
    -------
    >>> compute_metrics(df, 11111111, 20230101, 20231231)
        "New to return rate: 1.3
        Conversion rate: 0.23
        Total transaction revenue: $100
        Average transaction revenue: $2.33"
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError('Your data argument must be a pandas dataframe')
    if not isinstance(campaign_id, int):
        raise TypeError('The campaign ID should be an integer')
    if not isinstance(start_date, int):
        raise TypeError('Dates are entered as integers. 1st August, 2022 should be 20220801')
    if not isinstance(end_date, int):
        raise TypeError('Dates are entered as integers. 1st August, 2022 should be 20220801')
    
    df_filter_campaign = data.loc[(data['trafficSource.adwordsClickInfo.campaignId']==campaign_id)]
    df_filter_start = df_filter_campaign.loc[(df_filter_campaign['date'] >= start_date)]
    df_filtered = df_filter_start.loc[(df_filter_start['date'] <= end_date)]

    if df_filtered.shape[0] < 1:
        raise ValueError('There is no data matching your query')
    
    def total_transaction_revenue(df):

        revenue = df['totals.transactionRevenue'].sum()

        return revenue

    def average_transaction_revenue(df):
        
        
        mean_revenue = df['totals.transactionRevenue'].mean()

        return mean_revenue

    def new_to_return(df):

        visits_count = df['totals.newVisits'].shape[0]
        new_count = df['totals.newVisits'].sum()
        rate = new_count / visits_count

        return rate

    def conversion_rate(df):

        transaction_count = df['totals.transactions'].shape[0]
        conversion = df['totals.transactions'].sum()
        conversion_rate = conversion / transaction_count

        return conversion_rate

    conversion_rate = conversion_rate(df_filtered)
    new_to_return = new_to_return(df_filtered)
    average_transaction_revenue = average_transaction_revenue(df_filtered)
    total_transaction_revenue = total_transaction_revenue(df_filtered)
    metric_dict = {'conversion rate': conversion_rate,
                'new to return rate': new_to_return,
                'total transaction revenue': total_transaction_revenue,
                'average transaction revenue': average_transaction_revenue}

    print(f'conversion rate: {conversion_rate} \nnew to return rate: {new_to_return} \ntotal transaction revenue: ${total_transaction_revenue} \naverage transaction revenue: ${average_transaction_revenue}')

    return metric_dict
