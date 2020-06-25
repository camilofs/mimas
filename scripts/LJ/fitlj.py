#!/usr/bin/env python

'''fitlj.py: Script to fit Leonard-Jones to an energy(distance) file'''

__author__     = 'Camilo A. F. Salvador'
__email__      = "csalvador@usp.br"
__copyright__  = 'Copyright 2020, University of Sao Paulo'

'''
Comments on the script:
- Data will be loaded from 'filename' (.csv)
- *.csv file must contain e(r) data 
- The script will write the coefficients for LJ, plot a graph and save the results
'''

# -- start --

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn-pastel')

# Static variables
filename = 'csv/O_O.csv'

# Importing database
df = pd.read_csv(filename)

# Selecting an appropriate range of instances
uul = df['u'] < 0.001
ull = df['u'] > -0.05
fdf = df [uul & ull]			# filtered-dataframe
# rul = df['r'] < 5
# df = df [rul]

from scipy.optimize import curve_fit
from matplotlib.ticker import ScalarFormatter

# Defining a function (func) to fit the data
def func(x, e, s):				# as defined Leonard-Jones function
    return 4*e*(((s/x)**12)-((s/x)**6))

x = fdf['r'].values				# the fitting will use filtered data, from fdf
y = fdf['u'].values

# Fitting the data
popt, pcov = curve_fit(func, x, y, maxfev=100000, method='lm')
print("Parameters from the fit: \ne = {} \ns = {}".format(popt[0], popt[1]))

# Calculating 'u_calc' and printing errors
y2 = func(x, *popt) 			# the calc. energy (u_calc) based on the fit
mse = np.mean((y-y2)**2)		# the equation for the mean-squared-error
print ("MSE: {}".format(mse))	# print the error

# Exporting *.csv with the results
edf = pd.DataFrame(y2, columns=['u_calc'])
fdf = pd.concat([df, edf], axis=1, sort=False)
fdf.to_csv(r'csv/Results.csv', index = None, header = True)

# Plot and save a static image
fig = plt.figure()

# icyn to set the axes size
# ax = plt.axes(xlim=(2, 8), ylim=(-0.03, 0.05))		

plt.title("Energy vs distance")
plt.xlabel('rij (angstrom)')
plt.ylabel('energy u (eV)')
plt.plot(x, y, 'ro', label='Data')
plt.plot(x, func(x, *popt), 'b-', label='Fit')

name = filename.split('.')
plt.savefig(name[0]+'.png',dpi=150)
plt.legend()
plt.show()

# -- end --