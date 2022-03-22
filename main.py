# TODO: Simulate complex logistic network.
from decimal import localcontext
import pandas as pd
import multiprocessing as mp
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

def load_ports_data():
    raw_data = pd.read_csv("data/ports.csv", sep=",")
    raw_data['Longitude'] = raw_data['shape'].apply(lambda x : float(x[7:-1].split(' ')[0]))
    raw_data['Latitude'] = raw_data['shape'].apply(lambda x : float(x[7:-1].split(' ')[1]))
    raw_data = raw_data.drop(columns=["shape"])
    return raw_data

def load_trains_data():

    def transform_to_points(row):
        lcoords = ''.join(c for c in row['shape'][18:-2] if c not in (')','(', ',')).split(' ')
        return float(lcoords[0]), float(lcoords[1])

    raw_data = pd.read_csv("data/trains.csv", sep=",")
    res = pd.DataFrame()
    longitude = []
    latitude = []
    # with mp.Pool(8)as pool:
    #     result = pool.imap(transform_to_points, raw_data.itertuples(), chunksize=10)
    #     for v in result:
    #         longitude.append(v[0])
    #         latitude.append(v[1])

    for line in raw_data['shape']:
        lcoords = ''.join(c for c in line[18:-2] if c not in (')','(', ',')).split(' ')
        longitude.append((float(lcoords[0])))
        latitude.append((float(lcoords[1])))

    res['Longitude'] = longitude
    res['Latitude'] = latitude

    return res

def merge_data():
    res = pd.DataFrame()
    prts = load_ports_data()
    airprts = load_airports_data()


def main():
    data = load_airports_data()

    print(data.head())

if __name__ == "__main__":
    app = App(load_trains_data())
    app.run()