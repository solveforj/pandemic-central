import pandas as pd


def diabetes():
    diabetesData = pd.read_csv("/Users/josephgalasso/Documents/IHME_USA_COUNTY_DIABETES_PREVALENCE_1999_2012/IHME_Diabetes.csv")
    diabetesData = diabetesData[diabetesData['FIPS'] > 100]
    diabetesData = diabetesData.loc[:, diabetesData.columns.isin(['FIPS', 'Location', 'Prevalence, 2012, Both Sexes'])]
    diabetesData.rename(columns={'Prevalence, 2012, Both Sexes': 'Diabetes_Prevalence_Both_Sexes', }, inplace=True)
    diabetesData['FIPS'] = diabetesData['FIPS'].apply(lambda x: str(int(x)))

    diabetesData = diabetesData.reset_index(drop=True)
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
    mergedDF.rename(columns={'fips': 'FIPS', }, inplace=True)
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



def process_fips():
        fipsData = pd.read_csv("raw_data/health_data/all-geocodes-v2017.csv", dtype={'State Code (FIPS)': str, 'County Code (FIPS)': str})

        # Map 040 level fips code to state name in dictionary
        stateData = fipsData[fipsData['Summary Level'] == 40]
        stateMap = pd.Series(stateData['Area Name (including legal/statistical area description)'].values,index=stateData['State Code (FIPS)']).to_dict()

        # Get all county fips codes
        fipsData = fipsData[fipsData['Summary Level'] == 50]
        fipsData.insert(0, 'FIPS', fipsData['State Code (FIPS)'] + fipsData['County Code (FIPS)'])

        def make_identifier(a, b):
            state = stateMap[a[:2]]
            county = b.split(" ")
            county = county[0]

            return state + " " + county

        fipsData['Identifier'] = fipsData.apply(lambda row : make_identifier(row['FIPS'], row['Area Name (including legal/statistical area description)']), axis=1)
        fipsMap = pd.Series(fipsData['FIPS'].values, index=fipsData['Identifier']).to_dict()

        return fipsMap

fipsMap = process_fips()

def smoking_identifier(a, b):
    county = b.split(" ")[0]
    state = a
    id = state + " " + county
    try:
        fips = fipsMap[id]
        return fips
    except KeyError:
        fips = 'NA'
        return fips

def smoking_prevalence():
    smokingData = pd.read_csv("/Users/josephgalasso/Documents/IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012/IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012.csv")
    smokingData = smokingData[(smokingData['sex'] == 'Both') & (smokingData['year'] == 2012) & (smokingData['county'].notnull())]

    smokingData.insert(0, "fips", smokingData.apply(lambda row : smoking_identifier(row['state'], row['county']), axis=1))

    smokingData = smokingData.reset_index(drop=True)
    #Five rows of smokingData had NA values for the FIPS.  These are manually added in
    #print smokingData[smokingData['fips'] == 'NA']
    smokingData.iat[88,10] = "02158"
    smokingData.iat[309,10] = "11001"
    smokingData.iat[1131,10] = "22059"
    smokingData.iat[1791,10] = "35013"
    smokingData.iat[2406,10] = "46102"

    smokingData = smokingData.drop(['state', 'county', 'sex', 'year', 'total_lb', 'total_ub', 'daily_mean', 'daily_lb', 'daily_ub'], axis=1)
    smokingData.rename(columns={'fips': 'FIPS', 'total_mean': 'smoking_prevalence'}, inplace=True)
    return smokingData

def merge():
    dia = diabetes()
    dia.to_csv("raw_data/health_data/diabetes_data.csv", index=False)
    obe = obesity()
    obe.to_csv("raw_data/health_data/obesity_data.csv", index=False)
    mort = mortality()
    mort.to_csv("raw_data/health_data/mort_data.csv", index=False)
    id_mortality = infectious_disease_mortality()
    id_mortality.to_csv("raw_data/health_data/id_mortality.csv", index=False)
    rd_mortality = respiratory_disease_mortality()
    rd_mortality.to_csv("raw_data/health_data/rd_mortality.csv", index=False)
    smoking_prev = smoking_prevalence()
    smoking_prev.to_csv("raw_data/health_data/smoking_prev.csv", index=False)


    dia = pd.read_csv("raw_data/health_data/diabetes_data.csv")
    obe = pd.read_csv("raw_data/health_data/obesity_data.csv")
    mort = pd.read_csv("raw_data/health_data/mort_data.csv")
    id_mortality = pd.read_csv("raw_data/health_data/id_mortality.csv")
    rd_mortality = pd.read_csv("raw_data/health_data/rd_mortality.csv")
    smoking_prev = pd.read_csv("raw_data/health_data/smoking_prev.csv")

    mergedDF = pd.merge(left=dia, right=obe, how='left', on='FIPS', copy=False)
    mergedDF = pd.merge(left=mergedDF, right=mort, how='left', on = 'FIPS', copy=False)
    mergedDF = pd.merge(left=mergedDF, right=id_mortality, how='left', on='FIPS', copy=False)
    mergedDF = pd.merge(left=mergedDF, right=rd_mortality, how='left', on='FIPS', copy=False)
    mergedDF = pd.merge(left=mergedDF, right=smoking_prev, how='left', on='FIPS', copy=False)

    mergedDF.to_csv("raw_data/health_data/health_data.csv", index=False)
merge()
