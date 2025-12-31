"""
Real-Time Trading Simulation Tracker
=====================================
Tracks a simulated portfolio starting with $10,000 based on model predictions.
Designed to run for 5 months to evaluate model performance.

Features:
- Tracks daily portfolio value
- Records all trades (buy/sell decisions)
- Calculates win/loss for each prediction
- Maintains running statistics
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os
import json

class TradingSimulationTracker:
    """
    Real-time trading simulation that tracks portfolio based on predictions.

    Strategy:
    - When prediction is UP: Buy (invest 50% of portfolio)
    - When prediction is DOWN: Hold cash (no position)
    - Track actual market movement to determine win/loss
    """

    def __init__(self, initial_capital=10000.0, position_size=0.5):
        self.initial_capital = initial_capital
        self.position_size = position_size  # 50% of portfolio per trade

        # File paths
        self.portfolio_file = 'data/trading_simulation/portfolio_history.csv'
        self.trades_file = 'data/trading_simulation/trades_history.csv'
        self.summary_file = 'data/trading_simulation/simulation_summary.json'

        # Create directory if needed
        os.makedirs('data/trading_simulation', exist_ok=True)

        # Load or initialize portfolio
        self.portfolio_history = self._load_portfolio_history()
        self.trades_history = self._load_trades_history()

    def _load_portfolio_history(self):
        """Load existing portfolio history or create new"""
        if os.path.exists(self.portfolio_file):
            df = pd.read_csv(self.portfolio_file)
            df['date'] = pd.to_datetime(df['date'], format='mixed')
            return df
        else:
            # Initialize with starting capital
            return pd.DataFrame({
                'date': [datetime.now().strftime('%Y-%m-%d')],
                'portfolio_value': [self.initial_capital],
                'cash': [self.initial_capital],
                'position_value': [0.0],
                'shares': [0.0],
                'daily_return': [0.0],
                'cumulative_return': [0.0],
                'prediction': ['START'],
                'market_return': [0.0]
            })

    def _load_trades_history(self):
        """Load existing trades or create new"""
        if os.path.exists(self.trades_file):
            df = pd.read_csv(self.trades_file)
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='mixed')
            if 'data_date' in df.columns:
                df['data_date'] = pd.to_datetime(df['data_date'], format='mixed')
            return df
        else:
            return pd.DataFrame(columns=[
                'trade_date', 'prediction_date', 'prediction', 'confidence',
                'action', 'shares', 'price', 'trade_value',
                'result', 'profit_loss', 'portfolio_value_before', 'portfolio_value_after'
            ])

    def get_current_portfolio_value(self):
        """Get the most recent portfolio value"""
        if len(self.portfolio_history) > 0:
            return self.portfolio_history.iloc[-1]['portfolio_value']
        return self.initial_capital

    def get_current_position(self):
        """Get current position details"""
        if len(self.portfolio_history) > 0:
            last = self.portfolio_history.iloc[-1]
            return {
                'cash': last['cash'],
                'shares': last['shares'],
                'position_value': last['position_value'],
                'total_value': last['portfolio_value']
            }
        return {
            'cash': self.initial_capital,
            'shares': 0,
            'position_value': 0,
            'total_value': self.initial_capital
        }

    def process_prediction(self, prediction_date, data_date, direction, confidence,
                           current_price, next_price=None, next_date=None):
        """
        Process a prediction and update portfolio accordingly.

        Args:
            prediction_date: When prediction was made
            data_date: Date the prediction is for
            direction: 'UP' or 'DOWN'
            confidence: Model confidence (0-1)
            current_price: S&P 500 price on data_date
            next_price: Actual price on next trading day (for verification)
            next_date: The next trading day date

        Returns:
            dict with trade results
        """
        position = self.get_current_position()

        # Calculate trade details
        portfolio_before = position['total_value']

        # Determine action based on prediction
        if direction == 'UP':
            # Buy signal - invest position_size of portfolio
            action = 'BUY'
            invest_amount = position['cash'] * self.position_size
            shares_to_buy = invest_amount / current_price if current_price > 0 else 0

            new_cash = position['cash'] - invest_amount
            new_shares = position['shares'] + shares_to_buy
            new_position_value = new_shares * current_price
        else:
            # Hold/Sell signal - move to cash
            action = 'HOLD_CASH'
            # If we have shares, sell them
            if position['shares'] > 0:
                action = 'SELL'
                sell_value = position['shares'] * current_price
                new_cash = position['cash'] + sell_value
                new_shares = 0
                new_position_value = 0
            else:
                new_cash = position['cash']
                new_shares = 0
                new_position_value = 0

        # Calculate market return if next_price is available
        market_return = 0.0
        result = 'PENDING'
        profit_loss = 0.0

        if next_price is not None and current_price > 0:
            market_return = ((next_price - current_price) / current_price) * 100
            actual_direction = 'UP' if market_return > 0 else 'DOWN'

            # Determine if prediction was correct
            is_correct = (direction == actual_direction)

            # Calculate actual profit/loss based on position
            if action in ['BUY'] and new_shares > 0:
                # We held a position
                position_pnl = new_shares * (next_price - current_price)
                new_position_value = new_shares * next_price
                profit_loss = position_pnl

                if is_correct:
                    result = 'WIN' if market_return > 0 else 'CORRECT_HOLD'
                else:
                    result = 'LOSS' if market_return < 0 else 'WRONG_MISS'
            else:
                # We held cash
                if is_correct:
                    result = 'CORRECT_SAVE'  # Avoided loss
                else:
                    result = 'MISSED_GAIN'  # Missed opportunity

        # Calculate new portfolio value
        portfolio_after = new_cash + new_position_value
        daily_return = ((portfolio_after - portfolio_before) / portfolio_before) * 100 if portfolio_before > 0 else 0
        cumulative_return = ((portfolio_after - self.initial_capital) / self.initial_capital) * 100

        # Record the trade
        trade_record = {
            'trade_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prediction_date': prediction_date,
            'data_date': data_date,
            'prediction': direction,
            'confidence': confidence,
            'action': action,
            'shares': shares_to_buy if action == 'BUY' else (position['shares'] if action == 'SELL' else 0),
            'price': current_price,
            'trade_value': invest_amount if action == 'BUY' else (position['shares'] * current_price if action == 'SELL' else 0),
            'result': result,
            'profit_loss': profit_loss,
            'market_return': market_return,
            'portfolio_value_before': portfolio_before,
            'portfolio_value_after': portfolio_after
        }

        # Update portfolio history
        portfolio_record = {
            'date': next_date if next_date else data_date,
            'portfolio_value': portfolio_after,
            'cash': new_cash,
            'position_value': new_position_value,
            'shares': new_shares,
            'daily_return': daily_return,
            'cumulative_return': cumulative_return,
            'prediction': direction,
            'market_return': market_return
        }

        # Append to histories
        self.trades_history = pd.concat([
            self.trades_history,
            pd.DataFrame([trade_record])
        ], ignore_index=True)

        self.portfolio_history = pd.concat([
            self.portfolio_history,
            pd.DataFrame([portfolio_record])
        ], ignore_index=True)

        # Save to files
        self._save_all()

        return trade_record

    def update_pending_trades(self):
        """
        Update any pending trades with actual market results.
        Called after market data is available.
        """
        # Load predictions with accuracy data
        accuracy_file = 'predictions_with_accuracy.csv'
        if not os.path.exists(accuracy_file):
            return []

        acc_df = pd.read_csv(accuracy_file)
        acc_df['data_date'] = pd.to_datetime(acc_df['data_date'])

        # Find pending trades
        pending_mask = self.trades_history['result'] == 'PENDING'
        if not pending_mask.any():
            return []

        updated = []
        for idx, trade in self.trades_history[pending_mask].iterrows():
            trade_data_date = pd.to_datetime(trade['data_date'])

            # Find matching accuracy record
            match = acc_df[acc_df['data_date'] == trade_data_date]
            if len(match) > 0:
                actual = match.iloc[0]

                # Update trade result
                market_return = actual['actual_return']
                is_correct = actual['is_correct']

                if trade['action'] == 'BUY':
                    profit_loss = trade['shares'] * actual['current_price'] * (market_return / 100)
                    result = 'WIN' if is_correct else 'LOSS'
                else:
                    profit_loss = 0
                    result = 'CORRECT_SAVE' if is_correct else 'MISSED_GAIN'

                self.trades_history.at[idx, 'result'] = result
                self.trades_history.at[idx, 'profit_loss'] = profit_loss
                self.trades_history.at[idx, 'market_return'] = market_return

                updated.append(idx)

        if updated:
            self._save_all()

        return updated

    def _save_all(self):
        """Save all data to files"""
        self.portfolio_history.to_csv(self.portfolio_file, index=False)
        self.trades_history.to_csv(self.trades_file, index=False)
        self._save_summary()

    def _save_summary(self):
        """Save simulation summary"""
        summary = self.get_summary()
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

    def get_summary(self):
        """Get comprehensive simulation summary"""
        if len(self.trades_history) == 0:
            return {
                'status': 'NOT_STARTED',
                'initial_capital': self.initial_capital,
                'current_value': self.initial_capital,
                'total_return': 0,
                'trades_count': 0
            }

        current_value = self.get_current_portfolio_value()
        total_return = ((current_value - self.initial_capital) / self.initial_capital) * 100

        # Count results
        results = self.trades_history['result'].value_counts().to_dict()

        # Calculate win rate (excluding pending)
        completed = self.trades_history[self.trades_history['result'] != 'PENDING']
        wins = len(completed[completed['result'].isin(['WIN', 'CORRECT_SAVE'])])
        total_completed = len(completed)
        win_rate = (wins / total_completed * 100) if total_completed > 0 else 0

        # Calculate days active
        start_date = pd.to_datetime(self.portfolio_history['date'].min())
        end_date = pd.to_datetime(self.portfolio_history['date'].max())
        days_active = (end_date - start_date).days

        # Best and worst days
        if len(self.portfolio_history) > 1:
            best_day = self.portfolio_history.loc[self.portfolio_history['daily_return'].idxmax()]
            worst_day = self.portfolio_history.loc[self.portfolio_history['daily_return'].idxmin()]
        else:
            best_day = worst_day = None

        return {
            'status': 'ACTIVE',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'days_active': days_active,
            'months_active': round(days_active / 30, 1),
            'initial_capital': self.initial_capital,
            'current_value': round(current_value, 2),
            'total_return': round(total_return, 2),
            'total_return_dollars': round(current_value - self.initial_capital, 2),
            'trades_count': len(self.trades_history),
            'completed_trades': total_completed,
            'pending_trades': len(self.trades_history[self.trades_history['result'] == 'PENDING']),
            'results': results,
            'win_rate': round(win_rate, 2),
            'best_day': {
                'date': str(best_day['date']) if best_day is not None else None,
                'return': round(float(best_day['daily_return']), 2) if best_day is not None else None
            },
            'worst_day': {
                'date': str(worst_day['date']) if worst_day is not None else None,
                'return': round(float(worst_day['daily_return']), 2) if worst_day is not None else None
            }
        }

    def process_historical_predictions(self, predictions_with_accuracy_file='predictions_with_accuracy.csv'):
        """
        Process historical predictions to build simulation history.
        Use this to backfill the simulation from existing prediction data.
        """
        if not os.path.exists(predictions_with_accuracy_file):
            print("No predictions with accuracy file found")
            return

        df = pd.read_csv(predictions_with_accuracy_file)
        df['data_date'] = pd.to_datetime(df['data_date'])
        df = df.sort_values('data_date')

        # Reset simulation
        self.portfolio_history = pd.DataFrame()
        self.trades_history = pd.DataFrame(columns=[
            'trade_date', 'prediction_date', 'data_date', 'prediction', 'confidence',
            'action', 'shares', 'price', 'trade_value',
            'result', 'profit_loss', 'market_return',
            'portfolio_value_before', 'portfolio_value_after'
        ])

        # Initialize
        cash = self.initial_capital
        shares = 0.0

        print(f"\nProcessing {len(df)} historical predictions...")
        print(f"Starting capital: ${self.initial_capital:,.2f}")
        print("-" * 60)

        for idx, row in df.iterrows():
            current_price = row['current_price']
            next_price = row['next_price']
            prediction = row['predicted_direction']
            confidence = row['confidence']
            is_correct = row['is_correct']
            market_return = row['actual_return']

            portfolio_before = cash + (shares * current_price)

            # Execute trade based on prediction
            if prediction == 'UP':
                # Buy signal
                if shares == 0:  # Not already in position
                    invest_amount = cash * self.position_size
                    shares_to_buy = invest_amount / current_price if current_price > 0 else 0
                    cash -= invest_amount
                    shares = shares_to_buy
                    action = 'BUY'
                    trade_value = invest_amount
                else:
                    action = 'HOLD_LONG'
                    trade_value = 0
                    shares_to_buy = 0
            else:
                # Sell/Hold cash signal
                if shares > 0:
                    sell_value = shares * current_price
                    cash += sell_value
                    action = 'SELL'
                    trade_value = sell_value
                    shares_to_buy = shares
                    shares = 0
                else:
                    action = 'HOLD_CASH'
                    trade_value = 0
                    shares_to_buy = 0

            # Calculate P&L for day
            if shares > 0:
                # We held a position overnight
                position_pnl = shares * (next_price - current_price)
            else:
                position_pnl = 0

            # Update shares value to next day's price
            if shares > 0:
                position_value = shares * next_price
            else:
                position_value = 0

            portfolio_after = cash + position_value
            daily_return = ((portfolio_after - portfolio_before) / portfolio_before * 100) if portfolio_before > 0 else 0
            cumulative_return = ((portfolio_after - self.initial_capital) / self.initial_capital * 100)

            # Determine result
            if action == 'BUY' or action == 'HOLD_LONG':
                result = 'WIN' if is_correct else 'LOSS'
            else:
                result = 'CORRECT_SAVE' if is_correct else 'MISSED_GAIN'

            # Record trade
            trade_record = {
                'trade_date': row['prediction_date'],
                'prediction_date': row['prediction_date'],
                'data_date': row['data_date'],
                'prediction': prediction,
                'confidence': confidence,
                'action': action,
                'shares': shares_to_buy,
                'price': current_price,
                'trade_value': trade_value,
                'result': result,
                'profit_loss': position_pnl,
                'market_return': market_return,
                'portfolio_value_before': portfolio_before,
                'portfolio_value_after': portfolio_after
            }

            # Record portfolio state
            portfolio_record = {
                'date': row['next_date'] if 'next_date' in row else row['data_date'],
                'portfolio_value': portfolio_after,
                'cash': cash,
                'position_value': position_value,
                'shares': shares,
                'daily_return': daily_return,
                'cumulative_return': cumulative_return,
                'prediction': prediction,
                'market_return': market_return
            }

            self.trades_history = pd.concat([
                self.trades_history,
                pd.DataFrame([trade_record])
            ], ignore_index=True)

            self.portfolio_history = pd.concat([
                self.portfolio_history,
                pd.DataFrame([portfolio_record])
            ], ignore_index=True)

        # Save all data
        self._save_all()

        # Print summary
        summary = self.get_summary()
        print(f"\nSimulation Complete!")
        print(f"=" * 60)
        print(f"Start Date:       {summary['start_date']}")
        print(f"End Date:         {summary['end_date']}")
        print(f"Days Active:      {summary['days_active']} ({summary['months_active']} months)")
        print(f"-" * 60)
        print(f"Initial Capital:  ${summary['initial_capital']:,.2f}")
        print(f"Final Value:      ${summary['current_value']:,.2f}")
        print(f"Total Return:     {summary['total_return']:+.2f}% (${summary['total_return_dollars']:+,.2f})")
        print(f"-" * 60)
        print(f"Total Trades:     {summary['trades_count']}")
        print(f"Win Rate:         {summary['win_rate']:.1f}%")
        print(f"-" * 60)
        print(f"Results Breakdown:")
        for result, count in summary['results'].items():
            print(f"  {result}: {count}")
        print(f"=" * 60)

        return summary


def run_simulation_from_history():
    """Run simulation from existing prediction history"""
    tracker = TradingSimulationTracker(initial_capital=10000.0)
    summary = tracker.process_historical_predictions()
    return tracker, summary


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("S&P 500 TRADING SIMULATION TRACKER")
    print("=" * 60)
    print(f"Starting Capital: $10,000")
    print(f"Position Size: 50% per trade")
    print("=" * 60)

    tracker, summary = run_simulation_from_history()
