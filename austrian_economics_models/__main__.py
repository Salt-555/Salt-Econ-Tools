"""
Main entry point for the Austrian economics model simulation.
"""

import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from core.economy import Economy
from visualization.plots import Plotter
from visualization.gui import GUI

def main():
    # Initialize economy
    economy = Economy()
    
    # Initialize plotter
    plotter = Plotter(economy)
    
    # Initialize GUI
    gui = GUI(plotter)
    
    # Set up animation
    def update(frame):
        if not gui.paused:
            economy.update()
            plotter.update_plots()
        return plotter.market_line, *plotter.consumer_lines, *plotter.producer_lines
    
    ani = FuncAnimation(
        plotter.fig,
        update,
        frames=500,
        interval=100,
        blit=False
    )
    
    plt.show()

if __name__ == "__main__":
    main()
