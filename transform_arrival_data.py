import pandas as pd
from engine import get_engine
from s3 import download_file
from engine import get_engine
import os

csv_file = "ArrivalData.csv"

download_file(key="ArrivalData",file_name=csv_file)

eng = get_engine("TravelSTAGE")

arrival_data = pd.read_csv(csv_file,skiprows=4)

select_columns = ["Country Code"]

for i in range(1995,2021):
    select_columns.append(f"{i}")

arrival_data = arrival_data[select_columns]
new_arrival_data = pd.DataFrame(columns=["CountryCode", "ArrivalYear","TouristAmount"])

for row in arrival_data.iterrows():
    index = row[0]
    country_code = row[1]["Country Code"]
    series = row[1].drop(["Country Code"], axis=0)
    
    
    new_years = series.to_frame().reset_index()
    new_columns = {}
    new_columns["index"] = "ArrivalYear"
    new_columns[index] = "TouristAmount"
    new_years = new_years.rename(columns=new_columns)
    new_years["CountryCode"] = country_code
    new_years["TouristAmount"] = new_years["TouristAmount"].astype(float)
    new_years["ArrivalYear"] = new_years["ArrivalYear"].astype(int)
    new_arrival_data = pd.concat([new_arrival_data,new_years[["CountryCode","ArrivalYear","TouristAmount"]]])



with eng.begin() as conn:
    new_arrival_data.to_sql(name="STAGE_NoFillArrival", con=conn, if_exists='fail')
    


os.remove(csv_file)
