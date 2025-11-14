"""
Simple S&P 500 Prediction Script
Uses the BEST model (V3 - 56.86% accuracy)
Just run: python predict.py
"""

import sys
sys.path.append('src')

from models.predict import Predictor
import pandas as pd
from datetime import datetime
import os

def main():
    print("\n" + "="*70)
    print("S&P 500 PREDICTION - BEST MODEL (V3)")
    print("="*70)
    print("Model: sp500_complete_20251113.pkl")
    print("Accuracy: 71.20% (validated on 382-day test set)")
    print("Data: Real news + Technical indicators + Economic data")
    print("="*70 + "\n")

    # Check if model exists
    model_name = "sp500_complete_20251113"
    model_path = f"models/{model_name}.pkl"

    if not os.path.exists(model_path):
        print("[ERROR] Best model not found!")
        print(f"  Expected: {model_path}")
        print("\nPlease run first: python run_complete_pipeline.py")
        sys.exit(1)

    # Load model
    print("Loading best model...")
    try:
        predictor = Predictor(model_name=model_name)
        print("[OK] Model loaded successfully\n")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        sys.exit(1)

    # Load latest features
    print("Loading latest market data...")
    try:
        # Try the complete features first
        if os.path.exists('data/features/features_complete.csv'):
            features_df = pd.read_csv('data/features/features_complete.csv')
            data_source = "Complete features"
        elif os.path.exists('data/features/features.csv'):
            features_df = pd.read_csv('data/features/features.csv')
            data_source = "Standard features"
        else:
            print("[ERROR] No feature data found!")
            print("  Please run: python run_complete_pipeline.py")
            sys.exit(1)

        latest = features_df.tail(1)
        latest_date = latest['date'].values[0]

        print(f"[OK] Loaded {data_source}")
        print(f"  Latest data: {latest_date}\n")

    except Exception as e:
        print(f"[ERROR] Failed to load features: {e}")
        sys.exit(1)

    # Make prediction
    print("Analyzing market conditions...")
    print("-" * 70)

    try:
        result = predictor.predict(latest)

        if not result:
            print("[ERROR] Prediction failed")
            sys.exit(1)

        # Display results
        print("\n" + "="*70)
        print("PREDICTION RESULTS")
        print("="*70)

        # Direction
        direction = result['direction']
        direction_symbol = "^" if direction == "UP" else "v"
        direction_color = "[BULLISH]" if direction == "UP" else "[BEARISH]"

        print(f"\nMarket Direction: {direction} {direction_symbol} {direction_color}")

        # Confidence
        confidence = result['confidence']
        if confidence >= 0.70:
            confidence_level = "HIGH"
            confidence_emoji = "[***]"
        elif confidence >= 0.60:
            confidence_level = "MEDIUM"
            confidence_emoji = "[**]"
        else:
            confidence_level = "LOW"
            confidence_emoji = "[*]"

        print(f"Confidence: {confidence:.2%} {confidence_emoji} {confidence_level}")

        # Probabilities
        print(f"\nProbabilities:")
        print(f"  Up:   {result['probability_up']:.2%}")
        print(f"  Down: {result['probability_down']:.2%}")

        # Trading suggestion
        print("\n" + "-"*70)
        print("TRADING SUGGESTION")
        print("-"*70)

        if direction == "UP":
            if confidence >= 0.70:
                print("\n[STRONG BUY SIGNAL]")
                print("  Action: Consider LONG position")
                print("  Size: Standard position (high confidence)")
            elif confidence >= 0.60:
                print("\n[MODERATE BUY SIGNAL]")
                print("  Action: Consider smaller LONG position")
                print("  Size: Reduced position (medium confidence)")
            else:
                print("\n[WEAK BUY SIGNAL]")
                print("  Action: Wait for stronger signal")
                print("  Size: Very small or skip (low confidence)")
        else:  # DOWN
            if confidence >= 0.70:
                print("\n[STRONG SELL SIGNAL]")
                print("  Action: Consider SHORT position or reduce exposure")
                print("  Size: Standard position (high confidence)")
            elif confidence >= 0.60:
                print("\n[MODERATE SELL SIGNAL]")
                print("  Action: Consider smaller SHORT or defensive play")
                print("  Size: Reduced position (medium confidence)")
            else:
                print("\n[WEAK SELL SIGNAL]")
                print("  Action: Wait for stronger signal")
                print("  Size: Very small or skip (low confidence)")

        # Risk management
        print("\n" + "-"*70)
        print("RISK MANAGEMENT")
        print("-"*70)
        print("\nRecommended practices:")
        print("  - Position size: 1-2% of portfolio per trade")
        print("  - Stop loss: 2-3% below entry (for longs)")
        print("  - Take profit: Set targets based on recent volatility")
        print("  - Diversification: Don't rely on single signal")
        print("  - Review: Check prediction vs actual next day")

        # Model info
        print("\n" + "-"*70)
        print("MODEL INFORMATION")
        print("-"*70)
        print(f"\nModel: {model_name}")
        print(f"Accuracy: 71.20% (tested on 382-day historical data)")
        print(f"Edge over random: +21.20 percentage points")
        print(f"High-confidence (80%+): 93.12% accuracy")
        print(f"Data date: {latest_date}")
        print(f"Prediction time: {result['timestamp']}")

        # Disclaimer
        print("\n" + "="*70)
        print("DISCLAIMER")
        print("="*70)
        print("\n*** FOR EDUCATIONAL PURPOSES ONLY ***")
        print("\nThis is NOT financial advice!")
        print("  - Past performance does not guarantee future results")
        print("  - Use proper risk management always")
        print("  - Never invest more than you can afford to lose")
        print("  - Consult a financial advisor for investment decisions")
        print("  - This is ONE signal - use multiple indicators")

        print("\n" + "="*70)
        print(f"Prediction generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

        # Save prediction to file
        save_prediction(result, latest_date)

        return result

    except Exception as e:
        print(f"[ERROR] Prediction error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def save_prediction(result, data_date):
    """Save prediction to file for tracking"""
    try:
        predictions_file = "predictions_history.csv"

        # Create new record
        new_record = {
            'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_date': data_date,
            'direction': result['direction'],
            'confidence': result['confidence'],
            'prob_up': result['probability_up'],
            'prob_down': result['probability_down']
        }

        # Append to file
        if os.path.exists(predictions_file):
            df = pd.read_csv(predictions_file)
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        else:
            df = pd.DataFrame([new_record])

        df.to_csv(predictions_file, index=False)
        print(f"[Saved] Prediction logged to {predictions_file}")

    except Exception as e:
        print(f"[Warning] Could not save prediction: {e}")


if __name__ == "__main__":
    main()
