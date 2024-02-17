import pandas as pd
import altair as alt

def daily_plot(data, campaign_id, start_date, end_date, width=600, height=300):
    """Creating time-series chart

    Returns a time-series chart that visualises daily performance of a campaign
    in a period.

    Parameters
    ----------
    data : dataframe
        Dataframe containing information from google analytics
    campaign_id : int
        The unique id of the campaign.
     start_date : int
        The campaign start date.
    end_date : int
        The campaign end date.
    width : int, optional
        The width of the chart. Default is 400.
    height : int, optional
        The height of the chart. Default is 400.
        
    Returns
    -------
    altair.vegalite.v4.api.Chart
        An Altair Chart object representing the time-series plot.
            Four metrics:
                1. New to return rate
                2. Conversion rate
                3. Total transaction revenue
                4. Average transaction revenue 

    Examples
    --------
    >>> daily_plot(df, 452349492, 20220401, 20220430)
    """

    # Check Input Type
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input should be a pandas DataFrame.")
    if not isinstance(campaign_id, int):
        raise TypeError("Input should be integer.")
    if not isinstance(start_date, int):
        raise TypeError("Input should be integer.")
    if not isinstance(end_date, int):
        raise TypeError("Input should be integer.")
    if not isinstance(width, int):
        raise TypeError("Input should be integer.")
    if not isinstance(height, int):
        raise TypeError("Input should be integer.")
    
    # Check if width and height are positive
    if width < 0 or height < 0:
        raise ValueError("Width and height must be positive.")
    
    # Create functions to apply to each date
    def get_return_rate(data):
        return data['totals.newVisits'].fillna(0.0).mean()
    def get_conversion(data):
        return sum(data['totals.transactions'].fillna(0.0)) / sum(data['totals.visits'])
    
    # Select data based on imputs of Campaign Id, Start Date and End Date.
    data = data[(data['trafficSource.adwordsClickInfo.campaignId'] == campaign_id) & (data['date'] >= start_date) & (data['date'] <= end_date)]

    # Calculate four metrics for each date
    return_rates = data.groupby(['date'])[['date', 'totals.newVisits']].apply(get_return_rate).reset_index()
    conversion_rates = data.groupby(['date'])[['date', 'totals.transactions', 'totals.visits']].apply(get_conversion).reset_index()
    ttl_transac_revenues = data.fillna(0.0).groupby(['date'])['totals.transactionRevenue'].sum().reset_index()
    avg_transac_revenues = data.fillna(0.0).groupby(['date'])['totals.transactionRevenue'].mean().reset_index()

    # Merge four metrics into one dataframe 
    df = pd.merge(pd.merge(pd.merge(return_rates, conversion_rates, on='date'),ttl_transac_revenues, on='date'), avg_transac_revenues, on='date')
    df.columns = ['date', 'return_rates', 'conversion_rates', 'ttl_transac_revenues','avg_transac_revenues']

    # Convert date column from integer type to date type
    df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y%m%d')

    # Create time series plot
    base = alt.Chart().mark_line().encode(
    x='date',
    ).properties(
        width=width,
        height=height
    )

    return_rate_chart = base.encode(alt.Y('return_rates:Q').title('Return Rate')).properties(title='Return Rates by date')
    conversion_rates_chart = base.encode(alt.Y('conversion_rates:Q').title('Conversion Rate')).properties(title='Conversion Rates')
    ttl_transac_revenues_chart = base.encode(alt.Y('ttl_transac_revenues:Q').title('Total Transaction Revenue')).properties(title='Total Transaction Revenue by date(CAD)')
    avg_transac_revenues_chart = base.encode(alt.Y('avg_transac_revenues:Q').title('Average Transaction Revenue')).properties(title='Average Transaction Revenue by date(CAD)')

    combined_charts = alt.vconcat(return_rate_chart, conversion_rates_chart, ttl_transac_revenues_chart, avg_transac_revenues_chart, data=df)
    
    return combined_charts