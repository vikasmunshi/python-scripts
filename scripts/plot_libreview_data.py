#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
    plot blood glucose levels, stats, and trend from a downloaded LibreView data file
    requires: numpy pandas matplotlib
    note: calling tk.Tk() after importing matplotlib causes NSInvalidArgumentException
"""
import statistics as stats
from datetime import datetime as dt, timedelta as td

import pandas as pd


def read_file(filename: str = None) -> pd.DataFrame:
    if filename is None:
        import tkinter as tk
        from tkinter import filedialog
        window = tk.Tk()
        window.withdraw()
        raw = filedialog.askopenfile(mode='r', parent=window, filetypes=[('csv', '*.csv')], title='Choose Libre file')
        window.destroy()
    else:
        raw = open(filename, 'r')
    data = pd.read_csv(raw, header=1, converters={2: lambda x: dt.strptime(x, '%m-%d-%Y %I:%M %p')}, index_col=2)[
        ['Record Type', 'Historic Glucose mmol/L', 'Scan Glucose mmol/L']
    ]
    raw.close()
    data.index.names = ['datetime']
    data.columns = ('type', 'historic', 'scan')
    data['glucose'] = data['historic'].where(data['type'] == 0, data['scan'])
    return data[(data.type == 0) | (data.type == 1)][['glucose']]


def calculate_stats(data: pd.DataFrame) -> pd.DataFrame:
    data['low'] = 4.0
    data['high'] = 8.0
    data['min'] = data.groupby(data.index.week)['glucose'].transform(min)
    data['max'] = data.groupby(data.index.week)['glucose'].transform(max)
    data['mean'] = data.groupby(data.index.week)['glucose'].transform(stats.mean)
    # data['mode'] = data.groupby(data.index.week)['glucose'].transform(stats.mode)
    # data['median'] = data.groupby(data.index.week)['glucose'].transform(stats.median)
    data['variance'] = data.groupby(data.index.week)['glucose'].transform(stats.pvariance)
    # import numpy as np
    # date_nums = data.index.values.astype(np.float)
    # data['trend'] = np.poly1d(np.polyfit(date_nums, np.array(data['glucose']), 1))(date_nums)
    return data


def plot_data(data: pd.DataFrame) -> None:
    import matplotlib.dates
    import matplotlib.pyplot as plt
    ax = data.plot(
        figsize=(12, 6),
        color=(
            'xkcd:bright blue',  # glucose
            'xkcd:bright red',  # low
            'xkcd:bright red',  # high
            'xkcd:navy blue',  # min
            'xkcd:navy blue',  # max
            'xkcd:navy blue',  # mean
            # 'xkcd:navy blue',  # mode
            # 'xkcd:navy blue',  # median
            'xkcd:purple',  # variance
            # 'xkcd:burnt orange',  # trend
        )
    )
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d %b'))
    ax.xaxis.set_minor_locator(matplotlib.dates.HourLocator())
    min_date, max_date = data.index.min().date(), data.index.max().date()
    ax.set_xlim(left=min_date + td(days=(0, 6, 5, 4, 3, 2, 1)[min_date.weekday()]), right=max_date + td(days=1))
    ax.set(ylabel='mmol/L', xlabel='date', facecolor='xkcd:off white')
    ax.format_xdata = matplotlib.dates.DateFormatter('%d-%m-%Y %H:%M ')
    ax.format_ydata = lambda x: '%1.2f' % x
    ax.grid(True)
    ax.margins(x=0, y=0.05)
    plt.legend(ncol=data.shape[1])
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.09, top=1, wspace=0, hspace=0)
    plt.get_current_fig_manager().set_window_title('Glucose')
    plt.show()


if __name__ == '__main__':
    from sys import argv

try:
    plot_data(calculate_stats(read_file(argv[1] if len(argv) > 1 else None)))
except Exception as e:
    import traceback

    print('Traceback (trace limit 2):')
    traceback.print_tb(e.__traceback__, limit=2)
    print('Exception {} occurred at line {}\n{}'.format(type(e).__name__, e.__traceback__.tb_next.tb_lineno, e))
