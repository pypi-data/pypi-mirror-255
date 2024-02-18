# -*- coding: utf-8 -*-
# @Time    : 29/08/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

def add_time_features(data, seasons: list = None):
    if seasons is None:
        seasons = ['Summer', 'Fall', 'Winter', 'Spring']
    data['minute'] = data.index.minute
    data['hour'] = data.index.hour
    data['day'] = data.index.day
    data['weekday'] = data.index.weekday
    data['month'] = data.index.month_name()
    data['year'] = data.index.year
    data['seasons'] = (
            (data.index.month % 12 + 3) // 3
    ).map(
        {
            1: seasons[0],
            2: seasons[1],
            3: seasons[2],
            4: seasons[3]
        }
    )
    data['day_name'] = data.index.day_name()
    data.loc[(data.index.weekday >= 5), 'day_type'] = 'non-working'
    data.loc[(data.index.weekday < 5), 'day_type'] = 'working'
    count = 0
    data = data.reset_index()
    data['date'] = data[data.columns[0]].apply(lambda x: x.strftime('%Y-%m-%d'))
    for i in data['date'].unique():
        data.loc[data['date'] == i, 'count_day'] = f'D{count}'
        count += 1
    #datasets = datasets.drop(['date'], axis=1)
    data = data.set_index(data.columns[0])
    return data


def print_summary(data):
    print('Start date:: ', data.index.min())
    print('Final date: ', data.index.max())
    print('Total number of days: ', data.index.max() - data.index.min())

