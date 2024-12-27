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
    
    for option