from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
import openpyxl
import pandas as pd
import numpy as np
import statsmodels.api as sm

unit = "unit+apartment"
house = "house"
villa = "villa"
used = "established"
new = "new"
town_house = "townhouse"
blocks_of_unit = "unitblock"
acreage = "acreage"
rural = "rural"
land = "land"
retire = "retire"

def get_house_price(property_type, new_or_used):
    driver = webdriver.Chrome(f"C:/DRIVERS/chromedriver2.exe")
    driver.maximize_window()
    driver.implicitly_wait(4)
    today = datetime.datetime.now()
    excel_name = "House prices.xlsx"
    sheet_name = "Data"
    wb = openpyxl.load_workbook(excel_name)
    sheet = wb[sheet_name]
    for i in range(1, 50):
        try:
            driver.get(f'https://www.realestate.com.au/buy/property-{property_type}-in-orange,+nsw+2800/list-{i}?newOrEstablished={new_or_used}')
            soup = BeautifulSoup(driver.page_source, "html.parser")
            houses = soup.find_all("article", class_="results-card")
            if len(houses) <1:
                return
            for element in houses:
                try:
                    address = element.find("h2", class_="residential-card__address-heading").get_text(" ")
                except:
                    address = ""
                try:
                    land_size = element.find("div", class_="property-size").get_text(" ")
                    if "ha" in land_size:
                        land_size = float(str(land_size).partition(' ')[0])*10000
                    else:
                        land_size = str(land_size).partition(' ')[0]
                except:
                    land_size = ""
                try:
                    agent = element.find("img", class_="branding__image")["alt"]
                except:
                    agent = ""
                try:
                    bedrooms = element.find("span", class_="general-features__icon general-features__beds").get_text(" ")
                except:
                    bedrooms = ""
                try:
                    car = element.find("span", class_="general-features__icon general-features__cars").get_text(" ")
                except:
                    car = ""
                try:
                    price = element.find("span", class_="property-price").get_text(" ")
                except:
                    price = ""
                try:
                    bathroom = element.find("span", class_="general-features__icon general-features__baths").get_text(" ")
                except:
                    bathroom = ""
                type = property_type
                sheet.append([today, price, address, land_size, bathroom, bedrooms, car, type, agent ,new_or_used])
                wb.save(excel_name)
        except:
            print(f"{new_or_used} {property_type} number:{i} did not work")

unit = "unit+apartment"
house = "house"
villa = "villa"
used = "established"
new = "new"
town_house = "townhouse"
blocks_of_unit = "unitblock"
acreage = "acreage"
rural = "rural"
land = "land"
retire = "retire"


def get_house_prices():
    list = [unit, house, villa, town_house, blocks_of_unit, acreage, rural, retire]
    for type in list:
        get_house_price(type, used)
        get_house_price(type, new)



def run_regression():
    data = pd.read_excel("House prices.xlsx")
    df = pd.DataFrame(data=data)
    df = df[(df.type == "house") & (df.bedrooms < 8)]
    # print(dfr1.bedrooms)
    df = df[df['price'].str.contains(",") & (df['price'].str.contains("-") == False) & (df['price'].str.contains("to")== False) & (df['price'].str.contains("GST")== False)]
    df.drop_duplicates(subset=['address'], keep='last', inplace=True)
    df.land_size.replace("Na", "", inplace=True)
    Y = df.price
    Y.replace("Na", '', inplace=True)
    Y = Y.str.replace('[\$,)]', '', regex=True).astype(float)
    df["bedrooms"] = df.bedrooms.apply(lambda x: [x if x <= 4 else 5])

    df["bathroom"] = df.bathroom.apply(lambda x: [x if x <= 2 else 3])
    print(df.bathroom.head())
    bedrooms = pd.get_dummies(df["bedrooms"])
    bedrooms.set_axis(['Bedroom_1', 'Bedroom_2', 'Bedroom_3', 'Bedroom_4', "Bedroom+4"], axis=1, inplace=True)
    bedrooms.drop(columns="Bedroom_1", inplace=True)
    bathrooms = pd.get_dummies(df["bathroom"])
    bathrooms.set_axis(['Bathroom_1', 'Bathroom_2', 'Bathroom+2', ], axis=1, inplace=True)
    bathrooms.drop(columns="Bathroom_1", inplace=True)
    bathrooms["Bathrooms+3"] = bathrooms[bathrooms]
    house_type = pd.get_dummies(df["build_type"])
    house_type.drop(columns="established", inplace=True)
    print(bathrooms.head())
    X = pd.concat([bedrooms, bathrooms], axis=1)
    X = pd.concat([X,df.land_size],axis=1)
    print(X.head())
    # date	price	address	land_size	bathroom	bedrooms	car	type	agent
    X = sm.add_constant(X)
    model = sm.OLS(Y, X, missing='drop',hasconst=True).fit()
    print_model = model.summary()
    print(print_model)


#run_regression()
get_house_prices()