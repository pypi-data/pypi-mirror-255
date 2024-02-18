import matplotlib.pyplot as plt
from .display import  SignalDisplay
from .loader import ContinuousLoader
from .action import ActionHandler

class ContinuousViewer():
    def __init__(self,configs):
        fig, axs = plt.subplots((len(configs)))

        for i,config in enumerate(configs):
            ax = axs if len(configs)==1 else axs[i]
            display = SignalDisplay(ax,config)
            loader = ContinuousLoader(config)
            actionhandler = ActionHandler(config,display,loader)
            # Use a default argument to capture the current actionhandler
            fig.canvas.mpl_connect('key_press_event', lambda event, handler=actionhandler: handler(event.key))
            # load first image
            actionhandler('init')
    
        