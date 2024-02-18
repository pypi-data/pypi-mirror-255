import numpy as np
import mne
import scipy

class EventConfig():
    def __init__(self,path_signals,titles,channels,y_locations,x_start,x_end,Fq_signal,idx=0,**kwargs):
        self.idx = idx
        self.titles = titles
        self.path_signals = path_signals
        self.channels = channels
        self.y_locations = y_locations
        self.x_start = x_start
        self.x_end = x_end
        self.Fq_signal = Fq_signal
        for key, value in kwargs.items():
            setattr(self, key, value)

class SignalViewer():
    def __init__(self,ax,config):
        self.config = config
        self.lines = []
        for y_location in config.y_locations:
            n_points = int((config.x_end-config.x_start)*config.Fq_signal)
            line, = ax.plot((np.linspace(config.x_start,config.x_end,n_points)),([y_location]*n_points),'black',linewidth=0.7)
            self.lines.append(line)
        ax.set_yticks(config.y_locations,config.channels)
        self.ax = ax

    def plot_data(self,signal):
        for i,(line,y_location) in enumerate(zip(self.lines,self.config.y_locations)):
            channel_signal = signal[i,:]+y_location - np.mean(signal[i,:])
            line.set_ydata(channel_signal)

    def set_x_ticks(self,ticks,labels):
        self.ax.set_xticks(ticks,labels)
        
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

class ContinuousConfig():
    """
    Configuration class for continuous signal visualization.

    Attributes:
        path_signal (str): File path to the signal data.
        start (float): Start time for visualization (in seconds).
        windowsize (float): Size of the window for visualization (in seconds).
        stepsize (float): Step size for moving the window (in seconds).
        Fq_signal (int): Sampling frequency of the signal.
        channels (list of str): List of channel names.
        y_locations (list of float): Y-axis locations for each channel.
        title (str): Title for the visualization.
    """
    def __init__(self,path_signal=str,start=float,windowsize=float,stepsize=float,Fq_signal=int,channels=list,y_locations=list,title=str,**kwargs):
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
    """
    Loader class for continuous signal data.

    Attributes:
        config (ContinuousConfig): Configuration object for loading.
        transforms (list of callable): List of functions for signal transformation.
    """
    def __init__(self,config,transforms=None):
        self.config = config
        self.transforms = transforms if transforms is not None else []
        self.signal = self.load_full_signal(config.path_signal)
        
    def load_full_signal(self,path_signal):
        '''load the full signal data'''
        signal = np.load(path_signal)
        for transform in self.transforms:
            signal = transform(signal)
        return signal

    def load_signal(self,start):
        """
        Load a segment of the signal data.
        Args:
            start (float): Start time of the segment to load (in seconds).
        Returns:
            np.ndarray: Loaded segment of the signal.
        """
        start, end  = start* self.config.Fq_signal, (start+self.config.windowsize)*self.config.Fq_signal
        signal = self.signal[:,start:end]
        return signal

class ContinuousViewer():
    """
    Viewer class for continuous signal visualization.

    Attributes:
        config (ContinuousConfig): Configuration object for visualization.
        fig (matplotlib.figure.Figure): Matplotlib figure object.
        ax (matplotlib.axes.Axes): Matplotlib axes object.
        viewer0 (SignalViewer): SignalViewer object for visualization.
        loader0 (ContinuousLoader): ContinuousLoader object for loading signal data.
    """
    def __init__(self,config):
        self.config = config
        self.fig,self.ax = plt.subplots(1)
        self.viewer0 = SignalViewer(self.ax,config)
        self.loader0 = ContinuousLoader(config)
        self.refresh()
        self.connect_actions()

        plt.show()

    def refresh(self):
        """Refresh the visualization."""
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
        """Connect keyboard actions for interaction."""
        action_list = {
            'right': lambda: (setattr(self.config, 'start', self.config.start + self.config.stepsize), self.refresh()),
            'left': lambda: (setattr(self.config, 'start', self.config.start - self.config.stepsize), self.refresh()),
            }
        self.fig.canvas.mpl_connect('key_press_event',lambda event: action_list[event.key]())

