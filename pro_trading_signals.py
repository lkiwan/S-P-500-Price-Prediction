"""
Professional Trading Signals Module
====================================
Generates LONG/SHORT signals with ATR-based TP/SL levels
and calculates professional trading metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple
import os
import json

# Data paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_DIR = os.path.join(BASE_DIR, 'data', 'trading_signals')
SIGNALS_HISTORY_FILE = os.path.join(SIGNALS_DIR, 'signals_history.csv')
PRICE_DATA_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'price_data.csv')
FEATURES_FILE = os.path.join(BASE_DIR, 'data', 'features', 'features_complete.csv')
PREDICTIONS_FILE = os.path.join(BASE_DIR, 'predictions_with_accuracy.csv')


@dataclass
class TradingSignal:
    """Data class for a trading signal"""
    signal_id: int
    signal_date: str
    data_date: str
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    take_profit: float
    stop_loss: float
    confidence: float
    risk_reward: float
    atr: float
    bb_upper: float
    bb_lower: float
    status: str  # 'ACTIVE', 'TP_HIT', 'SL_HIT', 'EXPIRED'
    outcome: str  # 'WIN', 'LOSS', 'PENDING'
    exit_price: Optional[float] = None
    exit_date: Optional[str] = None
    pnl_percent: Optional[float] = None
    pnl_dollars: Optional[float] = None
    trade_duration_days: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    """
    Calculate Average True Range for volatility-based TP/SL.

    True Range = max(High - Low, |High - Prev Close|, |Low - Prev Close|)
    ATR = SMA(True Range, period)
    """
    high = df['High'] if 'High' in df.columns else df['high']
    low = df['Low'] if 'Low' in df.columns else df['low']
    close = df['Close'] if 'Close' in df.columns else df['close']

    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean().iloc[-1]

    return float(atr) if not pd.isna(atr) else 0.0


def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
    """Calculate Bollinger Bands (upper, middle, lower)"""
    close = df['Close'] if 'Close' in df.columns else df['close']

    middle = close.rolling(window=period).mean().iloc[-1]
    std = close.rolling(window=period).std().iloc[-1]

    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)

    return float(upper), float(middle), float(lower)


def calculate_hybrid_tp_sl(
    entry_price: float,
    direction: str,
    atr: float,
    bb_upper: float,
    bb_lower: float,
    confidence: float,
    recent_high: float,
    recent_low: float
) -> dict:
    """
    Hybrid TP/SL Calculation combining ATR and Support/Resistance

    ATR-based with confidence adjustment:
    - Higher confidence = wider TP, tighter SL
    - conf_factor ranges from 0.75 to 1.25
    """
    # Confidence adjustment factor (0.5 confidence -> 0.75, 1.0 confidence -> 1.25)
    conf_factor = 0.75 + (confidence - 0.5) * 1.0
    conf_factor = max(0.75, min(1.25, conf_factor))  # Clamp to range

    # Base ATR multipliers
    tp_multiplier = 1.5 * conf_factor
    sl_multiplier = 1.0 / conf_factor

    if direction == 'LONG':
        # ATR-based levels
        atr_tp = entry_price + (atr * tp_multiplier)
        atr_sl = entry_price - (atr * sl_multiplier)

        # S/R adjusted (cap TP at BB upper + 2%, floor SL at recent low - 0.5%)
        tp = min(atr_tp, bb_upper * 1.02)
        sl = max(atr_sl, recent_low * 0.995)

    else:  # SHORT
        atr_tp = entry_price - (atr * tp_multiplier)
        atr_sl = entry_price + (atr * sl_multiplier)

        # S/R adjusted
        tp = max(atr_tp, bb_lower * 0.98)
        sl = min(atr_sl, recent_high * 1.005)

    # Calculate risk/reward ratio
    risk = abs(entry_price - sl)
    reward = abs(tp - entry_price)
    risk_reward = reward / risk if risk > 0 else 0

    return {
        'take_profit': round(tp, 2),
        'stop_loss': round(sl, 2),
        'risk_reward': round(risk_reward, 2),
        'tp_distance_pct': round(abs(tp - entry_price) / entry_price * 100, 3),
        'sl_distance_pct': round(abs(entry_price - sl) / entry_price * 100, 3)
    }


class ProTradingSignalGenerator:
    """Generate professional trading signals with TP/SL levels"""

    def __init__(self):
        self.signals_dir = SIGNALS_DIR
        self.signals_file = SIGNALS_HISTORY_FILE
        os.makedirs(self.signals_dir, exist_ok=True)

    def load_price_data(self, days: int = 30) -> pd.DataFrame:
        """Load recent price data"""
        try:
            df = pd.read_csv(PRICE_DATA_FILE)
            # Standardize column names
            df.columns = [c.capitalize() if c.lower() in ['open', 'high', 'low', 'close', 'volume'] else c for c in df.columns]
            if 'Date' not in df.columns and 'date' in df.columns:
                df.rename(columns={'date': 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'], format='mixed')
            df = df.sort_values('Date').tail(days)
            return df
        except Exception as e:
            print(f"Error loading price data: {e}")
            return pd.DataFrame()

    def load_predictions(self) -> pd.DataFrame:
        """Load predictions with accuracy data"""
        try:
            df = pd.read_csv(PREDICTIONS_FILE)
            df['data_date'] = pd.to_datetime(df['data_date'], format='mixed')
            df['prediction_date'] = pd.to_datetime(df['prediction_date'], format='mixed')
            return df.sort_values('data_date')
        except Exception as e:
            print(f"Error loading predictions: {e}")
            return pd.DataFrame()

    def load_signals_history(self) -> pd.DataFrame:
        """Load existing signals history"""
        try:
            if os.path.exists(self.signals_file):
                df = pd.read_csv(self.signals_file)
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Error loading signals history: {e}")
            return pd.DataFrame()

    def save_signal(self, signal: TradingSignal):
        """Save a signal to history"""
        df = self.load_signals_history()
        new_row = pd.DataFrame([signal.to_dict()])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.signals_file, index=False)

    def generate_signal(self, prediction: dict, price_data: pd.DataFrame) -> Optional[TradingSignal]:
        """
        Generate a trading signal from prediction data.

        Args:
            prediction: dict with keys: direction, confidence, prob_up, prob_down, data_date
            price_data: Recent OHLCV data
        """
        if price_data.empty:
            return None

        # Get entry price (latest close)
        entry_price = float(price_data['Close'].iloc[-1])

        # Calculate ATR
        atr = calculate_atr(price_data)
        if atr == 0:
            atr = entry_price * 0.01  # Fallback: 1% of price

        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(price_data)

        # Get recent high/low (5 days)
        recent_high = float(price_data['High'].tail(5).max())
        recent_low = float(price_data['Low'].tail(5).min())

        # Determine direction
        direction = 'LONG' if prediction.get('direction', 'UP') == 'UP' else 'SHORT'
        confidence = float(prediction.get('confidence', 0.5))

        # Calculate TP/SL
        levels = calculate_hybrid_tp_sl(
            entry_price=entry_price,
            direction=direction,
            atr=atr,
            bb_upper=bb_upper,
            bb_lower=bb_lower,
            confidence=confidence,
            recent_high=recent_high,
            recent_low=recent_low
        )

        # Get next signal ID
        existing = self.load_signals_history()
        next_id = int(existing['signal_id'].max()) + 1 if not existing.empty and 'signal_id' in existing.columns else 1

        signal = TradingSignal(
            signal_id=next_id,
            signal_date=datetime.now().strftime('%Y-%m-%d'),
            data_date=str(prediction.get('data_date', datetime.now().strftime('%Y-%m-%d'))),
            direction=direction,
            entry_price=entry_price,
            take_profit=levels['take_profit'],
            stop_loss=levels['stop_loss'],
            confidence=confidence,
            risk_reward=levels['risk_reward'],
            atr=round(atr, 2),
            bb_upper=round(bb_upper, 2),
            bb_lower=round(bb_lower, 2),
            status='ACTIVE',
            outcome='PENDING'
        )

        return signal

    def update_signal_outcomes(self, price_data: pd.DataFrame):
        """Update outcomes for active signals based on price data"""
        df = self.load_signals_history()
        if df.empty:
            return

        active_signals = df[df['status'] == 'ACTIVE']

        for idx, signal in active_signals.iterrows():
            # Get price data after signal date
            signal_date = pd.to_datetime(signal['signal_date'])
            future_prices = price_data[price_data['Date'] > signal_date]

            if future_prices.empty:
                continue

            tp = signal['take_profit']
            sl = signal['stop_loss']
            direction = signal['direction']
            entry = signal['entry_price']

            for _, day in future_prices.iterrows():
                high = day['High']
                low = day['Low']
                close = day['Close']

                if direction == 'LONG':
                    # Check if TP hit
                    if high >= tp:
                        df.loc[idx, 'status'] = 'TP_HIT'
                        df.loc[idx, 'outcome'] = 'WIN'
                        df.loc[idx, 'exit_price'] = tp
                        df.loc[idx, 'exit_date'] = day['Date'].strftime('%Y-%m-%d')
                        df.loc[idx, 'pnl_percent'] = round((tp - entry) / entry * 100, 3)
                        df.loc[idx, 'trade_duration_days'] = (day['Date'] - signal_date).days
                        break
                    # Check if SL hit
                    elif low <= sl:
                        df.loc[idx, 'status'] = 'SL_HIT'
                        df.loc[idx, 'outcome'] = 'LOSS'
                        df.loc[idx, 'exit_price'] = sl
                        df.loc[idx, 'exit_date'] = day['Date'].strftime('%Y-%m-%d')
                        df.loc[idx, 'pnl_percent'] = round((sl - entry) / entry * 100, 3)
                        df.loc[idx, 'trade_duration_days'] = (day['Date'] - signal_date).days
                        break
                else:  # SHORT
                    # Check if TP hit (price goes down)
                    if low <= tp:
                        df.loc[idx, 'status'] = 'TP_HIT'
                        df.loc[idx, 'outcome'] = 'WIN'
                        df.loc[idx, 'exit_price'] = tp
                        df.loc[idx, 'exit_date'] = day['Date'].strftime('%Y-%m-%d')
                        df.loc[idx, 'pnl_percent'] = round((entry - tp) / entry * 100, 3)
                        df.loc[idx, 'trade_duration_days'] = (day['Date'] - signal_date).days
                        break
                    # Check if SL hit (price goes up)
                    elif high >= sl:
                        df.loc[idx, 'status'] = 'SL_HIT'
                        df.loc[idx, 'outcome'] = 'LOSS'
                        df.loc[idx, 'exit_price'] = sl
                        df.loc[idx, 'exit_date'] = day['Date'].strftime('%Y-%m-%d')
                        df.loc[idx, 'pnl_percent'] = round((entry - sl) / entry * 100, 3)
                        df.loc[idx, 'trade_duration_days'] = (day['Date'] - signal_date).days
                        break

        df.to_csv(self.signals_file, index=False)

    def get_current_signal(self) -> Optional[dict]:
        """Get the most recent active signal"""
        df = self.load_signals_history()
        if df.empty:
            return None

        # Get latest signal
        latest = df.iloc[-1].to_dict()

        # Get current price for P&L calculation
        price_data = self.load_price_data(5)
        if not price_data.empty:
            current_price = float(price_data['Close'].iloc[-1])
            entry = latest['entry_price']

            if latest['direction'] == 'LONG':
                latest['current_pnl_pct'] = round((current_price - entry) / entry * 100, 3)
            else:
                latest['current_pnl_pct'] = round((entry - current_price) / entry * 100, 3)

            latest['current_price'] = current_price

        return latest

    def backfill_signals(self):
        """Generate historical signals from existing predictions"""
        predictions = self.load_predictions()
        price_data = self.load_price_data(days=500)

        if predictions.empty or price_data.empty:
            print("No data available for backfill")
            return

        signals = []
        signal_id = 1

        for idx, pred in predictions.iterrows():
            pred_date = pred['data_date']

            # Get price data up to prediction date
            hist_prices = price_data[price_data['Date'] <= pred_date].tail(30)
            if len(hist_prices) < 14:  # Need at least 14 days for ATR
                continue

            entry_price = float(hist_prices['Close'].iloc[-1])
            atr = calculate_atr(hist_prices)
            if atr == 0:
                atr = entry_price * 0.01

            bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(hist_prices)
            recent_high = float(hist_prices['High'].tail(5).max())
            recent_low = float(hist_prices['Low'].tail(5).min())

            direction = 'LONG' if pred.get('predicted_direction', 'UP') == 'UP' else 'SHORT'
            confidence = float(pred.get('confidence', 0.5))

            levels = calculate_hybrid_tp_sl(
                entry_price=entry_price,
                direction=direction,
                atr=atr,
                bb_upper=bb_upper,
                bb_lower=bb_lower,
                confidence=confidence,
                recent_high=recent_high,
                recent_low=recent_low
            )

            # Check outcome using future prices
            future_prices = price_data[price_data['Date'] > pred_date].head(5)
            status = 'EXPIRED'
            outcome = 'PENDING'
            exit_price = None
            exit_date = None
            pnl_percent = None
            trade_duration = None

            tp = levels['take_profit']
            sl = levels['stop_loss']

            for _, day in future_prices.iterrows():
                high = day['High']
                low = day['Low']

                if direction == 'LONG':
                    if high >= tp:
                        status = 'TP_HIT'
                        outcome = 'WIN'
                        exit_price = tp
                        exit_date = day['Date'].strftime('%Y-%m-%d')
                        pnl_percent = round((tp - entry_price) / entry_price * 100, 3)
                        trade_duration = (day['Date'] - pred_date).days
                        break
                    elif low <= sl:
                        status = 'SL_HIT'
                        outcome = 'LOSS'
                        exit_price = sl
                        exit_date = day['Date'].strftime('%Y-%m-%d')
                        pnl_percent = round((sl - entry_price) / entry_price * 100, 3)
                        trade_duration = (day['Date'] - pred_date).days
                        break
                else:
                    if low <= tp:
                        status = 'TP_HIT'
                        outcome = 'WIN'
                        exit_price = tp
                        exit_date = day['Date'].strftime('%Y-%m-%d')
                        pnl_percent = round((entry_price - tp) / entry_price * 100, 3)
                        trade_duration = (day['Date'] - pred_date).days
                        break
                    elif high >= sl:
                        status = 'SL_HIT'
                        outcome = 'LOSS'
                        exit_price = sl
                        exit_date = day['Date'].strftime('%Y-%m-%d')
                        pnl_percent = round((entry_price - sl) / entry_price * 100, 3)
                        trade_duration = (day['Date'] - pred_date).days
                        break

            signal = {
                'signal_id': signal_id,
                'signal_date': pred_date.strftime('%Y-%m-%d') if hasattr(pred_date, 'strftime') else str(pred_date)[:10],
                'data_date': pred_date.strftime('%Y-%m-%d') if hasattr(pred_date, 'strftime') else str(pred_date)[:10],
                'direction': direction,
                'entry_price': entry_price,
                'take_profit': levels['take_profit'],
                'stop_loss': levels['stop_loss'],
                'confidence': confidence,
                'risk_reward': levels['risk_reward'],
                'atr': round(atr, 2),
                'bb_upper': round(bb_upper, 2),
                'bb_lower': round(bb_lower, 2),
                'status': status,
                'outcome': outcome,
                'exit_price': exit_price,
                'exit_date': exit_date,
                'pnl_percent': pnl_percent,
                'pnl_dollars': None,
                'trade_duration_days': trade_duration
            }

            signals.append(signal)
            signal_id += 1

        # Save all signals
        df = pd.DataFrame(signals)
        df.to_csv(self.signals_file, index=False)
        print(f"Backfilled {len(signals)} signals")
        return len(signals)


class ProTradingMetrics:
    """Calculate professional trading metrics"""

    def __init__(self):
        self.signals_file = SIGNALS_HISTORY_FILE

    def load_signals(self) -> pd.DataFrame:
        """Load signals history"""
        try:
            if os.path.exists(self.signals_file):
                return pd.read_csv(self.signals_file)
            return pd.DataFrame()
        except:
            return pd.DataFrame()

    def load_price_returns(self) -> pd.Series:
        """Load daily price returns"""
        try:
            df = pd.read_csv(PRICE_DATA_FILE)
            close = df['Close'] if 'Close' in df.columns else df['close']
            returns = close.pct_change().dropna()
            return returns
        except:
            return pd.Series()

    def calculate_sharpe_ratio(self, returns: pd.Series = None, risk_free_rate: float = 0.05) -> float:
        """
        Annualized Sharpe Ratio
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev * sqrt(252)
        """
        if returns is None:
            returns = self.load_price_returns()

        if returns.empty:
            return 0.0

        daily_rf = risk_free_rate / 252
        excess_returns = returns - daily_rf

        if excess_returns.std() == 0:
            return 0.0

        sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
        return round(float(sharpe), 2)

    def calculate_sortino_ratio(self, returns: pd.Series = None, risk_free_rate: float = 0.05) -> float:
        """
        Sortino Ratio - uses only downside deviation
        """
        if returns is None:
            returns = self.load_price_returns()

        if returns.empty:
            return 0.0

        daily_rf = risk_free_rate / 252
        excess_returns = returns - daily_rf

        # Downside deviation
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(252)
        return round(float(sortino), 2)

    def calculate_max_drawdown(self, equity_curve: pd.Series = None) -> dict:
        """Calculate maximum drawdown and associated dates"""
        if equity_curve is None:
            returns = self.load_price_returns()
            if returns.empty:
                return {'max_drawdown': 0, 'current_drawdown': 0}
            equity_curve = (1 + returns).cumprod()

        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max * 100

        max_dd = float(drawdown.min())
        current_dd = float(drawdown.iloc[-1])

        return {
            'max_drawdown': round(max_dd, 2),
            'current_drawdown': round(current_dd, 2)
        }

    def calculate_var(self, returns: pd.Series = None, confidence: float = 0.95) -> float:
        """Historical VaR at given confidence level"""
        if returns is None:
            returns = self.load_price_returns()

        if returns.empty:
            return 0.0

        var = returns.quantile(1 - confidence)
        return round(float(var * 100), 2)

    def calculate_profit_factor(self, signals: pd.DataFrame = None) -> float:
        """Gross Profit / Gross Loss"""
        if signals is None:
            signals = self.load_signals()

        if signals.empty or 'pnl_percent' not in signals.columns:
            return 0.0

        completed = signals[signals['outcome'].isin(['WIN', 'LOSS'])]
        if completed.empty:
            return 0.0

        gross_profit = completed[completed['pnl_percent'] > 0]['pnl_percent'].sum()
        gross_loss = abs(completed[completed['pnl_percent'] < 0]['pnl_percent'].sum())

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return round(gross_profit / gross_loss, 2)

    def calculate_expectancy(self, signals: pd.DataFrame = None) -> float:
        """Expected value per trade"""
        if signals is None:
            signals = self.load_signals()

        if signals.empty or 'pnl_percent' not in signals.columns:
            return 0.0

        completed = signals[signals['outcome'].isin(['WIN', 'LOSS'])]
        if completed.empty:
            return 0.0

        wins = completed[completed['outcome'] == 'WIN']
        losses = completed[completed['outcome'] == 'LOSS']

        win_rate = len(wins) / len(completed)
        avg_win = wins['pnl_percent'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['pnl_percent'].mean()) if len(losses) > 0 else 0

        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        return round(expectancy, 3)

    def calculate_win_rate_by_confidence(self, signals: pd.DataFrame = None) -> dict:
        """Win rate grouped by confidence level"""
        if signals is None:
            signals = self.load_signals()

        if signals.empty:
            return {'high': 0, 'medium': 0, 'low': 0}

        completed = signals[signals['outcome'].isin(['WIN', 'LOSS'])]
        if completed.empty:
            return {'high': 0, 'medium': 0, 'low': 0}

        def get_win_rate(df):
            if len(df) == 0:
                return 0.0
            return round(len(df[df['outcome'] == 'WIN']) / len(df) * 100, 1)

        high = completed[completed['confidence'] >= 0.7]
        medium = completed[(completed['confidence'] >= 0.6) & (completed['confidence'] < 0.7)]
        low = completed[completed['confidence'] < 0.6]

        return {
            'high': get_win_rate(high),
            'high_count': len(high),
            'medium': get_win_rate(medium),
            'medium_count': len(medium),
            'low': get_win_rate(low),
            'low_count': len(low)
        }

    def calculate_streaks(self, signals: pd.DataFrame = None) -> dict:
        """Calculate win/loss streaks"""
        if signals is None:
            signals = self.load_signals()

        if signals.empty or 'outcome' not in signals.columns:
            return {
                'current_streak': {'type': 'none', 'count': 0},
                'max_win_streak': 0,
                'max_loss_streak': 0
            }

        completed = signals[signals['outcome'].isin(['WIN', 'LOSS'])].sort_values('signal_date')
        if completed.empty:
            return {
                'current_streak': {'type': 'none', 'count': 0},
                'max_win_streak': 0,
                'max_loss_streak': 0
            }

        outcomes = completed['outcome'].tolist()

        # Current streak
        current_type = outcomes[-1].lower()
        current_count = 1
        for i in range(len(outcomes) - 2, -1, -1):
            if outcomes[i] == outcomes[-1]:
                current_count += 1
            else:
                break

        # Max streaks
        max_win = 0
        max_loss = 0
        current_win = 0
        current_loss = 0

        for outcome in outcomes:
            if outcome == 'WIN':
                current_win += 1
                current_loss = 0
                max_win = max(max_win, current_win)
            else:
                current_loss += 1
                current_win = 0
                max_loss = max(max_loss, current_loss)

        return {
            'current_streak': {'type': current_type, 'count': current_count},
            'max_win_streak': max_win,
            'max_loss_streak': max_loss
        }

    def get_best_worst_trades(self, signals: pd.DataFrame = None, n: int = 5) -> dict:
        """Get top N best and worst trades"""
        if signals is None:
            signals = self.load_signals()

        if signals.empty or 'pnl_percent' not in signals.columns:
            return {'best': [], 'worst': []}

        completed = signals[signals['outcome'].isin(['WIN', 'LOSS'])].copy()
        if completed.empty:
            return {'best': [], 'worst': []}

        # Convert pnl_percent to numeric
        completed['pnl_percent'] = pd.to_numeric(completed['pnl_percent'], errors='coerce')

        best = completed.nlargest(n, 'pnl_percent')[['signal_date', 'direction', 'pnl_percent', 'entry_price']].to_dict('records')
        worst = completed.nsmallest(n, 'pnl_percent')[['signal_date', 'direction', 'pnl_percent', 'entry_price']].to_dict('records')

        return {'best': best, 'worst': worst}

    def get_monthly_breakdown(self, signals: pd.DataFrame = None) -> List[dict]:
        """Get monthly performance breakdown"""
        if signals is None:
            signals = self.load_signals()

        if signals.empty:
            return []

        completed = signals[signals['outcome'].isin(['WIN', 'LOSS'])].copy()
        if completed.empty:
            return []

        completed['signal_date'] = pd.to_datetime(completed['signal_date'], format='mixed')
        completed['month'] = completed['signal_date'].dt.to_period('M')
        completed['pnl_percent'] = pd.to_numeric(completed['pnl_percent'], errors='coerce')

        monthly = []
        for month, group in completed.groupby('month'):
            monthly.append({
                'month': str(month),
                'trades': len(group),
                'wins': len(group[group['outcome'] == 'WIN']),
                'losses': len(group[group['outcome'] == 'LOSS']),
                'win_rate': round(len(group[group['outcome'] == 'WIN']) / len(group) * 100, 1),
                'total_pnl': round(group['pnl_percent'].sum(), 2),
                'avg_pnl': round(group['pnl_percent'].mean(), 3)
            })

        return sorted(monthly, key=lambda x: x['month'], reverse=True)

    def get_all_metrics(self) -> dict:
        """Get all professional metrics in one call"""
        signals = self.load_signals()
        returns = self.load_price_returns()

        completed = signals[signals['outcome'].isin(['WIN', 'LOSS'])] if not signals.empty else pd.DataFrame()

        # Basic stats
        total_signals = len(signals)
        completed_signals = len(completed)
        active_signals = len(signals[signals['status'] == 'ACTIVE']) if not signals.empty else 0

        overall_win_rate = 0
        avg_win = 0
        avg_loss = 0

        if not completed.empty:
            wins = completed[completed['outcome'] == 'WIN']
            losses = completed[completed['outcome'] == 'LOSS']
            overall_win_rate = round(len(wins) / len(completed) * 100, 1) if len(completed) > 0 else 0
            avg_win = round(wins['pnl_percent'].mean(), 3) if len(wins) > 0 else 0
            avg_loss = round(abs(losses['pnl_percent'].mean()), 3) if len(losses) > 0 else 0

        dd_info = self.calculate_max_drawdown()

        return {
            'summary': {
                'total_signals': total_signals,
                'completed_signals': completed_signals,
                'active_signals': active_signals,
                'overall_win_rate': overall_win_rate
            },
            'risk_metrics': {
                'sharpe_ratio': self.calculate_sharpe_ratio(returns),
                'sortino_ratio': self.calculate_sortino_ratio(returns),
                'max_drawdown': dd_info['max_drawdown'],
                'current_drawdown': dd_info['current_drawdown'],
                'var_95': self.calculate_var(returns, 0.95)
            },
            'performance_metrics': {
                'profit_factor': self.calculate_profit_factor(signals),
                'expectancy': self.calculate_expectancy(signals),
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'win_rate_by_confidence': self.calculate_win_rate_by_confidence(signals)
            },
            'trade_analysis': {
                'streaks': self.calculate_streaks(signals),
                'best_worst': self.get_best_worst_trades(signals),
                'avg_duration': round(completed['trade_duration_days'].mean(), 1) if not completed.empty and 'trade_duration_days' in completed.columns else 0
            },
            'monthly_breakdown': self.get_monthly_breakdown(signals)
        }


# Convenience functions for API use
def get_current_signal() -> dict:
    """Get current trading signal"""
    generator = ProTradingSignalGenerator()
    return generator.get_current_signal() or {}


def get_signals_history(limit: int = 50) -> List[dict]:
    """Get signals history"""
    generator = ProTradingSignalGenerator()
    df = generator.load_signals_history()
    if df.empty:
        return []
    return df.tail(limit).to_dict('records')[::-1]  # Most recent first


def get_all_metrics() -> dict:
    """Get all professional metrics"""
    metrics = ProTradingMetrics()
    return metrics.get_all_metrics()


def get_chart_data(days: int = 60) -> dict:
    """Get data for signal visualization chart"""
    generator = ProTradingSignalGenerator()
    price_data = generator.load_price_data(days)
    signals = generator.load_signals_history()

    if price_data.empty:
        return {'ohlc': [], 'signals': []}

    # Prepare OHLC data
    ohlc = []
    for _, row in price_data.iterrows():
        ohlc.append({
            'x': row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date'])[:10],
            'y': [float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])]
        })

    # Prepare signals overlay
    signal_overlays = []
    if not signals.empty:
        recent_signals = signals.tail(10)
        for _, sig in recent_signals.iterrows():
            signal_overlays.append({
                'date': str(sig['signal_date'])[:10],
                'entry': float(sig['entry_price']),
                'tp': float(sig['take_profit']),
                'sl': float(sig['stop_loss']),
                'direction': sig['direction'],
                'outcome': sig['outcome'],
                'status': sig['status']
            })

    return {
        'ohlc': ohlc,
        'signals': signal_overlays
    }


def backfill_historical_signals():
    """Backfill signals from historical predictions"""
    generator = ProTradingSignalGenerator()
    return generator.backfill_signals()


if __name__ == '__main__':
    # Test the module
    print("Testing Pro Trading Signals Module...")

    # Backfill historical signals
    print("\n1. Backfilling historical signals...")
    count = backfill_historical_signals()
    print(f"   Created {count} signals")

    # Get metrics
    print("\n2. Calculating metrics...")
    metrics = get_all_metrics()
    print(f"   Summary: {metrics['summary']}")
    print(f"   Risk Metrics: {metrics['risk_metrics']}")
    print(f"   Performance: {metrics['performance_metrics']}")

    # Get current signal
    print("\n3. Getting current signal...")
    signal = get_current_signal()
    if signal:
        print(f"   Direction: {signal.get('direction')}")
        print(f"   Entry: ${signal.get('entry_price')}")
        print(f"   TP: ${signal.get('take_profit')}")
        print(f"   SL: ${signal.get('stop_loss')}")

    print("\nDone!")
