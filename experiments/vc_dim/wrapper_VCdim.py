#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 12:18:29 2018
Wrapper to measure the VC dimension of a device using the measurement script measure_VCdim.py
This wrapper creates the binary labels for N points and for each label it finds the control voltages.
If successful (measured by a threshold on the correlation and by the perceptron accuracy), the entry 1 is set in a vector corresponding to all labellings.
@author: hruiz
"""
from create_binary import bintarget
try:
    import instruments.InstrumentImporter
except ModuleNotFoundError:
    print(r'No module named instruments')

import time
#import evolve_VCdim as vcd
import measure_VCdim as vcd
import numpy as np
from matplotlib import pyplot as plt
import time
import os

inputs = [[-0.7,0.7,-0.7,0.7,-0.35,0.35,0.,0.],[-0.7,-0.7,0.7,0.7,0.,0.,-1.0,1.0]]
#[[-0.7,0.7,-0.7,0.7,-0.35,0.35],[-0.7,-0.7,0.7,0.7,0.,0.]]
#[[-0.7,0.7,-0.7,0.7,-0.35,0.35,0.],[-0.7,-0.7,0.7,0.7,0.,0.,-1.0]] for paper
#[[-0.7,0.7,-0.7,0.7,-1.,1.],[-0.7,-0.7,0.7,0.7,0.,0.]]
N=len(inputs[0])
#Create save directory
filepath0 = r'D:/data/Hans/Results/VC_dim'
#r'/home/hruiz/Documents/PROJECTS/DARWIN/Data_Darwin/Results/VC_dim/Model' 
# evolution_test/VCdim_testing'#
filepath1 = filepath0+'/Capacity_N'+str(N)
date = time.strftime('%Y_%m_%d_%H-%M_Ampl-1000')
dirname = filepath1+'/'+date+'/'
if os.path.exists(filepath0):
    os.makedirs(dirname)
else:
    assert 1==0, 'No directory created. Parent target directory '+filepath0+' does not exist'
    
## Create binary labels for N samples
#binary_labels = bintarget(N).tolist()
bad_gates_dir = r'D:/data/Hans/Results/VC_dim/Capacity_N8/2019_05_30_22-53_Ampl-1000/'
bad_gates = np.load(bad_gates_dir+'Summary_Results.npz')['indx_nf']
binary_labels = bintarget(N)[bad_gates].tolist() 
print(f'Missed classifiers ({len(bad_gates)}) in previous run: \n {bad_gates}')
#bad_gates = # for N=6 on model [51]
####### On Device ########
#[55]#[22,23,48,52,53,55,57,60,61] for N=6 w. large range
# for N=6 with (+/-0.35, 0.) as inputs 5 & 6 w. range +/-[1.2,1.0]: [6,33,37,41,45,53,57,60,61]
# --> bad gates for N=6 w. range +/-0.9 and lower: [1,3,6,7,9,12,14,17,19,22,23,24,25,28,30,33,35,36,37,38,39,41,44,45,46,47,49,51,52,53,54,55,56,57,60,61,62]

threshold = (1-0.5/N)
print('Threshold for acceptance is set at: ',threshold)
#Initialize container variables
fitness_classifier = []
genes_classifier = []
output_classifier = []
accuracy_classifier = []
found_classifier = []
    
for bl in binary_labels:
    if len(set(bl))==1:
        print('Label ',bl,' ignored')
        genes, output, fitness, accuracy = np.nan, np.nan, np.nan, np.nan
        found_classifier.append(1)
    else:
        print('Finding classifier ',bl)
        
        genes, output, fitness, accuracy = vcd.evolve(inputs,bl, filepath=dirname, hush=True)
        if accuracy>threshold:
            found_classifier.append(1)
        else:
            found_classifier.append(0)
        
    genes_classifier.append(genes)
    output_classifier.append(output)
    fitness_classifier.append(fitness)
    accuracy_classifier.append(accuracy)
    
fitness_classifier = np.array(fitness_classifier)
accuracy_classifier = np.array(accuracy_classifier)
found_classifier = np.array(found_classifier)
capacity = np.mean(found_classifier)

for i in range(len(genes_classifier)):
    if genes_classifier[i] is np.nan:
        genes_classifier[i] = np.nan*np.ones_like(genes_classifier[1])
        output_classifier[i] = np.nan*np.ones_like(output_classifier[1])
        
output_classifier = np.array(output_classifier)
genes_classifier = np.array(genes_classifier)

not_found = found_classifier==0
if not_found.size > 0:
    try:
        indx_nf = np.arange(2**N)[not_found]
    except IndexError as error:
        print(f'{error} \n Trying indexing bad_gates')
        indx_nf = bad_gates[not_found]
    print('Classifiers not found: %s' % indx_nf)
    binaries_nf = np.array(binary_labels)[not_found]
    print('belongs to : \n', binaries_nf)
else:
    print('All classifiers found!')
    indx_nf = None

np.savez(dirname+'Summary_Results',
         inputs = inputs,
         binary_labels = binary_labels,
         capacity = capacity,
         found_classifier = found_classifier,
         fitness_classifier = fitness_classifier,
         accuracy_classifier = accuracy_classifier,
         output_classifier = output_classifier,
         genes_classifier = genes_classifier,
         threshold = threshold,
         indx_nf = indx_nf)

try:
    vcd.reset(0, 0)
except AttributeError: 
    print(r'module evolve_VCdim has no attribute reset')

plt.figure()
plt.plot(fitness_classifier,accuracy_classifier,'o')
plt.plot(np.linspace(np.nanmin(fitness_classifier),np.nanmax(fitness_classifier)),threshold*np.ones_like(np.linspace(0,1)),'-k')
plt.xlabel('Fitness')
plt.ylabel('Accuracy')
plt.show()

try:
    output_nf = output_classifier[not_found]
    #plt output of failed classifiers
    plt.figure()
    plt.plot(output_nf.T)
    plt.legend(binaries_nf)
    #plt gnes with failed classifiers
    plt.figure()
    plt.hist(genes_classifier[not_found,:5],30)
    plt.legend([1,2,3,4,5])
    
    plt.show()
except:
    print('Error in plotting output!')