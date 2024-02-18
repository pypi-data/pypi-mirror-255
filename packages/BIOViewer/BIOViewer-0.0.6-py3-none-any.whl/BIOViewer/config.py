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
    def __init__(self,path_signal=str,Fq_signal=int,display_channels=list,y_locations=list,dtype='npy',start=0,windowsize=15,stepsize=10,title=None,y_pad=10,real_time=False,x_ticks=True,**kwargs):
        self.path_signal = path_signal
        self.start = start
        self.dtype = dtype
        self.windowsize = windowsize
        self.Fq_signal = Fq_signal
        self.stepsize = stepsize
        self.x_start= start
        self.x_end = start+windowsize
        self.display_channels = display_channels
        self.y_locations = y_locations
        self.title = title
        self.y_pad = y_pad
        self.real_time =real_time
        self.x_ticks = x_ticks
        for key, value in kwargs.items():
            setattr(self, key, value)

