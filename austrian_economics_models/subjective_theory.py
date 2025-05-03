import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import matplotlib.widgets as widgets

class AustrianMarketModel:
    """A simplified Austrian market model with stable consumer values and competing producers."""
    
    def __init__(self, max_points=100):
        # Create the figure with a larger size
        self.fig = plt.figure(figsize=(20, 12))
        
        # Set up grid for multiple plots
        gs = plt.GridSpec(3, 2, width_ratios=[2, 1], height_ratios=[1, 1, 0.5], figure=self.fig)
        
        # Main Market Dynamics Plot
        self.market_ax = self.fig.add_subplot(gs[0, 0])
        self.market_ax.set_title('Market Dynamics', fontsize=12)
        self.market_ax.set_xlabel('Time')
        self.market_ax.set_ylabel('Price / Value / Cost')
        self.market_ax.grid(True, alpha=0.3)
        
        # Supply and Demand Plot
        self.sd_ax = self.fig.add_subplot(gs[0, 1])
        self.sd_ax.set_title('Supply and Demand', fontsize=12)
        self.sd_ax.set_xlabel('Price')
        self.sd_ax.set_ylabel('Quantity')
        self.sd_ax.grid(True, alpha=0.3)
        
        # Producer Performance Plot
        self.producer_ax = self.fig.add_subplot(gs[1, 0])
        self.producer_ax.set_title('Producer Performance', fontsize=12)
        self.producer_ax.set_xlabel('Time')
        self.producer_ax.set_ylabel('Price')
        self.producer_ax.grid(True, alpha=0.3)
        
        # Consumer Behavior Plot
        self.consumer_ax = self.fig.add_subplot(gs[1, 1])
        self.consumer_ax.set_title('Consumer Behavior', fontsize=12)
        self.consumer_ax.set_xlabel('Time')
        self.consumer_ax.set_ylabel('Value')
        self.consumer_ax.grid(True, alpha=0.3)
        
        # Control panel area
        control_gs = gs[2, :].subgridspec(1, 6)
        
        # Create control buttons
        self.add_company_button_ax = self.fig.add_subplot(control_gs[0, 0])
        self.add_company_button = widgets.Button(self.add_company_button_ax, 'Add Company', color='lightblue')
        self.add_company_button.on_clicked(self.add_company)
        
        self.reset_button_ax = self.fig.add_subplot(control_gs[0, 1])
        self.reset_button = widgets.Button(self.reset_button_ax, 'Reset', color='lightgreen')
        self.reset_button.on_clicked(self.reset_simulation)
        
        self.pause_button_ax = self.fig.add_subplot(control_gs[0, 2])
        self.pause_button = widgets.Button(self.pause_button_ax, 'Pause/Resume', color='lightcoral')
        self.pause_button.on_clicked(self.toggle_pause)
        
        # Create parameter sliders
        self.speed_slider_ax = self.fig.add_subplot(control_gs[0, 3])
        self.speed_slider = widgets.Slider(self.speed_slider_ax, 'Speed', 50, 500, valinit=100, valstep=10, color='lightblue')
        
        self.volatility_slider_ax = self.fig.add_subplot(control_gs[0, 4])
        self.volatility_slider = widgets.Slider(self.volatility_slider_ax, 'Volatility', 0.01, 0.2, valinit=0.1, color='lightgreen')
        
        self.competition_slider_ax = self.fig.add_subplot(control_gs[0, 5])
        self.competition_slider = widgets.Slider(self.competition_slider_ax, 'Competition', 0.1, 1.0, valinit=0.5, color='lightcoral')
        
        # Connect sliders
        self.speed_slider.on_changed(self.update_speed)
        self.volatility_slider.on_changed(self.update_volatility)
        self.competition_slider.on_changed(self.update_competition)
        
        # Status text area
        self.status_text = self.fig.text(0.02, 0.02, "Simulation Started", fontsize=10, color='darkblue')
        
        # Settings
        self.max_points = max_points
        self.counter = 0
        self.paused = False
        
        # Define number of consumers and producers
        self.num_consumers = 3
        self.num_producers = 3
        
        # Initialize data containers
        self.times = []
        self.consumer_values = [[] for _ in range(self.num_consumers)]
        self.producer_costs = [[] for _ in range(self.num_producers)]
        self.producer_prices = [[] for _ in range(self.num_producers)]
        self.market_price = []
        
        # Color maps for lines
        self.consumer_colors = ['blue', 'cornflowerblue', 'lightblue', 'royalblue', 'steelblue', 'dodgerblue']
        self.producer_cost_colors = ['darkred', 'firebrick', 'indianred', 'brown', 'maroon', 'darkmagenta']
        self.producer_price_colors = ['red', 'tomato', 'salmon', 'orangered', 'coral', 'crimson']
        
        # Define base cost that will be similar for all producers
        self.base_production_cost = 35
        
        # Create consumer traits - stable subjective values with minor variation
        self.consumer_traits = [
            {'name': 'Luxury Consumer', 'base_value': 75, 'variation': 0.05, 'quality_preference': 0.8},
            {'name': 'Average Consumer', 'base_value': 50, 'variation': 0.08, 'quality_preference': 0.5},
            {'name': 'Budget Consumer', 'base_value': 30, 'variation': 0.1, 'quality_preference': 0.2}
        ]
        
        # Create producer traits - similar costs but different perceived quality/luxury
        self.producer_traits = [
            {'name': 'Luxury Brand', 'base_cost': self.base_production_cost, 'tech_level': 1.0, 
             'innovation_rate': 0.02, 'markup': 0.4, 'quality': 0.9, 'luxury_appeal': 0.9},
            
            {'name': 'Mid-range Brand', 'base_cost': self.base_production_cost, 'tech_level': 1.0, 
             'innovation_rate': 0.03, 'markup': 0.25, 'quality': 0.7, 'luxury_appeal': 0.5},
            
            {'name': 'Economy Brand', 'base_cost': self.base_production_cost, 'tech_level': 1.0, 
             'innovation_rate': 0.04, 'markup': 0.15, 'quality': 0.5, 'luxury_appeal': 0.2}
        ]
        
        # Setup plot lines
        self.lines = []
        self.legend_elements = []
        
        # Initialize empty lines for all possible future producers (max 6)
        self.max_possible_producers = 6
        
        # Consumer value lines (dashed)
        for i in range(self.num_consumers):
            line, = self.market_ax.plot([], [], lw=2, linestyle='--', color=self.consumer_colors[i], 
                              label=f"{self.consumer_traits[i]['name']} Value")
            self.lines.append(line)
            self.legend_elements.append((line, f"{self.consumer_traits[i]['name']} Value"))
        
        # Producer cost lines (dotted)
        self.cost_lines = []
        for i in range(self.max_possible_producers):
            color = self.producer_cost_colors[i] if i < len(self.producer_cost_colors) else 'gray'
            line, = self.market_ax.plot([], [], lw=1.5, linestyle=':', color=color, visible=i<self.num_producers)
            self.lines.append(line)
            self.cost_lines.append(line)
            if i < self.num_producers:
                self.legend_elements.append((line, f"{self.producer_traits[i]['name']} Cost"))
        
        # Producer price lines (solid)
        self.price_lines = []
        for i in range(self.max_possible_producers):
            color = self.producer_price_colors[i] if i < len(self.producer_price_colors) else 'darkgray'
            line, = self.market_ax.plot([], [], lw=2, color=color, visible=i<self.num_producers)
            self.lines.append(line)
            self.price_lines.append(line)
            if i < self.num_producers:
                self.legend_elements.append((line, f"{self.producer_traits[i]['name']} Price"))
        
        # Market price line (thick black)
        market_line, = self.market_ax.plot([], [], lw=3, color='black', linestyle='-', 
                                 label='Market Price')
        self.lines.append(market_line)
        self.legend_elements.append((market_line, 'Market Price'))
        
        # Configure axes
        self.market_ax.set_xlim(0, max_points)
        self.market_ax.set_ylim(0, 100)
        self.market_ax.grid(True, alpha=0.3)
        
        # Custom legend with current entries
        self.update_legend()
        
        # Add annotations
        self.fig.text(0.01, 0.01, 
                     "\"Prices are determined not by objective factors, but by subjective valuations of consumers.\" - Ludwig von Mises",
                     fontsize=8, style='italic', color='darkblue')
        
        # Animation object placeholder
        self.ani = None
    
    def update_legend(self):
        """Update legend with current producers"""
        # Extract current lines and labels
        current_lines = [element[0] for element in self.legend_elements 
                        if element[0].get_visible()]
        current_labels = [element[1] for element in self.legend_elements 
                         if element[0].get_visible()]
        
        # Create legend
        self.market_ax.legend(current_lines, current_labels, loc='upper left', fontsize='small')
    
    def init_animation(self):
        """Initialize the animation with empty data"""
        for line in self.lines:
            line.set_data([], [])
            line.set_visible(True)
        self.status_text.set_text("")
        return self.lines + [self.status_text]

    def update(self, frame):
        """Update all data for each animation frame"""
        if self.paused:
            return
        
        self.counter += 1
        self.times.append(self.counter)
        
        # Calculate new consumer values (for each consumer-producer pair)
        for c_idx in range(self.num_consumers):
            # For each consumer, find the average value across all producers
            all_values = [self.calculate_consumer_value(c_idx, p_idx) for p_idx in range(self.num_producers)]
            avg_value = sum(all_values) / len(all_values) if all_values else 50
            self.consumer_values[c_idx].append(avg_value)
        
        # Calculate producer costs (with potential innovation)
        for p_idx in range(self.num_producers):
            cost = self.calculate_producer_cost(p_idx)
            self.producer_costs[p_idx].append(cost)
        
        # Determine producer prices based on costs and competition
        for p_idx in range(self.num_producers):
            price = self.determine_producer_price(p_idx)
            self.producer_prices[p_idx].append(price)
        
        # Calculate market price
        market_price = self.calculate_market_price()
        self.market_price.append(market_price)
        
        # Limit data to max points
        max_points = self.max_points
        if len(self.times) > max_points:
            self.times = self.times[-max_points:]
            
            for i in range(self.num_consumers):
                self.consumer_values[i] = self.consumer_values[i][-max_points:]
            
            for i in range(self.num_producers):
                self.producer_costs[i] = self.producer_costs[i][-max_points:]
                self.producer_prices[i] = self.producer_prices[i][-max_points:]
            
            self.market_price = self.market_price[-max_points:]
        
        # Update all line data
        for i in range(self.num_consumers):
            self.lines[i].set_data(self.times, self.consumer_values[i])
        
        for i in range(self.num_producers):
            self.lines[i + self.num_consumers].set_data(self.times, self.producer_costs[i])
            self.lines[i + self.num_consumers + self.num_producers].set_data(self.times, self.producer_prices[i])
        
        self.lines[-1].set_data(self.times, self.market_price)
        
        # Adjust x-axis for scrolling effect when needed
        if self.counter > max_points:
            self.market_ax.set_xlim(self.counter - max_points, self.counter)
        
        # Update status with market insights
        if self.counter % 10 == 0 and self.producer_prices and all(self.producer_prices):
            # Find most profitable producer
            profits = []
            for i in range(self.num_producers):
                cost = self.producer_costs[i][-1]
                price = self.producer_prices[i][-1]
                profit_margin = (price - cost) / price if price > 0 else 0
                profits.append((i, profit_margin))
            
            best_producer = max(profits, key=lambda x: x[1])
            status_msg = f"Most profitable: {self.producer_traits[best_producer[0]]['name']} ({best_producer[1]*100:.1f}% margin)"
            self.status_text.set_text(status_msg)
        
        # Plot supply and demand
        self.plot_supply_demand()
        
        # Plot producer performance
        self.plot_producer_performance()
        
        # Plot consumer behavior
        self.plot_consumer_behavior()
        
        return self.lines + [self.status_text]
    
    def calculate_consumer_value(self, consumer_idx, producer_idx):
        """Calculate consumer's subjective value for a specific producer's product"""
        consumer = self.consumer_traits[consumer_idx]
        producer = self.producer_traits[producer_idx]
        
        # Base value from consumer
        base_value = consumer['base_value']
        
        # Adjust based on producer's luxury appeal and consumer's quality preference
        # Luxury consumers are more influenced by luxury appeal
        luxury_adjustment = producer['luxury_appeal'] * consumer['quality_preference'] * 20
        
        # Small day-to-day variations
        variation = consumer['variation'] * base_value
        daily_change = random.normalvariate(0, variation)
        
        # Calculate total value with boundaries
        value = base_value + luxury_adjustment + daily_change
        return max(base_value * 0.7, min(base_value * 1.3, value))
    
    def calculate_producer_cost(self, producer_idx):
        """Calculate production cost with possibility of innovation"""
        producer = self.producer_traits[producer_idx]
        
        # Base cost affected by technology level
        base_cost = producer['base_cost'] / producer['tech_level']
        
        # Random daily variations in production process
        process_variation = random.normalvariate(0, base_cost * 0.05)
        
        # Check for cost-reducing innovation
        if random.random() < producer['innovation_rate']:
            # Technology improves permanently
            producer['tech_level'] = producer['tech_level'] * 1.02
            # Mark the event with a temporary cost reduction
            process_variation -= base_cost * 0.05
        
        # Calculate final cost with boundaries
        cost = base_cost + process_variation
        return max(producer['base_cost'] * 0.7, min(producer['base_cost'] * 1.3, cost))
    
    def determine_producer_price(self, producer_idx):
        """Set price based on costs, markup strategy, luxury appeal, and competition"""
        producer = self.producer_traits[producer_idx]
        
        # If no cost data yet, use default
        if not self.producer_costs[producer_idx]:
            # Higher markup for luxury brands
            return producer['base_cost'] * (1 + producer['markup'])
        
        # Get most recent cost
        cost = self.producer_costs[producer_idx][-1]
        
        # Calculate target price with markup
        # Luxury brands can command higher markups
        effective_markup = producer['markup'] * (1 + producer['luxury_appeal'] * 0.5)
        target_price = cost * (1 + effective_markup)
        
        # Adjust based on competition if market price exists
        if self.market_price:
            market_price = self.market_price[-1]
            
            # Luxury brands are less responsive to low market prices
            price_pressure = 1.0 - producer['luxury_appeal'] * 0.5
            
            # If market price is below cost, adjust to stay competitive
            if market_price < cost:
                # Luxury brands resist lowering prices more than economy brands
                target_price = max(cost * 1.05, market_price * (0.95 + producer['luxury_appeal'] * 0.1))
            
            # If we're way above market, try to capture more market share
            elif target_price > market_price * 1.3:
                # Luxury brands maintain higher prices compared to market
                adjustment_factor = 0.7 - producer['luxury_appeal'] * 0.3
                target_price = target_price * (1 - adjustment_factor) + market_price * adjustment_factor
        
        # Smooth price changes if we have previous prices
        if self.producer_prices[producer_idx]:
            prev_price = self.producer_prices[producer_idx][-1]
            max_change = 0.1  # Maximum 10% change per period
            
            if target_price > prev_price * (1 + max_change):
                target_price = prev_price * (1 + max_change)
            elif target_price < prev_price * (1 - max_change):
                target_price = prev_price * (1 - max_change)
        
        return target_price
    
    def calculate_market_price(self):
        """Determine market price from producer prices, weighted by consumer preferences"""
        # Calculate demand based on consumer values
        demand = sum([sum(values) for values in self.consumer_values]) / len(self.times) if self.times else 0

        # Calculate supply based on producer costs
        supply = sum([sum(costs) for costs in self.producer_costs]) / len(self.times) if self.times else 0

        # Simple equilibrium price calculation
        if supply == 0:
            return 0
        market_price = demand / supply * self.base_production_cost

        # Add some random variation to simulate market dynamics
        market_price *= random.uniform(0.95, 1.05)

        return market_price
    
    def plot_supply_demand(self):
        """Plot supply and demand curves"""
        if not hasattr(self, 'sd_ax'):
            self.sd_ax = self.fig.add_subplot(122)

        # Clear previous plot
        self.sd_ax.clear()

        # Generate price points
        prices = np.linspace(0, 100, 100)

        # Calculate demand
        demand = [sum([max(0, trait['base_value'] - p) for trait in self.consumer_traits]) for p in prices]

        # Calculate supply
        supply = [sum([max(0, p - trait['base_cost']) for trait in self.producer_traits]) for p in prices]

        # Plot curves
        self.sd_ax.plot(prices, demand, label='Demand', color='blue')
        self.sd_ax.plot(prices, supply, label='Supply', color='red')

        # Find equilibrium
        diff = np.array(demand) - np.array(supply)
        idx = np.argmin(np.abs(diff))
        eq_price = prices[idx]
        eq_quantity = demand[idx]

        # Plot equilibrium
        self.sd_ax.axvline(eq_price, color='gray', linestyle='--', alpha=0.5)
        self.sd_ax.axhline(eq_quantity, color='gray', linestyle='--', alpha=0.5)
        self.sd_ax.plot(eq_price, eq_quantity, 'go', markersize=10)

        # Format plot
        self.sd_ax.set_xlabel('Price')
        self.sd_ax.set_ylabel('Quantity')
        self.sd_ax.set_title('Supply and Demand')
        self.sd_ax.legend()
        self.sd_ax.grid(True, alpha=0.3)
    
    def plot_producer_performance(self):
        """Plot producer performance"""
        self.producer_ax.clear()
        for i in range(self.num_producers):
            self.producer_ax.plot(self.times, self.producer_prices[i], label=self.producer_traits[i]['name'])
        self.producer_ax.set_xlabel('Time')
        self.producer_ax.set_ylabel('Price')
        self.producer_ax.set_title('Producer Performance')
        self.producer_ax.legend()
        self.producer_ax.grid(True, alpha=0.3)
    
    def plot_consumer_behavior(self):
        """Plot consumer behavior"""
        self.consumer_ax.clear()
        for i in range(self.num_consumers):
            self.consumer_ax.plot(self.times, self.consumer_values[i], label=self.consumer_traits[i]['name'])
        self.consumer_ax.set_xlabel('Time')
        self.consumer_ax.set_ylabel('Value')
        self.consumer_ax.set_title('Consumer Behavior')
        self.consumer_ax.legend()
        self.consumer_ax.grid(True, alpha=0.3)
    
    def add_company(self, event):
        """Add a new company to the simulation"""
        if self.num_producers >= self.max_possible_producers:
            self.status_text.set_text("Maximum number of companies reached")
            return

        # Create a new producer with random traits
        company_types = ['Boutique', 'New Entrant', 'Innovative']
        company_name = f"{random.choice(company_types)} Producer {self.num_producers + 1}"

        new_producer = {
            'name': company_name,
            'base_cost': self.base_production_cost * random.uniform(0.9, 1.1),
            'tech_level': random.uniform(0.9, 1.1),
            'innovation_rate': random.uniform(0.02, 0.05),
            'markup': random.uniform(0.15, 0.35),
            'quality': random.uniform(0.4, 0.9),
            'luxury_appeal': random.uniform(0.3, 0.8)
        }

        # Add the new producer traits
        self.producer_traits.append(new_producer)
        self.num_producers += 1

        # Determine current length of time series
        current_length = len(self.times)

        # Add new data lists for the producer, padded with NaN values for the past time steps
        self.producer_costs.append([np.nan] * current_length)
        self.producer_prices.append([np.nan] * current_length)

        # Make the corresponding lines visible
        self.cost_lines[self.num_producers - 1].set_visible(True)
        self.price_lines[self.num_producers - 1].set_visible(True)

        # Update legend
        self.legend_elements.append((self.cost_lines[self.num_producers - 1], f"{new_producer['name']} Cost"))
        self.legend_elements.append((self.price_lines[self.num_producers - 1], f"{new_producer['name']} Price"))
        self.update_legend()

        self.status_text.set_text(f"Added new company: {new_producer['name']}")
    
    def reset_simulation(self, event):
        """Reset the simulation"""
        self.counter = 0
        self.times = []
        self.consumer_values = [[] for _ in range(self.num_consumers)]
        self.producer_costs = [[] for _ in range(self.num_producers)]
        self.producer_prices = [[] for _ in range(self.num_producers)]
        self.market_price = []
        
        # Reset technology levels
        for producer in self.producer_traits:
            producer['tech_level'] = random.uniform(0.9, 1.1)
        
        self.status_text.set_text("Simulation reset")
    
    def toggle_pause(self, event):
        """Pause or resume the simulation"""
        self.paused = not self.paused
        status = "paused" if self.paused else "resumed"
        self.status_text.set_text(f"Simulation {status}")
    
    def update_speed(self, val):
        """Update the animation speed"""
        self.ani.event_source.interval = int(val)
    
    def update_volatility(self, val):
        """Update the market volatility"""
        for consumer in self.consumer_traits:
            consumer['variation'] = val
    
    def update_competition(self, val):
        """Update the competition level"""
        for producer in self.producer_traits:
            producer['markup'] = val
    
    def run(self, frames=500, interval=100):
        """Run the animation"""
        try:
            self.ani = FuncAnimation(
                self.fig, 
                self.update, 
                frames=frames,
                init_func=self.init_animation,
                interval=interval, 
                blit=False
            )
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error running animation: {e}")
            plt.close(self.fig)


# Run the model when script is executed directly
if __name__ == "__main__":
    model = AustrianMarketModel(max_points=100)
    model.run(frames=500, interval=100)