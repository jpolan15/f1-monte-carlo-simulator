"""
F1 Monte Carlo Strategy Simulator - Python Data Layer & C++ SIMD Engine
========================================================================
Demonstrates zero-copy FFI bridge between Python (FastF1 telemetry data)
and compiled C++ SIMD OpenMP Monte Carlo race simulation engine.
"""

import os
import sys
import time
import ctypes
import argparse
import random
import numpy as np

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Define C++ Driver Struct / Result Struct matching F1SimPlugin.dll
NUM_DRIVERS = 8

class SimResults(ctypes.Structure):
    _fields_ = [
        ("winPct", ctypes.c_float * NUM_DRIVERS),
        ("podiumPct", ctypes.c_float * NUM_DRIVERS),
        ("elapsedMs", ctypes.c_double),
        ("totalSims", ctypes.c_longlong),
    ]

DRIVER_NAMES = [
    "Charles Leclerc (Ferrari)   [P1]",
    "Oscar Piastri   (McLaren)   [P2]",
    "Carlos Sainz    (Ferrari)   [P3]",
    "Lando Norris    (McLaren)   [P4]",
    "George Russell  (Mercedes)  [P5]",
    "Max Verstappen  (Red Bull)  [P6]",
    "Lewis Hamilton  (Mercedes)  [P7]",
    "Yuki Tsunoda    (RB)        [P8]"
]

def load_sim_dll():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dll_dir = os.path.join(current_dir, "cpp")
    dll_path = os.path.join(dll_dir, "F1SimPlugin.dll")
    
    if not os.path.exists(dll_path):
        dll_path = os.path.join(current_dir, "F1SimPlugin.dll")
    
    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"Could not locate F1SimPlugin.dll at: {dll_path}")
    
    # Enable Windows 10/11 DLL resolution for mingw/ucrt runtimes if available
    if hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(dll_dir)
        except Exception:
            pass
        if os.path.exists(r"C:\msys64\ucrt64\bin"):
            try:
                os.add_dll_directory(r"C:\msys64\ucrt64\bin")
            except Exception:
                pass
    
    sim_lib = ctypes.CDLL(dll_path)
    sim_lib.RunMonacoGridSimulation.argtypes = [
        ctypes.c_int,
        ctypes.POINTER(SimResults)
    ]
    sim_lib.RunMonacoGridSimulation.restype = None
    return sim_lib

def run_cpp_simulation(sim_lib, num_simulations=10_000_000):
    print(f"\n🏎️  [C++ SIMD Engine] Executing {num_simulations:,} full 78-lap Monaco GP races...")
    results = SimResults()
    
    start = time.perf_counter()
    # Zero-copy memory pointer handoff across C-ABI boundary
    sim_lib.RunMonacoGridSimulation(num_simulations, ctypes.byref(results))
    total_time = time.perf_counter() - start
    
    print("\n" + "=" * 76)
    print(f"🏁  SIMULATION COMPLETE: {num_simulations:,} RACES IN {results.elapsedMs:.2f} ms ({total_time:.3f}s total wall clock)")
    print("=" * 76)
    print(f"  {'Driver & Team':<34} {'Win Prob (%)':<18} {'Podium Prob (%)':<18}")
    print("-" * 76)
    
    for d in range(NUM_DRIVERS):
        print(f"  {DRIVER_NAMES[d]:<34} {results.winPct[d]:>8.2f} %           {results.podiumPct[d]:>8.2f} %")
    print("=" * 76 + "\n")
    return results

def run_python_benchmark(num_simulations=50_000):
    """
    Pure Python Monte Carlo baseline loop to demonstrate scalar interpreter overhead
    vs compiled SIMD C++ vectorized execution.
    """
    print(f"\n🐢  [Pure Python Baseline] Running {num_simulations:,} sample iterations to measure interpreter overhead...")
    
    grid = [
        {"name": "LEC", "base": 70.270, "deg": 0.082, "pos": 1},
        {"name": "PIA", "base": 70.424, "deg": 0.083, "pos": 2},
        {"name": "SAI", "base": 70.518, "deg": 0.082, "pos": 3},
        {"name": "NOR", "base": 70.542, "deg": 0.084, "pos": 4},
        {"name": "RUS", "base": 70.543, "deg": 0.085, "pos": 5},
        {"name": "VER", "base": 70.567, "deg": 0.085, "pos": 6},
        {"name": "HAM", "base": 70.621, "deg": 0.081, "pos": 7},
        {"name": "TSU", "base": 70.858, "deg": 0.088, "pos": 8},
    ]
    
    start = time.perf_counter()
    wins = [0] * NUM_DRIVERS
    
    for _ in range(num_simulations):
        safety_car = (random.random() < 0.68)
        sc_lap = random.randint(15, 60) if safety_car else -1
        
        times = []
        for d, drv in enumerate(grid):
            t = 0.0
            pitted = False
            for lap in range(1, 79):
                if safety_car and sc_lap <= lap <= sc_lap + 4:
                    t += drv["base"] + 35.0
                    if not pitted and lap == sc_lap:
                        t += 22.4 * 0.55
                        pitted = True
                    continue
                
                if not pitted and lap >= 25:
                    t += 22.4
                    pitted = True
                
                deg = drv["deg"] * (lap * 0.95 + (lap * lap * 0.008))
                noise = random.gauss(0, 0.13)
                track_penalty = 1.6 * (drv["pos"] - 1) if lap == 1 else 0.0
                t += drv["base"] + deg + (-0.033 * lap) + noise + track_penalty
            times.append((t, d))
        
        times.sort()
        wins[times[0][1]] += 1
    
    elapsed = time.perf_counter() - start
    rate = num_simulations / elapsed
    projected_10m = (10_000_000 / rate)
    
    print(f"[+] Python completed {num_simulations:,} races in {elapsed:.2f}s ({rate:,.0f} races/sec)")
    print(f"[!] Projected time for 10,000,000 races in Pure Python: {projected_10m:.1f} seconds (~{projected_10m/60:.1f} minutes)")
    return elapsed, projected_10m

def main():
    parser = argparse.ArgumentParser(description="F1 Monte Carlo Strategy Simulator (Python & C++ SIMD)")
    parser.add_argument("--sims", type=int, default=10_000_000, help="Number of Monte Carlo simulations to execute")
    parser.add_argument("--benchmark", action="store_true", help="Run comparative benchmark: Python Baseline vs C++ SIMD Engine")
    args = parser.parse_args()

    print("=" * 76)
    print("🏎️  F1 MONTE CARLO STRATEGY SIMULATOR (FastF1 + C++ SIMD)")
    print("=" * 76)

    try:
        sim_lib = load_sim_dll()
        print("[✓] C++ FFI Engine loaded successfully via ctypes (F1SimPlugin.dll)")
    except Exception as e:
        print(f"[✗] Failed to load C++ engine: {e}")
        sys.exit(1)

    # Run C++ Simulation
    cpp_results = run_cpp_simulation(sim_lib, num_simulations=args.sims)

    if args.benchmark:
        _, projected_py_10m = run_python_benchmark(num_simulations=50_000)
        cpp_sec = cpp_results.elapsedMs / 1000.0
        speedup = projected_py_10m / cpp_sec if cpp_sec > 0 else 0
        print("\n" + "=" * 76)
        print("⚡  BENCHMARK SUMMARY (10,000,000 RACES)")
        print("=" * 76)
        print(f"  • Pure Python Interpreter : {projected_py_10m:.1f}s (~{projected_py_10m/60:.1f} mins)")
        print(f"  • C++ SIMD + OpenMP Core  : {cpp_sec:.2f}s")
        print(f"  • Speedup Factor          : {speedup:.1f}× FASTER 🚀")
        print("=" * 76 + "\n")

if __name__ == "__main__":
    main()
