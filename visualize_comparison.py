"""
Model Comparison Visualization
Compare all three model versions
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Setup
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")

# Model data
models = ['V1: Synthetic\nSentiment', 'V2: Real\nNews', 'V3: Complete\n(Best)']
accuracy = [51.76, 50.98, 56.86]
precision = [58.02, 56.98, 60.10]
recall = [63.09, 65.77, 77.85]
f1_score = [60.45, 61.06, 67.84]
features = [73, 73, 91]

# Create figure with subplots
fig = plt.figure(figsize=(16, 10))

# 1. Accuracy Comparison
ax1 = plt.subplot(2, 3, 1)
bars = ax1.bar(models, accuracy, color=['#66c2a5', '#fc8d62', '#8da0cb'], edgecolor='black', linewidth=1.5)
ax1.axhline(y=50, color='red', linestyle='--', linewidth=2, label='Random Guess (50%)', alpha=0.7)
ax1.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax1.set_title('Model Accuracy Comparison', fontsize=14, fontweight='bold')
ax1.set_ylim(45, 60)
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, val in zip(bars, accuracy):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.3,
            f'{val:.2f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)

# 2. All Metrics Comparison
ax2 = plt.subplot(2, 3, 2)
x = np.arange(len(models))
width = 0.2

bars1 = ax2.bar(x - width*1.5, accuracy, width, label='Accuracy', color='#66c2a5', edgecolor='black')
bars2 = ax2.bar(x - width*0.5, precision, width, label='Precision', color='#fc8d62', edgecolor='black')
bars3 = ax2.bar(x + width*0.5, recall, width, label='Recall', color='#8da0cb', edgecolor='black')
bars4 = ax2.bar(x + width*1.5, f1_score, width, label='F1 Score', color='#e78ac3', edgecolor='black')

ax2.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
ax2.set_title('All Performance Metrics', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(models)
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_ylim(45, 85)

# 3. Feature Count
ax3 = plt.subplot(2, 3, 3)
colors = ['#66c2a5', '#fc8d62', '#8da0cb']
bars = ax3.bar(models, features, color=colors, edgecolor='black', linewidth=1.5)
ax3.set_ylabel('Number of Features', fontsize=12, fontweight='bold')
ax3.set_title('Feature Count by Model', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, features):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{val}', ha='center', va='bottom', fontweight='bold', fontsize=11)

# 4. Improvement Over Random
ax4 = plt.subplot(2, 3, 4)
improvements = [acc - 50 for acc in accuracy]
colors_improvement = ['green' if i > 0 else 'red' for i in improvements]
bars = ax4.bar(models, improvements, color=colors_improvement, alpha=0.7, edgecolor='black', linewidth=1.5)
ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax4.set_ylabel('Improvement over Random (%)', fontsize=12, fontweight='bold')
ax4.set_title('Edge Over Random Guessing', fontsize=14, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, improvements):
    height = bar.get_height()
    y_pos = height + 0.2 if height > 0 else height - 0.5
    ax4.text(bar.get_x() + bar.get_width()/2., y_pos,
            f'+{val:.2f}%' if val > 0 else f'{val:.2f}%',
            ha='center', va='bottom' if val > 0 else 'top',
            fontweight='bold', fontsize=11)

# 5. Model Evolution Timeline
ax5 = plt.subplot(2, 3, 5)
versions = [1, 2, 3]
ax5.plot(versions, accuracy, marker='o', markersize=12, linewidth=3, color='#8da0cb', label='Accuracy')
ax5.plot(versions, f1_score, marker='s', markersize=12, linewidth=3, color='#e78ac3', label='F1 Score')
ax5.axhline(y=50, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Random')
ax5.set_xlabel('Model Version', fontsize=12, fontweight='bold')
ax5.set_ylabel('Performance (%)', fontsize=12, fontweight='bold')
ax5.set_title('Model Evolution Over Time', fontsize=14, fontweight='bold')
ax5.set_xticks(versions)
ax5.set_xticklabels(['V1\nSynthetic', 'V2\nReal News', 'V3\nComplete'])
ax5.legend()
ax5.grid(True, alpha=0.3)
ax5.set_ylim(45, 75)

# 6. Data Sources by Version
ax6 = plt.subplot(2, 3, 6)
data_sources = {
    'V1': ['Technical\nIndicators', 'Synthetic\nSentiment'],
    'V2': ['Technical\nIndicators', 'Real News\nSentiment'],
    'V3': ['Technical\nIndicators', 'Real News\nSentiment', 'Economic\nData (18)']
}

y_pos = [3, 2, 1]
colors_list = ['#66c2a5', '#fc8d62', '#8da0cb']

for i, (version, sources) in enumerate(data_sources.items()):
    ax6.barh(y_pos[i], len(sources), color=colors_list[i], alpha=0.7, edgecolor='black', linewidth=1.5)
    ax6.text(len(sources) + 0.1, y_pos[i], version, va='center', fontweight='bold', fontsize=11)
    ax6.text(0.1, y_pos[i], ' + '.join(sources), va='center', fontsize=9)

ax6.set_xlabel('Number of Data Sources', fontsize=12, fontweight='bold')
ax6.set_title('Data Sources Integration', fontsize=14, fontweight='bold')
ax6.set_yticks([])
ax6.set_xlim(0, 4)
ax6.grid(True, alpha=0.3, axis='x')

plt.suptitle('S&P 500 Prediction Model Comparison\n V1 (Synthetic) → V2 (Real News) → V3 (Complete with Economics)',
            fontsize=16, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
print("\n[OK] Saved: model_comparison.png")
plt.show()

# Print summary
print("\n" + "="*70)
print("MODEL COMPARISON SUMMARY")
print("="*70)
print(f"\nV1: Synthetic Sentiment")
print(f"  Accuracy: {accuracy[0]:.2f}%")
print(f"  Features: {features[0]}")
print(f"  Edge: +{accuracy[0]-50:.2f}%")

print(f"\nV2: Real News")
print(f"  Accuracy: {accuracy[1]:.2f}%")
print(f"  Features: {features[1]}")
print(f"  Edge: +{accuracy[1]-50:.2f}%")

print(f"\nV3: Complete (BEST)")
print(f"  Accuracy: {accuracy[2]:.2f}% ⬆️")
print(f"  Features: {features[2]}")
print(f"  Edge: +{accuracy[2]-50:.2f}%")

print(f"\nImprovement from V1 to V3: +{accuracy[2]-accuracy[0]:.2f} percentage points")
print(f"Relative improvement: {((accuracy[2]-accuracy[0])/accuracy[0]*100):.1f}%")
print("="*70 + "\n")
