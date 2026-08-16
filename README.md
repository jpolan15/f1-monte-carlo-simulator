# 🏎️ F1 Monte Carlo Strategy Simulator
### High-Performance Python Telemetry Ingestion Layer & C++ SIMD Vectorized Race Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![C++20](https://img.shields.io/badge/C++-20-red.svg)](https://isocpp.org/)
[![OpenMP & SIMD](https://img.shields.io/badge/acceleration-OpenMP%20%2B%20AVX2%2FAVX--512-orange.svg)](https://www.openmp.org/)
[![FastF1](https://img.shields.io/badge/data-FastF1%20Telemetry-green.svg)](https://github.com/theOehrly/Fast-F1)
[![YouTube Video](https://img.shields.io/badge/YouTube-Watch%20Video-red.svg?logo=youtube)](https://youtu.be/3igJGATh75U)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **📺 Watch the Full Build Video on YouTube:** [Building an F1 Monte Carlo Strategy Simulator: Python Data Layer & C++ SIMD Engine](https://youtu.be/3igJGATh75U)  
> **Can we predict the 2026 Monaco Grand Prix winner?**  
> This repository contains the complete production code for the F1 Monte Carlo Simulator featured in the flagship YouTube video. We pull official 5Hz telemetry and qualifying lap times via **FastF1**, structure the physics parameters into contiguous C-compatible memory, and invoke a multi-threaded **C++ SIMD engine** via a **zero-copy ctypes FFI bridge** to simulate **10,000,000 full 78-lap Monaco races in under 8 seconds** (over **60× faster** than pure Python).

---

## ⚡ System Architecture & Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                 1. FastF1 Python Data Layer                 │
│  - Pulls 2025/2026 Monaco Grand Prix sessions               │
│  - 5Hz wheel speed, throttle %, braking, tire degradation   │
│  - Local disk cache prevents rate-limiting                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                Contiguous Struct Array (C-ABI)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│           2. Zero-Copy Python <-> C++ FFI Bridge            │
│  - ctypes.CDLL with direct pointer references (byref)       │
│  - Zero data marshalling / zero memory copy overhead        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                  Multi-Core SIMD Worker Pool
                               │
┌──────────────────────────────▼──────────────────────────────┐
│            3. C++ SIMD & OpenMP Monte Carlo Core            │
│  - 78-lap Monaco GP physics loop across 8 grid drivers      │
│  - Non-linear tire degradation: deg * (lap + 0.008*lap^2)   │
│  - Dynamic 68% Safety Car window & cheap pit delta math     │
│  - 10,000,000 iterations in ~7.8s (>1.2M races/second)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Benchmark: Pure Python vs. C++ SIMD Engine

Simulating **10,000,000 full 78-lap races** across 8 drivers (over **6.24 billion simulated race laps**):

| Implementation | Execution Time | Throughput | Speedup |
| :--- | :--- | :--- | :--- |
| **Pure Python (Scalar Loop)** | **482.0 seconds (~8.0 mins)** | ~20,700 races/sec | Baseline (1.0×) |
| **C++ SIMD + OpenMP (AVX2/512)** | **7.82 seconds** | **~1,280,000 races/sec** | **61.6× FASTER 🚀** |

---

## 🧠 Mathematical Modeling

### 1. Non-Linear Tire Degradation Model
Tire grip does not degrade linearly over a 78-lap stint. Thermal degradation follows a quadratic wear penalty curve:

$$\Delta t_{\text{deg}}(L) = R_{\text{compound}} \cdot \left(0.95 \cdot L + 0.008 \cdot L^2\right)$$

- **Soft Compound Rate ($R_{\text{soft}}$):** $+0.082\text{ s/lap}$
- **Medium Compound Rate ($R_{\text{med}}$):** $+0.045\text{ s/lap}$
- **Hard Compound Rate ($R_{\text{hard}}$):** $+0.021\text{ s/lap}$

### 2. Monaco Pit Stop Delta & Safety Car Window
- **Normal Green-Flag Pit Loss:** $+22.40\text{ seconds}$
- **Safety Car Pit Loss (55% discounted delta):** $+12.32\text{ seconds}$
- **Historical Monaco Safety Car Probability:** $P(\text{SC}) = 0.68$ (68%)

### 3. Fuel Burn Offset
Cars start with $\sim 110\text{ kg}$ of fuel and burn approximately $1.41\text{ kg/lap}$. The weight reduction speeds up lap times linearly:

$$\Delta t_{\text{fuel}}(L) = -0.033\text{ s/lap} \times L$$

---

## 🚀 Quickstart & Reproduction

### 1. Prerequisites
- Python 3.10+
- C++ Compiler with OpenMP support (`g++` / MinGW / Clang / MSVC)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/jpolan15/f1-monte-carlo-simulator.git
cd f1-monte-carlo-simulator

# Install Python requirements
pip install -r requirements.txt
```

### 3. Build the C++ SIMD Shared Library (Optional - precompiled binaries included)
```bash
# On Linux / macOS:
g++ -O3 -fopenmp -fPIC -shared -o cpp/F1SimPlugin.so cpp/sim_test.cpp

# On Windows (MinGW/UCRT):
g++ -O3 -fopenmp -static -static-libgcc -static-libstdc++ -shared -o cpp/F1SimPlugin.dll cpp/sim_test.cpp
```

### 4. Run the 10,000,000 Race Simulation
```bash
python run_simulator.py --sims 10000000
```

### 5. Run Python vs. C++ Benchmark
```bash
python run_simulator.py --sims 1000000 --benchmark
```

### 6. Pull Fresh Live F1 Telemetry (FastF1)
```bash
python python_data/extract_full_grid.py
```

---

## 📁 Repository Structure

```
f1_engine/
├── cpp/
│   ├── sim_test.cpp           # Core C++ Monte Carlo OpenMP simulation engine
│   ├── F1SimPlugin.dll        # Compiled Windows high-performance shared library
│   └── sim_benchmark.exe      # Standalone C++ benchmark binary
├── python_data/
│   ├── extract_telemetry.py   # FastF1 session extraction & 5Hz GPS telemetry
│   ├── extract_full_grid.py   # Top-10 Monaco grid physics constant extractor
│   ├── plot_telemetry.py      # Telemetry throttle/speed curve visualization
│   └── telemetry_summary.json # Cached qualifying sector & driver physics data
├── run_simulator.py           # Zero-copy ctypes Python CLI & benchmark runner
├── requirements.txt           # Python dependency specifications
└── README.md                  # Flagship documentation
```

---

## 👤 Author

**Jonathan Polanco**  
Software Engineering Student & Content Creator  
- **YouTube:** [Jonathan Polanco](https://www.youtube.com/@jonathanpolanco)  
- **GitHub:** [@jpolan15](https://github.com/jpolan15)  
- **LinkedIn:** [Jonathan Polanco](https://linkedin.com/in/jonathan-polanco)

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
