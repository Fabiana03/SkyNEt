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
import instruments.InstrumentImporter
import time
#import evolve_VCdim as vcd
import measure_VCdim as vcd
import numpy as np
from matplotlib import pyplot as plt
import time
import os

inputs = [[-0.7,0.7,-0.7,0.7,-0.35, 0.35],[-0.7,-0.7,0.7,0.7, 0., 0.]] ## MAYBE NEEDS TO BE ADAPTED!!
#[[-0.9,0.9,-0.9,0.9,0,0],[-0.9,-0.9,0.9,0.9,-0.6,0.6]]
N=len(inputs[0])
#Create save directory
filepath0 = r'D:/data/Hans/Results/VC_dim' # evolution_test/VCdim_testing'#
filepath1 = filepath0+'/Capacity_N'+str(N)
date = time.strftime('%Y_%m_%d_%H-%M_missclassif-2019_04_18_17-06')
dirname = filepath1+'/'+date+'/'
if os.path.exists(filepath0):
    os.makedirs(dirname)
else:
    assert 1==0, 'No directory created. Parent target directory '+filepath0+' does not exist'
    
# Create binary labels for N samples
bad_gates = [1,2,3,4,5,6,7,9,11,13,14,15,17,18,19,21,22,23,25,26,33,35,36,37,38,39,41,43,44,45,46,47,49,53,55,57,60,61,62]
binary_labels = bintarget(N)[bad_gates].tolist() 
#binary_labels = bintarget(N).tolist()  
threshold = (1-0.5/N)#1-(0.65/N)*(1+1.0/N)
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

np.savez(dirname+'Summary_Results',
         inputs = inputs,
         binary_labels = binary_labels,
         capacity = capacity,
         found_classifier = found_classifier,
         fitness_classifier = fitness_classifier,
         accuracy_classifier = accuracy_classifier,
         output_classifier = output_classifier,
         genes_classifier = genes_classifier)

plt.figure()
plt.plot(fitness_classifier,accuracy_classifier,'o')
plt.plot(np.linspace(np.nanmin(fitness_classifier),1.0),threshold*np.ones_like(np.linspace(0,1)),'-k')
plt.xlabel('Fitness')
plt.ylabel('Accuracy')
plt.show()

vcd.reset(0, 0)

try:
    not_found = found_classifier==0
    print('Classifiers not found: %s' % np.arange(len(found_classifier))[not_found])
    binaries_nf = np.array(binary_labels)[not_found]
    print('belongs to : \n', binaries_nf)
    output_nf = output_classifier[not_found]
    plt.figure()
    plt.plot(output_nf.T)
    plt.legend(binaries_nf)
    plt.show()
except:
    print('Error in plotting output!')