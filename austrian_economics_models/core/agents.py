"""
Agent behavior implementation for the Austrian economics model.
"""

import numpy as np

class Consumer:
    def __init__(self, base_value, quality_preference, variation):
        self.base_value = base_value
        self.quality_preference = quality_preference
        self.variation = variation
        
    def calculate_value(self, producer_traits):
        """Calculate subjective value for a producer's product."""
        value = self.base_value
        for trait in producer_traits:
            # Adjust value based on producer's luxury appeal and consumer's quality preference
            value += trait * self.quality_preference * 20
            
        # Add small day-to-day variations
        value += np.random.normal(0, self.variation * self.base_value)
        
        return max(self.base_value * 0.7, min(self.base_value * 1.3, value))

class Producer:
    def __init__(self, base_cost, tech_level, innovation_rate, markup, quality, luxury_appeal):
        self.base_cost = base_cost
        self.tech_level = tech_level
        self.innovation_rate = innovation_rate
        self.markup = markup
        self.quality = quality
        self.luxury_appeal = luxury_appeal
        
    def calculate_cost(self):
        """Calculate production cost with potential innovation."""
        # Base cost affected by technology level
        cost = self.base_cost / self.tech_level
        
        # Random daily variations
        cost += np.random.normal(0, cost * 0.05)
        
        # Check for innovation
        if np.random.random() < self.innovation_rate:
            self.tech_level *= 1.02
            cost -= cost * 0.05
        
        return max(self.base_cost * 0.7, min(self.base_cost * 1.3, cost))
        
    def set_price(self, cost):
        """Set price based on cost and markup strategy."""
        return cost * (1 + self.markup)
