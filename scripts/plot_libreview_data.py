#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
    plot blood glucose levels, stats, and trend from a downloaded LibreView data file
    requires: numpy pandas matplotlib mplcursors
    note: calling tk.Tk() after importing matplotlib causes NSInvalidArgumentException
"""
from datetime import datetime as dt, timedelta as td
from statistics import pstdev as stddev

import pandas as pd


def read_file(filename: str = None, timestamp_format: str = '%d-%m-%Y %H:%M') -> pd.DataFrame:
    if filename is None:
        import tkinter as tk
        from tkinter import filedialog as fd
        window = tk.Tk()
        window.withdraw()
        filename = fd.askopenfilename(parent=window, filetypes=[('csv', '*.csv')], title='Choose Libre file')
        window.destroy()
    with open(filename, 'r') as raw:
        data = pd.read_csv(raw, header=1, converters={2: lambda x: dt.strptime(x, timestamp_format)}, index_col=2)
    data = data[['Record Type', 'Historic Glucose mmol/L', 'Scan Glucose mmol/L']].sort_index()
    data.index.names = ('datetime',)
    data.columns = ('type', 'historic', 'scan')
    data['glucose'] = data.historic.where(data.type == 0, data.scan)
    return data[(data.type == 0) | (data.type == 1)][['glucose']]


def calculate_stats(data: pd.DataFrame) -> pd.DataFrame:
    daily_data = data.groupby(data.index.date)['glucose']
    data['min'] = daily_data.transform(min)
    data['max'] = daily_data.transform(max)
    data['stddev'] = daily_data.transform(stddev)
    data['range'] = daily_data.transform(lambda x: max(x) - min(x))
    for rolling_window in ('24h', '7d', '30d', '90d'):
        data['%s rolling average' % rolling_window] = data.glucose.rolling(rolling_window).mean()
    return data


def plot_data(data: pd.DataFrame, days: int = None) -> None:
    import matplotlib.dates as md
    from matplotlib import pyplot as plt

    lines = (
        [c for c in data.columns.values if c not in ['range', 'stddev', 'max', 'min']],
        ['range', 'stddev'],
        ['max', 'min']
    )
    # noinspection PyTypeChecker
    _, plots = plt.subplots(
        nrows=3,
        ncols=1,
        sharex=True,
        gridspec_kw={
            'height_ratios': [3, 1, 1],
            'left': 0.04,
            'right': 0.96,
            'bottom': 0.09,
            'top': 0.99,
            'wspace': 0,
            'hspace': 0.05,
        }
    )
    charts = (
        data[lines[0]].plot(ax=plots[0]),
        data[lines[1]].plot(color=('xkcd:dark grey', 'xkcd:grey',), ax=plots[1]),
        data[lines[2]].plot(color=('xkcd:black', 'xkcd:black',), ax=plots[2]),
    )

    min_date, max_date = data.index.min().date(), data.index.max().date() + td(days=1)  # min and max date range
    min_date = max(min_date, max_date - td(days=days or 91))  # adjust min range to show max days default 13 weeks
    if days is None:
        min_date += td(days=(0, 6, 5, 4, 3, 2, 1,)[min_date.weekday()])  # align min date to a week start (monday)

    for n, ax in enumerate(charts):
        ax.set(facecolor='xkcd:off white')  # set background color
        ax.format_xdata = md.DateFormatter('%a %d-%m-%Y %H:%M ')  # set format for x value
        ax.format_ydata = lambda x: '%1.2f' % x  # set format for y value
        ax.grid(b=True)  # show grid-lines
        ax.margins(x=0, y=0.05)  # adjust figure margins
        ax.tick_params(axis='x', rotation=90)  # set x tick params
        ax.xaxis.set_major_locator(md.DayLocator())  # set x axis major grid to date

        ax.xaxis.set_major_formatter(md.DateFormatter('%b-%d'))  # set x axis label format
        ax.set_xlim(left=min_date, right=max_date)  # set x axis min and max range to show
        _, legend = ax.get_legend_handles_labels()
        ymin = min(data.loc[min_date:max_date][legend].min().min().astype(int), (2, 0, 2,)[n])
        ymax = data.loc[min_date:max_date][legend].max().max().astype(int) + 1
        ax.set_yticks(range(0, ymax, (1, 4, 4,)[n]))  # y axis min, max, and ticks
        ax.set_ylim(bottom=ymin, top=ymax)  # set y axis min and max range to show
        ax.set(xlabel='', ylabel='mmol/L')  # set axis label
        ax.tick_params(axis='y', colors='xkcd:navy blue', labelright=True)  # set y tick params
        ax.legend(ncol=1, shadow=True, framealpha=0.25, loc='upper right', fontsize='small')  # legend format
        for i, label in enumerate(ax.xaxis.get_ticklabels()):
            label.set_horizontalalignment('left')  # align label left of tick
        for day in sorted(set(data.index.date)):
            if day.isoweekday() > 5:  # highlight weekends
                ax.axvspan(xmin=day, xmax=day + td(days=1), color='xkcd:light tan')
            midnight = dt(year=day.year, month=day.month, day=day.day, hour=0)
            for hour in range(0, 23, 6):  # six hourly bands
                ax.axvspan(xmin=midnight + td(hours=hour), xmax=midnight + td(hours=hour + 1),
                           color={
                               0: 'xkcd:light grey',
                               6: 'xkcd:light yellow',
                               12: 'xkcd:light orange',
                               18: 'xkcd:orange',
                           }[hour])
        if n in (0, 2,):
            ax.axhspan(ymin=3.9, ymax=6.8, color='xkcd:lime green')  # highlight target glucose range
            ax.axhspan(ymin=0, ymax=3.9, color='xkcd:saffron')  # highlight low glucose range

        def format_coord(chart_num):
            def status_str(x, _):
                loc = data.index.searchsorted(md.DateFormatter('%Y-%m-%d %H:%M:%S')(x), side='right')
                loc -= 1 if loc > 0 else 0
                val = data.iloc[loc][lines[chart_num]]
                return (val.name.strftime('%a %Y-%m-%d %H:%M:%S' if chart_num == 0 else '%a %Y-%m-%d')
                        + ''.join([' %s:%1.2f' % (c, v) for c, v in val.to_dict().items()]))

            return status_str

        ax.format_coord = format_coord(n)

    plt.get_current_fig_manager().set_window_title('glucose')  # set title
    plt.show()


if __name__ == '__main__':
    from sys import argv

    try:
        if len(argv) == 1:
            plot_data(calculate_stats(read_file()))
        elif len(argv) == 2:
            plot_data(calculate_stats(read_file(argv[1])))
        elif len(argv) == 3:
            plot_data(calculate_stats(read_file(argv[1])), int(argv[2]))
    except Exception as e:
        import traceback

        print('Traceback (trace limit 2):')
        traceback.print_tb(e.__traceback__, limit=2)
        print('Exception {} occurred at line {}\n{}'.format(type(e).__name__, e.__traceback__.tb_next.tb_lineno, e))
