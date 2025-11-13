"""
Advanced Backtesting Simulator
Simulates different trading strategies and calculates performance metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class Backtester:
    """
    Advanced backtesting engine for testing trading strategies
    """

    def __init__(self, initial_capital=10000, commission=0.001):
        """
        Initialize backtester

        Args:
            initial_capital: Starting capital in dollars
            commission: Trading commission (0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.trades = []
        self.equity_curve = []

    def run_strategy(self, predictions_df, price_df, strategy='simple',
                     stop_loss=None, take_profit=None, position_size=0.5):
        """
        Run backtesting simulation

        Args:
            predictions_df: DataFrame with predictions
            price_df: DataFrame with price data
            strategy: Trading strategy ('simple', 'confidence', 'kelly', 'martingale')
            stop_loss: Stop loss percentage (e.g., 0.02 = 2%)
            take_profit: Take profit percentage (e.g., 0.05 = 5%)
            position_size: Fraction of capital to use per trade (0-1)

        Returns:
            Dictionary with backtest results
        """
        capital = self.initial_capital
        position = 0  # Current position (-1: short, 0: neutral, 1: long)
        entry_price = 0
        trades = []
        equity_curve = []

        # Merge predictions with prices
        predictions_df['data_date'] = pd.to_datetime(predictions_df['data_date'])
        price_df['date'] = pd.to_datetime(price_df['date'])

        for _, pred in predictions_df.iterrows():
            pred_date = pred['data_date']

            # Find current and next day prices
            current_price_row = price_df[price_df['date'] == pred_date]

            if len(current_price_row) == 0:
                continue

            current_price = current_price_row.iloc[0]['close']
            current_idx = price_df[price_df['date'] == pred_date].index[0]

            # Get next day price
            if current_idx + 1 >= len(price_df):
                break

            next_price = price_df.iloc[current_idx + 1]['close']
            next_date = price_df.iloc[current_idx + 1]['date']

            # Calculate position size based on strategy
            if strategy == 'simple':
                trade_size = position_size
            elif strategy == 'confidence':
                # Use confidence to scale position size
                trade_size = position_size * pred['confidence']
            elif strategy == 'kelly':
                # Kelly Criterion: f = (bp - q) / b
                # where b = odds, p = win probability, q = 1-p
                # Simplified: use confidence as win probability
                p = pred['confidence']
                b = 1.0  # 1:1 odds
                kelly_fraction = (b * p - (1 - p)) / b
                trade_size = max(0, min(kelly_fraction, position_size))
            elif strategy == 'martingale':
                # Double position after losses (risky!)
                if len(trades) > 0 and trades[-1]['pnl'] < 0:
                    trade_size = min(position_size * 2, 1.0)
                else:
                    trade_size = position_size
            else:
                trade_size = position_size

            # Close existing position
            if position != 0:
                pnl = 0
                if position == 1:  # Long position
                    pnl = (next_price - entry_price) / entry_price
                elif position == -1:  # Short position
                    pnl = (entry_price - next_price) / entry_price

                # Apply commission
                pnl -= self.commission * 2  # Entry + exit

                # Update capital
                trade_capital = capital * abs(position)
                capital = capital + (trade_capital * pnl)

                trades.append({
                    'entry_date': entry_date,
                    'exit_date': next_date,
                    'entry_price': entry_price,
                    'exit_price': next_price,
                    'direction': 'LONG' if position == 1 else 'SHORT',
                    'pnl': pnl,
                    'pnl_dollars': trade_capital * pnl,
                    'capital': capital
                })

                position = 0

            # Check stop loss and take profit
            if stop_loss and position != 0:
                current_pnl = (next_price - entry_price) / entry_price if position == 1 else (entry_price - next_price) / entry_price
                if current_pnl <= -stop_loss:
                    # Stop loss triggered
                    position = 0
                    continue

            if take_profit and position != 0:
                current_pnl = (next_price - entry_price) / entry_price if position == 1 else (entry_price - next_price) / entry_price
                if current_pnl >= take_profit:
                    # Take profit triggered
                    position = 0
                    continue

            # Open new position based on prediction
            if pred['direction'] == 'UP':
                position = trade_size
                entry_price = next_price
                entry_date = next_date
            elif pred['direction'] == 'DOWN':
                position = -trade_size
                entry_price = next_price
                entry_date = next_date

            # Record equity
            equity_curve.append({
                'date': next_date,
                'capital': capital,
                'return': (capital - self.initial_capital) / self.initial_capital
            })

        # Calculate performance metrics
        results = self.calculate_metrics(trades, equity_curve)
        results['trades'] = trades
        results['equity_curve'] = equity_curve
        results['strategy'] = strategy

        return results

    def calculate_metrics(self, trades, equity_curve):
        """Calculate performance metrics"""
        if len(trades) == 0:
            return {
                'total_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_trades': 0
            }

        trades_df = pd.DataFrame(trades)
        equity_df = pd.DataFrame(equity_curve)

        # Total return
        final_capital = trades_df.iloc[-1]['capital']
        total_return = (final_capital - self.initial_capital) / self.initial_capital

        # Win rate
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        win_rate = winning_trades / len(trades_df)

        # Profit factor
        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl_dollars'].sum()
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl_dollars'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # Sharpe ratio (annualized)
        returns = equity_df['return'].pct_change().dropna()
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0

        # Maximum drawdown
        equity_df['peak'] = equity_df['capital'].cummax()
        equity_df['drawdown'] = (equity_df['capital'] - equity_df['peak']) / equity_df['peak']
        max_drawdown = equity_df['drawdown'].min()

        # Average trade metrics
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if len(trades_df) - winning_trades > 0 else 0

        return {
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'final_capital': final_capital,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'profit_factor': profit_factor,
            'total_trades': len(trades_df),
            'winning_trades': winning_trades,
            'losing_trades': len(trades_df) - winning_trades,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_win_pct': avg_win * 100,
            'avg_loss_pct': avg_loss * 100
        }

    def compare_strategies(self, predictions_df, price_df):
        """Compare multiple trading strategies"""
        strategies = {
            'Simple (50%)': {'strategy': 'simple', 'position_size': 0.5},
            'Confidence-Based': {'strategy': 'confidence', 'position_size': 1.0},
            'Kelly Criterion': {'strategy': 'kelly', 'position_size': 1.0},
            'Conservative (25%)': {'strategy': 'simple', 'position_size': 0.25},
            'Aggressive (100%)': {'strategy': 'simple', 'position_size': 1.0},
        }

        results = {}
        for name, params in strategies.items():
            result = self.run_strategy(predictions_df, price_df, **params)
            results[name] = result

        return results
