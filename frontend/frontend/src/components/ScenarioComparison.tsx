"use client";

import { motion } from "framer-motion";
import { Trash2, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface Scenario {
    id: string;
    name: string;
    winner: string;
    winProbability: number;
    strategy: string;
    raceTime: string;
    keyFactors: string[];
}

interface ScenarioComparisonProps {
    scenarios: Scenario[];
    onRemoveScenario: (id: string) => void;
}

export default function ScenarioComparison({
    scenarios,
    onRemoveScenario,
}: ScenarioComparisonProps) {
    if (scenarios.length === 0) {
        return (
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-12 text-center">
                <div className="text-gray-500 mb-4">
                    <p className="text-sm font-mono">No scenarios to compare</p>
                    <p className="text-xs text-gray-600 mt-2">Run multiple simulations to compare outcomes</p>
                </div>
            </div>
        );
    }

    // Find best scenario
    const bestScenario = scenarios.reduce((prev, current) =>
        (prev.winProbability > current.winProbability) ? prev : current
    );

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-mono text-gray-400 uppercase tracking-wider">
                    Scenario Comparison ({scenarios.length})
                </h3>
            </div>

            <div className="bg-[#111] rounded-xl border border-white/5 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead className="bg-white/5 border-b border-white/10">
                            <tr className="text-left text-gray-400 font-mono uppercase">
                                <th className="p-3 w-8"></th>
                                <th className="p-3">Scenario</th>
                                <th className="p-3">Winner</th>
                                <th className="p-3 text-right">Win %</th>
                                <th className="p-3">Strategy</th>
                                <th className="p-3">Race Time</th>
                                <th className="p-3">Key Factors</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {scenarios.map((scenario, idx) => (
                                <motion.tr
                                    key={scenario.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: idx * 0.1 }}
                                    className={cn(
                                        "hover:bg-white/5 transition-colors group",
                                        scenario.id === bestScenario.id ? "bg-green-500/5" : ""
                                    )}
                                >
                                    <td className="p-3">
                                        <button
                                            onClick={() => onRemoveScenario(scenario.id)}
                                            className="opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-300"
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                    </td>
                                    <td className="p-3">
                                        <div className="font-bold text-white flex items-center gap-2">
                                            {scenario.name}
                                            {scenario.id === bestScenario.id && (
                                                <TrendingUp className="w-3 h-3 text-green-500" />
                                            )}
                                        </div>
                                    </td>
                                    <td className="p-3">
                                        <div className="font-mono text-white">{scenario.winner}</div>
                                    </td>
                                    <td className="p-3 text-right">
                                        <div className="flex items-center justify-end gap-2">
                                            <div className="w-16 h-1 bg-gray-800 rounded-full overflow-hidden">
                                                <div
                                                    className={cn(
                                                        "h-full rounded-full",
                                                        scenario.id === bestScenario.id ? "bg-green-500" : "bg-[#E10600]"
                                                    )}
                                                    style={{ width: `${scenario.winProbability}%` }}
                                                />
                                            </div>
                                            <span className={cn(
                                                "font-mono font-bold w-10 text-right",
                                                scenario.id === bestScenario.id ? "text-green-400" : "text-gray-400"
                                            )}>
                                                {scenario.winProbability.toFixed(0)}%
                                            </span>
                                        </div>
                                    </td>
                                    <td className="p-3">
                                        <div className="font-mono text-gray-300">{scenario.strategy}</div>
                                    </td>
                                    <td className="p-3">
                                        <div className="font-mono text-gray-300">{scenario.raceTime}</div>
                                    </td>
                                    <td className="p-3">
                                        <div className="flex flex-wrap gap-1">
                                            {scenario.keyFactors.slice(0, 2).map((factor, i) => (
                                                <span
                                                    key={i}
                                                    className="px-2 py-0.5 bg-blue-500/10 border border-blue-500/20 rounded text-[9px] text-blue-400"
                                                >
                                                    {factor}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                </motion.tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Insights */}
            {scenarios.length >= 2 && (
                <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 flex items-start gap-3">
                    <div className="p-2 bg-green-500/20 rounded-lg">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                    </div>
                    <div>
                        <div className="text-xs font-mono text-green-400 mb-1">OPTIMAL STRATEGY FOUND</div>
                        <div className="text-sm text-gray-300">
                            <span className="font-bold text-white">{bestScenario.name}</span> yields the highest win probability of{" "}
                            <span className="font-bold text-green-400">{bestScenario.winProbability.toFixed(1)}%</span>.
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
