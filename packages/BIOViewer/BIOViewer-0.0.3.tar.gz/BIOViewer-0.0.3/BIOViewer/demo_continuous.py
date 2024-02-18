import matplotlib.pyplot as plt
from BIOViewer.src import ContinuousViewer, ContinuousConfig
import os
import numpy as np

path_signal = '/home/moritz/Desktop/programming/BIOViewer/BIOViewer/example.h5'
dtype = 'h5'
channels = ['F3', 'F4', 'C3', 'C4', 'O1', 'O2']
y_locations = [0, -100, -200, -300, -400, -500]
Fq_signal = 128
title = 'Test'
config = ContinuousConfig(path_signal,Fq_signal,channels,y_locations,title=title)

ContinuousViewer(config)


