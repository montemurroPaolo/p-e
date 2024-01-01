from django.shortcuts import render
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px
import os
from django.conf import settings

pd.set_option('display.float_format', lambda x: '%.6f' % x)
test=True

def Get_defillama():
    url = "https://api.llama.fi/overview/fees"
    params = {
        "excludeTotalDataChart": "true",
        "excludeTotalDataChartBreakdown": "true",
        "dataType": "dailyFees",
    }

    try:
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            # Now 'data' contains the JSON response from the API
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"An error occurred: {e}")
    
    return data

def Defillama_df_from_dict(data):
    protocols_data = data.get("protocols", [])

    # Create a list of dictionaries with the required values
    results = [
        {
            "name": protocol.get("name", None),
            "UserFees_info": protocol["methodology"].get("UserFees") if isinstance(protocol.get("methodology"), dict) else "IDK",
            "Fees_info": protocol["methodology"].get("Fees") if isinstance(protocol.get("methodology"), dict) else "IDK",
            "Revenue_info": protocol["methodology"].get("Revenue") if isinstance(protocol.get("methodology"), dict) else "IDK",
            "ProtocolRevenue_info": protocol["methodology"].get("ProtocolRevenue") if isinstance(protocol.get("methodology"), dict) else "IDK",
            "HoldersRevenue_info": protocol["methodology"].get("HoldersRevenue") if isinstance(protocol.get("methodology"), dict) else "IDK",
            "SupplySideRevenue_info": protocol["methodology"].get("SupplySideRevenue") if isinstance(protocol.get("methodology"), dict) else "IDK",
            "total24h": protocol.get("total24h", None),
            "total7d": protocol.get("total7d", None),
            "total30d": protocol.get("total30d", None),
        }
        for protocol in protocols_data
    ]

    # Create a Pandas DataFrame from the list of dictionaries
    df = pd.DataFrame(results)
    df = df.dropna(subset=["total24h"])
    df = df.sort_values(by="total24h", ascending=False)
    df["name"] = df["name"].str.lower()
    df["name"] = df["name"].str.replace(r'[^a-zA-Z0-9]', '')

    return df

def Coingecko_data():
    # Initialize an empty list to store dataframes
    dfs = []
    if test:
        range_max = 2
    else:
        range_max = 5

    # Loop through the first 30 pages
    for page in range(1,range_max):
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": page,
            "sparkline": False,
            "locale": "en"
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Create a dataframe for each page and append it to the list
        dfs.append(pd.DataFrame(data))

    # Concatenate all dataframes into a single dataframe
    final_df = pd.concat(dfs, ignore_index=True)

    final_df = final_df.dropna(subset=["name"])
    final_df["name"] = final_df["name"].str.lower()
    final_df["name"] = final_df["name"].str.replace(r'[^a-zA-Z0-9]', '')

    return final_df

def Merge_and_clean(df, final_df):
    inner_df = pd.merge(df, final_df, on="name", how="inner")
    inner_df["pe30d"] = inner_df["market_cap"]/(inner_df["total30d"]*12)
    inner_df["pe7d"] = inner_df["market_cap"]/(inner_df["total7d"]*45)
    inner_df["pe24h"] = inner_df["market_cap"]/(inner_df["total24h"]*365)
    inner_df["market_cap"] = inner_df["market_cap"]/1000000
    inner_df['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return inner_df


def Plot_pe(inner_df):
    hover_data = ["date","UserFees_info","Fees_info","Revenue_info","ProtocolRevenue_info","HoldersRevenue_info","SupplySideRevenue_info","name","pe24h","pe7d","pe30d","total30d","market_cap","market_cap_category"]
    bins = [0, 10, 25, 50, 100, 250, 1000, float('inf')]
    labels = ['a 0-10', 'b 10-25', 'c 25-50', 'd 50-100', 'e 100-250', 'f 250-1000', 'g 1000+']

    inner_df['market_cap_category'] = pd.cut(inner_df['market_cap'], bins=bins, labels=labels, right=False).astype(str)

    # Keep only last date
    inner_df = inner_df[inner_df['date'] == inner_df['date'].max()]

    fig = px.bar(inner_df, x="name", y="pe30d", log_y=True, title="Total30d Histogram", 
                hover_data=hover_data, color="market_cap_category", category_orders={"market_cap_category": labels})

    fig.update_layout(xaxis_title="Name", yaxis_title="pe30d", legend_title="Name", showlegend=True)
    fig.update_layout(xaxis={'categoryorder':'total ascending'}) # add only this line
    return fig

def Create_csv(inner_df):
    csv_file_path = "{}/pe_data.csv".format(settings.BASE_DIR)

    if os.path.exists(csv_file_path):
        existing_data = pd.read_csv(csv_file_path)
        existing_data["date"] = pd.to_datetime(existing_data["date"])
        inner_df["date"] = pd.to_datetime(inner_df["date"])

        if inner_df['date'].max() > existing_data['date'].max():
            inner_df.to_csv(csv_file_path, mode='a', header=False, index=False)
    else:
        inner_df.to_csv(csv_file_path, index=False, header=True)

def Create_csv_hour():
    csv_file_path = "{}/pe_data.csv".format(settings.BASE_DIR)
    csv_file_hour_path = "{}/pe_data_hour.csv".format(settings.BASE_DIR)

    existing_data = pd.read_csv(csv_file_path)
    existing_data['date'] = pd.to_datetime(existing_data['date'])

    result_df = existing_data.groupby(['name', existing_data['date'].dt.floor('T')], as_index=False).first()
    result_df.to_csv(csv_file_hour_path, index=False, header=True)