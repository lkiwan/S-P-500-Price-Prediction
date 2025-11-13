"""
Quick Prediction Script
Get tomorrow's S&P 500 direction prediction quickly
"""

import sys
sys.path.append('src')

from models.predict import Predictor
import pandas as pd
from datetime import datetime

print("\n" + "="*70)
print("S&P 500 - TOMORROW'S PREDICTION")
print("="*70 + "\n")

# Load latest features
try:
    features_df = pd.read_csv('data/features/features.csv')
    latest = features_df.tail(1)
    print(f"Using data up to: {latest['date'].values[0]}")
except Exception as e:
    print(f"[ERROR] Could not load features: {e}")
    sys.exit(1)

# Load model
try:
    model_name = "sp500_simple_20251113"
    predictor = Predictor(model_name=model_name)
except Exception as e:
    print(f"[ERROR] Could not load model: {e}")
    sys.exit(1)

# Make prediction
result = predictor.predict(latest)

if result:
    print("\n" + "="*70)
    print("PREDICTION RESULTS")
    print("="*70)

    direction_symbol = "^" if result['direction'] == "UP" else "v"
    confidence_color = "HIGH" if result['confidence'] > 0.7 else ("MEDIUM" if result['confidence'] > 0.6 else "LOW")

    print(f"\nDirection:       {result['direction']} {direction_symbol}")
    print(f"Confidence:      {result['confidence']:.2%} ({confidence_color})")
    print(f"Probability Up:  {result['probability_up']:.2%}")
    print(f"Probability Down: {result['probability_down']:.2%}")

    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

    if result['confidence'] > 0.7:
        print("\nHIGH CONFIDENCE prediction")
        print("  The model is quite confident in this prediction.")
        print(f"  Suggested action: Consider a position in {result['direction']} direction")
    elif result['confidence'] > 0.6:
        print("\nMEDIUM CONFIDENCE prediction")
        print("  The model has moderate confidence.")
        print("  Suggested action: Smaller position or wait for confirmation")
    else:
        print("\nLOW CONFIDENCE prediction")
        print("  The model is uncertain about this prediction.")
        print("  Suggested action: Wait for stronger signals or use other indicators")

    print("\n" + "="*70)
    print("RISK DISCLAIMER")
    print("="*70)
    print("\nThis is for educational purposes only - NOT financial advice!")
    print("  - Past performance does not guarantee future results")
    print("  - Use proper risk management")
    print("  - This should be ONE signal among many")
    print("  - Never invest more than you can afford to lose")

    print("\n" + "="*70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

else:
    print("[ERROR] Prediction failed")
