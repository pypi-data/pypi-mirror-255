from src import Config
from viewers import EventViewer
import os


path_signals = '/media/moritz/Expansion/Data/bonobo/raw/cluster_center'
filenames = [f.replace('.npy','') for f in os.listdir(path_signals)]
path_signals = [os.path.join(path_signals,f+'.npy') for f in filenames]

channels = ['Fp1', 'F3', 'C3', 'P3', 'F7', 'T3', 'T5', 'O1', 'Fz', 'Cz', 'Pz', 'Fp2', 'F4', 'C4', 'P4', 'F8', 'T4', 'T6', 'O2']
y_locations = [0, -100, -200, -300, -400, -500, -600, -700, -900, -1000, -1100, -1300, -1400, -1500, -1600, -1700, -1800, -1900, -2000]
config = Config(path_signals=path_signals,titles=filenames,channels = channels,y_locations = y_locations,x_start=0,x_end=15,Fq_signal=128)

EventViewer(config)