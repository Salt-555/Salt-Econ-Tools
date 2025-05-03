import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from collections import defaultdict

class BitcoinSimulation:
    def __init__(self):
        # Initialize parameters
        self.params = {
            'growth_rate': 0.0005,
            'base_fee_sats': 5,
            'urgency_distribution': 0.3,
            'initial_users': 1000
        }

        # Constants
        self.NUM_BLOCKS = 100000
        self.HALVING_INTERVAL = 10000
        self.INITIAL_REWARD = 50 * 100_000_000
        self.MAX_TXS_PER_BLOCK = 4000
        self.MAX_USERS = 1_000_000

        self.FEE_TIERS = {
            'urgent': {'multiplier': 4.0},
            'high': {'multiplier': 2.0},
            'medium': {'multiplier': 1.0},
            'low': {'multiplier': 0.5}
        }

        # Setup the plot
        self.setup_plot()

    def setup_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(bottom=0.3)  # Make room for sliders

        # Create sliders
        slider_color = 'lightgoldenrodyellow'
        slider_ax_growth = plt.axes([0.2, 0.15, 0.6, 0.03])
        slider_ax_fee = plt.axes([0.2, 0.1, 0.6, 0.03])
        slider_ax_urgency = plt.axes([0.2, 0.05, 0.6, 0.03])

        self.s_growth = Slider(slider_ax_growth, 'Growth Rate', 0.0001, 0.001, 
                             valinit=self.params['growth_rate'], color=slider_color)
        self.s_fee = Slider(slider_ax_fee, 'Base Fee (sats/byte)', 1, 20,
                           valinit=self.params['base_fee_sats'], color=slider_color)
        self.s_urgency = Slider(slider_ax_urgency, 'High Priority %', 0.1, 0.9,
                               valinit=self.params['urgency_distribution'], color=slider_color)

        # Connect sliders to update function
        self.s_growth.on_changed(self.update)
        self.s_fee.on_changed(self.update)
        self.s_urgency.on_changed(self.update)

        # Set log scale for y-axis
        self.ax.set_yscale('log')
        self.ax.grid(True)
        self.ax.set_xlabel('Block Number')
        self.ax.set_ylabel('BTC')
        self.ax.set_title('Bitcoin Mining Rewards Over Time')

        # Initial simulation
        self.update(None)

    def run_simulation(self):
        users = self.params['initial_users']
        mempool_by_tier = defaultdict(float)
        base_fee_rate = self.params['base_fee_sats']

        block_rewards = np.zeros(self.NUM_BLOCKS)
        tx_fees = np.zeros(self.NUM_BLOCKS)
        total_rewards = np.zeros(self.NUM_BLOCKS)

        for block in range(self.NUM_BLOCKS):
            # User growth
            users = min(users * (1 + self.params['growth_rate']), self.MAX_USERS)

            # Block subsidy
            halvings = block // self.HALVING_INTERVAL
            block_reward = self.INITIAL_REWARD / (2 ** halvings)
            block_rewards[block] = block_reward

            # New transactions
            new_txs = users * 0.1
            mempool_by_tier['urgent'] += new_txs * self.params['urgency_distribution'] * 0.2
            mempool_by_tier['high'] += new_txs * self.params['urgency_distribution'] * 0.3
            mempool_by_tier['medium'] += new_txs * (1 - self.params['urgency_distribution']) * 0.6
            mempool_by_tier['low'] += new_txs * (1 - self.params['urgency_distribution']) * 0.4

            # Process transactions
            block_space = self.MAX_TXS_PER_BLOCK
            total_fees = 0

            for tier, info in self.FEE_TIERS.items():
                if block_space <= 0:
                    break

                pending = mempool_by_tier[tier]
                competition = max(1, np.log2(pending / (self.MAX_TXS_PER_BLOCK / 4)))
                fee_rate = base_fee_rate * info['multiplier'] * competition

                included = min(pending, block_space)
                total_fees += included * 250 * fee_rate  # 250 bytes per tx
                block_space -= included
                mempool_by_tier[tier] = max(0, pending - included)

            tx_fees[block] = total_fees
            total_rewards[block] = block_reward + total_fees

            # Update base fee rate
            total_pending = sum(mempool_by_tier.values())
            global_competition = np.log2(1 + total_pending / self.MAX_TXS_PER_BLOCK)
            base_fee_rate = min(max(self.params['base_fee_sats'], 
                                  base_fee_rate * (1 + global_competition * 0.1)), 20)

        return block_rewards / 100_000_000, tx_fees / 100_000_000, total_rewards / 100_000_000

    def update(self, val):
        # Update parameters from sliders
        self.params['growth_rate'] = self.s_growth.val
        self.params['base_fee_sats'] = self.s_fee.val
        self.params['urgency_distribution'] = self.s_urgency.val

        # Clear previous plot
        self.ax.clear()

        # Run simulation and plot
        rewards, fees, totals = self.run_simulation()
        blocks = range(self.NUM_BLOCKS)

        self.ax.plot(blocks, rewards, label='Block Subsidy')
        self.ax.plot(blocks, fees, label='Transaction Fees')
        self.ax.plot(blocks, totals, label='Total Reward')

        self.ax.set_yscale('log')
        self.ax.grid(True)
        self.ax.set_xlabel('Block Number')
        self.ax.set_ylabel('BTC')
        self.ax.set_title('Bitcoin Mining Rewards Over Time')
        self.ax.legend()

        plt.draw()

# Instantiate and run
if __name__ == "__main__":
    BitcoinSimulation()
