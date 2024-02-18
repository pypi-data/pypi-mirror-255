import matplotlib.pyplot as plt
import datetime
from functools import partial

class ActionHandler():
    def __init__(self,config,display,loader):
        self.actions = {
            'right': partial(move_window, config, display, loader, 'right'), 
            'left': partial(move_window, config, display, loader, 'left'),
            'init': partial(init_viewer, config, display, loader)
            }

    def __call__(self,key):
        self.actions[key]()

def move_window(config,display,loader,direction='right'):
    if direction =='right':
        config.start = config.start + config.windowsize
    if direction =='left':
        config.start = config.start - config.windowsize
    signal = loader.load_signal(config.start)
    display.plot_data(signal)
    update_x_ticks(config,display)
    # add info 
    plt.draw()

def init_viewer(config,display,loader):
    signal = loader.load_signal(config.start)
    display.plot_data(signal)
    update_x_ticks(config,display)
    # add info 
    plt.draw()


def seconds_to_hms(seconds):
    # Construct a datetime object with a base date
    base_date = datetime.datetime(1900, 1, 1)
    # Add the timedelta to the base date
    result_datetime = base_date + datetime.timedelta(seconds=seconds)
    # Format the result as hours:minutes:seconds
    formatted_time = result_datetime.strftime('%H:%M:%S')

    return formatted_time

def update_x_ticks(config, display):
    ticks = list(range(0, config.windowsize + 1))
    labels = list(range(config.start, config.start+config.windowsize + 1))
    if config.x_ticks ==True:        
        if config.real_time==True:
            labels = [seconds_to_hms(label) for label in labels]
        display.set_x_ticks(ticks,labels)
    else:
        display.set_x_ticks(ticks,[None]*len(labels))

