import fastf1
import os
import json
import numpy as np

def extract_full_grid_telemetry():
    cache_dir = os.path.join(os.path.dirname(__file__), 'f1_cache')
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)
    print(f"[*] FastF1 cache enabled at: {cache_dir}")

    print("[*] Loading Monaco Grand Prix Qualifying Session for the entire top grid...")
    session = fastf1.get_session(2025, 'Monaco', 'Q')
    session.load()

    # Target Top 10 Drivers on the Monaco Grid
    target_drivers = ['LEC', 'PIA', 'SAI', 'NOR', 'RUS', 'VER', 'HAM', 'TSU', 'ALB', 'GAS']
    
    drivers_data = {}
    for code in target_drivers:
        try:
            lap = session.laps.pick_drivers(code).pick_fastest()
            tel = lap.get_telemetry()
            
            drivers_data[code] = {
                "name": str(lap['Driver']),
                "team": str(lap['Team']),
                "lap_time_s": round(float(lap['LapTime'].total_seconds()), 3),
                "compound": str(lap['Compound']),
                "top_speed_kph": round(float(tel['Speed'].max()), 1),
                "avg_throttle_pct": round(float(tel['Throttle'].mean()), 2),
                "time_at_full_throttle_pct": round(float((tel['Throttle'] == 100).mean() * 100), 2),
                "heavy_braking_events": int((tel['Brake'] > 0).sum()),
                "sample_points_count": len(tel)
            }
            print(f"[+] Processed {code} ({lap['Team']}): {drivers_data[code]['lap_time_s']}s")
        except Exception as e:
            print(f"[-] Could not load driver {code}: {e}")

    summary = {
        "circuit": "Circuit de Monaco",
        "season_year": 2026,
        "track_length_m": 3337,
        "total_grid_size": len(drivers_data),
        "drivers": drivers_data,
        "strategy_physics_constants": {
            "monaco_pit_lane_delta_s": 22.4,
            "tire_deg_penalty_per_lap_soft_s": 0.082,
            "tire_deg_penalty_per_lap_medium_s": 0.045,
            "tire_deg_penalty_per_lap_hard_s": 0.021,
            "safety_car_probability": 0.68
        }
    }

    output_path = os.path.join(os.path.dirname(__file__), 'telemetry_summary.json')
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n[OK] Full Top-10 grid telemetry dataset saved to: {output_path}")
    return summary

if __name__ == "__main__":
    extract_full_grid_telemetry()
