import pandas as pd
import json
import plotly.express as px
import matplotlib.pyplot as plt

polish_days = {
  0: 'Poniedziałek',
  1: 'Wtorek',
  2: 'Środa',
  3: 'Czwartek',
  4: 'Piątek',
  5: 'Sobota',
  6: 'Niedziela'}

polish_months = {
  1: 'Styczeń',
  2: 'Luty',
  3: 'Marzec',
  4: 'Kwiecień',
  5: 'Maj',
  6: 'Czerwiec',
  7: 'Lipiec',
  8: 'Sierpień',
  9: 'Wrzesień',
  10: 'Październik',
  11: 'Listopad',
  12: 'Grudzień'
}

def read_data(file_path):
  with open(file_path) as f:
    json_data = json.load(f)
    
  detections = json_data["detections"]
  df = pd.json_normalize(detections)
  df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Europe/Warsaw')
  df = df.drop(['id','provider', 'metadata', 'source', 'visible', 'time_received', 'altitude', 'frame_content', 'x', 'y', 'accuracy'], axis=1)
  df.columns = [ 'wysokość', 'szerokość', 'szerokość_geo', 'długość_geo', 'czas', 'id_urządzenia', 'id_użytkownika', 'id_zespołu']
  df = map_id(df)
  df = df[df['szerokość_geo']!=0.0]
  return df

def map_id(df):
  with open('/content/CREDO/user_mapping.json') as json_file:
    users_data = json.load(json_file)
  
  users = users_data['users'] 
  users_map = {user['id']: user['username'] for user in users}
  df['id_użytkownika'] = df['id_użytkownika'].map(users_map)
  
  with open('/content/CREDO/team_mapping.json') as json_file:
    teams_data = json.load(json_file)

  teams = teams_data['teams'] 
  teams_map = {team['id']: team['name'] for team in teams}
  df['id_zespołu'] = df['id_zespołu'].map(users_map)
  return df


def plot_histogram(data, bins, xticks, xtick_labels, xlabel, title):
  plt.hist(data, bins=bins, align='left', rwidth=0.8)
  plt.xticks(ticks=xticks, labels=xtick_labels, rotation=45)
  plt.xlabel(xlabel)
  plt.ylabel("Liczba wystąpień")
  plt.title(title)
  plt.tight_layout()
  plt.show()

def create_histogram(df):
  reverse_days = {v: k for k, v in polish_days.items()}
  reverse_months = {v: k for k, v in polish_months.items()}

  while True:
    data = df.copy()
    print("Jaki rodzaj histogramu chcesz wykonać? (dni tygodnia, miesiące, lata)")
    odp = input("Wybierz jedną z powyższych opcji. Zapisz ją dokładnie tak jak powyżej.\n")

    if odp == "dni tygodnia":
      data['dzień'] = data['dzień'].map(reverse_days)
      plot_histogram(
          data=data['dzień'],
          bins=range(8),
          xticks=range(7),
          xtick_labels=[polish_days[i] for i in range(7)],
          xlabel="Dzień tygodnia",
          title="Histogram dni tygodnia"
      )

    elif odp == "miesiące":
      data['miesiąc'] = data['miesiąc'].map(reverse_months)
      plot_histogram(
            data=data['miesiąc'],
            bins=range(1, 14),
            xticks=range(1, 13),
            xtick_labels=[polish_months[i] for i in range(1, 13)],
            xlabel="Miesiąc",
            title="Histogram miesięcy"
        )

    elif odp == "lata":
      min_year = data["rok"].min()
      max_year = data["rok"].max()
      years = list(range(min_year, max_year + 1))
      plot_histogram(
          data=data['rok'],
          bins=range(min_year, max_year + 2),
          xticks=years,
          xtick_labels=years,
          xlabel="Lata",
          title="Histogram dla lat"
      )

    else:
      print("Nieznana opcja. Spróbuj ponownie.\n")
      continue

    repeat = input("Czy chcesz wykonać kolejny histogram? (tak/nie)\n").strip().lower()
    if repeat != "tak":
      break
  print("Zakończenie rysowania.")

def filter_by_date(df, start_date, end_date=None):
  if end_date is not None:
    filtered_df = df[(df['czas'].dt.date >= pd.Timestamp(start_date).date()) &
                       (df['czas'].dt.date <= pd.Timestamp(end_date).date())]
  else:
    filtered_df = df[df['czas'].dt.date == pd.Timestamp(start_date).date()]
  
  return filtered_df

def weekdays(data, days):
  df = data.copy()
  if len(days) == 0:
    df['dzień'] = df['czas'].dt.weekday.map(polish_days)
  else:
    df = df[df['czas'].dt.weekday.isin(days)]
    df['dzień'] = df['czas'].dt.weekday.map(polish_days)  
  return df

def months(data, months):
  df = data.copy()
  if len(months) == 0:
    df['miesiąc'] = df['czas'].dt.month.map(polish_months)
  else:
    df = df[df['czas'].dt.month.isin(months)]
    df['miesiąc'] = df['czas'].dt.month.map(polish_months)  
  return df

def years(data, years):
  df = data.copy()
  if len(years) == 0:
    df['rok'] = df['czas'].dt.year  
  else:
    df = df[df['czas'].dt.year.isin(years)]
    df['rok'] = df['czas'].dt.year  
  return df

def users(data, user_names):
  df = data.copy()
  return df[df['id_użytkownika'].isin(user_names)]

def teams(data, team_names):
  df = data.copy()
  df = df[df['id_zespołu'].isin(team_names)]  
  return df

def show_on_map(df):
  points = df.groupby(['szerokość_geo', 'długość_geo']).size().reset_index(name='counts')
  points['sizes'] = points['counts']/points['counts'].max() + 0.05
  fig = px.scatter_mapbox(points, lon=points['długość_geo'], lat=points["szerokość_geo"], color=points["counts"], size=points["sizes"], zoom=3, )
  fig.update_layout(mapbox_style='open-street-map')
  fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
  fig.show()

def get_names(df):
  print("Nazwy użytkowników: ", df['id_użytkownika'].unique().tolist())
  print("Nazwy zespołów: ", df['id_zespołu'].unique().tolist())