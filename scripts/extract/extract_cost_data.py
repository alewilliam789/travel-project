from seleniumbase import Driver
from selenium.webdriver.common.by import By
from sqlalchemy import text
import pandas as pd
import time

from utils.engine import get_engine


with Driver(uc=True) as driver:
    
    eng = get_engine("TravelDB")

    sql = "SELECT CountryID, CountryName FROM DIM_Countries"

    with eng.connect() as conn:

        country_data_df = pd.read_sql(sql, conn)
    
    eng = get_engine("TravelSTAGE")

    with eng.begin() as conn:
        truncate_sql = f"TRUNCATE TABLE STAGE_Cost"

        conn.execute(text(truncate_sql))

        country_id = 0

        for row in country_data_df.iterrows():
            country_id = row[1]["CountryID"]
            country_name = row[1]["CountryName"]
            country_name = country_name.lower()
            country_name = country_name.replace(" ","-")
            
            try:
                driver.uc_open_with_reconnect(f"https://www.budgetyourtrip.com/{country_name}",4)
                label_elem = driver.find_element("div.cost-tile-label")
                cost_elem = driver.find_element("span.curvalue")

                
                if("Average Daily Cost" in label_elem.text):
                    country_cost = int(cost_elem.text)
                else:
                    country_cost = 'NULL'

                time.sleep(10)
            except:
                country_cost = 'NULL'

            insert_sql = f"INSERT INTO STAGE_Cost (CountryID, DailyCost) values ({country_id},{country_cost})"

            conn.execute(text(insert_sql))




    
        
            
        

