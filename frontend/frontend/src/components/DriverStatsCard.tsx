"use client";

import { TrendingUp, TrendingDown, Minus, Droplets } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface DriverStatsCardProps {
    driver: {
        name: string;
        team: string;
        qualiAvg: number;
        wetRating: number;
        overtakeRisk: "LOW" | "MEDIUM" | "HIGH";
        recentForm: number[];
        circuitHistory?: number;
    };
}

export default function DriverStatsCard({ driver }: DriverStatsCardProps) {
    const riskConfig = {
        LOW: { color: "text-green-400", bg: "bg-green-500/10" },
        MEDIUM: { color: "text-yellow-400", bg: "bg-yellow-500/10" },
        HIGH: { color: "text-red-400", bg: "bg-red-500/10" },
    };

    const formTrend = driver.recentForm.length >= 2
        ? driver.recentForm[driver.recentForm.length - 1] - driver.recentForm[0]
        : 0;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
            className="w-72 bg-[#1A1A1A] border border-white/10 rounded-xl p-4 shadow-2xl hover:shadow-[0_0_30px_rgba(225,6,0,0.3)] transition-shadow duration-300"
        >
            <div className="mb-4 pb-3 border-b border-white/10">
                <motion.h4
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="font-bold text-white text-sm"
                >
                    {driver.name}
                </motion.h4>
                <motion.p
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 }}
                    className="text-xs text-gray-500 uppercase"
                >
                    {driver.team}
                </motion.p>
            </div>

            <div className="space-y-3">
                <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="flex items-center justify-between"
                >
                    <span className="text-xs text-gray-400">Quali Avg (Last 5)</span>
                    <span className="text-sm font-mono font-bold text-white">
                        P{driver.qualiAvg.toFixed(1)}
                    </span>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.25 }}
                    className="flex items-center justify-between"
                >
                    <div className="flex items-center gap-1.5">
                        <Droplets className="w-3 h-3 text-blue-400" />
                        <span className="text-xs text-gray-400">Wet Rating</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-20 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${(driver.wetRating / 10) * 100}%` }}
                                transition={{ delay: 0.3, duration: 0.8, ease: "easeOut" }}
                                className="h-full bg-blue-400 rounded-full"
                            />
                        </div>
                        <span className="text-sm font-mono font-bold text-blue-400">
                            {driver.wetRating.toFixed(1)}/10
                        </span>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="flex items-center justify-between"
                >
                    <span className="text-xs text-gray-400">Overtake Risk</span>
                    <span
                        className={cn(
                            "text-xs font-bold px-2 py-0.5 rounded",
                            riskConfig[driver.overtakeRisk].color,
                            riskConfig[driver.overtakeRisk].bg
                        )}
                    >
                        {driver.overtakeRisk}
                    </span>
                </motion.div>

                {driver.circuitHistory && (
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.35 }}
                        className="flex items-center justify-between"
                    >
                        <span className="text-xs text-gray-400">Circuit Avg</span>
                        <span className="text-sm font-mono font-bold text-white">
                            P{driver.circuitHistory.toFixed(1)}
                        </span>
                    </motion.div>
                )}

                <div className="pt-3 border-t border-white/10">
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="flex items-center justify-between mb-2"
                    >
                        <span className="text-xs text-gray-400">Recent Form</span>
                        <div className="flex items-center gap-1">
                            {formTrend < 0 ? (
                                <TrendingUp className="w-3 h-3 text-green-400" />
                            ) : formTrend > 0 ? (
                                <TrendingDown className="w-3 h-3 text-red-400" />
                            ) : (
                                <Minus className="w-3 h-3 text-gray-400" />
                            )}
                            <span
                                className={cn(
                                    "text-xs font-mono",
                                    formTrend < 0 ? "text-green-400" : formTrend > 0 ? "text-red-400" : "text-gray-400"
                                )}
                            >
                                {formTrend < 0 ? "↑" : formTrend > 0 ? "↓" : "→"}
                            </span>
                        </div>
                    </motion.div>
                    <div className="flex gap-1">
                        {driver.recentForm.map((pos, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.45 + idx * 0.05, type: "spring" }}
                                whileHover={{ scale: 1.1 }}
                                className={cn(
                                    "flex-1 h-8 rounded flex items-center justify-center text-xs font-bold cursor-default",
                                    pos <= 3
                                        ? "bg-green-500/20 text-green-400 animate-pulse"
                                        : pos <= 10
                                            ? "bg-blue-500/20 text-blue-400"
                                            : "bg-gray-700/50 text-gray-500"
                                )}
                            >
                                P{pos}
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
