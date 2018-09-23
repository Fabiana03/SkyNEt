import numpy as np
from config.config_class import config_class

class experiment_config(config_class):
    '''This is a template for the configuration class that is experiment/user specific.
    It inherits from config_class default values that are known to work well with boolean logic.
    You can define user-specific parameters in the construction of the object in __init__() or define
    methods that you might need after, e.g. a new fitness function or input and output generators.
    Remember if you define a new fitness function or generator, you have to redefine the self.Fitness,
    self.Target_gen and self.Input_gen in __init__()
    '''

    def __init__(self):
        super().__init__() #DO NOT REMOVE!

        #define experiment
        self.amplification = 10 #makes up for the different IVVI amplifications, 1G = 1 and 1M = 1000 such that the output is in nA
        self.TargetGen = self.NOR
        #self.partition = [2, 2, 2, 2, 2]
        self.generations = 1
        self.genomes = 10000
        self.fs = 4000
        self.signallength = 8
        self.edgelength = 0.1
        self.lenpart = int(self.genomes/5)
        self.partition = [self.lenpart, self.lenpart, self.lenpart, self.lenpart, self.lenpart]


        ################################################
        ######### USER-SPECIFIC PARAMETERS #############
        ################################################

        ################# Save settings ################
        self.filepath = r'D:\Tao\TCSP2\\'
        self.name = 'SP'

        ############## New Fitness function ############

        ################################################
        ################# OFF-LIMITS ###################
        ################################################
        self.genomes = sum(self.partition)  # Make sure genomes parameter is correct
        self.genes = len(self.generange)  # Make sure genes parameter is correct

    #####################################################
    ############# USER-SPECIFIC METHODS #################
    #####################################################



        pass
