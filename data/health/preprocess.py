import pandas as pd

def preprocess_diabetes():
    # Source: Institute for Health Metrics and Evaluation (IHME). Diagnosed and Undiagnosed Diabetes Prevalence by County in the U.S.,
    #         1999-2012. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2016.
    # Note: Total sheet from .xslx file is exported as csv
    diabetes_data = pd.read_csv("data/health/IHME_Diabetes.csv")

    # Preprocess file
    diabetes_data = diabetes_data[diabetes_data['FIPS'] > 100]
    diabetes_data = diabetes_data.loc[:, diabetes_data.columns.isin(['FIPS', 'Location', 'Prevalence, 2012, Both Sexes'])]
    diabetes_data.rename(columns={'Prevalence, 2012, Both Sexes': 'Diabetes_Prevalence_Both_Sexes', }, inplace=True)
    diabetes_data['FIPS'] = diabetes_data['FIPS'].apply(lambda x: str(int(x)))
    diabetes_data = diabetes_data.reset_index(drop=True)

    return diabetes_data

def preprocess_obesity():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Physical Activity and Obesity Prevalence by County 2001-2011.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2013.
    # Link: ghdx.healthdata.org/record/ihme-data/united-states-physical-activity-and-obesity-prevalence-county-2001-2011
    obesity_data = pd.read_csv("data/health/IHME_USA_OBESITY_PHYSICAL_ACTIVITY_2001_2011.csv",dtype={'fips': str})

    # Preprocess data
    obesity_data = obesity_data[obesity_data['Outcome'] == 'Obesity']
    obesity_data = obesity_data.loc[:, obesity_data.columns.isin(['merged_fips', 'Sex', 'Prevalence 2011 (%)'])]
    male_obesity_data = obesity_data[obesity_data['Sex'] == "Male"]
    male_obesity_data = male_obesity_data.rename(columns={'Prevalence 2011 (%)': 'Male_Obesity_%', 'merged_fips':'fips'})
    male_obesity_data = male_obesity_data.drop(['Sex'], axis=1).reset_index(drop=True)
    female_obesity_data = obesity_data[obesity_data['Sex'] == "Female"]
    female_obesity_data = female_obesity_data.rename(columns={'Prevalence 2011 (%)': 'Female_Obesity_%', 'merged_fips':'fips'})
    female_obesity_data = female_obesity_data.drop(['Sex'], axis=1).reset_index(drop=True)
    merged_df = pd.merge(left=male_obesity_data, right=female_obesity_data, how='left', on='fips')
    merged_df.rename(columns={'fips': 'FIPS', }, inplace=True)
    merged_df['FIPS'] = merged_df['FIPS'].astype(str)

    return merged_df

def preprocess_mortality():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Life Expectancy and Age-specific Mortality Risk by County 1980-2014.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2017.
    # Link: http://ghdx.healthdata.org/record/ihme-data/united-states-life-expectancy-and-age-specific-mortality-risk-county-1980-2014
    # Note: All columns for all sheets in the original .xlsx file were merged into 1 sheet by FIPS,
    #       which was exported into a csv file
    mortality_data = pd.read_csv("data/health/IHME_Mortality.csv")

    # Preprocess data
    mortality_data = mortality_data[mortality_data['FIPS'] > 100.0]
    columns = mortality_data.columns[1:]
    for i in columns:
        mortality_data[i] = mortality_data[i].apply(lambda x : float(x.split(" ")[0]))
    mortality_data = mortality_data.reset_index(drop=True)
    mortality_data['FIPS'] = mortality_data['FIPS'].apply(lambda x : str(int(x)))

    return mortality_data

def preprocess_infectious_disease_mortality():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Infectious Disease Mortality Rates by County 1980-2014.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2018.
    # Link: http://ghdx.healthdata.org/record/ihme-data/united-states-infectious-disease-mortality-rates-county-1980-2014
    # Note: All columns for all sheets in the original .xlsx file were merged into 1 sheet by FIPS,
    #       which was exported into a csv file
    mortality_data = pd.read_csv("data/health/IHME_Infections_Disease_Mortality.csv")

    # Preprocess data
    mortality_data = mortality_data[mortality_data['FIPS'] > 100.0]
    columns = mortality_data.columns[1:]
    for i in columns:
        mortality_data[i] = mortality_data[i].apply(lambda x : float(x.split(" ")[0]))
    mortality_data = mortality_data.reset_index(drop=True)
    mortality_data['FIPS'] = mortality_data['FIPS'].apply(lambda x : str(int(x)))

    return mortality_data

def preprocess_respiratory_disease_mortality():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Chronic Respiratory Disease Mortality Rates by County 1980-2014.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2017.
    # Link: http://ghdx.healthdata.org/record/ihme-data/united-states-chronic-respiratory-disease-mortality-rates-county-1980-2014
    # Note: All columns for all sheets in the original .xlsx file were merged into 1 sheet by FIPS,
    #       which was exported into a csv file
    mortality_data = pd.read_csv("data/health/IHME_Respiratory_Disease_Mortality.csv")

    # Preprocess data
    mortality_data = mortality_data[mortality_data['FIPS'] > 100.0]
    columns = mortality_data.columns[1:]
    for i in columns:
        mortality_data[i] = mortality_data[i].apply(lambda x : float(x.split(" ")[0]))
    mortality_data = mortality_data.reset_index(drop=True)
    mortality_data['FIPS'] = mortality_data['FIPS'].apply(lambda x : str(int(x)))

    return mortality_data

def preprocess_smoking_prevalence():
    # Source: Institute for Health Metrics and Evaluation (IHME). United States Smoking Prevalence by County 1996-2012.
    #         Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2014
    # Link: ghdx.healthdata.org/record/ihme-data/united-states-smoking-prevalence-county-1996-2012
    # File: IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012.csv
    smoking_data = pd.read_csv("data/health/IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012.csv")

    # Preprocess data
    smoking_data = smoking_data[(smoking_data['sex'] == 'Both') & (smoking_data['year'] == 2012) & (smoking_data['county'].notnull())]
    smoking_data['state'] = smoking_data['state'].apply(lambda x : us_state_abbrev[x])
    smoking_data = smoking_data.drop(['sex', 'year', 'total_lb', 'total_ub', 'daily_mean', 'daily_lb', 'daily_ub'], axis=1)
    smoking_data.rename(columns={'fips': 'FIPS', 'total_mean': 'smoking_prevalence', 'county': 'Location', 'state':'region'}, inplace=True)

    return smoking_data

def merge_health_data():

    # Get all data files
    diabetes = preprocess_diabetes()
    obesity = preprocess_obesity()
    mortality = preprocess_mortality()
    id_mortality = preprocess_infectious_disease_mortality()
    rd_mortality = preprocess_respiratory_disease_mortality()

    # Merge all data files
    merged_df = pd.merge(left=diabetes, right=obesity, how='left', on='FIPS', copy=False)
    merged_df = pd.merge(left=merged_df, right=mortality, how='left', on = 'FIPS', copy=False)
    merged_df = pd.merge(left=merged_df, right=id_mortality, how='left', on='FIPS', copy=False)
    merged_df = pd.merge(left=merged_df, right=rd_mortality, how='left', on='FIPS', copy=False)

    merged_df.to_csv("data/health/health.csv", index=False)

def main():
    print('[ ] Process Health Data', end='\r')
    merge_health_data()
    print('[' + '+' + ']\n')

main()
