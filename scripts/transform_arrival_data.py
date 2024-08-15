import pandas as pd
from sqlalchemy import text
from engine import get_engine
from s3 import download_file
from engine import get_engine
import os

csv_file = "ArrivalData.csv"

download_file(key="ArrivalData",file_name=csv_file)

eng = get_engine("TravelSTAGE")

arrival_data = pd.read_csv(csv_file,skiprows=4)

select_columns = ["Country Name","Country Code"]

for i in range(1995,2021):
    select_columns.append(f"{i}")

arrival_data = arrival_data[select_columns]
new_arrival_data = pd.DataFrame(columns=["CountryCode", "ArrivalYear","TouristAmount", "CountryName"])

for row in arrival_data.iterrows():
    index = row[0]

    country_name = row[1]["Country Name"]
    country_code = row[1]["Country Code"]
    series = row[1].drop(["Country Name","Country Code"], axis=0)
    
    
    new_years = series.to_frame().reset_index()
    new_columns = {}
    new_columns["index"] = "ArrivalYear"
    new_columns[index] = "TouristAmount"
    new_years = new_years.rename(columns=new_columns)
    new_years["CountryName"] = country_name
    new_years["CountryCode"] = country_code
    new_years["TouristAmount"] = new_years["TouristAmount"].astype(float)
    new_years["ArrivalYear"] = new_years["ArrivalYear"].astype(int)
    new_arrival_data = pd.concat([new_arrival_data,new_years[["CountryCode","ArrivalYear","TouristAmount", "CountryName"]]])





with eng.begin() as conn:
    conn.execute(text("TRUNCATE TABLE TravelSTAGE.dbo.STAGE_NoFillArrival"))
    
    new_arrival_data.to_sql("STAGE_NoFillArrival", conn, if_exists='append')


os.remove(csv_file)
