"""
Plotting utility class.

Handles all data visualization tasks.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import pathlib
import numpy as np
import src.utils as utils

OUTPUT_PATH = 'outputs/'
VF_BLUE_DARK = '#00224e'
VF_BLUE = '#0056c4'
VF_BLUE_LIGHT = '#3292fb'
VF_LIGHT = '#9fcaf8'
VF_YELLOW = '#fbaf00'

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

        # Add font path to 'Inter' - Battery Report font
        font_path = pathlib.Path(__file__).parent.parent / "data" / "fonts" / "Inter.ttf"

        # Add the font
        fm.fontManager.addfont(str(font_path))

        if style == 'default':
            font = 'Inter'
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


    def make_table_plot_from_dict(self, this_dict,
                                  figsize=(10, 8),
                                  title=None,
                                  saveas=None
                                  ):
        """
        Starting with a dictionary, make a table and plot it.
        """

        table_data = [[k, v] for k, v in this_dict.items()]

        # Format the table to look more presentable
        for entry in table_data:
            if isinstance(entry[1], (int, np.integer)):
                entry[1] = f'{entry[1]:,}'
            elif isinstance(entry[1], (float, np.floating)):
                entry[1] = f'{entry[1]:.3f}'
            elif isinstance(entry[1], (str)):
                entry[1] = f'{entry[1]}'
            else:
                entry[1] = f'{type(entry[1])}'

        fig, ax = plt.subplots(figsize=figsize)
        ax.axis('off')
        ax.axis('tight')

        table = ax.table(cellText=table_data,
                        colLabels=['Key', 'Value'],
                        cellLoc='left',
                        loc='center')
        table.set_fontsize(12)
        plt.suptitle(title, x=0.02, y=0.93, ha='left')

        if saveas is not None:
            plt.savefig(str(pathlib.Path(OUTPUT_PATH) / saveas))

        plt.show()
        plt.close()


    def make_bar_plot_from_dict(self, input_dict,
                                figsize=None,
                                title=None,
                                num_elements=10,
                                saveas=None,
                                xlabel='Counts',
                                exclusions=[],
                                sorted=False,
                                replacements=None):


        this_dict = input_dict.copy()

        # Dictionary key replacements for figure aesthetics
        if replacements is not None:
            for k, v in replacements.items():
                if k in this_dict.keys():
                    this_dict[v] = this_dict.pop(k)

        # Peroform the sort
        if sorted:
            this_dict = utils.sort_dict(this_dict)

        data = list(this_dict.items())[:num_elements]
        labels, counts = zip(*data)

        # Keep things in strings instead of floats
        labels_new = ['nan' if x is np.nan else x for x in labels]
        labels_new = ['None' if x is None else x for x in labels_new]
        labels_new = ['False' if x is False else x for x in labels_new]
        labels_new = ['True' if x is True else x for x in labels_new]

        # Handle exclusions
        filtered_data = [(label, count) \
                         for label, count in zip(labels_new, counts) \
                         if label not in exclusions]

        # Check if there is any data left after filtering
        if filtered_data:
            labels_new, counts = zip(*filtered_data)
        else:
            labels_new, counts = [], []

        # Recalculate the total items after exclusions
        total_items = sum(counts)

        # Create a horizontal bar chart
        this_figsize = figsize if figsize is not None else \
            (6, 0.5 * (num_elements - len(exclusions)))
        plt.figure(figsize=this_figsize)
        plt.barh(labels_new, counts, color=VF_BLUE_DARK)
        plt.xlabel(xlabel)
        plt.title(title, loc='center')
        plt.gca().invert_yaxis()  # Invert y-axis to have the highest count on top

        # Add annotation for num_elements
        plt.text(0.95, 0.05,
                 f"""
                 Up to {num_elements - len(exclusions)} elements shown.
                 Total count: {total_items}
                 """,
             transform=plt.gca().transAxes,
             ha='right', va='bottom', fontsize=10,
             style='italic', color='gray')

        # Add text labels; figure out the logic for numeric labels later;
        # this only works for categorical labels where the y-values auto-increment
        all_numeric = all(isinstance(label, (int, float)) for label in labels_new)
        if all_numeric:
            pass
        else:
            for i, v in enumerate(counts):
                plt.text(v, i, f' {v:,}', va='center')

        if saveas is not None:
            plt.savefig(str(pathlib.Path(OUTPUT_PATH) / saveas))

        plt.show()
        plt.close()
