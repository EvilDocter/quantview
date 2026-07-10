"""
QuantView — Monte Carlo Simulation Forecasting Service

Generates randomized future stock price walks using geometric Brownian motion.
"""

import numpy as np

class MonteCarloService:
    """Simulates future asset price trajectories."""

    @staticmethod
    def run_monte_carlo_simulation(
        start_price: float,
        days: int = 252,
        simulations: int = 1000,
        mu: float = 0.1,    # Annual expected return
        sigma: float = 0.2  # Annual volatility
    ) -> list[list[float]]:
        """
        Runs geometric Brownian motion price projections.
        S_t = S_0 * exp( (mu - 0.5*sigma^2)*dt + sigma*W_t )
        """
        dt = 1.0 / 252
        trajectories = []

        for _ in range(simulations):
            prices = [start_price]
            current_price = start_price
            
            for _ in range(days):
                # Standard normal variable
                epsilon = np.random.normal()
                # Drift & diffusion calculations
                drift = (mu - 0.5 * (sigma ** 2)) * dt
                diffusion = sigma * np.sqrt(dt) * epsilon
                
                current_price = current_price * np.exp(drift + diffusion)
                prices.append(float(current_price))
                
            trajectories.append(prices)

        return trajectories
