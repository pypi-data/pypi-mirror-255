import numpy as np

class z_scaler():
    def __init__(self):
        pass
    def __call__(self,signal):
                # Calculate mean and standard deviation of the signal
        mean = np.mean(signal)
        std_dev = np.std(signal) + 1e-10

        # Z-scale the signal
        z_scaled_signal = (signal - mean) / std_dev
        return z_scaled_signal
    
class FilterChannels():
    ''' 
    A transformation class for filtering signal data by selected channels.

    This class is designed to filter out specific channels from a multi-channel signal, 
    reducing the signal from its original set of channels ('channels_storage') to a 
    subset of channels ('channels_display'). This is useful in contexts where only a 
    selection of the available signal channels are needed for further processing or visualization.

    Attributes:
        channel_ids (numpy.ndarray): An array of indices representing the channels 
            to be retained in the filtered signal.

    Parameters:
        channels_storage (list of str): The list of all channel names as stored in the 
            original signal data. This represents the complete set of channels available.
        channels_display (list of str): The list of channel names to be retained in the 
            filtered signal. These channels must exist in 'channels_storage'.

    Methods:
        __call__(signal): Applies the channel filtering transformation to the input signal.

    Example:
        >>> channels_storage = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2']
        >>> channels_display = ['F3', 'F4', 'C3', 'C4']
        >>> filter_channels = FilterChannels(channels_storage, channels_display)
        >>> signal = np.random.rand(10, 1000)  # Simulated signal [channels_storage, ts]
        >>> filtered_signal = filter_channels(signal)
        # filtered_signal now has shape [4, 1000], corresponding to 'channels_display'
    '''
    def __init__(self,channels_storage,channels_display):
        # get ids of channels 
        self.channel_ids = np.array([channels_storage.index(channel) for channel in channels_display])
    def __call__(self,signal):
        return signal[self.channel_ids,:]