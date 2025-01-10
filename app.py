import datetime
from flask import Flask, render_template, request
from pytrends.request import TrendReq
from apscheduler.schedulers.background import BackgroundScheduler
import time
import csv
import pandas as pd
import os
import csv
app = Flask(__name__)

# Create a scheduler
scheduler = BackgroundScheduler()

def fetch_data(search, country, language, selected_options, time_interval):
    pytrends = TrendReq(hl=language, tz=360, geo=country)
    
    print(f"Keyword: {search}")
    print(f"Selected Options: {selected_options}")
    print(f"Country: {country}")
    print(f"Language: {language}")
    print(f"Auto Run Interval (hours): {time_interval}")
    
    if time_interval == 0:
        print("The code will run once and stop.")
        
    # Initialize a list to store the results for this run
    result= [search, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    
    def delay_and_retry(func, max_retries=10, delay_seconds=20):
        for retry in range(max_retries):
            try:
                return func()
            except Exception as e:
                print(f"Error in Option {option}: {e}")
                print(f"Retrying in {delay_seconds} seconds. Retry {retry + 1}/{max_retries}") 
                time.sleep(delay_seconds)
        raise Exception("Max retries exceeded. Request still failed")
    
    for option in range(1, 10):
        if str(option) in selected_options:
            # Fetch data for the selected option
            try:
                if option == 1:
                    delay_and_retry(lambda: pytrends.build_payload(kw_list=[search]))
                    interest_over_time = delay_and_retry(lambda: pytrends.interest_over_time())
                    interest_over_time = interest_over_time[interest_over_time[search] != 0]
                    result.append(interest_over_time.head(10).to_string())
                elif option == 2:
                    delay_and_retry(lambda: pytrends.build_payload(kw_list=[search]))
                    interest_by_region = delay_and_retry(lambda: pytrends.interest_by_region())
                    result.append(interest_by_region.head(10).to_string())
                elif option == 3:
                    print("Fetching data for Option 3: Trending Searches")
                    trending_searches = delay_and_retry(lambda: pytrends.trending_searches())
                    print("Data fetched successfully.")
                    result.append(trending_searches.head(10).to_string(header=False, index=False))
                elif option == 4:
                    top_charts = delay_and_retry(lambda: pytrends.top_charts(2023, hl=language, tz=360, geo=country))
                    if top_charts is not None:
                        result.append(top_charts.to_string(index=False))
                    else:
                        result.append("Option 4 - Google Top Charts: No data available")
                        
                # Option 5: Related Queries
                elif option == 5:
                    print("Fetching data for Option 5: Related Queries")
                    try:
                        delay_and_retry(lambda: pytrends.build_payload(kw_list=[search], timeframe='now 1-d')) #<------here you can change the days accorging to you prefrence for example just put "7-d" for 7
                        related_queries = delay_and_retry(lambda: pytrends.related_queries()[search]['top'])
                        related_queries['percentage'] = related_queries['value'].apply(lambda x: "{:.2f}%".format(x))
                        
                        # Prepare the data to be stored in the CSV file
                        data = [search, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                        for i in range(min(25, len(related_queries))):
                            query = related_queries.iloc[i]['query']
                            percentage = related_queries.iloc[i]['percentage']
                            data.extend([query, percentage])
                            
                        # Define the CSV file path
                        csv_file_path = "related_queries_data.csv"                        