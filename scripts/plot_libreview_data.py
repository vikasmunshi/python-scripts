#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
    plot blood glucose levels, stats, and trend from a downloaded LibreView data file
    requires: numpy pandas matplotlib mplcursors
    note: calling tk.Tk() after importing pyplot from matplotlib causes NSInvalidArgumentException
"""
from datetime import datetime as dt, timedelta as td
from statistics import mean as average, pstdev as stddev

import pandas as pd
from matplotlib import dates as md
from matplotlib import rc as rc
from matplotlib import style as style

style.use('bmh')  # set style
rc('font', size=8)  # set font size
rc('lines', linewidth=1)  # set line width


def getfilename():
    import tkinter as tk
    from tkinter import filedialog as fd
    window = tk.Tk()
    window.withdraw()
    fn = fd.askopenfilename(parent=window, filetypes=[('csv', '*.csv')], title='Choose Libre file')
    window.destroy()
    return fn


def plot(filename: str = '', timestamp_format: str = '%d-%m-%Y %H:%M', days: int = 0) -> None:
    with open(filename or getfilename(), 'r') as raw:
        data = pd.read_csv(raw, header=1, converters={2: lambda x: dt.strptime(x, timestamp_format)}, index_col=2)

    data = data[['Record Type', 'Historic Glucose mmol/L', 'Scan Glucose mmol/L']].sort_index()
    data.index.names = ('datetime',)
    data.columns = ('type', 'historic', 'scan')
    data['glucose'] = data.historic.where(data.type == 0, data.scan)
    data = data[(data.type == 0) | (data.type == 1)][['glucose']]

    earliest_date, latest_date = data.index.min().date(), data.index.max().date() + td(days=1)  # min and max date range
    min_date = max(earliest_date, latest_date - td(days=days or 91))  # adjust min date to show default 13 weeks
    if not days:
        min_date += td(days=(0, 6, 5, 4, 3, 2, 1,)[min_date.weekday()])  # align min date to a week start (monday)
    all_days = tuple(pd.date_range(start=earliest_date, end=latest_date, freq='1D'))
    weekends = tuple(d for d in all_days if d.isoweekday() in (6, 7))

    daily_data = data.groupby(data.index.date)['glucose']
    data['daily max'] = daily_data.transform(max)
    data['daily average'] = daily_data.transform(average)
    data['daily min'] = daily_data.transform(min)
    data['daily range'] = daily_data.transform(lambda x: max(x) - min(x))
    data['daily stddev'] = daily_data.transform(stddev)
    for rolling_window in ('24h', '7d', '28d', '91d'):
        data['%s rolling average' % rolling_window] = data.glucose.rolling(rolling_window).mean()

    columns = tuple(data.columns)
    charts = ([c for c in columns if not c.startswith('daily')],)
    charts += ([c for c in columns if c not in charts[0] and all(not c.endswith(x) for x in ('stddev', 'range'))],)
    charts += ([c for c in columns if c not in charts[0] + charts[1]],)

    # need to import late to avoid exception due to conflict with tkinter
    from matplotlib import pyplot as plt
    # noinspection PyTypeChecker,SpellCheckingInspection
    for ax in (data[chart].plot(ax=fig)
               for fig, chart in zip(plt.subplots(nrows=len(charts), ncols=1, sharex=True,
                                                  gridspec_kw={'height_ratios': (4,) + (1,) * (len(charts) - 1),
                                                               'left': 0.04, 'right': 0.96, 'bottom': 0.09, 'top': 0.99,
                                                               'wspace': 0, 'hspace': 0.05, })[1], charts)):
        ax.set(facecolor='xkcd:off white')  # set background color
        ax.grid(b=True)  # show grid-lines
        ax.margins(x=0, y=0.05)  # adjust figure margins
        ax.tick_params(axis='x', rotation=90, bottom=True, top=False, direction='out')  # set x tick params
        ax.xaxis.set_major_locator(md.DayLocator())  # set x axis major grid to date
        ax.xaxis.set_major_formatter(md.DateFormatter('%b-%d'))  # set x axis label format
        ax.set_xlim(left=min_date, right=latest_date)  # set x axis min and max range to show
        _, legend = ax.get_legend_handles_labels()
        y_min = min(data.loc[min_date:latest_date][legend].min().min().astype(int), 2)
        y_max = data.loc[min_date:latest_date][legend].max().max().astype(int) + 2
        ax.set_yticks(range(0, y_max, 4))  # y axis min, max, and ticks
        ax.set_ylim(bottom=y_min, top=y_max)  # set y axis min and max range to show
        ax.set(xlabel='', ylabel='mmol/L')  # set axis label
        ax.tick_params(axis='y', labelright=True, right=True, left=True, direction='out')  # set y tick params
        ax.legend(ncol=len(legend), framealpha=0.5, loc='upper right')  # legend format
        for i, label in enumerate(ax.xaxis.get_ticklabels()):
            label.set_horizontalalignment('left')  # align label left of tick
        for w in weekends:
            ax.axvspan(w, w + td(days=1), color='xkcd:light tan')  # vertical band for weekends
        legend_str = ' '.join(legend)
        if all(s not in legend_str for s in ('range', 'stddev')):
            ax.axhspan(ymin=3.9, ymax=6.8, color='xkcd:lime green')  # highlight target glucose range
            ax.axhspan(ymin=0, ymax=3.9, color='xkcd:light orange')  # highlight low glucose range
        for d in all_days:
            # vertical line every six hours highlighted by white on both sides
            for hour, color in ((d, 'xkcd:grey'), (d + td(hours=6), 'xkcd:saffron'),
                                (d + td(hours=12), 'xkcd:sky blue'), (d + td(hours=18), 'xkcd:orange')):
                ax.axvspan(hour - td(minutes=1), hour - td(minutes=1), color='xkcd:off white')
                ax.axvspan(hour + td(minutes=1), hour + td(minutes=1), color='xkcd:off white')
                ax.axvspan(hour, hour, color=color)

        def format_coord(chart_legend):
            def status_str(x, _):
                loc = data.index.searchsorted(md.DateFormatter('%Y-%m-%d %H:%M:%S')(x), side='right')
                loc -= 1 if loc > 0 else 0
                val = data.iloc[loc][chart_legend]
                return (val.name.strftime('%a %Y-%m-%d %H:%M:%S' if chart_legend == 0 else '%a %Y-%m-%d')
                        + ''.join([' %s:%1.2f' % (c, v) for c, v in val.to_dict().items()]))

            return status_str

        ax.format_coord = format_coord(legend)

    plt.get_current_fig_manager().set_window_title('glucose')  # set title
    plt.show()


if __name__ == '__main__':
    from sys import argv

    try:
        if len(argv) == 1:
            plot()
        elif len(argv) == 2:
            plot(filename=argv[1])
        elif len(argv) == 3:
            plot(filename=argv[1], days=int(argv[2]))
    except Exception as e:
        import traceback

        print('Traceback (trace limit 2):')
        traceback.print_tb(e.__traceback__, limit=2)
        print('Exception {} occurred at line {}\n{}'.format(type(e).__name__, e.__traceback__.tb_next.tb_lineno, e))
