import pandas as pd
import matplotlib.pyplot as plt

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

def feature_importance():
    print("GRAPHING FEATURE IMPORTANCES\n")
    weeks = [1, 2, 3, 4]
    dates = ["2020-11-01", "2020-11-08", "2020-11-15", "2020-11-22", "2020-11-29", \
        "2020-12-06", "2020-12-13", "2020-12-20", "2020-12-27", "2021-01-03", "2021-01-10"]

    fig, ax = plt.subplots(2,2, figsize=(7,7))

    index_map = {"totalTestResultsIncrease_norm": "Daily Test\n Increase",
                "prediction_aligned_int_7": "7-Day Case\nForecast",
                "test_positivity": "Test\nPositivity",
                "totalTestResultsIncrease": "Daily Test\nIncrease",
                "prediction_aligned_int_14":"14-Day Case\nForecast",
                "rt_aligned_int_7":"7-Day $R_t$\nForecast",
                "rt_aligned_int_28":"28-Day $R_t$\nForecast",
                "ELDERLY_POP":"% of Population\n> 65 yrs.",
                "rt_aligned_int_14": "14-Day $R_t$\nForecast",
                "prediction_aligned_int_21":"21-Day Case\nForecast",
                "AIDS_mortality":"AIDS mortality\nrate",
                "prediction_aligned_int_21":"21-Day Case\nForecast",
                "rt_aligned_int_21":"21-Day $R_t$\nForecast",
                "prediction_aligned_int_28":"28-Day Case\nForecast",
                "fb_stationary":"Stationary %\nof Population"}

    ax_items = [ax[0,0], ax[0, 1], ax[1,0], ax[1, 1]]

    for i in weeks:
        ranking_dfs = []
        for j in dates:
            df_path = "output/feature_ranking/publication/franking_" + str(i) + "_" +  j + ".csv"
            read_df = pd.read_csv(df_path, index_col=0)
            ranking_dfs.append(read_df)
        ranking_df = pd.concat(ranking_dfs, axis=1)
        ranking_df.columns = range(ranking_df.shape[1])
        ranking_df['mean'] = ranking_df.mean(axis=1)
        ranking_df['std'] = ranking_df.std(axis=1)
        ranking_df = ranking_df.sort_values("mean", ascending=True).tail(7)
        ranking_df['variable'] = ranking_df.index
        ranking_df['hue'] = [1] * len(ranking_df)
        ranking_df = ranking_df.replace({'variable': index_map})
        ranking_df = ranking_df[['variable', 'mean', 'std', 'hue']]
        ax_ = ax_items[i-1]
        ax_.barh(ranking_df['variable'], ranking_df['mean'], xerr=ranking_df['std'])
        ax_.set_ylabel('')
        ax_.set_xlabel('Mean Permutation Importance')
        ax_.set_title(str(i) + "-Week Forecast RF")
        ax_.tick_params(axis='both', labelsize=8)

    # plt.rcParams["figure.figsize"] = (25,25
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.5, wspace=0.5)
    plt.savefig(f'publication/output/feature_importance_figures/feature-importances.svg', format='svg')
    #plt.show()
