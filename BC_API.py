import requests
import msal
import pandas as pd
import json
from datetime import datetime, date, timedelta
import sys
import os
from pathlib import Path
import keyring as kr
import BC_Customer_Data
import BC_Item_Data
import BC_Purchase_Header_Data
import BC_Purchase_Order_Line_Data
import BC_Purchase_Invoice_Line_Data
import BC_Purchase_Receipt_Line_Data
import BC_Sales_Header_Data
import BC_Sales_Order_Line_Data
import BC_Sales_Invoice_Line_Data
import BC_Sales_Shipment_Line_Data
import BC_Vendor_Data
cur_dir = Path(__file__).parent
sys.path.append(str(cur_dir / '../../../../../../Credentials'))
import connections

# ===============================================================================
def getToken(tenant, client_id, client_secret):
    print('Getting Token')
    authority = f"{microsoft_online_url}" + tenant
    scope = [f"{api_business_central_url.default}"]
    app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential = client_secret)
    access_token = app.acquire_token_for_client(scopes=scope)

    return access_token

# ===============================================================================
def main():
    # main script that runs all other api scripts
    # API Information
    tenant = connections.bc_tenant
    client_id = connections.bc_client_id
    client_secret = connections.bc_client_secret
    company_id = connections.bc_company_id
    company_name = connections.bc_company_name
    environment = connections.bc_environment
    access_token = getToken(tenant, client_id, client_secret)
    # MYSQL Data
    original_path = os.path.abspath(os.curdir)
    host_read = connections.host_read
    host_write = connections.host_write
    database_hq = connections.database_hq
    cred = kr.get_credential('hq_db', None)
    user = cred.username
    password = cred.password
    base_company_id_url = f'https://api.businesscentral.dynamics.com/v2.0/{tenant}/{environment}/api/v2.0/companies({company_id})'
    base_company_name_url = f"https://api.businesscentral.dynamics.com/v2.0/{tenant}/{environment}/ODataV4/Company('{company_name}')"
    today = date.today()
    day_look_back = 7 # Replace with your desired number of days to look back
    date_filter = today - timedelta(days=day_look_back)
    filter_year = date_filter.year
    filter_month = date_filter.month
    filter_day = date_filter.day
    set_date = datetime(filter_year, filter_month, filter_day, 0, 0, 0)
    api_date_filter = set_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    # Getting data from Business Central API
    BC_Customer_Data.main(
                        base_company_id_url,
                        base_company_name_url,
                        api_date_filter,
                        date_filter,
                        access_token,
                        host_read,
                        host_write,
                        database_hq,
                        user,
                        password,
                        original_path
                        )
    BC_Vendor_Data.main(
                        base_company_id_url,
                        base_company_name_url,
                        api_date_filter,
                        access_token,
                        host_read,
                        host_write,
                        database_hq,
                        user,
                        password,
                        original_path
                        )
    BC_Item_Data.main(
                    base_company_id_url,
                    base_company_name_url,
                    api_date_filter,
                    access_token,
                    host_read,
                    host_write,
                    database_hq,
                    user,
                    password,
                    original_path
                    )
    purchase_order_header_df, \
    purchase_invoice_header_df, \
    purchase_receipt_header_df = BC_Purchase_Header_Data.main(
                                                        base_company_id_url,
                                                        base_company_name_url,
                                                        api_date_filter,
                                                        tenant,
                                                        client_id,
                                                        client_secret,
                                                        access_token,
                                                        host_read,
                                                        host_write,
                                                        database_hq,
                                                        user,
                                                        password,
                                                        original_path
                                                        )
    BC_Purchase_Order_Line_Data.main(
                                    purchase_order_header_df,
                                    base_company_id_url,
                                    tenant,
                                    client_id,
                                    client_secret,
                                    date_filter,
                                    access_token,
                                    host_read,
                                    host_write,
                                    database_hq,
                                    user,
                                    password,
                                    original_path
                                    )
    BC_Purchase_Invoice_Line_Data.main(
                                    purchase_invoice_header_df,
                                    base_company_id_url,
                                    tenant,
                                    client_id,
                                    client_secret,
                                    api_date_filter,
                                    date_filter,
                                    access_token,
                                    host_read,
                                    host_write,
                                    database_hq,
                                    user,
                                    password,
                                    original_path
                                    )
    BC_Purchase_Receipt_Line_Data.main(
                                    purchase_receipt_header_df,
                                    base_company_id_url,
                                    tenant,
                                    client_id,
                                    client_secret,
                                    api_date_filter,
                                    date_filter,
                                    access_token,
                                    host_read,
                                    host_write,
                                    database_hq,
                                    user,
                                    password,
                                    original_path
                                    )
    sales_order_header_df, \
    sales_invoice_header_df, \
    sales_shipment_header_df = BC_Sales_Header_Data.main(
                                                        base_company_id_url,
                                                        base_company_name_url,
                                                        api_date_filter,
                                                        access_token,
                                                        host_read,
                                                        host_write,
                                                        database_hq,
                                                        user,
                                                        password,
                                                        original_path
                                                        )
    BC_Sales_Order_Line_Data.main(
                                sales_order_header_df,
                                sales_invoice_header_df,
                                base_company_id_url,
                                base_company_name_url,
                                tenant,
                                client_id,
                                client_secret,
                                date_filter,
                                access_token,
                                host_read,
                                host_write,
                                database_hq,
                                user,
                                password,
                                original_path
                                )
    BC_Sales_Invoice_Line_Data.main(
                                    sales_invoice_header_df,
                                    base_company_id_url,
                                    tenant,
                                    client_id,
                                    client_secret,
                                    api_date_filter,
                                    date_filter,
                                    access_token,
                                    host_read,
                                    host_write,
                                    database_hq,
                                    user,
                                    password,
                                    original_path
                                    )
    BC_Sales_Shipment_Line_Data.main(
                                    sales_shipment_header_df,
                                    base_company_id_url,
                                    tenant,
                                    client_id,
                                    client_secret,
                                    api_date_filter,
                                    date_filter,
                                    access_token,
                                    host_read,
                                    host_write,
                                    database_hq,
                                    user,
                                    password,
                                    original_path
                                    )

# ===============================================================================
if __name__ == '__main__':
    main()
