#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
    plot blood glucose levels, stats, and trend from a downloaded LibreView data file
    requires: numpy pandas matplotlib
    note: calling tk.Tk() after importing pyplot from matplotlib causes NSInvalidArgumentException
"""
from datetime import datetime as dt, timedelta as td
from statistics import mean, pstdev

import pandas as pd
from matplotlib import dates as md
from matplotlib import rc as rc
from matplotlib import style as style

style.use('bmh')  # set style
rc('font', size=8)  # set font size
rc('lines', linewidth=1)  # set line width
TS_FORMAT = '%d-%m-%Y %H:%M'
TARGET_MIN = 3.9
TARGET_MAX = 6.8


def getfilename():
    import tkinter as tk
    from tkinter import filedialog as fd
    window = tk.Tk()
    window.withdraw()
    fn = fd.askopenfilename(parent=window, filetypes=[('csv', '*.csv')], title='Choose Libre file')
    window.destroy()
    return fn


def plot(filename: str = '', timestamp_format: str = TS_FORMAT,
         days: int = 0, filter_data: bool = False, discard_last_date: bool = False) -> None:
    with open(filename or getfilename(), 'r') as raw:
        data = pd.read_csv(raw, header=1, converters={2: lambda x: dt.strptime(x, timestamp_format)}, index_col=2)

    data = data[['Record Type', 'Historic Glucose mmol/L', 'Scan Glucose mmol/L']]  # drop unused columns
    data.index.names = ('datetime',)  # rename index
    data.columns = ('type', 'historic', 'scan')  # rename columns
    data['glucose'] = data.historic.where(data.type == 0, data.scan)  # merge values from historic and scan columns
    data = data[(data.type == 0) | (data.type == 1)][['glucose']].dropna()  # drop unused rows
    data = data[~data.index.duplicated(keep='last')].sort_index()  # remove duplicates and sort index

    earliest_date = data.index.min().date()  # min of date range
    latest_date = data.index.max().date() + td(days=0 if discard_last_date else 1)  # max date range
    min_date = max(earliest_date, latest_date - td(days=days or 182))  # adjust min date to show default 26 weeks
    if not days:
        min_date += td(days=(0, 6, 5, 4, 3, 2, 1,)[min_date.weekday()])  # align min date to a week start (monday)
    if filter_data:
        data = data.loc[min_date:latest_date]
        earliest_date = min_date
    all_days = tuple(pd.date_range(start=earliest_date, end=latest_date, freq='1D'))
    weekends = tuple(d for d in all_days if d.isoweekday() in (6, 7))

    re_sampled_data = data.resample('min').interpolate(method='time')  # resample data to 1 minute interval
    daily_data = re_sampled_data.groupby(re_sampled_data.index.date)
    data['daily max'] = daily_data.transform(max)
    data['daily average'] = daily_data.transform(mean)
    data['daily min'] = daily_data.transform(min)
    data['daily range'] = daily_data.transform(lambda r: max(r) - min(r))
    data['daily stddev'] = daily_data.transform(pstdev)
    data['% in target'] = (daily_data.transform(lambda r: sum(r.between(TARGET_MIN, TARGET_MAX, inclusive=True))) /
                           daily_data.transform(len)) * 100
    for rolling_window in ('24h', '7d', '91d'):
        data['%s rolling average' % rolling_window] = re_sampled_data.glucose.rolling(rolling_window).mean()

    # need to import late to avoid exception due to conflict with tkinter
    from matplotlib import pyplot as plt
    charts = (['% in target'], ['daily max', 'daily average', 'daily min'], ['daily range', 'daily stddev'])
    charts = ([c for c in data.columns if c not in (i for s in charts for i in s)],) + charts

    # noinspection PyTypeChecker,SpellCheckingInspection
    _, figures = plt.subplots(nrows=len(charts), ncols=1, sharex=True,
                              gridspec_kw={'height_ratios': (len(charts) - 1,) + (1,) * (len(charts) - 1),
                                           'left': 0.05, 'right': 0.95, 'bottom': 0.1, 'top': 0.95,
                                           'wspace': 0, 'hspace': 0.15, })

    for n, ax in enumerate([data[chart].plot(ax=fig) for fig, chart in zip(figures, charts)]):
        ax.set(facecolor='xkcd:off white')  # set background color
        ax.grid(b=True)  # show grid-lines
        ax.margins(x=0, y=0.05)  # adjust figure margins
        ax.tick_params(axis='x', rotation=90, bottom=True, top=False, direction='out')  # set x tick params
        ax.xaxis.set_major_locator(md.DayLocator())  # set x axis major grid to date
        ax.xaxis.set_major_formatter(md.DateFormatter('%b-%d'))  # set x axis label format
        ax.set_xlim(left=min_date, right=latest_date)  # set x axis min and max range to show
        _, legend = ax.get_legend_handles_labels()
        y_min = (min(data.loc[min_date:latest_date][legend].min().min().astype(int), 2)) if n != 1 else 0
        y_max = (data.loc[min_date:latest_date][legend].max().max().astype(int) + 2) if n != 1 else 100
        ax.set_yticks(range(0, y_max + 1, int((y_max - y_min) / (10 if n == 0 else 4))))  # y axis min, max, and ticks
        ax.set_ylim(bottom=y_min, top=y_max)  # set y axis min and max range to show
        ax.set(xlabel='', ylabel='mmol/L' if n != 1 else '%')  # set axis label
        ax.tick_params(axis='y', labelright=True, right=True, left=True, direction='out')  # set y tick params
        ax.legend(ncol=len(legend), framealpha=0.5, loc='upper right' if n != 1 else 'lower right')  # legend format
        for i, label in enumerate(ax.xaxis.get_ticklabels()):
            label.set_horizontalalignment('left')  # align label left of tick
        for w in weekends:
            ax.axvspan(w, w + td(days=1), color='xkcd:light tan')  # vertical band for weekends
        if n in (0, 2):
            ax.axhspan(ymin=TARGET_MIN, ymax=TARGET_MAX, color='xkcd:lime green')  # highlight target glucose range
            ax.axhspan(ymin=0, ymax=TARGET_MIN, color='xkcd:light orange')  # highlight low glucose range
        if n == 1:
            ax.axhspan(ymin=90.0, ymax=100.0, color='xkcd:lime green')  # highlight > 90% in target range
        if n == 0:
            for d in all_days:
                # vertical line every six hours highlighted by white on both sides
                for hour, color in ((d, 'xkcd:grey'), (d + td(hours=6), 'xkcd:saffron'),
                                    (d + td(hours=12), 'xkcd:sky blue'), (d + td(hours=18), 'xkcd:orange')):
                    ax.axvspan(hour - td(minutes=1), hour - td(minutes=1), color='xkcd:off white')
                    ax.axvspan(hour + td(minutes=1), hour + td(minutes=1), color='xkcd:off white')
                    ax.axvspan(hour, hour, color=color)

        def format_coord(chart_legend, chart_num):
            def status_str(x, _):
                loc = data.index.searchsorted(md.DateFormatter('%Y-%m-%d %H:%M:%S')(x), side='right')
                loc -= 1 if loc > 0 else 0
                val = data.iloc[loc][chart_legend]
                return (val.name.strftime('%a %Y-%m-%d %H:%M ' if chart_num == 0 else '%a %Y-%m-%d ')
                        + ', '.join(['%s: %1.2f' % (c, v) for c, v in val.to_dict().items()]))

            return status_str

        ax.format_coord = format_coord(legend, n)

    plt.get_current_fig_manager().set_window_title('glucose')  # set title
    plt.show()


if __name__ == '__main__':
    from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

    parser = ArgumentParser(description='plot FreeStyle Libre data', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--filename', help='FreeStyle Libre download data csv file')
    parser.add_argument('-t', '--timestamp_format', default=TS_FORMAT, help='timestamp field format')
    parser.add_argument('-d', '--days', type=int, default=0, help='number of days to show')
    parser.add_argument('-r', '--filter_data', action='store_true', help='filter data to days to show')
    parser.add_argument('-l', '--discard_last_date', action='store_true', help='discard last date')

    args = parser.parse_args()

    try:
        plot(**vars(args))
    except Exception as e:
        import traceback

        print('Traceback (trace limit 2):')
        traceback.print_tb(e.__traceback__, limit=2)
        print('Exception {} occurred at line {}\n{}'.format(type(e).__name__, e.__traceback__.tb_next.tb_lineno, e))
