import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
from sklearn.linear_model import LinearRegression

def rt_alignment():
    print("GENERATING GRAPH OF Rt ALIGNMENT PROCESS\n")
    county_rt=pd.read_csv("data/Rt/rt_data.csv", dtype={"FIPS":str})
    case_data=pd.read_csv("data/JHU/jhu_data.csv", dtype={"FIPS":str})
    final=pd.merge(left=county_rt, right=case_data, how="left", on=['FIPS', 'date'], copy=False)
    testing_data=pd.read_csv("data/COVIDTracking/testing_data.csv.gz", dtype={"FIPS":str})

    final=pd.merge(left=final, right=testing_data, how="left", on=['FIPS','date'], copy=False)

    final[['confirmed_cases_norm','confirmed_cases']]=final[['confirmed_cases_norm','confirmed_cases']].mask(final[['confirmed_cases_norm','confirmed_cases']] < 0, 0)

    final['normalized_cases_norm']=(final['confirmed_cases_norm']/final['totalTestResultsIncrease_norm'])
    final['normalized_cases']=(final['confirmed_cases']/final['totalTestResultsIncrease'])

    final=final.sort_values(['FIPS', 'date'])

    final=final[(final['date'] > "2020-05-22") & (final['date'] < "2020-07-10")]
    final['date']=final['date'].apply(lambda x : "-".join(x.split("-")[1:]))
    pima=final[final['FIPS'] == "48201"]

    pima=pima.rename({"RtIndicator": "Rt", 'normalized_cases_norm': "Cases"}, axis=1)

    fig, ax=plt.subplots(4, 2, figsize=(10,10)) # don't change this line

    # County Rt is maximally correlated at a 10-day Rt shift (0.91 Pearson) (originally 0.38)
    # State Rt is maximally correlated at a 9-day Rt shift (0.85 Pearson) (originally 0.07)

    def plot_cases_rt(ax_, x, y1, y2, title, shift):
        l1,=ax_.plot(x, y1, color="blue")
        ax_.set_ylabel('Cases/100000/tests', fontsize=9)
        ax_.set_xlabel('Date', fontsize=9)

        ax_.set_title(title, fontsize=10)
        ax1_=ax_.twinx()
        l2,=ax1_.plot(x, y2.shift(shift), color="red")
        ax1_.set_ylabel("$R_t$", fontsize=9)

        ax_.legend([l1, l2], ["Cases", "$R_t$"], loc="upper left", fontsize=8)

        ax_.tick_params(axis='x', labelrotation=30, labelsize=7)
        ax_.tick_params(axis='y', labelsize=7)
        ax1_.tick_params(axis='y', labelsize=7)
        ax_.xaxis.set_major_locator(ticker.MultipleLocator(9))
        for tick in ax_.xaxis.get_major_ticks():
            tick.label1.set_horizontalalignment('right')

    plot_cases_rt(ax[0,0], pima['date'], pima['Cases'], pima['Rt'], "Unshifted County $R_t$ & Normalized Cases\n(Pearson=0.38, $R_t$ Shift=0 Days)", 0)
    plot_cases_rt(ax[1,0], pima['date'], pima['Cases'], pima['Rt'], "Shifted County $R_t$ & Normalized Cases\n(Pearson=0.91, $R_t$ Shift=10 Days)", 10)
    plot_cases_rt(ax[0,1], pima['date'], pima['Cases'], pima['state_rt'], "Unshifted State $R_t$ & Normalized Cases\n(Pearson=0.07, $R_t$ Shift=0 Days)", 0)
    plot_cases_rt(ax[1,1], pima['date'], pima['Cases'], pima['state_rt'], "Shifted State $R_t$ & Normalized Cases\n(Pearson=0.85, $R_t$ Shift=9 Days)", 9)

    pima_ = pima.copy(deep=True)
    pima_['Rt']=pima_['Rt'].shift(10)
    pima_=pima_.dropna()

    def plot_regression(ax_, x, y, title):
        X=x.values.reshape(-1, 1)
        Y=y.values.reshape(-1, 1)

        linear_regressor=LinearRegression()
        linear_regressor.fit(X, Y)
        Y_pred=linear_regressor.predict(X)
        R2=linear_regressor.score(X, Y)
        l1,=ax_.plot(X, Y, 'o', markersize=3, color="blue")
        l2,=ax_.plot(X, Y_pred, '-', color="red")
        ax_.set_ylabel('Cases/100000/tests', fontsize=9)
        ax_.set_xlabel('$R_t$', fontsize=9)
        ax_.tick_params(axis='x', labelsize=7)
        ax_.tick_params(axis='y', labelsize=7)
        ax_.set_title(title, fontsize=10)
        ax_.legend([l2], ["Linear Regression Fit\n($R^2$=" + str(round(R2, 2)) + ")"], loc="upper left", fontsize=8)
        return linear_regressor.coef_, linear_regressor.intercept_

    coefficients, intercept = plot_regression(ax[2,0], pima_['Rt'], pima_['Cases'],"Linear Regression of\nShifted County $R_t$ & Normalized Cases")
    #print(coefficients, intercept)

    pima['case_predictions'] = pima['Rt'].apply(lambda x: x*coefficients[0][0] + intercept[0])

    def plot_one(ax_, x, y1, title, legend_label, color, ylabel):
        l1,=ax_.plot(x, y1, color=color)
        ax_.set_ylabel(ylabel, fontsize=9)
        ax_.set_xlabel('Date', fontsize=9)

        ax_.set_title(title, fontsize=10)

        ax_.legend([l1], [legend_label], loc="upper left", fontsize=8)

        ax_.tick_params(axis='x', labelrotation=30, labelsize=7)
        ax_.tick_params(axis='y', labelsize=7)
        ax_.xaxis.set_major_locator(ticker.MultipleLocator(9))
        for tick in ax_.xaxis.get_major_ticks():
            tick.label1.set_horizontalalignment('right')

    plot_one(ax[3,0], pima['date'], pima['Rt'], "Unshifted County $R_t$", "$R_t$", "red", 'Cases/100000/test')
    plot_one(ax[3,1], pima['date'], pima['case_predictions'], "Case Projections from Unshifted County $R_t$", "Case Projections", "blue", '$R_t$')

    plt.tight_layout()
    plt.subplots_adjust(hspace=1.1)
    plt.savefig(f'publication/output/rt_alignment_figures/rt-alignment.svg', format='svg')
    #plt.show()
