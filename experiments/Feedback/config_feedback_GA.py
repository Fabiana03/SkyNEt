# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 16:43:24 2019

@author: Jardi
"""

import SkyNEt.experiments.boolean_logic.config_evolve_NN as config
import numpy as np

class config_feedback_GA(config.experiment_config):
    
    def __init__(self):
        super().__init__()
        
        self.generations = 10
        self.mutationrate = 0.1
        self.generange = [[-1.2,1.2], [-1.2,1.2], [-1.2,1.2], [-1.2,1.2], [-1,1], [-1,1], [-2, 2], [-5, 5], [0, 100]]
#        self.input_scaling = 0.9

        # Specify either partition or genomes
        self.partition = [5, 5, 5, 5, 5]
        
        self.skip = 200
        self.vir_nodes = 100
        self.output_nodes = 50
        self.input_electrode = 3
        self.theta = 1
        
        self.Fitness = self.getMC

        # Documentation
        self.genelabels = ['CV1','CV2','CV3','CV4','CV5','CV6','Input_gain','Feedback_gain','theta']

        # Save settings
        self.filepath = r'../../../Resultaten/GA/'
        self.name = 'feedback'
        
        self.genomes = sum(self.partition)  # Make sure genomes parameter is correct
        self.genes = len(self.generange)  # Make sure genes parameter is correct
        
    def getMC(self, outputs, weights, targets):
        prediction = np.dot(weights, np.transpose(outputs[self.skip+self.output_nodes:,:]))

        MCk = np.full(self.output_nodes, np.nan)
        for i in range(self.output_nodes):
            MCk[i] = np.corrcoef(targets[:,i], prediction[i,:])[0,1]**2
        return sum(MCk), MCk
        