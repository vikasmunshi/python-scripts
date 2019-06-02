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
        filename = filedialog.askopenfilename(parent=window, filetypes=[('csv', '*.csv')], title='Choose Libre file')
        window.destroy()
    with open(filename, 'r') as raw:
        data = pd.read_csv(raw, header=1, converters={2: lambda x: dt.strptime(x, '%m-%d-%Y %I:%M %p')}, index_col=2)
    data = data[['Record Type', 'Historic Glucose mmol/L', 'Scan Glucose mmol/L']]
    data.columns = ('type', 'historic', 'scan')
    data['glucose'] = data.historic.where(data.type == 0, data.scan)
    return data[(data.type == 0) | (data.type == 1)][['glucose']]


def calculate_stats(data: pd.DataFrame) -> pd.DataFrame:
    data['min'] = data.groupby(data.index.week)['glucose'].transform(min)
    data['max'] = data.groupby(data.index.week)['glucose'].transform(max)
    data['mean'] = data.groupby(data.index.week)['glucose'].transform(stats.mean)
    data['variance'] = data.groupby(data.index.week)['glucose'].transform(stats.pvariance)
    return data


def plot_data(data: pd.DataFrame) -> None:
    import matplotlib.dates
    import matplotlib.pyplot as plt
    ax = data.plot(
        figsize=(12, 6),
        color=(
            'xkcd:bright blue',  # glucose
            'xkcd:navy blue',  # min
            'xkcd:navy blue',  # max
            'xkcd:navy blue',  # mean
            'xkcd:grey',  # variance
        )
    )
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator())  # set x axis major grid to date
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d %b'))  # set x axis label format
    ax.xaxis.set_minor_locator(matplotlib.dates.HourLocator())  # set x axis minor grid to hour
    min_date, max_date = data.index.min().date(), data.index.max().date() + td(days=1)  # min and max date range
    min_date = max(min_date, max_date - td(days=35))  # adjust min range to show to include max 5 weeks
    min_date += td(days=(0, 6, 5, 4, 3, 2, 1)[min_date.weekday()])  # align min date to a week start (monday)
    ax.set_xlim(left=min_date, right=max_date)  # set x axis min and max range to show
    plt.yticks(range(0, data.glucose.max().astype(int) + 1, 1))  # set y axis min, max, and ticks
    ax.set(ylabel='mmol/L', xlabel='date', facecolor='xkcd:off white')  # set axis labels and background color
    ax.axhspan(ymin=4, ymax=8, color='xkcd:light green')  # highlight target glucose range
    ax.format_xdata = matplotlib.dates.DateFormatter('%d-%m-%Y %H:%M ')  # set format for x value
    ax.format_ydata = lambda x: '%1.2f' % x  # set format for y value
    ax.grid(True)  # show gridlines
    ax.margins(x=0, y=0.05)  # adjust figure margins
    plt.legend(ncol=data.shape[1])  # format legend to display in one row
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.09, top=1, wspace=0, hspace=0)  # adjust plot margins
    plt.get_current_fig_manager().set_window_title('Glucose')  # set title
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
