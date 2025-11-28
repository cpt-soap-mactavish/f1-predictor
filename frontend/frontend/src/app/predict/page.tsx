"use client";

import { useState } from "react";
import SimulationControls, { SimulationState } from "@/components/SimulationControls";
import PredictionResults from "@/components/PredictionResults";
import SimulationLoader from "@/components/SimulationLoader";
import DataSourceIndicator from "@/components/DataSourceIndicator";
import StrategyTimeline from "@/components/StrategyTimeline";
import ScenarioComparison from "@/components/ScenarioComparison";
import { motion } from "framer-motion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import WeatherForecast from "@/components/WeatherForecast";
import CircuitMap from "@/components/CircuitMap";

interface Prediction {
    position: number;
    driver_id: string;
    constructor_id: string;
    win_probability: number;
    podium_probability: number;
    confidence: number;
}

interface Scenario {
    id: string;
    name: string;
    winner: string;
    winProbability: number;
    strategy: string;
    raceTime: string;
    keyFactors: string[];
}

export default function PredictPage() {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<Prediction[]>([]);
    const [scenarios, setScenarios] = useState<Scenario[]>([]);
    const [currentParams, setCurrentParams] = useState<SimulationState | null>(null);

    const handleSimulate = async (params: SimulationState) => {
        setCurrentParams(params);
        setLoading(true);

        try {
            // Call Backend API
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    circuit: params.circuit,
                    air_temp: params.airTemp,
                    track_temp: params.trackTemp,
                    rain_prob: params.rainProb,
                    humidity: params.humidity,
                    tire: params.tire,
                    pit_stops: params.pitStops,
                    safety_car: params.safetyCar
                }),
            });

            if (!response.ok) {
                throw new Error('Prediction failed');
            }

            const data = await response.json();

            // Transform API response to frontend format
            const predictions: Prediction[] = data.predictions.map((p: any) => ({
                position: p.position,
                driver_id: p.driver_id,
                constructor_id: p.constructor_id,
                win_probability: p.win_probability,
                podium_probability: p.podium_probability,
                confidence: p.confidence
            }));

            setResults(predictions);

            // Generate scenario data based on prediction context
            const winner = predictions[0];
            const newScenario: Scenario = {
                id: Date.now().toString(),
                name: `Sim #${scenarios.length + 1} - ${params.circuit.toUpperCase()}`,
                winner: winner.driver_id.replace('_', ' ').toUpperCase(),
                winProbability: winner.win_probability,
                strategy: `${params.pitStops} Stop(s) - ${params.tire.toUpperCase()} Start`,
                raceTime: "1:28:32.451", // Estimated
                keyFactors: [
                    params.rainProb > 50 ? "Heavy Rain" : "Dry Track",
                    `${params.trackTemp}°C Track`,
                    "High Degradation"
                ]
            };

            setScenarios(prev => [...prev, newScenario]);

        } catch (error) {
            console.error("Simulation error:", error);
            // Fallback or error notification could go here
        } finally {
            setLoading(false);
        }
    };

    const handleRemoveScenario = (id: string) => {
        setScenarios(scenarios.filter(s => s.id !== id));
    };

    // Mock data for indicators
    // Dynamic Data Sources & Confidence
    const dataSources = [
        "HISTORICAL DATA (2010-2025)",
        "LIVE TELEMETRY (SIMULATED)",
        "TRACK CONDITIONS"
    ];

    const lastUpdated = new Date().toLocaleTimeString();

    // Calculate confidence based on the winner's score
    const topScore = results.length > 0 ? results[0].confidence : 0;
    const confidence = topScore > 70 ? "HIGH" : topScore > 50 ? "MEDIUM" : "LOW";

    // Mock strategy timeline
    // Dynamic strategy timeline with realistic tire degradation
    const totalLaps = currentParams?.laps || 72;
    const stops = currentParams?.pitStops || 2;

    // 1. Determine Tire Sequence
    const startTire = (currentParams?.tire.toUpperCase() as "SOFT" | "MEDIUM" | "HARD" || "SOFT");
    const tireSequence: ("SOFT" | "MEDIUM" | "HARD")[] = [];

    // Logic: Start with user choice, then go to Hard/Medium
    tireSequence.push(startTire);
    for (let i = 1; i <= stops; i++) {
        if (i === 1) {
            // Second stint usually Hard or Medium
            tireSequence.push(startTire === "HARD" ? "MEDIUM" : "HARD");
        } else {
            // Third stint: if 2 stops, maybe Soft at end or Medium
            tireSequence.push("MEDIUM");
        }
    }

    // 2. Assign Durability Weights (Soft lasts less than Hard)
    const weights = { "SOFT": 0.6, "MEDIUM": 0.85, "HARD": 1.1 };
    const totalWeight = tireSequence.reduce((sum, t) => sum + weights[t], 0);

    // 3. Calculate Stints
    let currentLap = 1;
    const stints = tireSequence.map((tire, index) => {
        const isLast = index === tireSequence.length - 1;

        // Calculate laps for this stint based on weight
        let laps = Math.floor((weights[tire] / totalWeight) * totalLaps);

        // Adjust last stint to ensure we hit totalLaps exactly
        if (isLast) {
            laps = totalLaps - currentLap + 1;
        }

        const start = currentLap;
        const end = currentLap + laps - 1;
        currentLap += laps;

        return {
            tire,
            startLap: start,
            endLap: end
        };
    });

    const strategyTimeline = {
        stints,
        totalLaps
    };

    return (
        <div className="min-h-screen bg-[#0A0A0F] text-white p-6">
            <div className="max-w-[1920px] mx-auto">
                <div className="grid grid-cols-12 gap-8">

                    {/* Left Sidebar - Controls */}
                    <motion.div
                        initial={{ x: -50, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        className="col-span-12 lg:col-span-3"
                    >
                        <SimulationControls onSimulate={handleSimulate} />
                    </motion.div>

                    {/* Main Content - Results */}
                    <motion.div
                        initial={{ x: 50, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="col-span-12 lg:col-span-9"
                    >
                        {loading ? (
                            <SimulationLoader />
                        ) : (
                            <div className="space-y-6">


                                {/* Data Source Indicators */}
                                {results.length > 0 && (
                                    <>
                                        <DataSourceIndicator
                                            sources={dataSources}
                                            lastUpdated={lastUpdated}
                                            confidence={confidence}
                                        />

                                        <div className="mt-8 mb-8">
                                            <div className="flex items-center justify-center gap-3 mb-6">
                                                <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-[#E10600]"></div>
                                                <h3 className="text-sm font-bold text-gray-400 tracking-[0.2em]">RACE WEEKEND CONDITIONS</h3>
                                                <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-[#E10600]"></div>
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
                                                <WeatherForecast
                                                    date={currentParams?.date}
                                                    summary={currentParams?.weatherSummary}
                                                    airTemp={currentParams?.airTemp || 0}
                                                    trackTemp={currentParams?.trackTemp || 0}
                                                    rainProb={currentParams?.rainProb || 0}
                                                    humidity={currentParams?.humidity || 0}
                                                />
                                                <CircuitMap circuitId={currentParams?.circuit || "bahrain"} className="h-full" />
                                            </div>
                                        </div>
                                    </>
                                )}

                                {/* Tabs for Results vs Comparison */}
                                <Tabs defaultValue="results" className="w-full">
                                    <TabsList className="bg-white/5 border border-white/10">
                                        <TabsTrigger value="results" className="data-[state=active]:bg-[#E10600]">
                                            Prediction Results
                                        </TabsTrigger>
                                        <TabsTrigger value="comparison" className="data-[state=active]:bg-[#E10600]">
                                            Scenario Comparison ({scenarios.length})
                                        </TabsTrigger>
                                    </TabsList>

                                    <TabsContent value="results" className="mt-6">
                                        {results.length > 0 ? (
                                            <>
                                                {/* Strategy Timeline */}
                                                <StrategyTimeline strategy={strategyTimeline} />

                                                {/* Prediction Results */}
                                                <PredictionResults results={results} loading={false} />
                                            </>
                                        ) : (
                                            <div className="h-96 flex items-center justify-center text-gray-500 font-mono text-sm">
                                                ADJUST PARAMETERS AND RUN SIMULATION
                                            </div>
                                        )}
                                    </TabsContent>

                                    <TabsContent value="comparison" className="mt-6">
                                        <ScenarioComparison
                                            scenarios={scenarios}
                                            onRemoveScenario={handleRemoveScenario}
                                        />
                                    </TabsContent>
                                </Tabs>
                            </div>
                        )}
                    </motion.div>

                </div>
            </div>
        </div>
    );
}
