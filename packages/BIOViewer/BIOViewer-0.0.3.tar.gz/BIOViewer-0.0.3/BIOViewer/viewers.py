import matplotlib.pyplot as plt
from BIOViewer.src import SignalDisplay, ContinuousLoader, ContinuousConfig

class EventViewer():
    def __init__(self,config):
        self.config = config
        self.fig,self.ax = plt.subplots(1)
        self.display0 = SignalDisplay(self.ax,config)
        self.loader0 = SignalLoader(config)
        self.refresh()
        self.connect_actions()
        plt.show()

    def refresh(self):
        # get idx
        idx = self.config.idx
        # load and display data
        path_signal = self.config.path_signals[idx]
        signal0 = self.loader0.load_signal(path_signal)
        self.display0.plot_data(signal0)
        # add info 
        self.fig.suptitle(self.config.titles[idx])
        self.fig.tight_layout()
        plt.draw()

    def connect_actions(self):
        action_list = {
            'right': lambda: (setattr(self.config, 'idx', self.config.idx + 1), self.refresh()),
            'left': lambda: (setattr(self.config, 'idx', self.config.idx - 1), self.refresh()),
            }
        self.fig.canvas.mpl_connect('key_press_event',lambda event: action_list[event.key]())
"""
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
"""
class ContinuousViewer():
    """
    Viewer class for continuous signal visualization.

    Attributes:
        config (ContinuousConfig): Configuration object for visualization.
        fig (matplotlib.figure.Figure): Matplotlib figure object.
        ax (matplotlib.axes.Axes): Matplotlib axes object.
        display0 (SignalDisplay): SignalDisplay object for visualization.
        loader0 (ContinuousLoader): ContinuousLoader object for loading signal data.
    """
    def __init__(self,config):
        self.config = config
        self.fig,self.ax = plt.subplots(1)
        self.display0 = SignalDisplay(self.ax,config)
        self.loader0 = ContinuousLoader(config)
        self.refresh(fig,display0,config)
        self.connect_actions()

        plt.show()


    def connect_actions(self):
        """Connect keyboard actions for interaction."""
        action_list = {
            'right': lambda: (setattr(self.config, 'start', self.config.start + self.config.stepsize), self.refresh()),
            'left': lambda: (setattr(self.config, 'start', self.config.start - self.config.stepsize), self.refresh()),
            }
        self.fig.canvas.mpl_connect('key_press_event',lambda event: action_list[event.key]())

    def refresh(self,fig,viewer,config):
        """Refresh the visualization."""
        # get idx
        start = config.start
        signal0 = loader0.load_signal(start)
        self.display0.plot_data(signal0)
        ticks = list(range(0, config.windowsize + 1))
        labels = list(range(start, start+config.windowsize + 1))
        display0.set_x_ticks(ticks,labels)
        # add info 
        fig.suptitle(config.title)
        fig.tight_layout()
        plt.draw()
