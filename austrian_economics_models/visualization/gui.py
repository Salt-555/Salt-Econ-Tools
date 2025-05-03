"""
GUI components for the Austrian economics model.
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import numpy as np

class GUI:
    def __init__(self, plotter):
        self.plotter = plotter
        self.paused = False
        
        # Set up control panel
        control_gs = plotter.fig.add_gridspec(1, 6, left=0.25, right=0.75, bottom=0.05, top=0.1)
        
        # Create control buttons
        self.add_company_button_ax = plotter.fig.add_subplot(control_gs[0, 0])
        self.add_company_button = Button(self.add_company_button_ax, 'Add Company', color='lightblue')
        self.add_company_button.on_clicked(self.add_company)
        
        self.reset_button_ax = plotter.fig.add_subplot(control_gs[0, 1])
        self.reset_button = Button(self.reset_button_ax, 'Reset', color='lightgreen')
        self.reset_button.on_clicked(self.reset)
        
        self.pause_button_ax = plotter.fig.add_subplot(control_gs[0, 2])
        self.pause_button = Button(self.pause_button_ax, 'Pause/Resume', color='lightcoral')
        self.pause_button.on_clicked(self.toggle_pause)
        
        # Create parameter sliders
        self.speed_slider_ax = plotter.fig.add_subplot(control_gs[0, 3])
        self.speed_slider = Slider(self.speed_slider_ax, 'Speed', 50, 500, valinit=100, valstep=10, color='lightblue')
        self.speed_slider.on_changed(self.update_speed)
        
        self.volatility_slider_ax = plotter.fig.add_subplot(control_gs[0, 4])
        self.volatility_slider = Slider(self.volatility_slider_ax, 'Volatility', 0.01, 0.2, valinit=0.1, color='lightgreen')
        self.volatility_slider.on_changed(self.update_volatility)
        
        self.competition_slider_ax = plotter.fig.add_subplot(control_gs[0, 5])
        self.competition_slider = Slider(self.competition_slider_ax, 'Competition', 0.1, 1.0, valinit=0.5, color='lightcoral')
        self.competition_slider.on_changed(self.update_competition)
        
        # Status text
        self.status_text = plotter.fig.text(0.02, 0.02, "Simulation Started", fontsize=10, color='darkblue')
        
    def add_company(self, event):
        """Add a new company to the simulation."""
        if self.plotter.economy.add_producer():
            self.status_text.set_text("Added new company")
        else:
            self.status_text.set_text("Maximum number of companies reached")
        
    def reset(self, event):
        """Reset the simulation."""
        self.plotter.economy.reset()
        self.status_text.set_text("Simulation reset")
        
    def toggle_pause(self, event):
        """Pause or resume the simulation."""
        self.paused = not self.paused
        status = "paused" if self.paused else "resumed"
        self.status_text.set_text(f"Simulation {status}")
        
    def update_speed(self, val):
        """Update the animation speed."""
        # This would be used by the animation system
        pass
        
    def update_volatility(self, val):
        """Update the market volatility."""
        for consumer in self.plotter.economy.consumers:
            consumer.variation = val
        
    def update_competition(self, val):
        """Update the competition level."""
        for producer in self.plotter.economy.producers:
            producer.markup = val
