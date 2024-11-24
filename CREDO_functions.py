import pandas as pd
import json

def read_data(file_path):
  with open(file_path) as f:
    json_data = json.load(f)
    
  detections = json_data["detections"]
  return pd.json_normalize(detections)
