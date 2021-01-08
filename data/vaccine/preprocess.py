"""
This module reads and preprocesses CDC Vaccine Data
"""

import pandas as pd
import os

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandamic Central, 2020'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '2.1.0'

# API Endpoints
CDC_MODERNA_API = 'https://data.cdc.gov/resource/b7pe-5nws.csv'
CDC_PFIZER_API = 'https://data.cdc.gov/resource/saz5-9hgg.csv'

# Strings in header to be replaced
LABELS = ['first_doses_', 'doses_allocated_week_of_', 'doses_allocated_week_']

def vaccine_alloc():
    """
    Feeding datasets are from data.CDC.gov:

    - Pfizer Vaccine Allocation by Jurisdiction
    https://data.cdc.gov/Vaccinations/COVID-19-Vaccine-Distribution-Allocations-by-Juris/saz5-9hgg

    - Moderna Vaccine Allocation by Jurisdiction
    https://data.cdc.gov/Vaccinations/COVID-19-Vaccine-Distribution-Allocations-by-Juris/b7pe-5nws

    The output file covid_vaccine_by_state.csv:

        - state: name of state in two-letter format
        - date: date of distribution allocations
        - pfizer_first_doses: number of Pfizer doses allocated (not cumulative)
        - moderna_first_doses: number of Moderna doses allocated (not cumulative)
        - total_first_doses: pfizer_first_doses + moderna_first_doses (not cumulative)

    Other facts we have known of:

        - 2nd doses of Pfizer are scheduled to be adminstered 21 days after 1st doses

        - 2nd doses of Moderna are scheduled to be adminstered 28 days after 1st doses

        Source: https://www.cdc.gov/vaccines/covid-19/info-by-product/clinical-considerations.html

        - The efficacy of Pfizer is claimed to be ~95% on 28th day after first dose

        Source: https://www.pfizer.com/news/press-release/press-release-detail/pfizer-and-biontech-conclude-phase-3-study-covid-19-vaccine

        - Generally, longer gap between first and booster doses create a better
        immune response. However, there has not been enough data about extending
        the gap with COVID-19 vaccines.

        - Again, this data is NOT cumulative, doses are NEW allocated ones on specified dates
    """

    print('• Processing CDC Vaccine Data')

    # Read Pfizer's vaccine data
    pfizer_df = pd.read_csv(CDC_PFIZER_API)
    pfizer_df['jurisdiction'] = pfizer_df['jurisdiction'].str.replace('*', '')
    pfizer_df = pfizer_df.rename(columns={'jurisdiction':'state'})
    for i in LABELS:
        pfizer_df.columns = pfizer_df.columns.str.replace(i, '')
    drop_list = []
    for col in pfizer_df.columns:
        if len(col) > 5:
            drop_list.append(col)
    pfizer_df = pfizer_df.drop(drop_list, 1)
    for col in pfizer_df.columns[1:]:
        pfizer_df[col] = pfizer_df[col].str.replace(',','')

    # Read Moderna's vaccine data
    moderna_df = pd.read_csv(CDC_MODERNA_API)
    moderna_df['jurisdiction'] = moderna_df['jurisdiction'].str.replace('*', '')
    moderna_df = moderna_df.rename(columns={'jurisdiction':'state'})
    for i in LABELS:
        moderna_df.columns = moderna_df.columns.str.replace(i, '')
    drop_list = []
    for col in moderna_df.columns:
        if len(col) > 5:
            drop_list.append(col)
    moderna_df = moderna_df.drop(drop_list, 1)
    for col in moderna_df.columns[1:]:
        moderna_df[col] = moderna_df[col].str.replace(',','')

    # Replace statename with its two-letter abbreviation and strip off non-state data
    geo = pd.read_csv('data/geodata/state_fips.csv', usecols=[0,2])
    geo_dict = dict(zip(geo['name'], geo['abbr']))
    pfizer_df['state'] = pfizer_df['state'].replace(geo_dict)
    moderna_df['state'] = moderna_df['state'].replace(geo_dict)
    pfizer_df = pfizer_df[pfizer_df['state'].str.len()==2]
    moderna_df = moderna_df[moderna_df['state'].str.len()==2]

    # Reformat data
    pfizer_df = pd.melt(pfizer_df, id_vars=['state'],\
                var_name='date',\
                value_name='pfizer_first_doses')
    pfizer_df['date'] = '2021-' + pfizer_df['date'].str.replace('_', '-')
    for i in ['14', '21', '28']:
        pfizer_df['date'] = pfizer_df['date'].str.replace(f'2021-12-{i}', f'2020-12-{i}')
    pfizer_df = pfizer_df.sort_values(by=['state', 'date'])

    moderna_df = pd.melt(moderna_df, id_vars=['state'],\
                var_name='date',\
                value_name='moderna_first_doses')
    moderna_df['date'] = '2021-' + moderna_df['date'].str.replace('_', '-')
    for i in ['14', '21', '28']:
        moderna_df['date'] = moderna_df['date'].str.replace(f'2021-12-{i}', f'2020-12-{i}')
    moderna_df = moderna_df.sort_values(by=['state', 'date'])

    # Get total df
    total_df = pfizer_df.merge(moderna_df, on=['state', 'date'], how='outer')
    total_df = total_df.fillna(0)
    total_df['total_first_doses'] = total_df['pfizer_first_doses'].astype('int') +\
                                    total_df['moderna_first_doses'].astype('int')

    # Export data
    total_df.to_csv('data/vaccine/covid_vaccine_by_state.csv', index=False)

    print('  Finished\n')
