import matplotlib.pyplot as plt
from src import SignalViewer
import os
import numpy as np

class ContinuousConfig():
    def __init__(self,path_signal,start,windowsize,stepsize,Fq_signal,channels,y_locations,title,**kwargs):
        self.path_signal = path_signal

        self.start = start
        self.windowsize = windowsize
        self.Fq_signal = Fq_signal
        self.stepsize = stepsize
        self.x_start,self.x_end = start,start+windowsize
        self.channels = channels
        self.y_locations = y_locations
        self.title = title
        for key, value in kwargs.items():
            setattr(self, key, value)


class ContinuousLoader():
    def __init__(self,config,transforms=None):
        self.config = config
        self.transforms = transforms if transforms is not None else []
        self.signal = self.load_full_signal(config.path_signal)
        
    def load_full_signal(self,path_signal):
        signal = np.load(path_signal)
        for transform in self.transforms:
            signal = transform(signal)
        return signal

    def load_signal(self,start):
        start, end  = start* self.config.Fq_signal, (start+self.config.windowsize)*self.config.Fq_signal
        signal = self.signal[:,start:end]
        return signal

class ContinuousViewer():
    def __init__(self,config):
        self.config = config
        self.fig,self.ax = plt.subplots(1)
        self.viewer0 = SignalViewer(self.ax,config)
        self.loader0 = ContinuousLoader(config)
        self.refresh()
        self.connect_actions()

        plt.show()

    def refresh(self):
        # get idx
        start = self.config.start
        signal0 = self.loader0.load_signal(start)
        self.viewer0.plot_data(signal0)
        ticks = list(range(0, self.config.windowsize + 1))
        labels = list(range(start, start+self.config.windowsize + 1))
        self.viewer0.set_x_ticks(ticks,labels)
        # add info 
        self.fig.suptitle(self.config.title)
        self.fig.tight_layout()
        plt.draw()


    def connect_actions(self):
        action_list = {
            'right': lambda: (setattr(self.config, 'start', self.config.start + self.config.stepsize), self.refresh()),
            'left': lambda: (setattr(self.config, 'start', self.config.start - self.config.stepsize), self.refresh()),
            }
        self.fig.canvas.mpl_connect('key_press_event',lambda event: action_list[event.key]())

path_signal = '/media/moritz/a80fe7e6-2bb9-4818-8add-17fb9bb673e1/Data/mgh_psg/continuous/121273430_2.npy'
channels = ['Fp1', 'F3', 'C3', 'P3', 'F7', 'T3']
y_locations = [0, -100, -200, -300, -400, -500]
title='random_signal'
config = ContinuousConfig(path_signal,start=0,windowsize=15,stepsize=10,Fq_signal=128,channels=channels,y_locations=y_locations,title=title)

ContinuousViewer(config)