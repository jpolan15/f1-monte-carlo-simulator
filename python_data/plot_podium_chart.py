import matplotlib.pyplot as plt
import numpy as np
import os
import json

def generate_grid_leaderboard_chart():
    # Set dark high-tech styling
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('#070b12')
    ax.set_facecolor('#0d131f')

    drivers = [
        'Y. Tsunoda (RB)',
        'L. Hamilton (Mercedes)',
        'M. Verstappen (Red Bull)',
        'G. Russell (Mercedes)',
        'L. Norris (McLaren)',
        'C. Sainz (Ferrari)',
        'O. Piastri (McLaren)',
        'C. Leclerc (Ferrari)'
    ]

    podium_probs = [0.0, 0.27, 0.0, 0.0, 1.66, 98.16, 99.91, 100.0]
    colors = [
        '#6692FF',  # RB
        '#00D2BE',  # Mercedes
        '#3671C6',  # Red Bull
        '#00D2BE',  # Mercedes
        '#FF8000',  # McLaren
        '#E80020',  # Ferrari
        '#FF8000',  # McLaren
        '#E80020'   # Ferrari
    ]

    y_pos = np.arange(len(drivers))
    bars = ax.barh(y_pos, podium_probs, color=colors, height=0.62, edgecolor='white', linewidth=0.8, alpha=0.9)

    # Styling and Grid
    ax.set_yticks(y_pos)
    ax.set_yticklabels(drivers, fontsize=11, fontweight='bold', color='#f8fafc')
    ax.set_xlabel('Simulated Podium Probability (%) — 10,000,000 Monte Carlo Runs', fontsize=12, fontweight='bold', color='#38bdf8', labelpad=12)
    ax.set_xlim(0, 115)
    ax.grid(axis='x', color='#1e293b', linestyle='--', alpha=0.7)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#334155')
    ax.spines['bottom'].set_color('#334155')

    # Add data labels
    for bar, prob in zip(bars, podium_probs):
        width = bar.get_width()
        text_str = f"{prob:.1f}%"
        ax.text(width + 2.0, bar.get_y() + bar.get_height()/2, text_str,
                va='center', ha='left', fontsize=11, fontweight='bold', color='#f8fafc')

    ax.set_title('MONACO GP 2026: MONTE CARLO PODIUM CONVERSION (N=10,000,000)', fontsize=14, fontweight='bold', color='#f8fafc', pad=18)

    # Save to 04_assets
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '04_assets')
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, 'monaco_monte_carlo_podium_chart.png')
    plt.tight_layout()
    plt.savefig(out_file, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    print(f"[OK] Podium probability chart saved to: {out_file}")

if __name__ == "__main__":
    generate_grid_leaderboard_chart()
