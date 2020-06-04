import pandas as pd

def diabetes():
    diabetesData = pd.read_csv("/Users/josephgalasso/Documents/IHME_USA_COUNTY_DIABETES_PREVALENCE_1999_2012/IHME_Diabetes.csv")
    diabetesData = diabetesData[diabetesData['FIPS'] > 100]
    diabetesData = diabetesData.loc[:, diabetesData.columns.isin(['FIPS', 'Location', 'Prevalence, 2012, Both Sexes'])]
    diabetesData.rename(columns={'Prevalence, 2012, Both Sexes': 'Diabetes_Prevalence_Both_Sexes', }, inplace=True)
    diabetesData['FIPS'] = diabetesData['FIPS'].apply(lambda x: str(int(x)))

    return diabetesData

def obesity():
    obesityData = pd.read_csv("/Users/josephgalasso/Documents/IHME_USA_OBESITY_PHYSICAL_ACTIVITY_2001_2011.csv",dtype={'fips': str})
    obesityData = obesityData[obesityData['Outcome'] == 'Obesity']
    obesityData = obesityData.loc[:, obesityData.columns.isin(['merged_fips', 'Sex', 'Prevalence 2011 (%)'])]

    maleObesityData = obesityData[obesityData['Sex'] == "Male"]
    maleObesityData.rename(columns={'Prevalence 2011 (%)': 'Male_Obesity_%', 'merged_fips':'fips'}, inplace=True)
    maleObesityData = maleObesityData.drop(['Sex'], axis=1).reset_index(drop=True)

    femaleObesityData = obesityData[obesityData['Sex'] == "Female"]
    femaleObesityData.rename(columns={'Prevalence 2011 (%)': 'Female_Obesity_%', 'merged_fips':'fips'}, inplace=True)
    femaleObesityData = femaleObesityData.drop(['Sex'], axis=1).reset_index(drop=True)

    mergedDF = pd.merge(left=maleObesityData, right=femaleObesityData, how='left', on='fips')

    return mergedDF

def mortality():
    mortalityData = pd.read_csv("/Users/josephgalasso/Documents/IHME_Mortality.csv")
    mortalityData = mortalityData[mortalityData['FIPS'] > 100.0]
    columns = mortalityData.columns[1:]
    for i in columns:
        mortalityData[i] = mortalityData[i].apply(lambda x : float(x.split(" ")[0]))
    mortalityData = mortalityData.reset_index(drop=True)
    mortalityData['FIPS'] = mortalityData['FIPS'].apply(lambda x : str(int(x)))

    return mortalityData

def infectious_disease_mortality():
    mortalityData = pd.read_csv("/Users/josephgalasso/Documents/IHME_Infections_Disease_Mortality.csv")
    mortalityData = mortalityData[mortalityData['FIPS'] > 100.0]
    columns = mortalityData.columns[1:]
    for i in columns:
        mortalityData[i] = mortalityData[i].apply(lambda x : float(x.split(" ")[0]))
    mortalityData = mortalityData.reset_index(drop=True)
    mortalityData['FIPS'] = mortalityData['FIPS'].apply(lambda x : str(int(x)))
    return mortalityData

def respiratory_disease_mortality():
    mortalityData = pd.read_csv("/Users/josephgalasso/Documents/IHME_Respiratory_Disease.csv")
    mortalityData = mortalityData[mortalityData['FIPS'] > 100.0]
    columns = mortalityData.columns[1:]
    for i in columns:
        mortalityData[i] = mortalityData[i].apply(lambda x : float(x.split(" ")[0]))
    mortalityData = mortalityData.reset_index(drop=True)
    mortalityData['FIPS'] = mortalityData['FIPS'].apply(lambda x : str(int(x)))
    return mortalityData



# Smoking, Infectious Disease Mortality, Respiratory Disease Mortality,
