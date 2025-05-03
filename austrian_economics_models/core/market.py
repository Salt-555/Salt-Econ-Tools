"""
Core market dynamics implementation for the Austrian economics model.
"""

import numpy as np

class Market:
    def __init__(self, base_production_cost=35):
        self.base_production_cost = base_production_cost
        self.prices = []
        self.volumes = []
        
    def calculate_equilibrium(self, demand, supply):
        """Calculate market equilibrium price and quantity."""
        if not demand or not supply:
            return 0, 0
            
        # Find the point where demand equals supply
        for price in range(len(demand)):
            if demand[price] <= supply[price]:
                return price, demand[price]
        return 0, 0
        
    def update_market(self, consumer_values, producer_costs):
        """Update market state based on consumer and producer data."""
        # Calculate aggregate demand
        demand = sum(consumer_values) / len(consumer_values) if consumer_values else 0
        
        # Calculate aggregate supply
        supply = sum(producer_costs) / len(producer_costs) if producer_costs else 0
        
        # Calculate equilibrium price
        price = demand / supply * self.base_production_cost if supply > 0 else 0
        
        # Add some random variation
        price *= np.random.uniform(0.95, 1.05)
        
        self.prices.append(price)
        self.volumes.append(demand)
        
        return price
