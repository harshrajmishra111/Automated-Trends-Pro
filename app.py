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
                        
                        # Check if the CSV file already exists
                        file_exists = os.path.isfile(csv_file_path)
                        
                        # Write the data to the CSV file
                        with open(csv_file_path, 'a', newline='') as file:
                            writer = csv.writer(file)
                            
                            # Write the header row if the file doesn't exist
                            if not file_exists:
                                header = ['Keyword', 'Date']
                                for i in range(1, 26):
                                    header.extend([f'Related Query {i}', f'Percentage {i}'])
                                    writer.writerow(header)
                                    
                            writer.writerow(data)
                            
                        result.append("Data stored in the CSV file.")
                        
                    except KeyError:
                        result.append("No top queries data available")
                        
                        
                elif option == 6:
                    print("Fetching data for Option 6: Related Topics")
                    try:
                        delay_and_retry(lambda: pytrends.build_payload(kw_list=[search], timeframe='now 1-d')) #<------here you can change the days accorging to you prefrence for example just put "7-d" for 7 days and "1-d" for 1 day
                        related_topics = delay_and_retry(lambda: pytrends.related_topics()[search]['rising'])
                        if related_topics is not None and not related_topics.empty:
                            related_topics['percentage'] = related_topics['value'].apply(lambda x: "{:.2f}%".format(x))
                            
                            # Prepare the data to be stored in the CSV file
                            data = [search, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                            for i in range(min(25, len(related_topics))):
                                topic = related_topics.iloc[i]['topic_title']
                                percentage = related_topics.iloc[i]['percentage']
                                data.extend([topic, percentage])
                                
                            # Define the CSV file path
                            csv_file_path = "related_topics_data.csv"
                            
                            # Check if the CSV file already exists
                            file_exists = os.path.isfile(csv_file_path)
                            
                            # Write the data to the CSV file
                            with open(csv_file_path, 'a', newline='') as file:
                                writer = csv.writer(file) 
                                
                                # Write the header row if the file doesn't exist
                                if not file_exists:
                                    header = ['Keyword', 'Date']
                                    for i in range(1, min(26, len(related_topics) + 1)):
                                        header.extend([f'Related Topic {i}', f'Percentage {i}'])
                                    writer.writerow(header)
                                    
                                writer.writerow(data)
                                
                            result.append("Data stored in the CSV file.")
                        else:
                            result.append("No top topics data available")
                           
                    except Exception as e:
                        error_message = f"Error in Option 6: {e}"
                        print(error_message)
                        result.append(error_message)
                
                elif option == 7:
                    print("Fetching data for Option 7: Multi-Interest Over Time (Past 7 days)")
                    try:
                        end_date = pd.Timestamp.now()
                        start_date = end_date - pd.DateOffset(days=10)
                        start_date_str = start_date.strftime('%Y-%m-%d')
                        end_date_str = end_date.strftime('%Y-%m-%d')
                        delay_and_retry(lambda: pytrends.build_payload([search], cat=0, timeframe=f'{start_date_str} {end_date_str}', geo='', gprop=''))                                
                        multi_interest = delay_and_retry(lambda: pytrends.interest_over_time())
                        
                        # Add the date as a separate column
                        multi_interest['Date'] = multi_interest.index.date
                        
                        result.append(multi_interest.to_string(index=False))
                    except Exception as e:
                        error_message = f"Error in Option 7: {e}"
                        print(error_message)
                        result.append(error_message)
                
                elif option == 8:
                    print("Fetching data for Option 8: Historical Hourly Data (Past 7 days)")
                    end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                    start_date = end_date - datetime.timedelta(days=7)
                    start_date_str = start_date.strftime('%Y-%m-%d')
                    end_date_str = end_date.strftime('%Y-%m-%d')
                    hourly_data = pd.DataFrame()
                    for i in range(7):
                        day_start = start_date + datetime.timedelta(days=i)
                        day_end = day_start + datetime.timedelta(days=1)
                        day_start_str = day_start.strftime('%Y-%m-%d')
                        day_end_str = day_end.strftime('%Y-%m-%d')
                        delay_and_retry(lambda: pytrends.build_payload([search], cat=0, timeframe=f'{day_start_str} {day_end_str}', geo='', gprop=''))
                        hourly_interest = delay_and_retry(lambda: pytrends.interest_over_time()) 
                        
                        # Convert the index to a 'Date' column
                        hourly_interest.reset_index(inplace=True)
                        
                        hourly_data = pd.concat([hourly_data, hourly_interest])
                        time.sleep(10)  # Delay for 10 seconds to avoid rate limiting
                        
                    hourly_data = hourly_data[hourly_data[search] > 0]
                    result.append(hourly_data.to_string(index=False))
                    
            except Exception as e:
                result.append(f"Error in Option {option}: {e}")
                
        else:
            result.append("Option not selected")
            
    # Save the result to a CSV file
    output_file = 'output_data.csv'
    with open(output_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if os.path.getsize(output_file) == 0:
            # Write the header row if the file is empty
            writer.writerow(['Keyword', 'Date & Time', 'Interest over Time', 'Interest by Region', 'Trending Searches', 'Top Charts', 'Related Topics', 'Keyword Suggestions', 'Multi Interest', 'Hourly Data'])                                                                                 
        writer.writerow(result)
        
    # Print the result in the terminal
    print(result)   
    
    
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        country = request.form.get('countrySelect')
        language = request.form.get('languageSelect')
        search = request.form.get('Keyword')
        selected_options = request.form.getlist('output-checkbox')
        time_interval = int(request.form.get('TimeInterval'))
        
        partial_fetch_data = fetch_data
        partial_fetch_data(search, country, language, selected_options, time_interval)
        
        if time_interval > 0:
            # Schedule data fetch if the time interval is greater than 0
            schedule_data_fetch(search, country, language, selected_options, time_interval)
            
    return render_template('index.html', error_message='')

def schedule_data_fetch(search, country, language, selected_options, time_interval):
    partial_fetch_data = fetch_data
    # Schedule the data fetch task at the specified time interval
    scheduler.add_job(partial_fetch_data, 'interval', args=[search, country, language, selected_options, time_interval],
                      hours=time_interval, id='data_fetch_job', replace_existing=True)
    
if __name__ == '__main__':
    scheduler.start()
    app.run()    
    
    


        
        
        
        
