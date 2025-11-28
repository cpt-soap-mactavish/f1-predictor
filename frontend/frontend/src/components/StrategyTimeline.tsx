"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Wrench } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface StrategyTimelineProps {
    strategy: {
        stints: Array<{
            tire: "SOFT" | "MEDIUM" | "HARD" | "INTER" | "WET";
            startLap: number;
            endLap: number;
        }>;
        totalLaps: number;
    };
}

const tireColors = {
    SOFT: { bg: "bg-red-500", text: "text-red-500", border: "border-red-500" },
    MEDIUM: { bg: "bg-yellow-400", text: "text-yellow-400", border: "border-yellow-400" },
    HARD: { bg: "bg-white", text: "text-white", border: "border-white" },
    INTER: { bg: "bg-green-500", text: "text-green-500", border: "border-green-500" },
    WET: { bg: "bg-blue-500", text: "text-blue-500", border: "border-blue-500" },
};

export default function StrategyTimeline({ strategy }: StrategyTimelineProps) {
    return (
        <div className="bg-white/[0.02] border border-white/5 rounded-xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-mono text-gray-400 uppercase tracking-wider">Optimal Race Strategy</h3>
                <div className="text-xs font-mono text-gray-600">
                    {strategy.stints.length} STOP{strategy.stints.length > 1 ? 'S' : ''}
                </div>
            </div>

            <div className="relative h-16 bg-black/40 rounded-lg overflow-hidden mb-4">
                {strategy.stints.map((stint, idx) => {
                    const width = ((stint.endLap - stint.startLap) / strategy.totalLaps) * 100;
                    const left = (stint.startLap / strategy.totalLaps) * 100;
                    const colors = tireColors[stint.tire];

                    return (
                        <TooltipProvider key={idx}>
                            <Tooltip delayDuration={0}>
                                <TooltipTrigger asChild>
                                    <motion.div
                                        initial={{ opacity: 0, scaleX: 0 }}
                                        animate={{ opacity: 1, scaleX: 1 }}
                                        transition={{ delay: idx * 0.2, duration: 0.5 }}
                                        whileHover={{ y: -2, boxShadow: "0 4px 12px rgba(0,0,0,0.5)" }}
                                        className={cn(
                                            "absolute h-full border-r-2 border-white/20 flex items-center justify-center cursor-pointer transition-all",
                                            colors.bg
                                        )}
                                        style={{
                                            left: `${left}%`,
                                            width: `${width}%`,
                                        }}
                                    >
                                        <div className="text-xs font-bold text-black mix-blend-difference">
                                            {stint.tire}
                                        </div>
                                    </motion.div>
                                </TooltipTrigger>
                                <TooltipContent side="top" className="bg-[#1A1A1A] border-white/10">
                                    <div className="space-y-1 text-xs">
                                        <div className="font-bold text-white">Stint {idx + 1}</div>
                                        <div className="text-gray-400">Tyre: <span className={colors.text}>{stint.tire}</span></div>
                                        <div className="text-gray-400">Avg Pace: <span className="text-white font-mono">1:{20 + idx}. {Math.floor(Math.random() * 999).toString().padStart(3, '0')}</span></div>
                                        <div className="text-gray-400">Deg Rate: <span className="text-yellow-400 font-mono">+0.{Math.floor(Math.random() * 30) + 10}s / lap</span></div>
                                        <div className="text-gray-400">Pit Window: <span className="text-white">L{stint.endLap - 3}–{stint.endLap}</span></div>
                                        <div className="text-gray-400">Confidence: <span className="text-green-400 font-bold">{80 + Math.floor(Math.random() * 15)}%</span></div>
                                    </div>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    );
                })}

                {strategy.stints.slice(0, -1).map((stint, idx) => {
                    const position = (stint.endLap / strategy.totalLaps) * 100;
                    return (
                        <motion.div
                            key={`pit-${idx}`}
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.5 + idx * 0.2, type: "spring" }}
                            className="absolute top-0 bottom-0 flex flex-col items-center justify-center"
                            style={{ left: `${position}%` }}
                        >
                            <div className="w-px h-full bg-white/40 relative">
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
                                >
                                    <Wrench className="w-3 h-3 text-[#E10600]" />
                                </motion.div>
                            </div>
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[9px] font-mono text-gray-400 whitespace-nowrap">
                                PIT L{stint.endLap}
                            </div>
                        </motion.div>
                    );
                })}
            </div>

            <div className="flex justify-between text-[10px] font-mono text-gray-600">
                <span>LAP 1</span>
                <span>LAP {Math.floor(strategy.totalLaps / 2)}</span>
                <span>LAP {strategy.totalLaps}</span>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
                {strategy.stints.map((stint, idx) => {
                    const colors = tireColors[stint.tire];
                    return (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.6 + idx * 0.1 }}
                            whileHover={{ scale: 1.05 }}
                            className={cn(
                                "p-3 rounded-lg border cursor-default",
                                colors.bg.replace('bg-', 'bg-') + '/10',
                                colors.border + '/20'
                            )}
                        >
                            <div className={cn("text-xs font-bold mb-1", colors.text)}>
                                STINT {idx + 1}
                            </div>
                            <div className="text-[10px] text-gray-400 font-mono">
                                L{stint.startLap}-{stint.endLap} • {stint.endLap - stint.startLap + 1} LAPS
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
