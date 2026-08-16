import matplotlib.pyplot as plt
import os

def generate_code_cards():
    plt.style.use('dark_background')
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '04_assets')
    os.makedirs(output_dir, exist_ok=True)

    # 1. Python FastF1 Ingestion Snippet
    python_code = """import fastf1
import numpy as np

# Enable local disk cache for fast repeat access
fastf1.Cache.enable_cache('f1_cache')

# Load official 2025 Monaco Qualifying session
session = fastf1.get_session(2025, 'Monaco', 'Q')
session.load()

# Extract 10Hz wheel speed, throttle, and braking data
lec_lap = session.laps.pick_driver('LEC').pick_fastest()
telemetry = lec_lap.get_telemetry()

# Distance, Speed (km/h), Throttle (0-100%), Brake (Boolean)
speed_vector    = np.array(telemetry['Speed'])
throttle_vector = np.array(telemetry['Throttle'])
brake_events    = int((telemetry['Brake'] > 0).sum())"""

    fig1, ax1 = plt.subplots(figsize=(12, 7.5))
    fig1.patch.set_facecolor('#070b14')
    ax1.set_facecolor('#0c1220')
    ax1.axis('off')

    # Add window dots
    fig1.patches.extend([
        plt.Circle((0.04, 0.94), 0.012, color='#ef4444', transform=fig1.transFigure, clip_on=False),
        plt.Circle((0.065, 0.94), 0.012, color='#eab308', transform=fig1.transFigure, clip_on=False),
        plt.Circle((0.09, 0.94), 0.012, color='#22c55e', transform=fig1.transFigure, clip_on=False),
    ])
    fig1.text(0.12, 0.933, "f1_engine/python_data/extract_telemetry.py", fontsize=13, fontweight='bold', color='#38bdf8', family='monospace')

    ax1.text(0.04, 0.88, python_code, fontsize=12.5, family='monospace', color='#e2e8f0',
             verticalalignment='top', horizontalalignment='left', linespacing=1.45,
             transform=ax1.transAxes)

    out_py = os.path.join(output_dir, 'code_card_python_fastf1.png')
    plt.tight_layout()
    plt.savefig(out_py, dpi=200, facecolor=fig1.get_facecolor(), bbox_inches='tight')
    plt.close(fig1)
    print(f"[OK] Python Code card saved: {out_py}")

    # 2. C++ SIMD OpenMP Monte Carlo Core Snippet
    cpp_code = """#include <iostream>
#include <random>
#include <omp.h>

struct DriverConfig {
    const char* code;
    float basePace;      // Lap pace (e.g. 70.27s)
    float softDegPerLap; // 0.082s/lap thermal decay
    float consistency;   // Driver pace std dev
};

// 10,000,000 Monaco Grand Prix Simulations
#pragma omp parallel
{
    std::mt19937_64 rng(1337 + omp_get_thread_num() * 99991);
    std::uniform_real_distribution<float> unif(0.0f, 1.0f);
    std::normal_distribution<float> norm(0.0f, 1.0f);

    #pragma omp for schedule(static)
    for (int sim = 0; sim < 10000000; sim++) {
        bool safetyCar = (unif(rng) < 0.68f); // 68% SC probability
        // Lap iteration, tire wear curve, and pit delta calculation...
    }
}"""

    fig2, ax2 = plt.subplots(figsize=(12, 7.5))
    fig2.patch.set_facecolor('#070b14')
    ax2.set_facecolor('#0c1220')
    ax2.axis('off')

    fig2.patches.extend([
        plt.Circle((0.04, 0.94), 0.012, color='#ef4444', transform=fig2.transFigure, clip_on=False),
        plt.Circle((0.065, 0.94), 0.012, color='#eab308', transform=fig2.transFigure, clip_on=False),
        plt.Circle((0.09, 0.94), 0.012, color='#22c55e', transform=fig2.transFigure, clip_on=False),
    ])
    fig2.text(0.12, 0.933, "f1_engine/cpp/sim_test.cpp (OpenMP + AVX2 Core)", fontsize=13, fontweight='bold', color='#38bdf8', family='monospace')

    ax2.text(0.04, 0.88, cpp_code, fontsize=12.5, family='monospace', color='#e2e8f0',
             verticalalignment='top', horizontalalignment='left', linespacing=1.45,
             transform=ax2.transAxes)

    out_cpp = os.path.join(output_dir, 'code_card_cpp_sim.png')
    plt.tight_layout()
    plt.savefig(out_cpp, dpi=200, facecolor=fig2.get_facecolor(), bbox_inches='tight')
    plt.close(fig2)
    print(f"[OK] C++ Code card saved: {out_cpp}")

if __name__ == "__main__":
    generate_code_cards()
