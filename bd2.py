import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Define the GraphQL endpoint
url = "https://admin.firstlovecenter.com/graphql"

# Define the headers with the provided access token
headers = {
     "Authorization": f"Bearer {os.getenv('GRAPHQL_TOKEN')}",
    "Content-Type": "application/json",
}

# Define the constituency IDs
constituency_ids = {
    "GES 1": "92de9259-bbc0-48fd-aa59-6669fb369d3e",
    "GES AGBOGBA": "e21b6f3f-8ab9-4e22-9cfc-927e1c536d95",
    "GES Gloryzone": "15cb81b2-777b-4be7-a952-c3dc2fc8668b",
    "GES ATU": "44c412e7-e54c-4664-8321-4c38abe6dd21",
}

# Define the GraphQL query template
query_template = """
query constituencyGraphs($id: ID!) {
  constituencies(where: {id: $id}) {
    id
    name
    leader {
      id
      firstName
      lastName
      fullName
      pictureUrl
      nameWithTitle
      __typename
    }
    aggregateServiceRecords(limit: 4) {
      id
      attendance
      income
      numberOfServices
      week
      __typename
    }
    aggregateBussingRecords(limit: 4) {
      id
      attendance
      week
      numberOfSprinters
      numberOfUrvans
      numberOfCars
      __typename
    }
    services(limit: 4) {
      id
      createdAt
      attendance
      income
      week
      serviceDate {
        date
        __typename
      }
      __typename
    }
    memberCount
    __typename
  }
}
"""

# Function to fetch data for a single constituency
def fetch_constituency_data(id):
    payload = {
        "operationName": "constituencyGraphs",
        "query": query_template,
        "variables": {"id": id},
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Function to extract relevant data from the response
def extract_data(response):
    constituency = response["data"]["constituencies"][0]
    # Find the data for the current week (assuming the data is for week 30)
    current_week_data = None
    for record in constituency["aggregateServiceRecords"]:
        if record["week"] == 30:
            current_week_data = record
            break

    if current_week_data:
        return {
            "Constituency": constituency["name"].strip(),  # Strip whitespace
            "Attendance": current_week_data["attendance"],
            "Income": current_week_data["income"],
        }
    else:
        return {
            "Constituency": constituency["name"].strip(),  # Strip whitespace
            "Attendance": None,
            "Income": None,
        }

# Function to fetch and return data for all constituencies
def fetch_all_constituency_data():
    all_data = []
    for name, id in constituency_ids.items():
        response = fetch_constituency_data(id)
        data = extract_data(response)
        all_data.append(data)
    df_all_data = pd.DataFrame(all_data)
    df_all_data['Constituency'] = df_all_data['Constituency'].str.strip()  # Strip whitespace
    return df_all_data

def fetch_topup_data(file_path):
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(file_path, sheet_name=xls.sheet_names[0])
    df['Constituency'] = df['Constituency'].str.strip()  # Strip whitespace
    grouped_topup = df.groupby('Constituency')['Top Up'].sum().reset_index()
    return grouped_topup

def fetch_api_data(arrival_date):
    headers = {
        "Content-Type": "application/json",
         "Authorization": f"Bearer {os.getenv('GRAPHQL_TOKEN')}",
    }
    query = {
        "operationName": "councilByConstituencyArrivals",
        "query": """query councilByConstituencyArrivals($id: ID!, $arrivalDate: String!) {
          councils(where: {id: $id}, options: {limit: 1}) {
            id
            name
            constituencies {
              id
              name
              leader {
                id
                firstName
                lastName
                currentTitle
                nameWithTitle
                pictureUrl
                __typename
              }
              activeBacentaCount
              bacentasHaveArrivedCount(arrivalDate: $arrivalDate)
              bussingMembersHaveArrivedCount(arrivalDate: $arrivalDate)
              bussesThatArrivedCount(arrivalDate: $arrivalDate)
              __typename
            }
            __typename
          }
        }""",
        "variables": {"id": "c65c638e-b708-492c-bb73-4b9e9ac2f8c0", "arrivalDate": arrival_date}
    }

    response = requests.post(url, headers=headers, data=json.dumps(query))
    response_data = response.json()

    councils = response_data.get('data', {}).get('councils', [])
    constituencies_data = []

    for council in councils:
        for constituency in council.get('constituencies', []):
            constituencies_data.append({
                "Constituency": constituency.get('name').strip(),
                "Active Bacentas": constituency.get('activeBacentaCount'),
                "Busses Arrived": constituency.get('bussesThatArrivedCount'),
                "Members Arrived": constituency.get('bussingMembersHaveArrivedCount')
            })

    df_api = pd.DataFrame(constituencies_data)
    df_api = df_api.groupby('Constituency').sum().reset_index()  # Sum data for duplicate constituencies
    return df_api

def getallBacentas():
    headers = {
        "Content-Type": "application/json",
         "Authorization": f"Bearer {os.getenv('GRAPHQL_TOKEN')}",
    }
    query = {
    "operationName": "getCouncilConstituencies",
    "query": """
        query getCouncilConstituencies($id: ID!) {
          councils(where: {id: $id}) {
            id
            name
            leader {
              id
              firstName
              lastName
              fullName
              __typename
            }
            memberCount
            admin {
              id
              firstName
              lastName
              stream_name
              __typename
            }
            constituencies {
              name
              id
              stream_name
              memberCount
              bacentaCount
              target
              leader {
                id
                firstName
                lastName
                stream_name
                pictureUrl
                __typename
              }
              admin {
                id
                firstName
                lastName
                stream_name
                __typename
              }
              bacentas {
                id
                name
                __typename
              }
              __typename
            }
            __typename
          }
        }
    """,
    "variables": {"id": "c65c638e-b708-492c-bb73-4b9e9ac2f8c0"}}

    response = requests.post(url, headers=headers, data=json.dumps(query))
    response_data = response.json()
    # print(response_data)
    # return

    councils = response_data.get('data', {}).get('councils', [])
    bacentas_data = []

    for council in councils:
        for constituency in council.get('constituencies', []):
            bacentas_data.append({
                "Constituency": constituency.get('name').strip(),
                "Total Bacentas": constituency.get('bacentaCount'),
                })

    df_bacentas = pd.DataFrame(bacentas_data)
    return df_bacentas


def main(file_path, arrival_date):
    # Fetch the data
    grouped_topup = fetch_topup_data(file_path)
    df_api = fetch_api_data(arrival_date)
    constituency_data = fetch_all_constituency_data()
    allbacenta_data = getallBacentas()

    # Strip whitespace from 'Constituency' column in each dataframe before merging
    grouped_topup['Constituency'] = grouped_topup['Constituency'].str.strip()
    df_api['Constituency'] = df_api['Constituency'].str.strip()
    constituency_data['Constituency'] = constituency_data['Constituency'].str.strip()
    allbacenta_data['Constituency'] = allbacenta_data['Constituency'].str.strip()

    # Merge the dataframes
    combined_df = pd.merge(grouped_topup, df_api, on='Constituency', how='outer')
    combined_df = pd.merge(combined_df, constituency_data, on='Constituency', how='outer')
    combined_df = pd.merge(combined_df, allbacenta_data, on='Constituency', how='outer')

    # Renaming the columns as per the requirements
    combined_df.rename(columns={
        'Constituency': 'Governor',
        'Top Up': 'Bussing Expense',
        'Attendance': 'Weekday Attendance',
        'Income': 'Weekday Income',
        'Members Arrived': 'Bussing Attendance',
        'Busses Arrived': 'Bacentas That Bussed'
    }, inplace=True)

    # Updating Governor names
    combined_df.replace({
        'GES 1': 'Bishop Daniel',
        'GES AGBOGBA': 'Frederick Asare',
        'GES Gloryzone': 'David Akande',
        'GES ATU': 'Richmond Annan'
    }, inplace=True)

    # Adding new columns and setting values
    combined_df['Bacentas On Vacation'] = combined_df['Total Bacentas'] - combined_df['Active Bacentas']
    combined_df['Bacentas That Didn’t Bus'] = combined_df['Active Bacentas'] - combined_df['Bacentas That Bussed']

    # Setting the order of rows
    governors_order = ['Bishop Daniel', 'Frederick Asare', 'David Akande', 'Richmond Annan']
    combined_df['Governor'] = pd.Categorical(combined_df['Governor'], categories=governors_order, ordered=True)
    combined_df.sort_values('Governor', inplace=True)

    # Reordering the columns
    combined_df = combined_df[['Governor', 'Active Bacentas', 'Bacentas On Vacation', 'Bacentas That Bussed', 'Bacentas That Didn’t Bus', 'Bussing Attendance', 'Bussing Expense', 'Weekday Attendance', 'Weekday Income']]

    # Adding the total row
    total_row = combined_df.sum(numeric_only=True)
    total_row['Governor'] = 'Total'
    combined_df = pd.concat([combined_df, total_row.to_frame().T], ignore_index=True)

    # Save the combined data to an Excel file
    combined_df.to_excel('output/combined_data.xlsx', index=False)
    return combined_df

    # Display the combined data
    # print(combined_df)



# main(file_path, arrival_date)
# getallBacentas()
