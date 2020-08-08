import pandas as pd
import sys
sys.path.append(sys.path[0] + "/..")
from geodata.utils import get_state_fips
from align_Rt import align_rt


def preprocess_Rt():
    print("• Processing Rt Data")

    state_map, fips_data = get_state_fips()

    # Rt calculations from rt.live
    rt_data = pd.read_csv("https://d14wlfuexuxgcm.cloudfront.net/covid/rt.csv", usecols=['date', 'region', 'mean'])
    rt_data['state'] = rt_data['region'].apply(lambda x : state_map[x])

    date_list = rt_data['date'].unique()
    fips_list = fips_data['FIPS'].unique()

    df = pd.DataFrame()
    df['FIPS'] = fips_list
    df['date'] = [date_list]*len(fips_list)
    df = df.explode('date').reset_index(drop=True)
    df['state'] = df['FIPS'].apply(lambda x : x[0:2])

    # Rt calculations from covid19-projections.com
    projections = pd.read_csv("https://raw.githubusercontent.com/youyanggu/covid19_projections/master/projections/combined/latest_us.csv", usecols=['date', 'region', 'r_values_mean'])
    #projections['datetime'] = projections['date'].apply(lambda x: pd.datetime.strptime(x, '%Y-%m-%d'))
    projections['datetime'] = pd.to_datetime(projections['date'])
    projections = projections[(projections['region'].notnull()) & (projections['datetime'] < pd.to_datetime('today'))]
    projections.insert(0, "state", projections['region'].apply(lambda x : state_map[x]))
    projections = projections.drop(['datetime', 'region'], axis=1).reset_index(drop=True)

    # Merge Rt values from both sources together
    merged_df = pd.merge(left=df, right=rt_data, how='left', on=['state', 'date'], copy=False)
    merged_df = merged_df[merged_df['region'].notnull()]
    merged_df = merged_df.rename({'mean':'rt_mean_rt.live'},axis=1)
    merged_df = pd.merge(left=merged_df, right=projections, on=['state', 'date'], copy=False)
    merged_df = merged_df.rename({'r_values_mean':'rt_mean_MIT'},axis=1)
    merged_df = merged_df.sort_values(['FIPS', 'state'])

    # Add county-level Rt values
    county_rt = pd.read_csv("https://data.covidactnow.org/latest/us/counties.WEAK_INTERVENTION.timeseries.csv", dtype={"fips": str}, \
        usecols=['date', 'fips', 'RtIndicator'])
    county_rt = county_rt.rename({'fips':'FIPS'}, axis=1)
    final_rt = pd.merge(left=merged_df, right=county_rt, how="left", on=['FIPS', 'date'], copy=False)
    #final_rt['RtIndicator'] = final_rt['RtIndicator'].fillna(final_rt['rt_mean_MIT'])
    final_rt = final_rt

    final_rt.to_csv("data/Rt/rt_data.csv", index=False, sep=',')

    align_rt()

    print("  Finished\n")

if __name__ == "__main__":
    preprocess_Rt()
