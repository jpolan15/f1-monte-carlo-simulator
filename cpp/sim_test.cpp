#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <chrono>
#include <iomanip>
#include <algorithm>
#include <omp.h>

#define EXPORT_API extern "C" __declspec(dllexport)

struct DriverConfig {
    const char* code;
    const char* team;
    float basePace;        // Qualifying lap time (s)
    float softDegPerLap;   // Soft degradation penalty (s/lap)
    float medDegPerLap;    // Medium degradation penalty (s/lap)
    float consistency;     // Standard deviation of driver pace noise (s)
    int startingGridPos;   // Starting position on grid (1 to N)
};

const int NUM_DRIVERS = 8;

struct SimResults {
    float winPct[NUM_DRIVERS];
    float podiumPct[NUM_DRIVERS];
    double elapsedMs;
    long long totalSims;
};

// Monaco 78-lap Full Grid Monte Carlo Simulator
EXPORT_API void RunMonacoGridSimulation(int numSimulations, SimResults* results) {
    auto startTime = std::chrono::high_resolution_clock::now();

    const int TOTAL_LAPS = 78;
    const float PIT_LANE_DELTA = 22.4f;
    const float SAFETY_CAR_PROB = 0.68f;
    const float FUEL_EFFECT_PER_LAP = -0.033f;

    // Real extracted telemetry from Monaco Qualifying Session
    DriverConfig grid[NUM_DRIVERS] = {
        {"LEC", "Ferrari",         70.270f, 0.082f, 0.045f, 0.12f, 1},
        {"PIA", "McLaren",         70.424f, 0.083f, 0.045f, 0.13f, 2},
        {"SAI", "Ferrari",         70.518f, 0.082f, 0.045f, 0.13f, 3},
        {"NOR", "McLaren",         70.542f, 0.084f, 0.046f, 0.14f, 4},
        {"RUS", "Mercedes",        70.543f, 0.085f, 0.047f, 0.14f, 5},
        {"VER", "Red Bull",        70.567f, 0.085f, 0.046f, 0.13f, 6},
        {"HAM", "Mercedes",        70.621f, 0.081f, 0.044f, 0.15f, 7},
        {"TSU", "RB",              70.858f, 0.088f, 0.049f, 0.16f, 8}
    };

    long long wins[NUM_DRIVERS] = {0};
    long long podiums[NUM_DRIVERS] = {0};

    #pragma omp parallel
    {
        std::mt19937_64 rng(1337 + omp_get_thread_num() * 99991);
        std::uniform_real_distribution<float> uniform01(0.0f, 1.0f);
        std::normal_distribution<float> standardNorm(0.0f, 1.0f);

        long long localWins[NUM_DRIVERS] = {0};
        long long localPodiums[NUM_DRIVERS] = {0};

        #pragma omp for schedule(static)
        for (int sim = 0; sim < numSimulations; sim++) {
            float totalRaceTime[NUM_DRIVERS] = {0.0f};

            bool safetyCarActive = (uniform01(rng) < SAFETY_CAR_PROB);
            int safetyCarLap = safetyCarActive ? (int)(15 + uniform01(rng) * 45) : -1;

            // Strategy variations across teams
            int plannedPitLap[NUM_DRIVERS] = {25, 24, 26, 27, 23, 22, 28, 21};

            for (int d = 0; d < NUM_DRIVERS; d++) {
                int tireAge = 0;
                bool onSofts = true;
                bool hasPitted = false;
                float driverTime = 0.0f;

                for (int lap = 1; lap <= TOTAL_LAPS; lap++) {
                    tireAge++;

                    // Safety car speed delta
                    if (safetyCarActive && lap >= safetyCarLap && lap <= safetyCarLap + 4) {
                        driverTime += (grid[d].basePace + 35.0f);
                        if (!hasPitted && lap == safetyCarLap) {
                            driverTime += (PIT_LANE_DELTA * 0.55f);
                            hasPitted = true;
                            onSofts = false;
                            tireAge = 0;
                        }
                        continue;
                    }

                    // Scheduled pit stop
                    if (!hasPitted && lap >= plannedPitLap[d]) {
                        driverTime += PIT_LANE_DELTA;
                        hasPitted = true;
                        onSofts = false;
                        tireAge = 0;
                    }

                    float degRate = onSofts ? grid[d].softDegPerLap : grid[d].medDegPerLap;
                    float tireDegPenalty = degRate * (tireAge * 0.95f + (tireAge * tireAge * 0.008f));
                    float fuelWeightGain = FUEL_EFFECT_PER_LAP * lap;
                    float paceVariance = standardNorm(rng) * grid[d].consistency;

                    // Grid start offset penalty (Monaco track position handicap)
                    float trackPositionPenalty = (lap == 1) ? (grid[d].startingGridPos - 1) * 1.6f : 0.0f;

                    float lapTime = grid[d].basePace + tireDegPenalty + fuelWeightGain + paceVariance + trackPositionPenalty;
                    driverTime += lapTime;
                }

                totalRaceTime[d] = driverTime;
            }

            // Determine race finishing order
            std::vector<std::pair<float, int>> finishOrder;
            for (int d = 0; d < NUM_DRIVERS; d++) {
                finishOrder.push_back({totalRaceTime[d], d});
            }
            std::sort(finishOrder.begin(), finishOrder.end());

            localWins[finishOrder[0].second]++;
            localPodiums[finishOrder[0].second]++;
            localPodiums[finishOrder[1].second]++;
            localPodiums[finishOrder[2].second]++;
        }

        #pragma omp critical
        {
            for (int d = 0; d < NUM_DRIVERS; d++) {
                wins[d] += localWins[d];
                podiums[d] += localPodiums[d];
            }
        }
    }

    auto endTime = std::chrono::high_resolution_clock::now();
    double durationMs = std::chrono::duration<double, std::milli>(endTime - startTime).count();

    if (results) {
        for (int d = 0; d < NUM_DRIVERS; d++) {
            results->winPct[d] = (float)wins[d] / numSimulations * 100.0f;
            results->podiumPct[d] = (float)podiums[d] / numSimulations * 100.0f;
        }
        results->elapsedMs = durationMs;
        results->totalSims = numSimulations;
    }
}

int main() {
    std::cout << "==========================================================================" << std::endl;
    std::cout << "🏎️ MONACO GP 2026: 8-DRIVER FULL GRID MONTE CARLO RACE SIMULATION" << std::endl;
    std::cout << "==========================================================================" << std::endl;

    const int SIM_RUNS = 10000000;
    std::cout << "[*] Simulating " << SIM_RUNS << " full 78-lap Monaco races across top 8 grid drivers..." << std::endl;

    SimResults res;
    RunMonacoGridSimulation(SIM_RUNS, &res);

    const char* names[NUM_DRIVERS] = {
        "Charles Leclerc (Ferrari)   [P1]",
        "Oscar Piastri   (McLaren)   [P2]",
        "Carlos Sainz    (Ferrari)   [P3]",
        "Lando Norris    (McLaren)   [P4]",
        "George Russell  (Mercedes)  [P5]",
        "Max Verstappen  (Red Bull)  [P6]",
        "Lewis Hamilton  (Mercedes)  [P7]",
        "Yuki Tsunoda    (RB)        [P8]"
    };

    std::cout << "\n🏁 10,000,000 RACES SIMULATED IN " << std::fixed << std::setprecision(2) << res.elapsedMs << " ms!" << std::endl;
    std::cout << "--------------------------------------------------------------------------" << std::endl;
    std::cout << "  Driver & Team                   Win Prob (%)    Podium Prob (%)" << std::endl;
    std::cout << "--------------------------------------------------------------------------" << std::endl;
    for (int d = 0; d < NUM_DRIVERS; d++) {
        std::cout << "  " << std::left << std::setw(32) << names[d]
                  << std::right << std::setw(8) << std::setprecision(2) << res.winPct[d] << " %      "
                  << std::setw(8) << std::setprecision(2) << res.podiumPct[d] << " %" << std::endl;
    }
    std::cout << "==========================================================================" << std::endl;

    return 0;
}
