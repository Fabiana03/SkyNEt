#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 09:31:26 2018
This script is a template to train the NN on the data loaded by DataLoader(dir), which devides the 
data into training and validation sets and returns a tensor object used by the NN class. 
@author: hruiz
"""
import numpy as np
from matplotlib import pyplot as plt
from SkyNEt.modules.Nets.staNNet import staNNet
from SkyNEt.modules.Nets.lightNNet import lightNNet
from SkyNEt.modules.Nets.DataHandler import DataLoader as dl
from SkyNEt.modules.Nets.DataHandler import GetData as gtd
#%%
###############################################################################
########################### LOAD DATA  ########################################
###############################################################################

np.random.seed(22)
Seed = False
main_dir = r'C:\Users\User\APH\Thesis\Data\wave_search\paper_chip_dataset2\2019_05_17_095928_trainData_3d\data4nn\20_05_2019\\'
file_name = 'data_for_training_lightNNet.npz'
data = dl(main_dir, file_name, syst='cpu', steps=12)
factor = 0.05
#freq = torch.sqrt(torch.tensor([2,np.pi,5,7,13,17,19],dtype=torch.float32)) * factor
freq = np.sqrt(np.array([2,np.pi,5,7,13,17,19])) * factor
amplitude = np.array([0.9, 0.9, 0.9, 0.9, 0.9, 0.5, 0.5])
offset = np.array([-0.3, -0.3, -0.3, -0.3, -0.3, -0.2, -0.2])
fs = 50
generate_input = True
noisefit = False
phase = np.zeros(7)
#phase = torch.zeros(7,dtype=torch.float32)

#%%
###############################################################################
############################ DEFINE NN and RUN ################################
###############################################################################
depth = 10
width = 90

learning_rate,nr_epochs,batch_size = 1e-3, 2, [512]

runs = 1
valerror = np.zeros((runs,nr_epochs))
trainerror = np.zeros((runs,nr_epochs))
beta1 = 0.9
beta2 = 0.75
for i in range(runs):
    if generate_input:
        net = lightNNet(data,depth,width,freq,amplitude,fs,offset,phase,noisefit)
    else:
        net = staNNet(data,depth,width)
    net.train_nn(learning_rate,nr_epochs,batch_size[i],betas=(beta1, beta2),seed=Seed)
    valerror[i] = net.L_val
    trainerror[i] = net.L_train
    print('Run nr. ',i)
    # Save every run so that they can be used to determine test error
    net.save_model(main_dir+'MSE_d'+ str(depth) + 'w90_'+str(nr_epochs)+'ep_lr1e-3_b'+str(batch_size[i])+'_b1b2_'+str(beta1) + str(beta2) + '.pt')
norm_valerror = valerror

#%%
###############################################################################
########################### LOAD NN & TEST ####################################
###############################################################################
if generate_input:
    net = lightNNet(main_dir+'MSE_n_d'+ str(depth) + 'w90_300ep_lr3e-3_b'+str(batch_size[i])+'_b1b2_'+str(beta1) + str(beta2) + '_seed.pt')
else:
    net = staNNet(main_dir+'MSE_n_d'+ str(depth) + 'w90_300ep_lr3e-3_b'+str(batch_size[i])+'_b1b2_'+str(beta1) + str(beta2) + '_seed.pt')

########################## TEST GENERALIZATION  ###############################

#file_dir = r'C:\Users\User\APH\Thesis\Data\wave_search\paper_chip\2019_04_29_133910_test_data_5h_f_0_05\test_set_skip3.npz'
file_dir = r'C:\Users\User\APH\Thesis\Data\wave_search\paper_chip\2019_04_29_195754_test_set_rand\test_set.npz'
factor = 0.05
freq = np.sqrt(np.array([2, np.pi, 5, 7, 13, 17, 19])) * factor
amplitude = np.array([0.9, 0.9, 0.9, 0.9, 0.9, 0.5, 0.5])
offset = np.array([-0.3, -0.3, -0.3, -0.3, -0.3, -0.2, -0.2])
phase = np.ones(7)
fs = 50
#phase = np.zeros(7)
generate_input = False

inputs, targets = gtd(file_dir) #function to load data returning torch Variable with correct form and dtype 
targets = targets
if generate_input:
    prediction = net.outputs(inputs,freq,amplitude,fs,offset,phase)*10
else:
    prediction = net.outputs(inputs)*10

### Training profile
plt.figure()
plt.plot(np.arange(nr_epochs),valerror.T)
plt.title('Validation MSE Profile while Training')
plt.xlabel('Epochs')
plt.show()

### Test Error
subsample = np.random.permutation(len(prediction))[:20000]
plt.figure()
plt.subplot(1,2,1)
plt.plot(targets[subsample],prediction[subsample],'.')
plt.xlabel('True Output (nA)')
plt.ylabel('Predicted Output (nA)')
min_out = np.min(np.concatenate((targets[subsample],prediction[subsample])))
max_out = np.max(np.concatenate((targets[subsample],prediction[subsample])))
plt.plot(np.linspace(min_out,max_out),np.linspace(min_out,max_out),'k')
#plt.title('Predicted vs True values')

error = (targets[:]-prediction[:]).T#/np.sqrt(baseline_var)
print(f'MSE on Test Set: \n {np.mean(error**2)}')

plt.subplot(1,2,2)
plt.hist(error[subsample],100)
plt.xlabel('error (nA)')
plt.ylabel('nr. of samples')
#plt.title('Scaled error histogram')
plt.show()
