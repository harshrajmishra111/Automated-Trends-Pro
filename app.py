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