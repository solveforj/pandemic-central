import pandas as pd

def preprocess_census(year = 2018, drop_tot = False):
    # Import census data file (in same directory as repository)
    # Source: US census
    # Link: www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html
    # File: Annual County Resident Population Estimates by Age, Sex, Race, and Hispanic Origin: April 1, 2010 to July 1, 2018 (CC-EST2018-ALLDATA)
    census_file = "data/census/cc-est2018-alldata.csv.gz"
    census_data = pd.read_csv(census_file,  encoding = "ISO-8859-1", dtype={'STATE': str, 'COUNTY': str})
    census_data.insert(loc = 0, column = "FIPS", value = census_data["STATE"] + census_data["COUNTY"])

    # Filter data for year and minority populations
    census_data = census_data[(census_data['YEAR'] == year - 2007)]
    census_data = census_data.loc[:, census_data.columns.isin(['FIPS','TOT_POP', 'AGEGRP','TOT_MALE'\
    'TOT_FEMALE','H_MALE','H_FEMALE','BA_MALE','BA_FEMALE','IA_MALE','IA_FEMALE',\
    'NA_MALE','NA_FEMALE','TOM_MALE','TOM_FEMALE'])]

    # Add population of elderly in each county
    new_census_data = census_data[census_data['AGEGRP'] == 0].reset_index(drop=True)
    elderly_data = census_data[census_data['AGEGRP'] >= 13]
    elderly_population = elderly_data.groupby('FIPS')['TOT_POP'].sum().reset_index(drop=True)
    new_census_data['ELDERLY_POP'] = elderly_population
    new_census_data = new_census_data.drop(['AGEGRP'], axis=1)

    # Normalize data by county size
    # Source: United States Department of Agriculture
    # Link: www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/
    # File: 2010 Rural-Urban Commuting Area Codes (revised 7/3/2019)
    # Note: File was converted to csv format from xlsx without header
    county_sizes = pd.read_csv("data/census/ruca2010revised.csv", dtype={'State-County FIPS Code':str}, encoding="ISO-8859-1")
    county_sizes = county_sizes.rename({'State-County FIPS Code': 'FIPS', 'Land Area (square miles), 2010':'Land Area'}, axis=1)
    county_sizes['Land Area'] = county_sizes['Land Area'].apply(lambda x : float(x.replace(",", "")))
    individual_sizes = pd.DataFrame(county_sizes.groupby('FIPS')['Land Area'].apply(lambda x: x.sum()))
    individual_sizes.insert(0,'FIPS', individual_sizes.index)
    individual_sizes = individual_sizes.reset_index(drop=True)

    # Make final dataframe
    merged_df = pd.merge(left=new_census_data, right=individual_sizes, how='left', on='FIPS', copy=False)
    merged_df[merged_df.columns[1:]] = merged_df[merged_df.columns[1:]].astype(float)
    merged_df[merged_df.columns[2:-1]] = merged_df[merged_df.columns[2:-1]].div(merged_df['TOT_POP'], axis=0)
    merged_df.insert(1, "POP_DENSITY", merged_df['TOT_POP']/merged_df['Land Area'])
    if drop_tot == True:
        merged_df = merged_df.drop(['TOT_POP', 'Land Area'], axis=1)

    merged_df.to_csv("data/census/census.csv", index=False)

def main():
    print('[ ] Process Census Data', end='\r')
    preprocess_census()
    print('[' + '+' + ']\n')

main()
