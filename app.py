import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pytrends.request import TrendReq
import time
from pytrends.exceptions import TooManyRequestsError

# Create a dictionary mapping state names to geo codes
state_geo_codes = {
    'Maharashtra': 'IN-MH',
    'Delhi': 'IN-DL',
    'Karnataka': 'IN-KA',
    'Gujarat': 'IN-GJ',
    'Tamil Nadu': 'IN-TN',
    'West Bengal': 'IN-WB',
    'Uttar Pradesh': 'IN-UP',
    'Rajasthan': 'IN-RJ',
    # Add more states as needed
}
st.set_page_config(
    page_title="InsightZ |",
    page_icon="📈",
    layout='wide'
)

top_df= pd.read_csv('D:/nekostreamlit/dress-top.csv').head(5)


def fetch_interest_over_time(pytrends):
    for i in range(5):  # Retry up to 5 times
        try:
            return pytrends.interest_over_time()
        except TooManyRequestsError:
            wait_time = 2 ** i  # Exponential backoff
            st.warning(f"fetching results...")
            time.sleep(wait_time)  # Wait before retrying
    st.error("Failed to fetch data after multiple attempts.")
    return None

# Streamlit application
st.title('InsightZ trend analysis')

# Sidebar for input
st.sidebar.header('Input Parameters')
state_name = st.sidebar.selectbox('Select a State', list(state_geo_codes.keys()))
mens_wear_input = st.sidebar.text_input("Enter the brands available (comma-separated, e.g., Shirt, Jeans, Jacket):")
keywords = st.sidebar.text_input("Enter Topic")
    

if st.sidebar.button('Analyze'):
    geo_code = state_geo_codes.get(state_name)
    pytrends = TrendReq(hl='en-US', tz=360)
    suggestions=pytrends.suggestions(keyword=keywords)
    topic_df = pd.DataFrame(suggestions)
    final_df= topic_df.drop(columns="mid").head(5)

    mens_wear_kw = [item.strip() for item in mens_wear_input.split(',')]

    # Function to plot search interest for the selected category
    def plot_trends(kw_list, geo_code):
        pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo=geo_code, gprop='')
        data = fetch_interest_over_time(pytrends)
        if data is None:
            return None

        if 'isPartial' in data.columns:
            data = data.drop(columns=['isPartial'])

        df = pd.DataFrame(data)
        top_2 = df.sum().nlargest(2).index

        fig = go.Figure()
        for product in top_2:
            fig.add_trace(go.Scatter(x=df.index, y=df[product], mode='lines', name=product))

        fig.update_layout(
            title=f'Search Interest Over Time for Top 2 Searched Brands in ({state_name})',
            xaxis_title='Date',
            yaxis_title='Search Interest',
            legend_title='Brands',
            xaxis_tickangle=-45
        )
        return fig

    def plot_pie_chart(kw_list, geo_code):
        pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo=geo_code, gprop='')
        data = fetch_interest_over_time(pytrends)
        if data is None:
            return None

        if 'isPartial' in data.columns:
            data = data.drop(columns=['isPartial'])

        total_interest = data.sum()
        fig = go.Figure(data=[go.Pie(labels=total_interest.index, values=total_interest.values, hole=0.3)])
        fig.update_layout(title=f'Search Interest Proportion for Entered Brands in ({state_name})')
        return fig

    # Display charts in columns
    col1, col2 = st.columns([2,1], gap="large")

    with col1:
        line_chart = plot_trends(mens_wear_kw, geo_code)
        if line_chart:
            st.plotly_chart(line_chart)

    with col2:
        pie_chart = plot_pie_chart(mens_wear_kw, geo_code)
        if pie_chart:
            st.plotly_chart(pie_chart)
    col3, col4= st.columns(2)

    st.divider()


    with col3:
        st.write(top_df)

    
    with col4:
        st.write(final_df)