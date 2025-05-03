"""
Plotting functions for the Austrian economics model.
"""

import matplotlib.pyplot as plt
import numpy as np

class Plotter:
    def __init__(self, economy):
        self.economy = economy
        self.fig = plt.figure(figsize=(20, 12))
        
        # Set up a single plot for emergent behavior
        self.ax = self.fig.add_subplot(111)
        
        # Initialize lines
        self.market_line, = self.ax.plot([], [], lw=3, color='black', linestyle='-', label='Market Price')
        self.consumer_lines = []
        self.producer_lines = []
        
        # Initialize colors
        self.consumer_colors = ['blue', 'cornflowerblue', 'lightblue', 'royalblue', 'steelblue', 'dodgerblue']
        self.producer_colors = ['red', 'tomato', 'salmon', 'orangered', 'coral', 'crimson']
        
        # Initialize legend
        self.ax.legend()
        
    def update_plots(self):
        """Update all plots with current data."""
        # Ensure arrays have compatible shapes
        min_length = min(len(self.economy.times), len(self.economy.market.prices), 
                        *[len(values) for values in self.economy.consumer_values], 
                        *[len(prices) for prices in self.economy.producer_prices])
        times = self.economy.times[:min_length]
        prices = self.economy.market.prices[:min_length]
        
        # Update market plot
        self.market_line.set_data(times, prices)
        
        # Update consumer plots
        for i, values in enumerate(self.economy.consumer_values):
            if i >= len(self.consumer_lines):
                line, = self.ax.plot([], [], lw=2, linestyle='--', 
                                   color=self.consumer_colors[i], 
                                   label=f'Consumer {i+1} Value')
                self.consumer_lines.append(line)
            self.consumer_lines[i].set_data(times, values[:min_length])
        
        # Update producer plots
        for i, prices in enumerate(self.economy.producer_prices):
            if i >= len(self.producer_lines):
                line, = self.ax.plot([], [], lw=1.5, linestyle=':', 
                                   color=self.producer_colors[i], 
                                   label=f'Producer {i+1} Price')
                self.producer_lines.append(line)
            self.producer_lines[i].set_data(times, prices[:min_length])
        
        # Update axes limits to show only the most recent data
        if times:
            window_size = 100  # Number of points to show
            start_idx = max(0, len(times) - window_size)
            self.ax.set_xlim(times[start_idx], times[-1] + 1)
            self.ax.set_ylim(0, 100)
        
        # Redraw the plot
        self.fig.canvas.draw()
