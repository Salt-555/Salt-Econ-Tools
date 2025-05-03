"""
Overall economy management for the Austrian economics model.
"""

from .market import Market
from .agents import Consumer, Producer
import numpy as np

class Economy:
    def __init__(self, num_consumers=3, num_producers=3, max_points=100):
        self.num_consumers = num_consumers
        self.num_producers = num_producers
        self.max_points = max_points
        
        # Initialize market
        self.market = Market()
        
        # Initialize consumers
        self.consumers = [
            Consumer(base_value=75, quality_preference=0.8, variation=0.05),
            Consumer(base_value=50, quality_preference=0.5, variation=0.08),
            Consumer(base_value=30, quality_preference=0.2, variation=0.1)
        ]
        
        # Initialize producers
        self.producers = [
            Producer(base_cost=35, tech_level=1.0, innovation_rate=0.02, markup=0.4, quality=0.9, luxury_appeal=0.9),
            Producer(base_cost=35, tech_level=1.0, innovation_rate=0.03, markup=0.25, quality=0.7, luxury_appeal=0.5),
            Producer(base_cost=35, tech_level=1.0, innovation_rate=0.04, markup=0.15, quality=0.5, luxury_appeal=0.2)
        ]
        
        # Initialize data storage
        self.times = []
        self.consumer_values = [[] for _ in range(self.num_consumers)]
        self.producer_costs = [[] for _ in range(self.num_producers)]
        self.producer_prices = [[] for _ in range(self.num_producers)]
        
    def update(self):
        """Update the economy state for one time step."""
        self.times.append(len(self.times))
        
        # Update consumer values
        for i, consumer in enumerate(self.consumers):
            values = [consumer.calculate_value([producer.luxury_appeal]) for producer in self.producers]
            avg_value = sum(values) / len(values)
            self.consumer_values[i].append(avg_value)
            
        # Update producer costs and prices
        for i, producer in enumerate(self.producers):
            cost = producer.calculate_cost()
            self.producer_costs[i].append(cost)
            price = producer.set_price(cost)
            self.producer_prices[i].append(price)
            
        # Update market
        market_price = self.market.update_market(
            [values[-1] for values in self.consumer_values],
            [costs[-1] for costs in self.producer_costs]
        )
        self.market.prices.append(market_price)
        
        # Limit data to max points
        if len(self.times) > self.max_points:
            self.times = self.times[-self.max_points:]
            for i in range(self.num_consumers):
                self.consumer_values[i] = self.consumer_values[i][-self.max_points:]
            for i in range(self.num_producers):
                self.producer_costs[i] = self.producer_costs[i][-self.max_points:]
                self.producer_prices[i] = self.producer_prices[i][-self.max_points:]
            self.market.prices = self.market.prices[-self.max_points:]
        
        return market_price
        
    def add_producer(self):
        """Add a new producer to the economy."""
        if self.num_producers >= 6:
            return False
            
        new_producer = Producer(
            base_cost=35 * np.random.uniform(0.9, 1.1),
            tech_level=np.random.uniform(0.9, 1.1),
            innovation_rate=np.random.uniform(0.02, 0.05),
            markup=np.random.uniform(0.15, 0.35),
            quality=np.random.uniform(0.4, 0.9),
            luxury_appeal=np.random.uniform(0.3, 0.8)
        )
        
        self.producers.append(new_producer)
        self.num_producers += 1
        self.producer_costs.append([np.nan] * len(self.times))
        self.producer_prices.append([np.nan] * len(self.times))
        return True
        
    def reset(self):
        """Reset the economy to initial state."""
        self.times = []
        self.consumer_values = [[] for _ in range(self.num_consumers)]
        self.producer_costs = [[] for _ in range(self.num_producers)]
        self.producer_prices = [[] for _ in range(self.num_producers)]
        
        # Reset producer technology levels
        for producer in self.producers:
            producer.tech_level = np.random.uniform(0.9, 1.1)
