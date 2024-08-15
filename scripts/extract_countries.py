import requests
from sqlalchemy import text
from engine import get_engine



eng = get_engine("TravelDB")


response = requests.get("https://restcountries.com/v3.1/independent?status=true&fields=name,cca3")

countries = response.json()

with eng.begin() as conn:

    for country in countries:
        common_name =country["name"]["common"]
        common_name = common_name.replace("'","''")

        cca = country["cca3"]

        conn.execute(text(f"INSERT INTO DIM_Countries (CountryName, CCA3) VALUES ('{common_name}', '{cca}')"))

