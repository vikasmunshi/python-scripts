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
        from tkinter import filedialog as fd
        window = tk.Tk()
        window.withdraw()
        filename = fd.askopenfilename(parent=window, filetypes=[('csv', '*.csv')], title='Choose Libre file')
        window.destroy()
    with open(filename, 'r') as raw:
        data = pd.read_csv(raw, header=1, converters={2: lambda x: dt.strptime(x, '%d-%m-%Y %H:%M')}, index_col=2)
    data = data[['Record Type', 'Historic Glucose mmol/L', 'Scan Glucose mmol/L']]
    data.columns = ('type', 'historic', 'scan')
    data['glucose'] = data.historic.where(data.type == 0, data.scan)
    return data[(data.type == 0) | (data.type == 1)][['glucose']]


def calculate_stats(data: pd.DataFrame) -> pd.DataFrame:
    data['min'] = data.groupby(data.index.date)['glucose'].transform(min)
    data['max'] = data.groupby(data.index.date)['glucose'].transform(max)
    data['average'] = data.groupby(data.index.date)['glucose'].transform(stats.mean)
    data['stdev'] = data.groupby(data.index.date)['glucose'].transform(stats.pstdev)
    data['range'] = data.groupby(data.index.date)['glucose'].transform(lambda x: max(x) - min(x))
    return data


def plot_data(data: pd.DataFrame) -> None:
    import matplotlib.dates as md
    import matplotlib.pyplot as plt
    # noinspection PyTypeChecker
    _, sub_plots = plt.subplots(
        nrows=2,
        ncols=1,
        sharex=True,
        gridspec_kw={
            'height_ratios': [3, 1],
            'left': 0.04,
            'right': 0.96,
            'bottom': 0.06,
            'top': 0.99,
            'wspace': 0,
            'hspace': 0,
        }
    )

    charts = (
        data[['glucose', 'min', 'max', 'average']].plot(
            color=('xkcd:sky blue', 'xkcd:dark blue', 'xkcd:dark blue', 'xkcd:dark grey',),
            ax=sub_plots[0]),
        data[['stdev', 'range']].plot(color=('xkcd:grey', 'xkcd:dark grey',), ax=sub_plots[1])
    )

    min_date, max_date = data.index.min().date(), data.index.max().date() + td(days=1)  # min and max date range
    min_date = max(min_date, max_date - td(days=182))  # adjust min range to show to include max 26 weeks
    min_date += td(days=(0, 6, 5, 4, 3, 2, 1)[min_date.weekday()])  # align min date to a week start (monday)
    charts[0].xaxis.set_major_locator(md.DayLocator())  # set x axis major grid to date
    charts[0].xaxis.set_major_formatter(md.DateFormatter('%b-%d'))  # set x axis label format
    charts[0].set_xlim(left=min_date, right=max_date)  # set x axis min and max range to show

    for ax in charts:
        ax.set(facecolor='xkcd:off white')  # set background color
        ax.format_xdata = md.DateFormatter('%a %d-%m-%Y %H:%M ')  # set format for x value
        ax.format_ydata = lambda x: '%1.2f' % x  # set format for y value
        ax.grid(b=True)  # show grid-lines
        ax.margins(x=0, y=0.05)  # adjust figure margins

    charts[0].set_yticks(range(0, data.glucose.max().astype(int) + 1, 2))  # set y axis min, max, and ticks
    charts[0].axhspan(ymin=4.0, ymax=6.8, color='xkcd:lime green')  # highlight target glucose range
    charts[0].axhspan(ymin=3.9, ymax=4.0, color='xkcd:red')  # highlight low glucose range
    charts[0].set(xlabel='', ylabel='mmol/L')  # set axis label
    charts[0].tick_params(axis='y', colors='xkcd:navy blue', labelright=True)  # set y tick params
    for text in charts[0].legend(ncol=69, shadow=True).get_texts():  # set legend to show in one row
        text.set_color('xkcd:navy blue')  # set legend font color

    charts[1].set_yticks(range(0, data.range.max().astype(int) + 1, 4))
    charts[1].set(xlabel='', ylabel='mmol/L')  # set axis label
    charts[1].yaxis.label.set_color('xkcd:dark red')  # set label color
    charts[1].tick_params(axis='y', colors='xkcd:dark red', labelright=True)  # set y tick params
    for text in charts[1].legend(ncol=69, shadow=True).get_texts():  # set legend to show in one row
        text.set_color('xkcd:dark red')  # set legend font color
    for label in charts[1].xaxis.get_ticklabels()[1::2]:
        label.set_visible(False)  # hide every other date label

    fig = plt.get_current_fig_manager()
    fig.set_window_title('Glucose')  # set title
    if hasattr(fig, 'window'):
        fig.window.showMaximized()
    else:
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
