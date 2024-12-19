import pathlib

"""
Plotting utility class.

Handles all data visualization tasks.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import pathlib
import numpy as np

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
        font_path = pathlib.Path(__file__).parent / "fonts" / "Inter.ttf"
        print(font_path)

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


    def make_table_plot_from_dictionary(self, this_dict,
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


    def make_bar_plot_from_dictionary(self, this_dict,
                                      figsize=(10, 8),
                                      title=None,
                                      num_elements=10,
                                      saveas=None,
                                      xlabel='Counts',
                                      exclusions=[]):

        # Sum up total items before processing
        total_items = sum(this_dict.values())

        data = list(this_dict.items())[:num_elements]
        labels, counts = zip(*data)

        # Handle nans
        labels_new = ['nan' if x is np.nan else x for x in labels]
        labels_new = ['None' if x is None else x for x in labels_new]

        # Filter out excluded labels
        exclusion_count = 0
        for exclusion in exclusions:
            if exclusion in labels_new:
                exclusion_count += 1
                idx = labels_new.index(exclusion)
                labels_new.pop(idx)
                counts = counts[:idx] + counts[idx+1:]

        # Create a horizontal bar chart
        plt.figure(figsize=(10, 6))
        plt.barh(labels_new, counts, color=VF_LIGHT)
        plt.xlabel(xlabel)
        plt.title(title, loc='center')
        plt.gca().invert_yaxis()  # Invert y-axis to have the highest count on top

        # Add annotation for num_elements
        plt.text(0.95, 0.05,
                 f"""
                 Up to {num_elements - exclusion_count} elements shown.
                 Total count: {total_items}
                 """,
             transform=plt.gca().transAxes,
             ha='right', va='bottom', fontsize=10,
             style='italic', color='gray')

        # Add text labels
        for i, v in enumerate(counts):
            plt.text(v, i, f' {v:,}', va='center')

        if saveas is not None:
            plt.savefig(str(pathlib.Path(OUTPUT_PATH) / saveas))

        plt.show()
        plt.close()
