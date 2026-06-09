import mysql.connector
import requests
import pandas as pd
import json
import os

# ===============================================================================
def connect(host, database, user, password):
    conn = mysql.connector.connect(host=host,
                                    database=database,
                                    user=user,
                                    password=password,
                                    ssl_disabled=True)

    return conn

# ===============================================================================
def get_customers(base_company_id_url, api_date_filter, access_token):
    print('Getting Customers')
    # Create filter for API call
    filter_query = f"lastModifiedDateTime ge {api_date_filter}"
    # Initialize the request URL
    url = f"{base_company_id_url}/customers?$filter={filter_query}"
    # Build the request headers
    headers = {
        'Accept-Language': 'en-us',
        'Authorization': f"Bearer {access_token['access_token']}"
    }
    # Initialize an empty DataFrame to store all customer data
    customer_df = pd.DataFrame()
    while url:  # Loop through pages as long as there's a `@odata.nextLink`
        # Fetch the data
        response = requests.get(url, headers=headers)
        # Check for successful response
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break
        # Parse the response JSON
        data = response.json()
        # Convert the current page of data to a DataFrame
        if 'value' in data:
            current_page_df = pd.DataFrame(data['value'])
            # Select only the desired columns if data is not empty
            if not current_page_df.empty:
                current_page_df = current_page_df[['number', 'displayName', 'type', 'addressLine1',
                                   'addressLine2', 'city', 'state', 'country', 'postalCode',
                                   'phoneNumber', 'email', 'balanceDue', 'creditLimit']]
                # Append the current page's DataFrame to the main DataFrame
                customer_df = pd.concat([customer_df, current_page_df], ignore_index=True)
        # Get the next page URL from `@odata.nextLink`
        url = data.get('@odata.nextLink')  # Set to None when no more pages are available
    # Check if the DataFrame is still empty
    if customer_df.empty:
        print('Customer DataFrame Is Empty')

    return customer_df

# ===============================================================================
def get_customer_price_group_code(base_company_name_url, date_filter, access_token):
    print('Getting Customer Price Group Code')
    # Create filter for API call
    filter_query = f"Last_Date_Modified ge {date_filter}"
    # Initialize the request URL
    url = f"{base_company_name_url}/Analytics_Customers?$filter={filter_query}"
    # Build the request headers
    headers = {
        'Accept-Language': 'en-us',
        'Authorization': f"Bearer {access_token['access_token']}"
    }
    # Initialize an empty DataFrame to store all customer price group code data
    customer_price_group_code_df = pd.DataFrame()
    while url:  # Loop through pages as long as there's a `@odata.nextLink`
        # Fetch the data
        response = requests.get(url, headers=headers)
        # Check for successful response
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break
        # Parse the response JSON
        data = response.json()
        # Convert the current page of data to a DataFrame
        if 'value' in data:
            current_page_df = pd.DataFrame(data['value'])
            # Select only the desired columns if data is not empty
            if not current_page_df.empty:
                current_page_df = current_page_df[['No', 'Customer_Price_Group']]
                current_page_df.rename(columns={'No': 'number'}, inplace=True)
                # Append the current page's DataFrame to the main DataFrame
                customer_price_group_code_df = pd.concat([customer_price_group_code_df, current_page_df], ignore_index=True)
        # Get the next page URL from `@odata.nextLink`
        url = data.get('@odata.nextLink')  # Set to None when no more pages are available
    # Check if the DataFrame is still empty
    if customer_price_group_code_df.empty:
        print('Customer Ship To Address DataFrame Is Empty')

    return customer_price_group_code_df

# ===============================================================================
def combine_customer_data_frames(customer_df, customer_price_group_code_df):
    customer_df = customer_df.merge(customer_price_group_code_df, on=['number'], how='left')
    customer_df['Customer_Price_Group'] = customer_df['Customer_Price_Group'].replace('', None)

    return customer_df

# ===============================================================================
def get_customer_ship_to_address(base_company_name_url, date_filter, access_token):
    print('Getting Customer Ship To Addresses')
    # Create filter for API call
    filter_query = f"Last_Date_Modified ge {date_filter}"
    # Initialize the request URL
    url = f"{base_company_name_url}/Analytics_Ship_To_Address?$filter={filter_query}"
    # Build the request headers
    headers = {
        'Accept-Language': 'en-us',
        'Authorization': f"Bearer {access_token['access_token']}"
    }
    # Initialize an empty DataFrame to store all customer ship to address data
    customer_ship_to_address_df = pd.DataFrame()
    while url:  # Loop through pages as long as there's a `@odata.nextLink`
        # Fetch the data
        response = requests.get(url, headers=headers)
        # Check for successful response
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break
        # Parse the response JSON
        data = response.json()
        # Convert the current page of data to a DataFrame
        if 'value' in data:
            current_page_df = pd.DataFrame(data['value'])
            # Select only the desired columns if data is not empty
            if not current_page_df.empty:
                current_page_df = current_page_df[['Customer_No',
                                        'Code', 'Name', 'Address', 'Address_2',
                                        'City', 'County', 'Country_Region_Code',
                                        'Post_Code', 'Phone_No', 'E_Mail',
                                        'Contact', 'Location_Code']]
                current_page_df.rename(columns={'County': 'State',
                                    'Country_Region_Code': 'Country'}, inplace=True)
                # Append the current page's DataFrame to the main DataFrame
                customer_ship_to_address_df = pd.concat([customer_ship_to_address_df, current_page_df], ignore_index=True)
        # Get the next page URL from `@odata.nextLink`
        url = data.get('@odata.nextLink')  # Set to None when no more pages are available
    # Check if the DataFrame is still empty
    if customer_ship_to_address_df.empty:
        print('Customer Ship To Address DataFrame Is Empty')

    return customer_ship_to_address_df

# ===============================================================================
def get_customer_price_groups(base_company_name_url, date_filter, access_token):
    print('Getting Customer Price Groups')
    # Initialize the request URL
    url = f"{base_company_name_url}/Analytics_Customer_Price_Groups"
    # Build the request headers
    headers = {
        'Accept-Language': 'en-us',
        'Authorization': f"Bearer {access_token['access_token']}"
    }
    # Initialize an empty DataFrame to store all customer price group data
    customer_price_groups_df = pd.DataFrame()
    while url:  # Loop through pages as long as there's a `@odata.nextLink`
        # Fetch the data
        response = requests.get(url, headers=headers)
        # Check for successful response
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break
        # Parse the response JSON
        data = response.json()
        # Convert the current page of data to a DataFrame
        if 'value' in data:
            current_page_df = pd.DataFrame(data['value'])
            # Select only the desired columns if data is not empty
            if not current_page_df.empty:
                current_page_df = current_page_df[['Code', 'Description']]
                # Append the current page's DataFrame to the main DataFrame
                customer_price_groups_df = pd.concat([customer_price_groups_df, current_page_df], ignore_index=True)
        # Get the next page URL from `@odata.nextLink`
        url = data.get('@odata.nextLink')  # Set to None when no more pages are available
    # Check if the DataFrame is still empty
    if customer_price_groups_df.empty:
        print('Customer Ship To Address DataFrame Is Empty')

    return customer_price_groups_df

# ===============================================================================
def customer_price_groups_upload(customer_price_groups_df, original_path, conn_write):
    if customer_price_groups_df.empty:
        print('Customer Price Groups Is Empty')
    else:
        print('Outputting Customer Price Groups')
        os.chdir('../Queries/Customer_Queries')
        folder = os.path.abspath(os.curdir)
        upload_list = customer_price_groups_df.to_dict('records')
        with open(folder + '/customer_price_groups_upload.sql', 'r') as query:
            cursor = conn_write.cursor()
            cursor.executemany(query.read(), upload_list)
            conn_write.commit()
            cursor.close()
        os.chdir(original_path)

# ===============================================================================
def customer_upload(customer_df, original_path, conn_write):
    if customer_df.empty:
        print('Customer Is Empty')
    else:
        print('Outputting Customers')
        os.chdir('../Queries/Customer_Queries')
        folder = os.path.abspath(os.curdir)
        upload_list = customer_df.to_dict('records')
        with open(folder + '/customer_upload.sql', 'r') as query:
            cursor = conn_write.cursor()
            cursor.executemany(query.read(), upload_list)
            conn_write.commit()
            cursor.close()
        os.chdir(original_path)

# ===============================================================================
def customer_ship_to_address_upload(customer_ship_to_address_df, original_path,
                                    conn_write):
    if customer_ship_to_address_df.empty:
        print('Customer Ship To Is Empty')
    else:
        print('Outputting Customer Ship To Addresses')
        os.chdir('../Queries/Customer_Queries')
        folder = os.path.abspath(os.curdir)
        upload_list = customer_ship_to_address_df.to_dict('records')
        with open(folder + '/customer_ship_to_addresses_upload.sql', 'r') as query:
            cursor = conn_write.cursor()
            cursor.executemany(query.read(), upload_list)
            conn_write.commit()
            cursor.close()
        os.chdir(original_path)

# ===============================================================================
def main(base_company_id_url, base_company_name_url, api_date_filter, date_filter,
        access_token, host_read, host_write, database_hq,
        user, password, original_path):
    # Getting data from Business Central API
    customer_df = get_customers(base_company_id_url, api_date_filter,
                                access_token)
    customer_price_group_code_df = get_customer_price_group_code(base_company_name_url, date_filter, access_token)
    customer_df = combine_customer_data_frames(customer_df, customer_price_group_code_df)
    customer_ship_to_address_df = get_customer_ship_to_address(base_company_name_url,
                                                date_filter, access_token)
    customer_price_groups_df = get_customer_price_groups(base_company_name_url, date_filter, access_token)
    # Outputting data to database
    conn_write = connect(host_write, database_hq, user, password)
    customer_price_groups_upload(customer_price_groups_df, original_path, conn_write)
    customer_upload(customer_df, original_path, conn_write)
    customer_ship_to_address_upload(customer_ship_to_address_df, original_path,
                                    conn_write)
    conn_write.close()