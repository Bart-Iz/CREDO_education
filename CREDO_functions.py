import pandas as pd
import json
import plotly.express as px
import matplotlib.pyplot as plt

def read_data(file_path):
  with open(file_path) as f:
    json_data = json.load(f)
    
  detections = json_data["detections"]
  df = pd.json_normalize(detections)
  df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Europe/Warsaw')
  df = df.drop(['id','provider', 'metadata', 'source', 'visible', 'time_received', 'altitude', 'frame_content', 'x', 'y'], axis=1)
  df.columns = ['precyzja', 'wysokość', 'szerokość', 'szerokość_geo', 'długość', 'czas', 'id_telefonu', 'id_użytkownika', 'id_zespołu']
  return df

def particle_flux(data):
    time = 0
    surface = 0
    n = 0
    for device in data['device_id'].unique():
        size = data[data['device_id'] == device][['height', 'width']].head(1)
        surface += float(size['height'].values[0]) * float(size['width'].values[0])*10**(-10)
        time_stamps = data[data['device_id'] == device]['timestamp']
        time_stamps = time_stamps.sort_values().reset_index(drop=True)
        time_diffs = time_stamps.diff().dropna()
        time_diffs = pd.to_timedelta(time_diffs).dt.total_seconds()
        time_diffs = time_diffs[time_diffs<=300]
        n += len(time_diffs)+1
        time += time_diffs.sum()
    return n/(surface*time)

def filter_by_date(df, start_date, end_date=None):
    if end_date:
        filtered_df = df[(df['czas'].dt.date >= pd.Timestamp(start_date).date()) &
                         (df['czas'].dt.date <= pd.Timestamp(end_date).date())]
    else:
        filtered_df = df[df['czas'].dt.date == pd.Timestamp(start_date).date()]
    
    return filtered_df

def weekdays(df, weekdays):
    df = df[df['czas'].dt.day_name(locale='pl_PL').isin(weekdays)]
    df['dzień'] = df['czas'].dt.day_name(locale='pl_PL')  
    return filtered_df

def month(df, months):
    df = df[df['czas'].dt.month_name(locale='pl_PL').isin(weekdays)]
    df['miesiąc'] = df['czas'].dt.month_name(locale='pl_PL')  
    return filtered_df

def year(df, years):
    filtered_df = df[df['czas'].dt.year.isin(years)]
    df['rok'] = df['czas'].dt.year  
    return filtered_df

