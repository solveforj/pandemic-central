import pandas as pd
import numpy as np
n = """
from scipy import stats as sps
from scipy.interpolate import interp1d

k = np.array([20, 40, 55, 90])

# We create an array for every possible value of Rt
R_T_MAX = 12
r_t_range = np.linspace(0, R_T_MAX, R_T_MAX*100+1)

# Gamma is 1/serial interval
# https://wwwnc.cdc.gov/eid/article/26/7/20-0282_article
# https://www.nejm.org/doi/full/10.1056/NEJMoa2001316
GAMMA = 1/7

def highest_density_interval(pmf, p=.9, debug=False):
    # If we pass a DataFrame, just call this recursively on the columns
    if(isinstance(pmf, pd.DataFrame)):
        return pd.DataFrame([highest_density_interval(pmf[col], p=p) for col in pmf],
                            index=pmf.columns)

    cumsum = np.cumsum(pmf.values)

    # N x N matrix of total probability mass for each low, high
    total_p = cumsum - cumsum[:, None]

    # Return all indices with total_p > p
    lows, highs = (total_p > p).nonzero()

    # Find the smallest range (highest density)
    best = (highs - lows).argmin()

    low = pmf.index[lows[best]]
    high = pmf.index[highs[best]]

    return pd.Series([low, high],
                     index=['Low_p',
                            'High_p'])

def prepare_cases(cases, cutoff=25):

    smoothed = cases.rolling(7,
        win_type='gaussian',
        min_periods=1,
        center=True).mean(std=2).round()
    smoothed = smoothed.iloc[:,0]

    idx_start = np.searchsorted(smoothed, cutoff)

    smoothed = smoothed.iloc[idx_start[0]:]
    original = cases.loc[smoothed.index]

    return smoothed


def get_posteriors(sr, sigma=0.15):

    # (1) Calculate Lambda
    lam = sr[:-1].values * np.exp(GAMMA * (r_t_range[:, None] - 1))

    # (2) Calculate each day's likelihood
    likelihoods = pd.DataFrame(
        data = sps.poisson.pmf(sr[1:].values, lam),
        index = r_t_range,
        columns = sr.index[1:])

    # (3) Create the Gaussian Matrix
    process_matrix = sps.norm(loc=r_t_range,
                              scale=sigma
                             ).pdf(r_t_range[:, None])

    # (3a) Normalize all rows to sum to 1
    process_matrix /= process_matrix.sum(axis=0)

    # (4) Calculate the initial prior
    #prior0 = sps.gamma(a=4).pdf(r_t_range)
    prior0 = np.ones_like(r_t_range)/len(r_t_range)
    prior0 /= prior0.sum()

    # Create a DataFrame that will hold our posteriors for each day
    # Insert our prior as the first posterior.

    posteriors = pd.DataFrame(
        index=r_t_range,
        columns=sr.index,
        data={sr.index[0]: prior0}
    )


    # We said we'd keep track of the sum of the log of the probability
    # of the data for maximum likelihood calculation.
    log_likelihood = 0.0

    # (5) Iteratively apply Bayes' rule
    for previous_day, current_day in zip(sr.index[:-1], sr.index[1:]):

        #(5a) Calculate the new prior
        current_prior = np.multiply(process_matrix[:,0],posteriors[previous_day])

        #(5b) Calculate the numerator of Bayes' Rule: P(k|R_t)P(R_t)
        numerator = likelihoods[current_day] * current_prior

        #(5c) Calcluate the denominator of Bayes' Rule P(k)
        denominator = np.sum(numerator)

        # Execute full Bayes' Rule
        posteriors[current_day] = numerator/denominator

        # Add to the running sum of log likelihoods
        log_likelihood += np.log(denominator)

    return posteriors, log_likelihood

url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
states = pd.read_csv(url)
states = states[states['FIPS'].notnull() & states['Admin2'].notnull()]
states = states.drop(['UID', 'iso2', 'iso3', 'code3', 'Admin2', 'Province_State', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'], axis=1)
states['FIPS'] = states['FIPS'].apply(lambda x : str(int(x)))
fips_list = states['FIPS'].tolist()
print states[states['FIPS'] == "36005"]
states = states.melt(id_vars=["FIPS"],
        var_name="Date",
        value_name="New_Cases")
states = states.reset_index(drop=True).set_index(['FIPS', 'Date'])

sigmas = np.linspace(1/20, 1, 20)
num = 0
results = {}

for fips in fips_list[0:1]:
    cases = states.xs("13121")
    print cases
    smoothed = prepare_cases(cases)
    if len(smoothed) > 0:
        result = {}
        posteriors, log_likelihood = get_posteriors(smoothed, sigma=0.25)
        print posteriors.idxmax()
        print log_likelihood
        result['posteriors'] = posteriors
        result['log_likelihoods'] = log_likelihood
        num += 1
        results[fips] = result
        print "Completed " + str(num) + "/" + str(len(fips_list))

#for fips, result in results.items():
#    print(fips)
#    posteriors = result['posteriors']
#    most_likely = posteriors.idxmax()
#    print most_likely
    #result = pd.concat([most_likely, hdis_90, hdis_50], axis=1)
    #if final_results is None:
    #    final_results = result
    #else:
    #    final_results = pd.concat([final_results, result])
    #clear_output(wait=True)
"""
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

fipsData = pd.read_csv("raw_data/health_data/all-geocodes-v2017.csv",encoding = "ISO-8859-1", dtype={'State Code (FIPS)': str, 'County Code (FIPS)': str})

# Map 040 level fips code to state name in dictionary
stateData = fipsData[fipsData['Summary Level'] == 40]
stateData['state_abbrev'] = stateData['Area Name (including legal/statistical area description)'].apply(lambda x : us_state_abbrev[x])
stateMap = pd.Series(stateData['State Code (FIPS)'].values,index=stateData['state_abbrev']).to_dict()
stateMap['AS'] = "60"
stateMap['GU'] = "66"
stateMap['MP'] = "69"
stateMap['PR'] = "72"
stateMap['VI'] = "78"

# Get all county fips codes
fipsData = fipsData[fipsData['Summary Level'] == 50]
fipsData.insert(0, 'FIPS', fipsData['State Code (FIPS)'] + fipsData['County Code (FIPS)'])
fipsData = fipsData[['FIPS', 'State Code (FIPS)']]

rt_data = pd.read_csv("raw_data/rt_data/rt.csv", usecols=['date', 'region', 'mean'])
rt_data['state'] = rt_data['region'].apply(lambda x : stateMap[x])

date_list = rt_data['date'].unique()
fips_list = fipsData['FIPS'].unique()

df = pd.DataFrame()
df['FIPS'] = fips_list
df['date'] = [date_list]*len(fips_list)
df = df.explode('date').reset_index(drop=True)
df['state'] = df['FIPS'].apply(lambda x : x[0:2])

# MIT Model
projections = pd.read_csv("https://raw.githubusercontent.com/youyanggu/covid19_projections/master/projections/combined/latest_us.csv", usecols=['date', 'region', 'r_values_mean'])
projections['datetime'] = projections['date'].apply(lambda x: pd.datetime.strptime(x, '%Y-%m-%d'))
projections = projections[(projections['region'].notnull()) & (projections['datetime'] < pd.to_datetime('today'))]
projections.insert(0, "state", projections['region'].apply(lambda x : stateMap[x]))
projections = projections.drop(['datetime', 'region'], axis=1).reset_index(drop=True)


merged_df = pd.merge(left=df, right=rt_data, how='left', on=['state', 'date'], copy=False)
merged_df = merged_df[merged_df['region'].notnull()]
merged_df = merged_df.rename({'mean':'rt_mean_MIT'},axis=1)

new_merged_df = pd.merge(left=merged_df, right=projections, on=['state', 'date'], copy=False)

new_merged_df.to_csv("raw_data/rt_data/rt_data.csv", index=False, sep=',')
