import numpy as np
from SkyNEt.config.config_class import config_class
import os

class experiment_config(config_class):
    '''
    This is the config for testing the convergence of increasing sample time.
    
    '''
    def __init__(self):
        super().__init__()      

        self.device = 'NN' # Specifies whether the experiment is used on the NN or on the physical device. Is either 'chip' or 'NN'
        self.main_dir = r'..\\..\\test\\'
        self.NN_name = 'checkpoint3000_02-07-23h47m.pt'
        self.verbose = True
        #######################
        # Physical parameters #
        #######################

        self.controls = 7        
        self.staticControls = 0.6*np.array([1,1,1,1,1,1,1])       
        self.freq = np.array([2,3,5,9,13,19,23])
        self.sampleTime = np.round(np.linspace(0.1,10,100),3) #/ self.freq[0]
        self.fs = 1000
        self.n = 10               # Amount of iterations

        self.amplification = 100
        self.postgain = 1
        
        self.waveAmplitude = 0.02*np.ones(7) #np.array([0.07, 0.05, 0.05, 0.03, 0.03, 0.005, 0.005])   # Amplitude of the waves used in the controls
        self.rampT = 0.5           # time to ramp up and ramp down the voltages at start and end of a measurement.
        self.name = 'name'
        #                        Summing module S2d      Matrix module           device
        # For the first array: 7 is always the output, 0 corresponds to ao0, 1 to ao1 etc.
        self.electrodeSetup = [[0,1,2,3,4,5,6,7],[1,3,5,7,11,13,15,17],[5,6,7,8,1,2,3,4]]
        
        self.controlLabels = ['ao0','ao1','ao2','ao3','ao4','ao5']
        
        ###################
        # rest parameters #
        ###################
          
        self.phase_thres = 90 # in degrees
        self.filepath =  r'filepath'
    
        self.configSrc = os.path.dirname(os.path.abspath(__file__))
        self.gainFactor = self.amplification/self.postgain
        
        
    def lock_in_gradient(self, output, freq, A_in, fs=1000, phase_thres=90): 
        ''' This function calculates the gradients of the output with respect to
        the given frequencies using the lock-in method and outputs them in the 
        same order as the frequencies are given.
        output:         output data to compute derivative for
        freq:           frequencies for the derivatives
        A_in:           amplitude used for input waves
        fs:             sample frequency
        phase_thres:    threshold for the phase of the output wave, determines whether the gradient is positive or negative
        '''
        
        t = np.arange(0,output.shape[0]/fs,1/fs)
        y_ref1 = np.sin(freq[:,np.newaxis] * 2*np.pi*t)
        y_ref2 = np.sin(freq[:,np.newaxis] * 2*np.pi*t + np.pi/2)
        
        y_out1 = y_ref1 * (output - np.mean(output))
        y_out2 = y_ref2 * (output - np.mean(output))
        
        amp1 = (np.mean(y_out1,axis=1)) # 'Integrating' over the multiplied signal
        amp2 = (np.mean(y_out2,axis=1))
        
        A_out = 2*np.sqrt(amp1**2 + amp2**2)
        phase_out = np.arctan2(amp2,amp1)*180/np.pi
        sign = 2*(abs(phase_out) < phase_thres) - 1
        
        return sign * A_out/A_in, phase_out