#!/usr/bin/env python

'''svetplot.py: Script to plot graphs from SVET data (in batches)'''

__author__     = 'Camilo A. F. Salvador'
__email__      = "csalvador@usp.br"
__copyright__  = 'Copyright 2020, University of Sao Paulo'
__credits__    = ['Camilo A. F. Salvador', 'Eloa L. Maia']

'''
Comments on the script:
- Data will be loaded from /csv and plotted to /results
- *.csv files must have '_' on their names -- see lines 104-105
- In the *.csv files: [YPSDInPh_uApsqcm] represents the SVET current (mA); [X] and [Y] are abs coordinates
- One (common) range is defined to all colormaps; the script will plot an independent colorbar with the selected range
- A html report is saved suggesting a contrast range for the colormaps
'''

# -- start --

import math
import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.pyplot import figure

# Static variables
all_entries = []
MAX_Z = []
MIN_Z = []
report = ['--- report log ---<br />']

# Define the desired style/colorscale
plt.style.use('seaborn-deep')
CMAP = mpl.cm.PuOr_r

# Define the range, normalization method and color to the colorbar
LMIN_Z = -2000
LMAX_Z = 2000

# Linear colorscale
NORM = mpl.colors.Normalize(vmin=LMIN_Z, vmax=LMAX_Z)

## Power colorscale
# NORM = mpl.colors.PowerNorm(gamma=0.75, vmin=LMIN_Z, vmax=LMAX_Z) # gamma controls the contrast; gamma = 1 (linear interpol.)
## Log colorscale
# NORM = norm=colors.SymLogNorm(linthresh=0.1, linscale=0.1, vmin=LMIN_Z, vmax=LMAX_Z)

results_dir = os.path.join(os.path.abspath(os.curdir), 'results/')
try:
    os.mkdir(results_dir)
except OSError:
    print ('Directory already exists')
else:
    print ('Successfully created the directory: {}'.format(results_dir))

'''
Data structure
'''
class data(object):
    def __init__(self, name, dataframe):
    	self.name = name									# a name (string)
    	self.df = dataframe 								# a dataframe (pandas)

    # The following lines are required for printing and sorting
    def __repr__(self):
        return '\n{}'.format(self.df)
# end of class data(object)


'''
Phase 1 - Loading the data
'''
def load_data():
	# Method to load the data
	csv_dir = os.path.join(os.path.abspath(os.curdir), 'csv') 
	print ('Loading from directory {}'.format(csv_dir))		# current dir/csv

	entries = os.listdir(csv_dir)
	print ('Entries found:\n{}'.format(entries))

	for entry in entries:

		entry_dir = os.path.join(csv_dir, entry)			# full path to each csv entry

		df = pd.read_csv(entry_dir)							# imports the database

		fdf = df[['X', 'Y', 'YPSDInPh_uApsqcm']]  			# filtering the dataframe
		fdf = fdf.drop(fdf.index[0])						# excluding 1st line
		fdf = fdf.drop(fdf.index[-1])						# excluding the last line

		# helps checking the colorbar limits 
		MAX_Z.append(max(fdf['YPSDInPh_uApsqcm'].values))
		MIN_Z.append(min(fdf['YPSDInPh_uApsqcm'].values))

		base = os.path.basename(entry_dir)					# gets the name w/ extension
		base = os.path.splitext(base)[0]					# excludes the extension [1]
		name = base.split('_')								# breaks name at the '_'
		name = repr(name[8])								# use name[8] for raw data

		dataframe = data(name, fdf)							# creates a data() instance
		all_entries.append(dataframe)						# stores all data objects

	return all_entries
# end of method load_data

'''
Phase 2 - Plotting the data
'''
def plot_data(data):
	all_entries = data
	results_dir = os.path.join(os.path.abspath(os.curdir), 'results/')
	lresults_dir = results_dir
	print('Exporting data to {}'.format(results_dir))

	# Rule of thumb for contrast
	min_z = np.median(MIN_Z)/2
	max_z = np.median(MAX_Z)/2

	# Updating the report
	report.append('Colorscale should be ranged from i = {} to {}'.format(min_z, max_z))
	report.append('<br />')

	for entry in all_entries:

		# Exporting each entry as a *.csv 
		filename = ('{}.csv'.format(entry.name))
		filepath = r'{}'.format(results_dir)
		entry.df.to_csv(filepath+filename, index = None, header = True)

		# Passing on the static range
		min_z = LMIN_Z 
		max_z = LMAX_Z 

		# Pre-processing the data to obtain the plot
		x = entry.df['X'].values
		y = entry.df['Y'].values
		z = entry.df['YPSDInPh_uApsqcm'].values

		# Setting the aspect ratio
		x_dim = int((max(x) - min(x)))/1000
		y_dim = int((max(y) - min(y)))/1000
		print ('The figure dimensions were set to x:{} y:{}'.format(x_dim, y_dim))

		# added room for labels - adjust size if needed
		plt.rcParams["figure.figsize"] = ((x_dim)*1.400, (y_dim)*1.725)
		axes = plt.gca()
		axes.set_xlim([min(x),max(x)])
		axes.set_ylim([min(y),max(y)])
		
		# Countour plot 
		fig, ax = plt.subplots()	
		plot = ax.tripcolor(x,y,z, cmap=CMAP, vmin=min_z, vmax=max_z)
		plot = ax.plot(x,y, 'ko ', alpha=0.2)

		# Save a static image
		filename = ('{}.png'.format(entry.name))
		plt.tight_layout()
		fig.savefig(filepath+filename, dpi=150)


		# Additional plot with a mild interpolation (20)
		fig, ax = plt.subplots()	
		plot = ax.tricontourf(x,y,z, 20, cmap=CMAP, vmin=min_z, vmax=max_z)
		# plot = ax.plot(x,y, 'ko ')						# use it if you want display each data point	

		# Save a static image
		filename = ('trif_{}.png'.format(entry.name))
		plt.tight_layout()
		fig.savefig(filepath+filename, dpi=150)

		# Saving report info
		report.append('---Tripcolor plot for {} saved'.format(entry.name))
		report.append('---<br />')
		report.append('---Tricontourf plot for {} saved'.format(entry.name))
		report.append('---<br />')

	report.append('--- end of report ---')
	with open('results/report.html', 'a') as freport:
		freport.write("\n{}".format(report))

# end of method fit_data(data)

plot_data(load_data())										# calls both methods


'''
Phase 3 - Plotting the colorbar
'''
print ('\nFinal step... plotting the colorbar\n')

plt.rcParams.update({'font.size': 16})
fig, ax = plt.subplots(figsize=(2, 4))
fig.subplots_adjust(left=0.1)

# Change the colomap here too 
norm = mpl.colors.Normalize(vmin=LMIN_Z, vmax=LMAX_Z)

cb1 = mpl.colorbar.ColorbarBase(ax, cmap=CMAP,
                                norm=norm,
                                orientation='vertical')
cb1.set_label('Current (uA)')
plt.tight_layout()
#plt.show()

# Save a static image
fig.savefig('results/colorbar.png', dpi=150)

# -- end --
