from flask import Flask, render_template, request
import time
import random
from pytrends.request import TrendReq
import pandas as pd
import plotly.graph_objects as go
from requests.exceptions import HTTPError

app = Flask(__name__)

# Define geo codes for Indian states
state_geo_codes = {
    'Andhra Pradesh': 'IN-AP', 'Arunachal Pradesh': 'IN-AR', 'Assam': 'IN-AS',
    'Bihar': 'IN-BR', 'Chhattisgarh': 'IN-CT', 'Goa': 'IN-GA', 'Gujarat': 'IN-GJ',
    'Haryana': 'IN-HR', 'Himachal Pradesh': 'IN-HP', 'Jharkhand': 'IN-JH',
    'Karnataka': 'IN-KA', 'Kerala': 'IN-KL', 'Madhya Pradesh': 'IN-MP',
    'Maharashtra': 'IN-MH', 'Manipur': 'IN-MN', 'Meghalaya': 'IN-ML',
    'Mizoram': 'IN-MZ', 'Nagaland': 'IN-NL', 'Odisha': 'IN-OR', 'Punjab': 'IN-PB',
    'Rajasthan': 'IN-RJ', 'Sikkim': 'IN-SK', 'Tamil Nadu': 'IN-TN', 'Telangana': 'IN-TG',
    'Tripura': 'IN-TR', 'Uttar Pradesh': 'IN-UP', 'Uttarakhand': 'IN-UT',
    'West Bengal': 'IN-WB'
}

def analyze_and_plot_trends(state_name, womens_wear_kw):
    # Set up pytrends
    pytrends = TrendReq(hl='en-US', tz=360)
    geo_code = state_geo_codes.get(state_name)
    
    # Check if the state name is valid
    if geo_code is None:
        return f"Invalid state name: {state_name}. Please enter a valid state."

    # Function to analyze Google Trends data
    def analyze_trends(kw_list, category, geo_code):
        retries = 3
        for i in range(retries):
            try:
                pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo=geo_code, gprop='')
                data = pytrends.interest_over_time()
                if 'isPartial' in data.columns:
                    data = data.drop(columns=['isPartial'])
                # Explicitly downcast data types
                data = data.apply(pd.to_numeric, errors='ignore', downcast='float')
                df = pd.DataFrame(data)
                most_trending_brand = df.sum().idxmax()
                return df, most_trending_brand
            except HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = (2 ** i) + random.uniform(0, 1)
                    time.sleep(wait_time)
                else:
                    raise e

    # Get trends for women's wear
    womens_wear_data, most_trending_brand = analyze_trends(womens_wear_kw, "Women's Wear", geo_code)

    # Function to plot trends
    def plot_trends(df, category):
        top_2 = df.sum().nlargest(2).index
        fig = go.Figure()
        for product in top_2:
            fig.add_trace(go.Scatter(x=df.index, y=df[product], mode='lines', name=product))
        fig.update_layout(
            width=550,
            height=300,
            xaxis_title='Date',
            yaxis_title='Search Interest',
            legend_title=f'{category} Item',
            xaxis_tickangle=-45
        )
        return fig.to_html(full_html=False)

    # Plot for women's wear
    plot_html = plot_trends(womens_wear_data, "Women's Wear")
    return most_trending_brand, plot_html

@app.route('/', methods=['GET', 'POST'])
def index():
    graph_html = None
    state_name = request.form.get('state')
    womens_wear_kw = request.form.get('brands')

    if state_name and womens_wear_kw:
        most_trending_brand, graph_html = analyze_and_plot_trends(state_name, womens_wear_kw)

    

    return render_template('home.html', graph_html=graph_html, state_name=state_name, womens_wear_kw=womens_wear_kw, state_geo_codes=state_geo_codes)
@app.route('/suggestions', methods=['POST', 'GET'])
def suggestions():
    if request.method == 'POST':
        keyword = request.form['keyword']
        pytrend = TrendReq()
        suggestions = pytrend.suggestions(keyword=keyword)
        topic_df = pd.DataFrame(suggestions)
        topic_df.drop(columns=['mid'], inplace=True)
        return render_template('home.html', tables=[topic_df.to_html(classes='data')], titles=topic_df.columns.values)
    return render_template('home.html')
    
if __name__ == "__main__":
    app.run(debug=True)
