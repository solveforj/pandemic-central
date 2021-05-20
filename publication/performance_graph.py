import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
from epiweeks import Week
from datetime import date

__author__ = 'Duy Cao, Joseph Galasso'
__copyright__ = '© Pandemic Central, 2021'
__license__ = 'MIT'
__status__ = 'release'
__url__ = 'https://github.com/solveforj/pandemic-central'
__version__ = '3.0.0'

MODELS = ['JHU_IDD',\
            'OneQuietNight',\
            'RF',\
            'Google_Harvard',\
            'JHUAPL-Bucky']

MODELS_2 = ['JHU_IDD',\
            'OneQuietNight',\
            'RF',\
            'Google_Harvard',\
            'JHUAPL-Bucky']

METRICS = {'MAE': 'Mean Absolute Error',
            'MSE': 'Mean Squared Error',
            'R2': 'R-squared'}

def back_to_the_future(model, metric):
    """
    Input:
        - path: path to the _performance file
        - metric: choose one from ['R2', 'MAE', 'MSE']
    """
    # Load data
    path = f'stats/{model}_performance.csv'
    df = pd.read_csv(path, usecols=['date', 'target', metric])
    dfs = []

    # Sort data into weeks
    for wk in list(range(1,5)):
        data = df[df.target == f'{wk} wk ahead inc case'].drop(['target'], 1).reset_index(drop=True).shift(wk-1)
        data[f'{metric} of Week {wk}'] = data[metric]
        data = data.drop([metric], 1)
        dfs.append(data)

    # Combine into one dataset
    df = pd.concat(dfs, axis=1)

    # Remove duplicated column ('date')
    df = df.loc[:,~df.columns.duplicated()]

    # Graph
    df.plot(x='date', y=[f'{metric} of Week 1', f'{metric} of Week 2', f'{metric} of Week 3', f'{metric} of Week 4'])
    plt.suptitle(f'{METRICS[metric]} of Projections in Week N in the Past', fontsize=16.5)
    plt.grid(alpha=0.4, linestyle='--')
    plt.box(on=None)
    plt.xlabel(f'Model: {model}')
    #plt.show()

def weekly_all_model(models, metric):
    # Load data
    dfs = {}
    for wk in range(1,5):
        for model in models:
            df = pd.read_csv(f'stats/{model}_performance.csv', usecols=['date', 'target', metric], parse_dates=['date'])
            df = df[df['target'] == f'{wk} wk ahead inc case'].drop(['target'], 1)
            df['week'] = df['date'].dt.strftime('%Y-%W')
            df = df.drop(['date'], 1)
            df = df.rename(columns={metric:f'{model}-{metric}'})
            dfs[model] = df
        df = dfs[models[0]]
        for model in models[1:]:
            df = df.merge(dfs[model], on=['week'], how='outer')
        df = df.sort_values(['week']).reset_index(drop=True)
        plt.rcParams["figure.figsize"] = (10,7)
        df.plot(x='week')
        plt.suptitle(f'{METRICS[metric]} of {wk}-week-ahead projections', fontsize=10)
        plt.grid(alpha=0.4, linestyle='--')
        plt.box(on=None)
        if metric == 'MAE' or metric == 'MSE':
            plt.ylabel('Number of case / 100,000 people')
        plt.xlabel('Epiweek')
        plt.savefig(f'{metric}-week-{wk}.svg', format='svg')
        plt.close()
        # plt.show()

def publish(models):
    # Load data
    dfs = {}
    for wk in range(1,5):
        for model in models:
            df = pd.read_csv(f'publication/output/model_performance/{model}_performance.csv', usecols=['date', 'target', 'MAE', 'R2'], dtype={'date':str})
            df = df[df['target'] == f'{wk} wk ahead inc case'].drop(['target'], 1)
            weeks = []
            for d in df['date'].values:
                w = Week.fromdate(date.fromisoformat(d)).cdcformat()
                weeks.append(w)
            df['week'] = weeks
            df = df.drop(['date'], 1)
            df = df.rename(columns={'MAE':f'{model}-MAE'})
            df = df.rename(columns={'R2':f'{model}-R2'})
            dfs[model] = df
        df = dfs[models[0]]
        for model in models[1:]:
            df = df.merge(dfs[model], on=['week'], how='outer')
        df = df.sort_values(['week']).reset_index(drop=True)
        # df = df.dropna(subset=['OneQuietNight-R2'])
        # df = df[df['week']<'2021-02']

        df = df.rename(columns={'PandemicCentral-R2':'RF-R2', 'PandemicCentral-MAE':'RF-MAE'})

        plt.rcParams["figure.figsize"] = (12,8)

        fig, (ax1, ax2) = plt.subplots(2, sharex=True)
        # ax1.set_title(METRICS['MAE'], fontsize=10)
        for model in MODELS_2:
            ax1.plot(df.week, df[f'{model}-MAE'], label=model)
            ax1.tick_params(axis='x', bottom=False)
        ax1.set_ylabel('Mean Absolute Error', fontsize=15)
        ax1.legend()
        ax1.grid(alpha=0.4, linestyle='--')
        ax1.yaxis.set_major_locator(MaxNLocator(5))
        ax1.set_ylim([0,450])
        # plt.box(on=None)

        # ax2.set_title(METRICS['R2'], fontsize=10)
        for model in MODELS_2:
            ax2.plot(df.week, df[f'{model}-R2'], label=model)
        # ax2.legend()
        ax2.grid(alpha=0.4, linestyle='--')
        ax2.locator_params(axis='y', nbins=5)
        #ax2.set(ylabel='$R^2$')

        # plt.box(on=None)
        #

        # df.plot(x='week')
        # plt.suptitle(f'{METRICS[metric]} of {wk}-week-ahead projections', fontsize=10)

        # if metric == 'MAE' or metric == 'MSE':
        #     plt.ylabel('Number of case / 100,000 people')
        ax2.set_ylabel('$R^2$', fontsize=15)
        ax2.set_xlabel('Week', fontsize=15, labelpad=7)
        ax2.set_ylim([-1, 1])
        # # plt.savefig(f'{metric}-week-{wk}.svg', format='svg')
        # # plt.close()
        if wk == 1:
            fig.suptitle(f'{wk}-week Projections', fontsize=16.5)
        else:
            fig.suptitle(f'{wk}-week Projections', fontsize=16.5)
        plt.tight_layout()
        # if wk == 1:
        #     plt.show()


        plt.savefig(f'publication/output/performance_figures/Week-{wk}.png', format='png')
        plt.savefig(f'publication/output/performance_figures/Week-{wk}.svg', format='svg')
        plt.close()


def performance_graph():
    # back_to_the_future(MODELS[0], 'MSE')
    # weekly_all_model(MODELS, 'MSE')
    print("GENERATING PERFORMANCE TIME-SERIES GRAPHS FOR ALL MODELS\n")
    publish(MODELS)
