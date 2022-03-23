import pandas as pd
import numpy as np
from multiprocessing import Pool
from app import *

def load_airports_data() -> pd.DataFrame:
    names = [
        "ICAO",
        "IATA",
        "Name",
        "City",
        "Country",
        "Lat_d",
        "Lat_m",
        "Lat_s",
        "Lat_dir",
        "Lon_d",
        "Lon_m",
        "Lon_s",
        "Lon_dir",
        "Altitude",
        "Latitude",
        "Longitude"
        ]
    data = pd.read_csv("data/airports.csv", names=names, sep=":")
    return data

def load_ports_data() -> pd.DataFrame:
    raw_data = pd.read_csv("data/ports.csv", sep=",")
    raw_data['Longitude'] = raw_data['shape'].apply(lambda x : float(x[7:-1].split(' ')[0]))
    raw_data['Latitude'] = raw_data['shape'].apply(lambda x : float(x[7:-1].split(' ')[1]))
    raw_data = raw_data.drop(columns=["shape"])
    return raw_data

def load_trains_data() -> pd.DataFrame:

    def format_df(df):
        
        def get_longitude(shape):
            return float(''.join(c for c in shape[18:-2] if c not in (')','(', ',')).split(' ')[0])

        def get_latitude(shape):
            return float(''.join(c for c in shape[18:-2] if c not in (')','(', ',')).split(' ')[1])

        df['Longitude'] = df['shape'].apply(lambda x: get_longitude(x))
        df['Latitude'] = df['shape'].apply(lambda x: get_latitude(x))
        df = df.rename(columns={"country" : "Country"})

        return df[["Longitude", "Latitude", "Country"]]

    raw_data = pd.read_csv("data/trains.csv", sep=",")
    return format_df(raw_data)

def merge_data() -> pd.DataFrame:
    res = pd.DataFrame()
    ports = load_ports_data()[["Longitude","Latitude","country"]]
    ports = ports.rename(columns={"country" : "Country"})
    airports = load_airports_data()[["Longitude","Latitude","Country"]]
    # trains = load_trains_data()[["Longitude","Latitude","Country"]]
    ports['Type'] = ["Port" for _ in range(len(ports))]
    airports['Type'] = ["Airport" for _ in range(len(airports))]
    # trains['Type'] = ["Station" for _ in range(len(trains))]
    return pd.concat([ports, airports])

def main():
    app = App(merge_data())
    app.run()

if __name__ == "__main__":
    main()