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