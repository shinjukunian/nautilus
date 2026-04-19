"""
Nautilus Break Test — Stress testing the protocol's economic invariants.
"""

import math
from typing import List, Tuple
# Import from the existing simulation engine
from nautilus_mc_engine import NautilusEngine, Wallet, SOL, STAGE_SUPPLY, PRICE_TABLE

def test_monotonicity_micro_sells():
    """
    Test 1: Does sell_price ALWAYS increase or stay same, 
    even with tiny amounts that might hit rounding edges?
    """
    print("Testing Monotonicity under Micro-Sells...")
    engine = NautilusEngine()
    
    # Setup: Fill Stage 0 and 1
    w1 = Wallet(wallet_id=1, sol=100 * SOL)
    engine.buy(w1, 10_000) # Stage 0 -> 1
    engine.buy(w1, 10_000) # Stage 1 -> 2
    
    # Now we are in Stage 2 (idx 2)
    # Buy some more to have a treasury
    engine.buy(w1, 10_000) 
    
    initial_sp = engine.sell_price()
    print(f"  Initial Sell Price: {initial_sp} lamports")
    
    # Execute 5000 sells of 1 token each
    for i in range(5000):
        prev_sp = engine.sell_price()
        res = engine.sell(w1, 1)
        if not res.success:
            print(f"  FAILED at step {i}: {res.reason}")
            break
        
        current_sp = engine.sell_price()
        if current_sp < prev_sp:
            print(f"  VIOLATION: Sell price decreased! {prev_sp} -> {current_sp}")
            return False
            
    final_sp = engine.sell_price()
    print(f"  Final Sell Price after 5000 micro-sells: {final_sp} lamports")
    print(f"  Improvement: {final_sp - initial_sp} lamports")
    print("  ✓ Monotonicity held.")
    return True

def test_stage_speedrun_cost():
    """
    Test 2: How much does it cost a bot to advance stages?
    Every buy/sell cycle advances 'stage_sold' in Stage 2+.
    """
    print("\nTesting Stage 2+ Speed-run Cost...")
    engine = NautilusEngine()
    bot = Wallet(wallet_id=0, sol=1_000_000 * SOL)
    
    # Advance to Stage 2 (where cumulative issuance starts governing advancement)
    engine.buy(bot, 20_000) 
    
    start_stage = engine.state.current_stage 
    start_sol = bot.sol
    
    # Target: Advance to Stage 10
    target_stage = 10
    print(f"  Target: Advance from Stage {start_stage+1} to {target_stage+1}")
    
    while engine.state.current_stage < target_stage:
        rem = engine.remaining_in_stage()
        # Buy remaining in stage
        engine.buy(bot, min(rem, 100_000))
        # Sell immediately
        if bot.tokens > 0:
            engine.sell(bot, bot.tokens)
            
    end_sol = bot.sol
    total_cost = (start_sol - end_sol) / SOL
    print(f"  Total SOL lost to treasury spread to reach Stage {target_stage+1}: {total_cost:.4f} SOL")
    print(f"  Treasury balance: {engine.state.treasury_balance / SOL:.4f} SOL")
    print(f"  Final Sell Price: {engine.sell_price() / SOL:.6f} SOL")
    return True

def test_last_man_standing():
    """
    Test 3: Does the spread concentration create a massive 'bounty' for the last holders?
    """
    print("\nTesting 'Last Man Standing' Effect...")
    engine = NautilusEngine()
    
    # 100 wallets each buy 1000 tokens
    wallets = [Wallet(wallet_id=i, sol=10 * SOL) for i in range(100)]
    for w in wallets:
        engine.buy(w, 1000)
        
    print(f"  Total tokens: {engine.state.total_sold}")
    print(f"  Initial Sell Price: {engine.sell_price() / SOL:.6f} SOL")
    
    # 99 wallets exit
    for i in range(99):
        engine.sell(wallets[i], wallets[i].tokens)
        
    final_sp = engine.sell_price()
    print(f"  Final Sell Price for the last holder: {final_sp / SOL:.6f} SOL")
    last_w = wallets[99]
    print(f"  Last holder wealth: {last_w.mark_to_market(final_sp) / SOL:.4f} SOL")
    return True

if __name__ == "__main__":
    test_monotonicity_micro_sells()
    test_stage_speedrun_cost()
    test_last_man_standing()
