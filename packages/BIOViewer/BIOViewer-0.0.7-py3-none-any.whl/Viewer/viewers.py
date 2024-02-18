import matplotlib.pyplot as plt
from src import SignalLoader, SignalViewer

class EventViewer():
    def __init__(self,config):
        self.config = config
        self.fig,self.ax = plt.subplots(1)
        self.viewer0 = SignalViewer(self.ax,config)
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
        self.viewer0.plot_data(signal0)
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
