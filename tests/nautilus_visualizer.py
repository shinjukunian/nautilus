"""
Nautilus Visualizer — Generates graphs for the technical report.
"""

import matplotlib.pyplot as plt
import numpy as np
import os
from nautilus_mc_engine import NautilusEngine, Wallet, SOL, STAGE_SUPPLY, PRICE_TABLE, preset_stage2_done
import random

# Ensure output directory exists
os.makedirs("docs/images", exist_ok=True)

def plot_recovery_floor():
    """Plots Buy vs Sell price over stages to visualize the 1/phi floor."""
    print("Generating Recovery Floor plot...")
    stages = range(1, 16)
    buy_prices = [PRICE_TABLE[i-1] / SOL for i in stages]
    
    # Simulate sell prices at stage completion
    engine = NautilusEngine()
    sell_prices = []
    w = Wallet(wallet_id=1, sol=1_000_000 * SOL)
    
    for s in stages:
        rem = engine.remaining_in_stage()
        engine.buy(w, rem)
        sell_prices.append(engine.sell_price() / SOL)
        
    plt.figure(figsize=(10, 6))
    plt.plot(stages, buy_prices, 'r-o', label='Buy Price (Fixed)')
    plt.plot(stages, sell_prices, 'b-o', label='Sell Price (At Completion)')
    
    # Add theoretical 1/phi line for Stage 3+
    phi = (1 + 5**0.5) / 2
    floor_line = [bp / phi for bp in buy_prices]
    plt.plot(stages, floor_line, 'g--', alpha=0.5, label='Theoretical Floor (1/phi)')
    
    plt.title("Nautilus Protocol: Buy vs Sell Price Floor")
    plt.xlabel("Human Stage Number")
    plt.ylabel("Price (SOL)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig("docs/images/recovery_floor.png")
    plt.close()

def plot_bootstrap_resistance():
    """Visualizes the difference between Net Supply and Cumulative Volume."""
    print("Generating Bootstrap Resistance plot...")
    engine = NautilusEngine()
    bot = Wallet(wallet_id=0, sol=100 * SOL)
    
    net_supply = []
    cumulative_volume = []
    
    # 5 cycles of buy/sell
    for i in range(5):
        engine.buy(bot, 5_000)
        net_supply.append(engine.state.total_sold)
        cumulative_volume.append(sum(engine.state.stage_sold))
        
        engine.sell(bot, 5_000)
        net_supply.append(engine.state.total_sold)
        cumulative_volume.append(sum(engine.state.stage_sold))
        
    plt.figure(figsize=(10, 6))
    plt.plot(net_supply, 'b-x', label='Net Circulating Supply (Logic for Stage 1-2)')
    plt.plot(cumulative_volume, 'r--', label='Cumulative Volume')
    plt.axhline(y=10000, color='g', linestyle=':', label='Stage 1 Advance Threshold')
    
    plt.title("Bootstrap Phase: Wash Trading Resistance")
    plt.xlabel("Transaction Step")
    plt.ylabel("Token Count")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("docs/images/bootstrap_logic.png")
    plt.close()

def plot_windfall_spread():
    """Visualizes the 'Tax' on a Whale vs the Benefit to an Early Holder."""
    print("Generating Windfall Spread plot...")
    # Scenario: 20k tokens held from Stage 1. Whale wash-trades Stage 3.
    engine = NautilusEngine()
    early_holder = Wallet(wallet_id=1, sol=100 * SOL)
    whale = Wallet(wallet_id=2, sol=1000 * SOL)
    
    # Buy base supply
    engine.buy(early_holder, 10_000)
    engine.buy(early_holder, 10_000) # Stage 2 reached
    
    sell_prices = [engine.sell_price() / SOL]
    steps = [0]
    
    # Whale wash-trades Stage 3 (Human Stage 4)
    for i in range(1, 11):
        engine.buy(whale, 2000)
        engine.sell(whale, 2000)
        sell_prices.append(engine.sell_price() / SOL)
        steps.append(i)
        
    plt.figure(figsize=(10, 6))
    plt.fill_between(steps, sell_prices[0], sell_prices, color='green', alpha=0.2, label='Accumulated Spread (Profit for Early Holder)')
    plt.plot(steps, sell_prices, 'g-^', label='Sell Price (Floor)')
    
    plt.title("Stage 2->3 Transition: Windfall from Wash Trading")
    plt.xlabel("Whale Wash-Trade Cycles (in Stage 3)")
    plt.ylabel("Protocol Sell Price (SOL)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("docs/images/windfall_effect.png")
    plt.close()

if __name__ == "__main__":
    plot_recovery_floor()
    plot_bootstrap_resistance()
    plot_windfall_spread()
    print("All plots generated in docs/images/")
