''''
Measurement script to perform an evolution experiment of a selected
gate. This will initially be tested on the Heliox (with nidaq) setup.
'''

# Import packages
import numpy as np
import torch
from torch.autograd import Variable
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import sys
sys.path.append('/home/hruiz/Documents/PROJECTS/')
sys.path.append('/home/hruiz/Documents/PROJECTS/DARWIN/Code/SkyNEt/')
import modules.PlotBuilder as PlotBuilder
import modules.GenerateInput as GenerateInput
import modules.Evolution_Gauss as Evolution
import modules.PostProcess as PostProcess
import modules.SaveLib as SaveLib
from Nets.predNNet import predNNet

#np.random.seed(333)
########################### LOAD NN & DATA ########################################
main_dir = r'/home/hruiz/Documents/PROJECTS/DARWIN/Data_Darwin/'
data_dir = main_dir+'25_07_2018_CP-full-search-77K/'#'180130-S1-13-77K-full-search-withoutInM/'
syst = 'cuda' # 'cpu' #
if syst is 'cuda':
    print('Train with CUDA')
    dtype = torch.cuda.FloatTensor
    itype = torch.cuda.LongTensor
else: 
    print('Train with CPU')
    dtype = torch.FloatTensor
    itype = torch.LongTensor

net = predNNet(data_dir+'lr2e-4_eps1000_mb512_25072018CP.pt')#'1000eps_lr2e-4_mb512_noBN.pt')

# Import config file
from config_NN import *
filepath = main_dir+filepath
# initialize genepool
genePool = Evolution.GenePool(genes, genomes)

# initialize benchmark
# Obtain benchmark input (P and Q are input1, input2)
[t, P, Q, W] = GenerateInput.softwareInput(benchmark, SampleFreq, WavePeriods, WaveFrequency)

# format for nidaq
x = np.empty((2, len(P)))
x[0,:] = P
x[1,:] = Q
# Obtain benchmark target
[t, target] = GenerateInput.targetOutput(
    benchmark, SampleFreq, WavePeriods, WaveFrequency)

# TODO: Define input x (substitute P for the corresponding array below), 
#target, t (time axis) and W weight-mask 
#inputs, target, W = GenerateInput.ControlProblem()

# np arrays to save genePools, outputs and fitness
geneArray = np.empty((generations, genes, genomes))
outputArray = np.empty((generations, len(target) - skipstates, genomes))
fitnessArray = np.empty((generations, genomes))

# temporary arrays, overwritten each generation
fitnessTemp = np.empty((genomes, fitnessAvg))
trained_output = np.empty((len(target) - skipstates, fitnessAvg))
outputTemp = np.empty((len(target) - skipstates, genomes))
controlVoltages = np.empty(genes)

# initialize save directory
saveDirectory = SaveLib.createSaveDirectory(filepath, name)

# initialize main figure
mainFig = PlotBuilder.initMainFigEvolution(genes, generations, genelabels, generange)


for i in range(generations):

    for j in range(genomes):

        # set the DAC voltages
        for k in range(genes-1):
            controlVoltages[k] = Evolution.mapGenes(
                generange[k], genePool.pool[k, j])

        #set the input scaling
        x_scaled = x * 0.9 #Evolution.mapGenes(generange[-1], genePool.pool[genes-1, j])

        for avgIndex in range(fitnessAvg):

            # feed input to NN
            g = np.ones_like(target)[:,np.newaxis]*genePool.pool[:, j][:,np.newaxis].T
            x_dummy = np.concatenate((x_scaled.T,g),axis=1) # First input then genes; dims of input TxD
            x_dummy = torch.from_numpy(x_dummy).type(dtype)
            output = net.model(Variable(x_dummy))[:,0]
            output = output.data.cpu().numpy()

            # plot genome
#            PlotBuilder.currentGenomeEvolution(mainFig, genePool.pool[:, j])
            
            # Train output
            trained_output[:, avgIndex] =10 * np.asarray(output)  # empty for now, as we have only one output node

            # Calculate fitness
            fitnessTemp[j, avgIndex]= PostProcess.fitnessREvolution(
#            fitnessTemp[j, avgIndex]= PostProcess.alphaFit(
#            fitnessTemp[j, avgIndex]= PostProcess.fitnessNegMSE(
                trained_output[:, avgIndex], target[skipstates:], W, fitnessParameters)

            #plot output
#            PlotBuilder.currentOutputEvolution(mainFig, t, target, output, j + 1, i + 1, fitnessTemp[j, avgIndex])

        outputTemp[:, j] = trained_output[:, np.argmin(fitnessTemp[j, :])]

    genePool.fitness = fitnessTemp.min(1)
    print("Generation nr. " + str(i + 1) + " completed")
    print("Highest fitness: " + str(max(genePool.fitness)))

    # save generation data
    geneArray[i, :, :] = genePool.returnPool()
    outputArray[i, :, :] = outputTemp
    fitnessArray[i, :] = fitnessTemp.min(1)

#    PlotBuilder.currentOutputEvolution(mainFig, t, target, output, j + 1, i + 1, fitnessTemp[j, avgIndex])
#    PlotBuilder.updateMainFigEvolution(mainFig, geneArray, fitnessArray, outputArray, i + 1, t, target, output)
#	
#	#save generation
#    SaveLib.saveMain(saveDirectory, geneArray, outputArray, fitnessArray, t, x, target)
	
    # evolve the next generation
    genePool.nextGen()

#SaveLib.saveMain(filepath, geneArray, outputArray, fitnessArray, t, x, target)
#
    
#plt.figure();
#n=1
#for i in range(5):
#    for j in range(i+1,5):
#        plt.subplot(5,2,n)
#        plt.plot(geneArray[:,i,-1],geneArray[:,j,-1],'k.',label='lowest fitness')
#        plt.plot(geneArray[0,i,-1],geneArray[0,j,-1],'*r',label='Start')
#        plt.plot(geneArray[-1,i,-1],geneArray[-1,j,-1],'y*',label='End')
#        plt.plot(geneArray[:,i,0],geneArray[:,j,0],'c-o',label='highest fitness')
#        plt.plot(geneArray[0,i,0],geneArray[0,j,0],'*r')
#        plt.plot(geneArray[-1,i,0],geneArray[-1,j,0],'y*')
#        if i==0 and j==1: plt.legend()
#        plt.xlabel('CV '+str(i))
#        plt.ylabel('CV '+str(j))
#        n += 1 
#plt.tight_layout()

plt.figure();
plt.subplot(1,3,1)
plt.plot(target,'-.')
plt.plot(outputArray[-1,:,0],'r')
plt.title('Target and Output')
plt.subplot(1,3,2)
plt.plot(fitnessArray[:,0])
plt.title('Fitness')
plt.subplot(1,3,3)
plt.plot(geneArray[:,:,0])
plt.title('Genes')
    

#plt.figure()
#plt.plot(np.arange(generations),geneArray[:,0,:10],'-x')
#plt.plot(np.arange(generations),geneArray[:,0,10:],':x')
#plt.title('CV0')

flat_geneArray = np.swapaxes(geneArray,0,1).reshape((genes,generations*genomes))
flat_fitness = fitnessArray.reshape((generations*genomes,))

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#plt.title('')
#X = geneArray[:,0,:].reshape((generations*genomes,1))
#Y = geneArray[:,1,:].reshape((generations*genomes,1))
#Z = geneArray[:,2,:].reshape((generations*genomes,1))
#s = np.abs(np.log(-flat_fitness))
#sc = ax.scatter(X,Y,Z,s=10/(1+s),c=s)
#plt.colorbar(sc)
#ax.set_xlabel('CV 1')
#ax.set_ylabel('CV 2')
#ax.set_zlabel('CV 3')
#plt.title('Fitness for all explored genomes')
#
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#neglog_fitness = np.log(-fitnessArray.reshape((generations*genomes,)))
#sc = ax.scatter(X,Y,neglog_fitness,s=10/(1+s),c=s)
#plt.colorbar(sc)
#ax.set_xlabel('CV 1')
#ax.set_ylabel('CV 2')
#ax.set_zlabel('neg. log-Fitness')
#plt.title('Fitnes for gene 1 and 2')

PlotBuilder.finalMain(mainFig)
generange_array = np.array(generange[:5])
ctrl_volt = genePool.returnPool()[:,0]*(generange_array[:,1]-generange_array[:,0])+generange_array[:,0]
print('Control Voltages obtained for {}:\n'.format(benchmark[1]),ctrl_volt)