import gspread
import pandas as pd
import os
import json

def get_google_client():
    credentials_json = os.getenv("GOOGLE_CREDENTIALS")

    if credentials_json:
        credentials_dict = json.loads(credentials_json)
        return gspread.service_account_from_dict(credentials_dict)

    return gspread.service_account(
        filename="google_credentials.json"
    )




def dataframe_to_values(df):
    export_df = df.copy()

    export_df = export_df.astype(object).where(
        pd.notna(export_df),
        ''
    )

    values = [export_df.columns.tolist()] + export_df.values.tolist()

    return values


def upload_dataframe(df,worksheet):
    values = dataframe_to_values(df)

    worksheet.clear()

    worksheet.resize(
        rows = len(values),
        cols = len(values[0])
    )

    worksheet.update(values, 'A1')


def main():
    client = get_google_client()

    spreadsheet = client.open_by_url(
        'https://docs.google.com/spreadsheets/d/18rkmNABwqXhXpmoemtkG1_pUlQnS6ONPpC6b6ZOHpeo/edit?usp=sharing'
    )

    worksheet = spreadsheet.worksheet('incidents')
    incidents_df = pd.read_csv('processed_incidents.csv')

    worksheet_2 = spreadsheet.worksheet('sectors')
    sectors_df = pd.read_csv('processed_sectors.csv')

    upload_dataframe(incidents_df, worksheet)
    upload_dataframe(sectors_df,worksheet_2)

    print('Uploaded successfully')


if __name__ == '__main__':
    main()