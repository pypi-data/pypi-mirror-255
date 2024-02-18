import numpy as np
import h5py 

class ContinuousLoader():
    """
    Loader class for continuous signal data.

    Attributes:
        config (ContinuousConfig): Configuration object for loading.
        transforms (list of callable): List of functions for signal transformation.
    """
    def __init__(self,path_signal,Fs,windowsize,dtype,transforms=None):
        self.transforms = transforms if transforms is not None else []
        self.windowsize = windowsize
        self.Fs = Fs
        if dtype == 'npy':
            self.signal = np.load(path_signal)
        if dtype == 'h5':
            self.signal = load_full_signal_h5(path_signal)

    def load_signal(self,start):
        """
        Load a segment of the signal data.
        Args:
            start (float): Start time of the segment to load (in seconds).
        Returns:
            np.ndarray: Loaded segment of the signal.
        """
        signal = self.signal[:,start* self.Fs :(start+self.windowsize)*self.Fs]
        for transform in self.transforms:
            signal = transform(signal)
        return signal

class EventLoader():
    def __init__(self,config,transforms=None):
        self.config = config
        self.transforms = transforms if transforms is not None else []

    def load_signal(self,path_signal):
        signal = np.load(path_signal)
        start, end  = self.config.t_start*self.config.Fs, self.config.t_end*self.config.Fs
        signal = signal[:,start:end]
        for transform in self.transforms:
            signal = transform(signal)
        return signal


def load_full_signal_h5(path_signal):
    signal = []
    with h5py.File(path_signal,'r') as f:
        for channel in f.keys():
            signal.append(f[channel][:])
    signal = np.array(signal)

    if transforms is not None:
        for transform in transforms:
            signal = transform(signal)
    return signal
    
