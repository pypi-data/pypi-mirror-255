import numpy as np

class ContinuousLoader():
    """
    Loader class for continuous signal data.

    Attributes:
        config (ContinuousConfig): Configuration object for loading.
        transforms (list of callable): List of functions for signal transformation.
    """
    def __init__(self,config,transforms=None):
        self.config = config
        self.transforms = transforms if transforms is not None else []
        self.signal = load_full_signal_npy(config.path_signal,transforms)
        
    def load_signal(self,start):
        """
        Load a segment of the signal data.
        Args:
            start (float): Start time of the segment to load (in seconds).
        Returns:
            np.ndarray: Loaded segment of the signal.
        """
        signal = self.signal[:,start* self.config.Fq_signal :(start+self.config.windowsize)*self.config.Fq_signal]
        return signal

class EventLoader():
    def __init__(self,config,transforms=None):
        self.config = config
        self.transforms = transforms if transforms is not None else []

    def load_signal(self,path_signal):
        signal = np.load(path_signal)
        start, end  = self.config.x_start*self.config.Fq_signal, self.config.x_end*self.config.Fq_signal
        signal = signal[:,start:end]
        for transform in self.transforms:
            signal = transform(signal)
        return signal

def load_full_signal_npy(path_signal,transforms):
    '''load the full signal data'''
    signal = np.load(path_signal)
    if transforms is not None:
        for transform in transforms:
            signal = transform(signal)
    return signal

def load_full_signal_h5(path_signal,load_channels,transforms):
    signal = []
    with h5py.File(path_signal,'r') as f:
        for channel in load_channels:
            signal.append(f[channel][:])
    signal = np.array(signal)

    if transforms is not None:
        for transform in transforms:
            signal = transform(signal)
    return signal
    
