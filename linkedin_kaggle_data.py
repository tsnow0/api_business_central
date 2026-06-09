# kaggle dataset: https://www.kaggle.com/datasets/arshkon/linkedin-job-postings/data
# only includes USA jobs right according to kaggle discussion so not going to worry about currency conversion.
# There are some CAD and other currency types so will look at those individually and see if I need to actually do a conversion
import kaggle as kg
import pandas as pd
import os
import numpy as np

def download_data():
    # Download latest version
    kg.api.dataset_download_files(dataset="arshkon/linkedin-job-postings", path='on.zip', unzip=True)
    df = pd.read_csv('on.zip/postings.csv', encoding='ISO-8859-1')

    return df

def clean_data(df):
    # only include listing that have a salary
    df = df.dropna(subset=['pay_period'])

    # if pay_period is hourly, update salary to yearly
    df['min_salary'] = np.where(df['pay_period'] == 'HOURLY', df['min_salary']*40*52, np.where(df['pay_period'] == 'MONTHLY', df['min_salary']*12, df['min_salary']))
    df['max_salary'] = np.where(df['pay_period'] == 'HOURLY', df['max_salary']*40*52, np.where(df['pay_period'] == 'MONTHLY', df['max_salary']*12, df['max_salary']))
    df['med_salary'] = np.where(df['pay_period'] == 'HOURLY', df['med_salary']*40*52, np.where(df['pay_period'] == 'MONTHLY', df['med_salary']*12, df['med_salary']))
    df['pay_period'] = df['pay_period'].replace('HOURLY', 'YEARLY')


    return df
if __name__ == '__main__':
    os.environ['KAGGLE_USERNAME'] = 'user-name'
    os.environ['KAGGLE_KEY'] = 'kaggle-key'

    kg.api.authenticate()
    df = download_data()

    # only data jobs
    d_df = df.loc[df['title'].str.contains('Data')]
    d_df = clean_data(d_df)
    avg_min_salary = d_df['min_salary'].mode()
    print(f'Common Min Salary: {avg_min_salary.tolist()}')
    avg_max_salary = d_df['max_salary'].mode()
    print(f'Common Max Salary: {avg_max_salary.tolist()}')
    avg_med_salary = d_df['med_salary'].mode()
    print(f'Common Med Salary: {avg_med_salary.tolist()}')

    # only data analyst jobs
    da_df = df.loc[df['title'].str.contains('Data Analyst')]
    da_df = clean_data(da_df)
    avg_min_salary = da_df['min_salary'].mode()
    print(f'Common DA Min Salary: {avg_min_salary.tolist()}')
    avg_max_salary = da_df['max_salary'].mode()
    print(f'Common DA Max Salary: {avg_max_salary.tolist()}')
    avg_med_salary = da_df['med_salary'].mode()
    print(f'Common DA Med Salary: {avg_med_salary.tolist()}')

    # only data jobs
    de_df = df.loc[df['title'].str.contains('Data Engineer')]
    de_df = clean_data(de_df)
    avg_min_salary = de_df['min_salary'].mode()
    print(f'Common DE Min Salary: {avg_min_salary.tolist()}')
    avg_max_salary = de_df['max_salary'].mode()
    print(f'Common DE Max Salary: {avg_max_salary.tolist()}')
    avg_med_salary = de_df['med_salary'].mode()
    print(f'Common DE Med Salary: {avg_med_salary.tolist()}')

    # only data jobs
    bi_df = df.loc[df['title'].str.contains('Business Intelligence')]
    bi_df = clean_data(bi_df)
    avg_min_salary = bi_df['min_salary'].mode()
    print(f'Common BI Min Salary: {avg_min_salary.tolist()}')
    avg_max_salary = bi_df['max_salary'].mode()
    print(f'Common BI Max Salary: {avg_max_salary.tolist()}')
    avg_med_salary = bi_df['med_salary'].mode()
    print(f'Common BI Med Salary: {avg_med_salary.tolist()}')