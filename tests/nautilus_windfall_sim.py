"""
Comparative Windfall Analysis
Comparing ROI for a Stage 1-2 holder when Stage 3 advances via:
1. Organic growth (new buyers holding).
2. Wash trading (high volume, same net supply).
"""

from nautilus_mc_engine import NautilusEngine, Wallet, SOL, preset_stage2_done
import random

def run_windfall_comparison():
    # Setup RNG for reproducible results
    rng = random.Random(42)
    
    # --- Scenario A: Organic Growth ---
    # preset_stage2_done initializes engine at Stage 2 (Human 3) 
    # and distributes 20,000 tokens to the wallets.
    engine_org, wallets_org = preset_stage2_done(n_wallets=1, sol_per_wallet=100*SOL, rng=rng)
    early_holder = wallets_org[0]
    
    # Fill Stage 3 organically (Human Stage 4)
    # Stage 2 supply is 20,000 tokens
    organic_buyer = Wallet(wallet_id=2, sol=100 * SOL)
    engine_org.buy(organic_buyer, 20_000)
    
    sp_org = engine_org.sell_price()
    # Note: total_buy_cost for the early_holder in preset_stage2_done might be zero 
    # if it just sets the tokens. Let's manually set it to the base price cost.
    early_holder.total_buy_cost = 20_000 * 1_000_000 # 20k tokens at 0.001 SOL
    
    roi_org = (early_holder.mark_to_market(sp_org) / early_holder.total_buy_cost - 1) * 100
    
    # --- Scenario B: Wash-Trading Growth ---
    engine_wash, wallets_wash = preset_stage2_done(n_wallets=1, sol_per_wallet=100*SOL, rng=rng)
    early_holder_wash = wallets_wash[0]
    
    # A bot wash-trades Stage 3 (equivalent volume)
    bot = Wallet(wallet_id=3, sol=1000 * SOL)
    
    # Wash-trade 20,000 tokens of volume (chunks of 1,000)
    for _ in range(20):
        engine_wash.buy(bot, 1000)
        engine_wash.sell(bot, 1000)
        
    sp_wash = engine_wash.sell_price()
    early_holder_wash.total_buy_cost = 20_000 * 1_000_000
    
    roi_wash = (early_holder_wash.mark_to_market(sp_wash) / early_holder_wash.total_buy_cost - 1) * 100

    print("=== Windfall Comparison (Stage 1-2 Holder) ===")
    print(f"Scenario A (Organic Growth through Stage 3):")
    print(f"  Final Sell Price: {sp_org/SOL:.6f} SOL")
    print(f"  Early Holder ROI: {roi_org:.2f}%")
    print(f"\nScenario B (Wash-Trading through Stage 3):")
    print(f"  Final Sell Price: {sp_wash/SOL:.6f} SOL")
    print(f"  Early Holder ROI: {roi_wash:.2f}%")
    print(f"\nSpread 'Bounty' from Wash-Trading: {(sp_wash - sp_org)/SOL:.6f} SOL per token")
    print(f"Difference in ROI: {roi_wash - roi_org:.2f} percentage points")

if __name__ == "__main__":
    run_windfall_comparison()
