"use client";

import { motion } from "framer-motion";
import { Clock, Flag, Gauge } from "lucide-react";

interface RaceStatusBarProps {
    currentLap: number;
    totalLaps: number;
    timeElapsed: string;
    stintDuration: number;
    tireCompound: string;
}

export default function RaceStatusBar({
    currentLap,
    totalLaps,
    timeElapsed,
    stintDuration,
    tireCompound,
}: RaceStatusBarProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-6 bg-black/60 backdrop-blur-sm border border-white/10 rounded-lg px-4 py-2 text-xs font-mono"
        >
            <div className="flex items-center gap-2">
                <Flag className="w-3 h-3 text-[#E10600]" />
                <span className="text-gray-400">Laps:</span>
                <span className="text-white font-bold">
                    {currentLap} / {totalLaps}
                </span>
            </div>

            <div className="h-4 w-px bg-white/10" />

            <div className="flex items-center gap-2">
                <Clock className="w-3 h-3 text-blue-400" />
                <span className="text-gray-400">Elapsed:</span>
                <span className="text-white font-bold">{timeElapsed}</span>
            </div>

            <div className="h-4 w-px bg-white/10" />

            <div className="flex items-center gap-2">
                <Gauge className="w-3 h-3 text-yellow-400" />
                <span className="text-gray-400">Stint:</span>
                <span className="text-white font-bold">
                    {stintDuration} laps on{" "}
                    <span
                        className={
                            tireCompound === "SOFT"
                                ? "text-red-400"
                                : tireCompound === "MEDIUM"
                                    ? "text-yellow-400"
                                    : "text-white"
                        }
                    >
                        {tireCompound}
                    </span>
                </span>
            </div>
        </motion.div>
    );
}
