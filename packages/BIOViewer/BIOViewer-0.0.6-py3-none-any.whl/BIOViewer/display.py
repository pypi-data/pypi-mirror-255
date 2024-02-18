import numpy as np

class SignalDisplay():
    def __init__(self,ax,config):
        self.config = config
        self.lines = []
        for y_location in config.y_locations:
            n_points = int((config.x_end-config.x_start)*config.Fq_signal)
            line, = ax.plot((np.linspace(config.x_start,config.x_end,n_points)),([y_location]*n_points),'black',linewidth=0.7)
            self.lines.append(line)
        ax.set_yticks(config.y_locations,config.display_channels)
        ax.set_ylim(min(config.y_locations)-config.y_pad,max(config.y_locations)+config.y_pad)
        self.ax = ax

    def plot_data(self,signal):
        for i,(line,y_location) in enumerate(zip(self.lines,self.config.y_locations)):
            channel_signal = signal[i,:]+y_location
            line.set_ydata(channel_signal)

    def set_x_ticks(self,ticks,labels):
        self.ax.set_xticks(ticks,labels)