"use client";

import { motion } from "framer-motion";
import { Trophy, Flag } from "lucide-react";
import { cn } from "@/lib/utils";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import DriverStatsCard from "@/components/DriverStatsCard";

interface Prediction {
    position: number;
    driver_id: string;
    constructor_id: string;
    win_probability: number;
    podium_probability: number;
    confidence: number;
}

interface PredictionResultsProps {
    results: Prediction[];
    loading: boolean;
}

const teamColors: Record<string, string> = {
    red_bull: "#3671C6", ferrari: "#E80020", mercedes: "#27F4D2",
    mclaren: "#FF8000", alpine: "#FF87BC", aston_martin: "#229971",
    williams: "#64C4FF", haas: "#B6BABD", rb: "#6692FF", sauber: "#52E252",
};

// Realistic Driver Stats Map (2025 Estimates)
const driverStatsMap: Record<string, { team: string; wetRating: number; overtakeRisk: "LOW" | "MEDIUM" | "HIGH"; qualiAvg: number; recentForm: number[] }> = {
    max_verstappen: { team: "Red Bull Racing", wetRating: 9.9, overtakeRisk: "HIGH", qualiAvg: 1.2, recentForm: [1, 1, 2, 1, 1] },
    tsunoda: { team: "Red Bull Racing", wetRating: 7.8, overtakeRisk: "HIGH", qualiAvg: 5.0, recentForm: [4, 5, 4, 5, 4] },
    hamilton: { team: "Scuderia Ferrari", wetRating: 9.6, overtakeRisk: "HIGH", qualiAvg: 3.5, recentForm: [3, 4, 2, 5, 3] },
    leclerc: { team: "Scuderia Ferrari", wetRating: 8.8, overtakeRisk: "MEDIUM", qualiAvg: 2.5, recentForm: [4, 3, 3, 2, 4] },
    norris: { team: "McLaren", wetRating: 9.2, overtakeRisk: "MEDIUM", qualiAvg: 2.1, recentForm: [2, 2, 1, 3, 2] },
    piastri: { team: "McLaren", wetRating: 8.5, overtakeRisk: "MEDIUM", qualiAvg: 4.0, recentForm: [5, 5, 4, 4, 5] },
    russell: { team: "Mercedes-AMG", wetRating: 8.9, overtakeRisk: "HIGH", qualiAvg: 3.8, recentForm: [6, 6, 5, 6, 6] },
    antonelli: { team: "Mercedes-AMG", wetRating: 7.2, overtakeRisk: "HIGH", qualiAvg: 9.0, recentForm: [8, 9, 8, 7, 8] },
    alonso: { team: "Aston Martin", wetRating: 9.3, overtakeRisk: "HIGH", qualiAvg: 6.5, recentForm: [7, 8, 7, 7, 8] },
    stroll: { team: "Aston Martin", wetRating: 8.5, overtakeRisk: "MEDIUM", qualiAvg: 13.0, recentForm: [13, 14, 13, 13, 14] },
    gasly: { team: "Alpine F1 Team", wetRating: 8.7, overtakeRisk: "HIGH", qualiAvg: 9.0, recentForm: [9, 10, 9, 9, 10] },
    colapinto: { team: "Alpine F1 Team", wetRating: 7.5, overtakeRisk: "MEDIUM", qualiAvg: 10.0, recentForm: [10, 11, 10, 10, 11] },
    albon: { team: "Williams Racing", wetRating: 8.2, overtakeRisk: "MEDIUM", qualiAvg: 11.0, recentForm: [11, 12, 11, 11, 12] },
    sainz: { team: "Williams Racing", wetRating: 8.4, overtakeRisk: "MEDIUM", qualiAvg: 7.0, recentForm: [8, 7, 8, 8, 7] },
    lawson: { team: "Visa Cash App RB", wetRating: 7.5, overtakeRisk: "MEDIUM", qualiAvg: 8.0, recentForm: [6, 7, 6, 5, 6] },
    hadjar: { team: "Visa Cash App RB", wetRating: 6.5, overtakeRisk: "MEDIUM", qualiAvg: 17.0, recentForm: [17, 18, 17, 17, 18] },
    ocon: { team: "Haas F1 Team", wetRating: 8.6, overtakeRisk: "HIGH", qualiAvg: 10.0, recentForm: [10, 9, 10, 10, 9] },
    bearman: { team: "Haas F1 Team", wetRating: 7.3, overtakeRisk: "HIGH", qualiAvg: 14.0, recentForm: [14, 15, 14, 14, 15] },
    hulkenberg: { team: "Sauber F1 Team", wetRating: 8.0, overtakeRisk: "LOW", qualiAvg: 14.0, recentForm: [14, 13, 14, 14, 13] },
    bortoleto: { team: "Sauber F1 Team", wetRating: 7.0, overtakeRisk: "MEDIUM", qualiAvg: 16.0, recentForm: [16, 17, 16, 16, 17] },
};

const getDriverStats = (driverId: string) => {
    const stats = driverStatsMap[driverId] || {
        team: "Unknown Team",
        wetRating: 7.0,
        overtakeRisk: "MEDIUM" as "LOW" | "MEDIUM" | "HIGH",
        qualiAvg: 10.0,
        recentForm: [10, 10, 10, 10, 10]
    };

    return {
        name: driverId.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
        team: stats.team,
        qualiAvg: stats.qualiAvg,
        wetRating: stats.wetRating,
        overtakeRisk: stats.overtakeRisk,
        recentForm: stats.recentForm,
        circuitHistory: stats.qualiAvg + (Math.random() * 2 - 1), // Slight variation for circuit
    };
};

export default function PredictionResults({ results, loading }: PredictionResultsProps) {
    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center space-y-4">
                    <div className="w-16 h-16 border-4 border-[#E10600] border-t-transparent rounded-full animate-spin mx-auto" />
                    <div className="text-sm font-mono text-gray-400 animate-pulse">RUNNING SIMULATION...</div>
                </div>
            </div>
        );
    }

    if (results.length === 0) {
        return (
            <div className="h-full flex items-center justify-center text-gray-500 font-mono text-sm">
                ADJUST PARAMETERS AND RUN SIMULATION
            </div>
        );
    }

    const winner = results[0];
    const podium = results.slice(0, 3);

    return (
        <div className="space-y-8 h-full overflow-y-auto pr-2">
            {/* Winner Card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-[#1A1A1A] to-black p-8 group"
            >
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                    <Flag className="w-32 h-32" />
                </div>

                <div className="relative z-10 flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-2 text-[#E10600] font-bold tracking-widest text-sm mb-2">
                            <Trophy className="w-4 h-4" />
                            PREDICTED WINNER
                        </div>
                        <h1 className="text-5xl font-black italic uppercase tracking-tighter text-white mb-2">
                            {winner.driver_id.split('_').map(w => w.toUpperCase()).join(' ')}
                        </h1>
                        <div className="flex items-center gap-3">
                            <div className="h-4 w-1 rounded-full" style={{ backgroundColor: teamColors[winner.constructor_id] }} />
                            <span className="text-xl text-gray-400 font-mono uppercase">
                                {winner.constructor_id.replace(/_/g, ' ')}
                            </span>
                        </div>
                    </div>

                    <div className="text-right">
                        <div className="text-6xl font-bold text-white tabular-nums">
                            {winner.win_probability.toFixed(1)}<span className="text-2xl text-gray-500">%</span>
                        </div>
                        <div className="text-xs text-gray-500 font-mono mt-1">WIN PROBABILITY</div>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-8 h-2 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${winner.win_probability}% ` }}
                        transition={{ duration: 1, delay: 0.5 }}
                        className="h-full rounded-full shadow-[0_0_15px_currentColor]"
                        style={{ backgroundColor: teamColors[winner.constructor_id], color: teamColors[winner.constructor_id] }}
                    />
                </div>
            </motion.div>

            {/* Podium & Grid Split */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Podium List */}
                <div className="lg:col-span-1 space-y-4">
                    <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest border-b border-white/10 pb-2">
                        Podium Forecast
                    </h3>
                    <div className="space-y-3">
                        {podium.map((p, idx) => (
                            <motion.div
                                key={p.driver_id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                className="bg-white/5 rounded-xl p-4 border border-white/5 flex items-center gap-4"
                            >
                                <div className={cn(
                                    "w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm border-2",
                                    idx === 0 ? "border-yellow-500 text-yellow-500 bg-yellow-500/10" :
                                        idx === 1 ? "border-gray-400 text-gray-400 bg-gray-400/10" :
                                            "border-orange-600 text-orange-600 bg-orange-600/10"
                                )}>
                                    {idx + 1}
                                </div>
                                <div>
                                    <div className="font-bold text-white text-sm uppercase">
                                        {p.driver_id.split('_').pop()}
                                    </div>
                                    <div className="text-[10px] text-gray-500 uppercase">
                                        {p.constructor_id.replace(/_/g, ' ')}
                                    </div>
                                </div>
                                <div className="ml-auto text-right">
                                    <div className="font-mono text-sm font-bold text-green-400">
                                        {p.podium_probability.toFixed(0)}%
                                    </div>
                                    <div className="text-[9px] text-gray-600">PODIUM</div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* Full Grid Table */}
                <div className="lg:col-span-2">
                    <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest border-b border-white/10 pb-2 mb-4">
                        Full Classification
                    </h3>
                    <div className="bg-[#111] rounded-xl border border-white/5 overflow-hidden">
                        <table className="w-full text-xs">
                            <thead className="bg-white/5">
                                <tr className="text-left text-gray-500 font-mono uppercase">
                                    <th className="p-3 w-12 text-center">Pos</th>
                                    <th className="p-3">Driver</th>
                                    <th className="p-3 text-right">Win %</th>
                                    <th className="p-3 text-right">Podium %</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {results.slice(3).map((p) => (
                                    <tr key={p.driver_id} className="hover:bg-white/5 transition-colors">
                                        <td className="p-3 text-center font-mono text-gray-400">{p.position}</td>
                                        <td className="p-3">
                                            <Popover>
                                                <PopoverTrigger asChild>
                                                    <div className="flex items-center gap-2 cursor-pointer hover:text-white transition-colors">
                                                        <div className="w-0.5 h-3 rounded-full" style={{ backgroundColor: teamColors[p.constructor_id] }} />
                                                        <span className="font-bold text-gray-300">
                                                            {p.driver_id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                                                        </span>
                                                    </div>
                                                </PopoverTrigger>
                                                <PopoverContent side="right" className="p-0 border-0">
                                                    <DriverStatsCard driver={getDriverStats(p.driver_id)} />
                                                </PopoverContent>
                                            </Popover>
                                        </td>
                                        <td className="p-3 text-right font-mono text-gray-500">
                                            {p.win_probability > 0.1 ? `${p.win_probability.toFixed(1)}% ` : '<1%'}
                                        </td>
                                        <td className="p-3 text-right font-mono text-gray-500">
                                            {p.podium_probability > 0.1 ? `${p.podium_probability.toFixed(1)}% ` : '<1%'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
