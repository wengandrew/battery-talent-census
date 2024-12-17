import pathlib

"""
Plotting utility class.

Handles all data visualization tasks.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pathlib

OUTPUT_PATH = 'outputs/'

class Plotter:


    def __init__(self, style='default'):
        """
        Initialize the plotter

        Style: 'default', 'ieee'
        """

        self.set_aesthetics(plt, style)


    def set_aesthetics(self, plt, style='default'):
        """
        Initialize the plot configuration

        Style: 'default', 'ieee'
        """

        if style == 'default':
            font = 'Helvetica'
        elif style == 'ieee':
            font = 'Times New Roman'

        plt.rc('font', **{'family'     : 'serif',
                    'serif' : [font],
                    'size': 12
                    })

        # Latex font formatting (dejavusans, dejavuserif, cm, stix, stixsans)
        plt.rcParams['mathtext.fontset'] = 'cm'

        plt.rc('figure', **{'autolayout' : True,
                        'figsize'    : (6, 4)
                        })

        plt.rc('lines', linewidth=2)

        plt.rc('xtick', labelsize='small',
                        direction='in',
                        top=True)

        plt.rc('xtick.major', width=1.0)
        # plt.rc('xtick.minor', visible=True)

        plt.rc('ytick', labelsize='medium',
                        direction='in',
                        right=True)

        plt.rc('ytick.major', width=1.0)
        # plt.rc('ytick.minor', visible=True)

        plt.rc('axes',  labelsize='medium',
                        grid=False,
                        linewidth=1.0,
                        titlelocation='left')

        plt.rc('legend', fontsize='medium',
                         frameon=False)

        plt.rc('savefig', dpi=300)


    def make_timeseries_plot(self, x, y,
                             figsize=(6,6),
                             title=None,
                             xlabel=None,
                             ylabel=None,
                             saveas=None):
        """
        Make a timeseries plot
        """

        fig = plt.figure(figsize=figsize)
        plt.plot(x, y, c='k')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
        fig.autofmt_xdate()
        plt.gca().grid(True)

        if saveas is not None:
            plt.savefig(str(pathlib.Path(OUTPUT_PATH) / saveas))

        plt.show()
        plt.close()
        # plt.savefig(OUTPUT_PATH + filename)
        # plt.close()
