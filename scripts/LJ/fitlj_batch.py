#!/usr/bin/env python

'''fitlj_batch.py: Script to fit Leonard-Jones to energy(distance) files (batch)'''

__author__     = 'Camilo A. F. Salvador'
__email__      = "csalvador@usp.br"
__copyright__  = 'Copyright 2020, Camilo A. F. Salvador'

'''
Comments on the script:
- Data will be loaded from the /csv folder
- *.csv files must contain e(r) data 
- The script will write the coefficients for LJ, save graphs and the results
'''

# -- start --

import numpy as np
import pandas as pd
import os
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
plt.style.use('tableau-colorblind10')						# matplolib styles

# Static variables 
all_entries = []

# Creating (checking) a results/ dir 
results_dir = os.path.join(os.path.abspath(os.curdir), 'results/')
try:
    os.mkdir(results_dir)
except OSError:
    print ('Directory already exists')
else:
    print ('Successfully created the directory: {}'.format(results_dir))

'''
Data class
'''
class data(object):
    def __init__(self, name, dataframe):
    	self.name = name									# a name (string)
    	self.df = dataframe 								# a dataframe (pandas)

    # The following lines are required for printing and sorting
    def __repr__(self):
        return '\n{}'.format(self.df)
# end of class data(object)

def load_data():
	# Method to load the data
	csv_dir = os.path.join(os.path.abspath(os.curdir), 'csv') 
	print ('Loading from directory {}'.format(csv_dir))		# current dir/csv

	entries = os.listdir(csv_dir)
	print ('Entries found:\n{}'.format(entries))

	for entry in entries:
		entry_dir = os.path.join(csv_dir, entry)			# full path for each entry

		df = pd.read_csv(entry_dir)							# imports the database
		
		uul = df['u'] < 0.01								# filtering the dataframe
		ull = df['u'] > -0.05								# ...
		fdf = df [uul & ull]								# ... done
		#fdf = df
		
		base = os.path.basename(entry_dir)					# gets the name w/ extension
		name = os.path.splitext(base)[0]					# excludes the extension [1]

		dataframe = data(name, fdf)							# creates a data() instance
		all_entries.append(dataframe)						# stores all data objects

	return all_entries
# end of method load_data


def func(x, e, s):
	# Method to define a function (func) to fit the data			
    return 4*e*(((s/x)**12)-((s/x)**6))						# Leonard-Jones
# end of method func

report = ['--- report log ---']

def fit_data(data):
	all_entries = data
	results_dir = os.path.join(os.path.abspath(os.curdir), 'results/')
	print('Exporting data to {}'.format(results_dir))

	for entry in all_entries:
		x = entry.df['r'].values
		y = entry.df['u'].values

		# Fitting the data
		popt, pcov = curve_fit(func, x, y, maxfev=100000, method='lm')
		
		# Calculating 'u_calc' and printing errors
		y2 = func(x, *popt) 								# the calc. energy (u_calc) based on the fit
		mse = np.mean((y-y2)**2)							# the equation for the mean-squared-error
		
		# Printing info
		print ('---')
		print ('Data for {}'.format(entry.name))
		print ('Parameters from the fit: \ne = {} \ns = {}'.format(popt[0], popt[1]))
		print ('MSE: {}'.format(mse))						# print the error
		print ('---')
		print ('Exporting data to {}'.format(results_dir))

		# Saving info
		report.append('---')
		report.append('Data for {}'.format(entry.name))
		report.append('Parameters from the fit: e = {} s = {}'.format(popt[0], popt[1]))
		report.append('MSE: '.format(mse))
		report.append('---')
		
		# Exporting *.csv with the results
		edf = pd.DataFrame(y2, columns=['u_calc'])
		fdf = pd.concat([entry.df, edf], axis=1, sort=False)
		
		filename = ('{}.csv'.format(entry.name))
		filepath = r'{}'.format(results_dir)
		fdf.to_csv(filepath+filename, index = None, header = True)

		# Plot and save a static image
		filename = ('{}.png'.format(entry.name))
		fig = plt.figure()
		#ax = plt.axes(xlim=(2, 8), ylim=(-0.03, 0.05))		# icyn to set the axes size
		plt.title('{} interaction'.format(entry.name))
		plt.xlabel('Rij (angstrom)')
		plt.ylabel('Energy (eV)')
		plt.plot(x, y, 'ro', label='Data')
		plt.plot(x, func(x, *popt), 'b-', label='Fit')
		plt.savefig(filepath+filename,dpi=600)
		plt.legend()

	report.append('--- end of report ---')
	with open('results/report.txt', 'a') as freport:
		freport.write("\n{}".format(report))

# end of method fit_data(data)

fit_data(load_data())										# calls both methods

# -- end --

