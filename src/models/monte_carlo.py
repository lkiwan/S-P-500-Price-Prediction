"""
Monte Carlo Simulation for S&P 500 Predictions
Simulates thousands of possible future price paths
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class MonteCarloSimulator:
    """
    Monte Carlo simulation for stock price forecasting
    """

    def __init__(self, price_df):
        """
        Initialize Monte Carlo simulator

        Args:
            price_df: DataFrame with historical price data
        """
        self.price_df = price_df
        self.price_df['date'] = pd.to_datetime(self.price_df['date'])
        self.price_df = self.price_df.sort_values('date')

        # Calculate historical statistics
        self.price_df['returns'] = self.price_df['close'].pct_change()
        self.mean_return = self.price_df['returns'].mean()
        self.std_return = self.price_df['returns'].std()

    def simulate_price_paths(self, days=30, num_simulations=1000, use_gbm=True):
        """
        Run Monte Carlo simulation

        Args:
            days: Number of days to simulate
            num_simulations: Number of simulation paths
            use_gbm: Use Geometric Brownian Motion (True) or simple random walk (False)

        Returns:
            Dictionary with simulation results
        """
        current_price = self.price_df.iloc[-1]['close']
        simulations = np.zeros((num_simulations, days + 1))
        simulations[:, 0] = current_price

        # Geometric Brownian Motion parameters
        if use_gbm:
            drift = self.mean_return - (0.5 * self.std_return ** 2)
            dt = 1  # Daily timestep

        # Run simulations
        for sim in range(num_simulations):
            for day in range(1, days + 1):
                if use_gbm:
                    # Geometric Brownian Motion
                    random_shock = np.random.normal(0, 1)
                    simulations[sim, day] = simulations[sim, day - 1] * np.exp(
                        drift * dt + self.std_return * np.sqrt(dt) * random_shock
                    )
                else:
                    # Simple random walk
                    random_return = np.random.normal(self.mean_return, self.std_return)
                    simulations[sim, day] = simulations[sim, day - 1] * (1 + random_return)

        # Calculate statistics
        final_prices = simulations[:, -1]
        percentiles = {
            '5th': np.percentile(final_prices, 5),
            '25th': np.percentile(final_prices, 25),
            '50th': np.percentile(final_prices, 50),
            '75th': np.percentile(final_prices, 75),
            '95th': np.percentile(final_prices, 95)
        }

        # Calculate probability of profit
        prob_profit = np.sum(final_prices > current_price) / num_simulations

        # Calculate expected returns
        returns = (final_prices - current_price) / current_price
        expected_return = np.mean(returns)
        expected_return_std = np.std(returns)

        # Value at Risk (VaR) - 95% confidence
        var_95 = np.percentile(returns, 5)

        # Conditional Value at Risk (CVaR) - Expected loss beyond VaR
        cvar_95 = returns[returns <= var_95].mean()

        # Generate daily statistics for each day
        daily_stats = []
        last_date = self.price_df.iloc[-1]['date']

        for day in range(days + 1):
            day_prices = simulations[:, day]
            day_date = last_date + timedelta(days=day)

            daily_stats.append({
                'day': day,
                'date': day_date.strftime('%Y-%m-%d'),
                'mean': np.mean(day_prices),
                'median': np.median(day_prices),
                'std': np.std(day_prices),
                '5th_percentile': np.percentile(day_prices, 5),
                '25th_percentile': np.percentile(day_prices, 25),
                '75th_percentile': np.percentile(day_prices, 75),
                '95th_percentile': np.percentile(day_prices, 95),
                'min': np.min(day_prices),
                'max': np.max(day_prices)
            })

        return {
            'simulations': simulations.tolist(),
            'current_price': float(current_price),
            'days': days,
            'num_simulations': num_simulations,
            'final_price_stats': {
                'mean': float(np.mean(final_prices)),
                'median': float(np.median(final_prices)),
                'std': float(np.std(final_prices)),
                'min': float(np.min(final_prices)),
                'max': float(np.max(final_prices))
            },
            'percentiles': {k: float(v) for k, v in percentiles.items()},
            'prob_profit': float(prob_profit),
            'prob_profit_pct': float(prob_profit * 100),
            'expected_return': float(expected_return),
            'expected_return_pct': float(expected_return * 100),
            'expected_return_std': float(expected_return_std),
            'var_95': float(var_95),
            'var_95_pct': float(var_95 * 100),
            'cvar_95': float(cvar_95),
            'cvar_95_pct': float(cvar_95 * 100),
            'daily_stats': daily_stats,
            'historical_stats': {
                'mean_return': float(self.mean_return),
                'std_return': float(self.std_return),
                'mean_return_pct': float(self.mean_return * 100),
                'std_return_pct': float(self.std_return * 100)
            }
        }

    def run_scenario_analysis(self, scenarios=None):
        """
        Run specific scenario analyses

        Args:
            scenarios: Dict of scenarios (bull, base, bear) with custom parameters

        Returns:
            Results for each scenario
        """
        if scenarios is None:
            # Default scenarios
            scenarios = {
                'Bull Case': {
                    'mean_return': self.mean_return * 1.5,
                    'std_return': self.std_return * 0.8
                },
                'Base Case': {
                    'mean_return': self.mean_return,
                    'std_return': self.std_return
                },
                'Bear Case': {
                    'mean_return': self.mean_return * -0.5,
                    'std_return': self.std_return * 1.2
                }
            }

        results = {}

        for scenario_name, params in scenarios.items():
            # Temporarily override parameters
            original_mean = self.mean_return
            original_std = self.std_return

            self.mean_return = params['mean_return']
            self.std_return = params['std_return']

            # Run simulation
            result = self.simulate_price_paths(days=30, num_simulations=1000)
            result['scenario'] = scenario_name
            results[scenario_name] = result

            # Restore original parameters
            self.mean_return = original_mean
            self.std_return = original_std

        return results

    def calculate_option_probabilities(self, strike_price, days=30, option_type='call'):
        """
        Calculate probability of an option being in-the-money

        Args:
            strike_price: Option strike price
            days: Days until expiration
            option_type: 'call' or 'put'

        Returns:
            Probability statistics
        """
        result = self.simulate_price_paths(days=days, num_simulations=10000)
        simulations = np.array(result['simulations'])
        final_prices = simulations[:, -1]

        if option_type == 'call':
            itm = final_prices > strike_price
            intrinsic_value = np.maximum(final_prices - strike_price, 0)
        else:  # put
            itm = final_prices < strike_price
            intrinsic_value = np.maximum(strike_price - final_prices, 0)

        prob_itm = np.sum(itm) / len(final_prices)
        expected_payoff = np.mean(intrinsic_value)

        return {
            'option_type': option_type,
            'strike_price': float(strike_price),
            'current_price': float(result['current_price']),
            'days_to_expiration': days,
            'prob_itm': float(prob_itm),
            'prob_itm_pct': float(prob_itm * 100),
            'expected_payoff': float(expected_payoff),
            'max_payoff': float(np.max(intrinsic_value)),
            'avg_itm_payoff': float(np.mean(intrinsic_value[itm])) if np.sum(itm) > 0 else 0
        }
