import matplotlib.pyplot as plt
from BIOViewer.src import ContinuousViewer, ContinuousConfig
import os
import numpy as np

path_signal = '/home/moritz/Desktop/programming/BIOViewer/BIOViewer/P40-2-4.hf5'
dtype = 'h5'
channels = ['abd','flow_reductions']
y_locations = [0, 10]
Fq_signal = 128
title = 'Test'
config = ContinuousConfig(path_signal,Fq_signal,channels,y_locations,title=title)
ContinuousViewer(config)
