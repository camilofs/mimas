#!/usr/bin/env python

'''degree.py: Calculate the degree of collapse from beta to omega'''

__author__     = 'Camilo A. F. Salvador'
__email__      = "csalvador@usp.br"

'''
Atom class to contain the positions (x, y, z) of a single atom
deg = the degree of collapse, from 0 (beta) to 0.66 (fully-collapsed omega)
CONTCAR files must be clear - keep only the atomic positions
'''
# -- start --

import os
import sys
import numpy as np

script_dir = os.path.dirname(__file__)
input_path = os.path.join(script_dir, "CONTCAR")
output_path = os.path.join(script_dir, "out.txt")

beta_pos = np.array([0, 1/6, 1/3, 1/2, 2/3, 5/6, 1]) # the beta original positions
delta = (((1/6)/3)/2) # the expected +/- shift from original positions 

atoms = [] # a list of objs (Atom)

class Atom(object):
    def __init__(self):
        self.number = 666
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.degx = 0.0
        self.degy = 0.0
        self.degz = 0.0
        self.deg = 0.0

    def get_deg(self):
        return self.deg

    def __str__(self):
    	print_output = "Atom {}\n{} {} {}\n Deg {}\n".format(self.number, self.x, self.y, self.z, 
    		self.deg)
    	return print_output

    def __repr__(self):
    	print_output = "Atom {}\n{} {} {}\n Deg {}\n".format(self.number, self.x, self.y, self.z, 
    		self.deg)
    	return print_output

'''
Find the closest number to a sorted array
'''
def find_closest(A, target):
    #A must be sorted
    idx = A.searchsorted(target)
    idx = np.clip(idx, 1, len(A)-1)
    left = A[idx-1]
    right = A[idx]
    idx -= target - left < right - target
    return idx

'''
Load the atom positions from a single CONTCAR file
'''

def load_atoms():
	i = 1
	for line in open(input_path):
		atom = Atom()
		atom.number = i
		atom.x = float(line.split('  ')[1])
		# calculating the degree of collapse relative to x
		near_idx = find_closest(beta_pos, atom.x)
		atom.degx = abs((atom.x - beta_pos[near_idx])/delta)
		if atom.degx > 1:
			res = atom.degx - 1
			atom.degx = 1 - res
		#
		atom.y = float(line.split('  ')[2])
		# calculating the degree of collapse relative to y
		near_idx = find_closest(beta_pos, atom.y)
		atom.degy = abs((atom.y - beta_pos[near_idx])/delta)
		if atom.degy > 1:
			res = atom.degy - 1
			atom.degy = 1 - res
		#
		atom.z = float(line.split('  ')[3])
		# calculating the degree of collapse relative to z
		near_idx = find_closest(beta_pos, atom.z)
		atom.degz = abs((atom.z - beta_pos[near_idx])/delta)
		if atom.degz > 1:
			res = atom.degz - 1
			atom.degz = 1 - res
		#
		atom.deg = (atom.degx + atom.degy + atom.degz)/3
		i += 1
		atoms.append(atom)
		
load_atoms()
print (atoms)

mean_deg = np.mean([atom.deg for atom in atoms])
sd_deg = np.std([atom.deg for atom in atoms])

print ('The final degree of collapse is: {} +/- {}\n'.format(mean_deg, sd_deg))
print ('the degree of collapse goes from 0 (beta) to 0.66 (fully-collapsed omega)')

# -- end --

