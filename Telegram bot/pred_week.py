import pandas as pd
import datetime
import pmdarima as pm
import matplotlib.pyplot as plt


def week_prediction(data):
    """simple predictions based on stock dynamics"""
    data.columns = data.columns.str.lower()
    # train and predict auto ARIMA
    model = pm.auto_arima(y=data['adj close'], start_p=1, start_q=1, d=1, stepwise=True,
                          suppress_warnings=True, error_action="ignore", max_p=7, max_q=7, race=False)
    pred, conf = model.predict(n_periods=7, return_conf_int=True)
    # prep dataframe with predictions
    today = datetime.date.today()
    add_dates = [(today + datetime.timedelta(day)).strftime('%Y-%m-%d') for day in range(12)
                 if (today + datetime.timedelta(day)).weekday() not in [5, 6]][:7]
    pred_df = pd.DataFrame(pred.values, columns=['prediction'], index=add_dates)
    pred_df['left_int'] = [i[0] for i in conf]
    pred_df['right_int'] = [i[1] for i in conf]
    # add ts features
    new_days = pd.DataFrame(7 * [0], columns=['adj close'], index=add_dates)
    data = pd.concat([data, new_days])
    data['lag_7days'] = data['adj close'].shift(7).fillna(0)
    data['ma5_with_7shift'] = data['lag_7days'].rolling(window=5).mean().fillna(0)
    pred_df['lag_7days'] = data['lag_7days'].values[-7:]
    pred_df['ma5_with_7shift'] = data['ma5_with_7shift'].values[-7:]
    pred_df['history'] = 7*[None]
    return pred_df


def plot_prediction(ts, pred_df, symb):
    """concatenate previous week values with predictions and plot dynamics"""
    back = 7
    prev_week = ts[-back:]
    prev_week['prediction'] = back*[None]
    prev_week['left_int'] = back*[None]
    prev_week['right_int'] = back*[None]
    prev_week['lag_7days'] = back*[None]
    prev_week['ma5_with_7shift'] = back*[None]
    prev_week = prev_week.rename(columns={'adj close': 'history'})
    prev_week = prev_week[['prediction', 'left_int', 'right_int', 'lag_7days', 'ma5_with_7shift', 'history']]
    prev_week.index = prev_week.index.strftime('%Y-%m-%d')
    plt_df = pd.concat([prev_week, pred_df])
    # plot
    plt.figure()
    plt.plot(plt_df[['history', 'prediction', 'lag_7days', 'ma5_with_7shift']])
    plt.fill_between(x=plt_df.index, y1=plt_df['left_int'], y2=plt_df['right_int'], color='b', alpha=.1)
    plt.legend(['history', 'prediction', 'lag_7days', 'ma5_with_7shift', 'confidence int.'])
    plt.xticks(rotation=25)
    plt.tick_params(axis="x", labelsize=6)
    plt.title(f"Прогноз на неделю стоимости {symb}")
    return plt
