"""
Nautilus Edge Case Simulation
1. Stage 2->3 Transition: The shift from Circulating to Cumulative logic.
2. Rent Lock-in: When Solana's rent-exempt minimum traps the treasury.
"""

from nautilus_mc_engine import NautilusEngine, Wallet, SOL, DEFAULT_RENT_MINIMUM

def sim_stage_transition_hijack():
    """
    Simulates a whale waiting for the Stage 2->3 transition to hijack the price.
    """
    print("=== Simulation 1: Stage 2->3 Transition Hijack ===")
    engine = NautilusEngine()
    
    whale = Wallet(wallet_id=0, sol=1000 * SOL)
    organic = Wallet(wallet_id=1, sol=10 * SOL)
    
    # 1. Fill Stage 0 and 1 (Bootstrap)
    # We need 20,000 net circulating tokens to hit Stage 2 (Human Stage 3)
    engine.buy(whale, 19_900)
    print(f"Initial: Stage {engine.state.current_stage + 1}, Total Sold: {engine.state.total_sold}")
    
    # 2. Organic buyer pushes the protocol over the edge
    print("Organic buyer buys 100 tokens...")
    engine.buy(organic, 100)
    print(f"Status: Stage {engine.state.current_stage + 1}, Total Sold: {engine.state.total_sold}")
    
    # Now in Stage 2 (Human 3). Logic is now CUMULATIVE.
    # 3. Whale immediately wash-trades to "speed-run" Stage 3
    print("Whale begins wash-trading Stage 3 (Cumulative logic)...")
    stage_3_supply = 20_000 
    
    # Whale buys and sells in chunks to advance the stage_sold counter
    # Note: In Stage 2 (Human 3), we need 20,000 cumulative tokens to advance.
    for i in range(5):
        engine.buy(whale, 4_000)
        engine.sell(whale, 4_000)
        
    print(f"Post-Wash: Stage {engine.state.current_stage + 1}, Total Sold: {engine.state.total_sold}")
    print(f"Current Buy Price: {engine.buy_price() / SOL:.6f} SOL")
    print(f"Current Sell Price: {engine.sell_price() / SOL:.6f} SOL")
    
    # 4. Result for the organic buyer
    organic_mtm = organic.mark_to_market(engine.sell_price())
    print(f"Organic Buyer (who entered at Stage 2 entry) ROI: {(organic_mtm/organic.total_buy_cost - 1)*100:.2f}%")
    print("---")

def sim_rent_lockin():
    """
    Simulates the treasury running dry and rent-exempt minimum trapping funds.
    """
    print("\n=== Simulation 2: Rent Lock-in Threshold ===")
    engine = NautilusEngine(rent_minimum=DEFAULT_RENT_MINIMUM)
    
    # Setup: A tiny protocol state
    user = Wallet(wallet_id=1, sol=10 * SOL)
    engine.buy(user, 1000) # Stage 0
    
    print(f"Treasury Balance: {engine.state.treasury_balance} lamports")
    print(f"Rent Minimum: {DEFAULT_RENT_MINIMUM} lamports")
    
    # Simulate the user trying to sell in smaller and smaller chunks
    # as the treasury nears the rent floor.
    tokens_to_sell = 100
    while tokens_to_sell > 0:
        sp = engine.sell_price()
        payout = (sp * tokens_to_sell) * 9950 // 10000
        
        res = engine.sell(user, tokens_to_sell)
        if not res.success:
            print(f"FAILED to sell {tokens_to_sell} tokens. Reason: {res.reason}")
            print(f"Calculated Payout would have been: {payout} lamports")
            print(f"Treasury was: {engine.state.treasury_balance} lamports")
            print(f"Gap: {engine.state.treasury_balance - payout} (Must be > {DEFAULT_RENT_MINIMUM})")
            
            if tokens_to_sell > 1:
                tokens_to_sell //= 2
                print(f"Trying smaller amount: {tokens_to_sell}...")
                continue
            else:
                break
        else:
            print(f"Successfully sold {tokens_to_sell} tokens. Remaining: {user.tokens}")
            
    print(f"Final Trapped tokens: {user.tokens}")
    print(f"Final Trapped SOL in treasury: {engine.state.treasury_balance / SOL:.6f} SOL")

if __name__ == "__main__":
    sim_stage_transition_hijack()
    sim_rent_lockin()
