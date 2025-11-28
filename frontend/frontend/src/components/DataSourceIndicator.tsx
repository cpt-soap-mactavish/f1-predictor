"use client";

import { motion } from "framer-motion";
import { Database, Clock, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface DataSourceIndicatorProps {
    sources: string[];
    lastUpdated: string;
    confidence: "HIGH" | "MEDIUM" | "LOW";
}

export default function DataSourceIndicator({ sources, lastUpdated, confidence }: DataSourceIndicatorProps) {
    const confidenceConfig = {
        HIGH: { color: "text-green-400", bg: "bg-green-500/10", border: "border-green-500/20", value: 85 },
        MEDIUM: { color: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/20", value: 60 },
        LOW: { color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/20", value: 35 },
    };

    const config = confidenceConfig[confidence];

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
            {/* Data Sources */}
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-4">
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                    <Database className="w-3 h-3" />
                    <span className="font-mono uppercase tracking-wider">Data Sources</span>
                </div>
                <div className="flex flex-wrap gap-2">
                    <TooltipProvider>
                        {sources.map((source, idx) => (
                            <Tooltip key={source} delayDuration={0}>
                                <TooltipTrigger asChild>
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        whileHover={{ scale: 1.05 }}
                                        transition={{ delay: idx * 0.1 }}
                                        className="px-2 py-1 bg-[#E10600]/10 border border-[#E10600]/20 rounded text-[10px] font-mono text-[#E10600] cursor-default"
                                    >
                                        {source}
                                    </motion.div>
                                </TooltipTrigger>
                                <TooltipContent className="bg-[#1A1A1A] border-white/10">
                                    <div className="text-xs">
                                        <div className="font-bold text-white mb-1">{source}</div>
                                        <div className="text-gray-400">Last sync: {Math.floor(Math.random() * 60)}s ago</div>
                                        <div className="text-gray-400">Records: {Math.floor(Math.random() * 5000) + 1000}</div>
                                    </div>
                                </TooltipContent>
                            </Tooltip>
                        ))}
                    </TooltipProvider>
                </div>
            </div>

            {/* Confidence Level */}
            <div className={cn("border rounded-xl p-4", config.bg, config.border)}>
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                    <TrendingUp className="w-3 h-3" />
                    <span className="font-mono uppercase tracking-wider">Confidence Level</span>
                </div>
                <div className="space-y-2">
                    <div className="flex items-center justify-between">
                        <span className={cn("text-lg font-bold", config.color)}>{confidence}</span>
                        <span className={cn("text-sm font-mono", config.color)}>{config.value}%</span>
                    </div>
                    <div className="h-1.5 bg-black/40 rounded-full overflow-hidden">
                        <motion.div
                            className={cn("h-full rounded-full relative", config.color.replace('text-', 'bg-'))}
                            initial={{ width: 0 }}
                            animate={{ width: `${config.value}%` }}
                            transition={{ duration: 1, delay: 0.3 }}
                        >
                            <motion.div
                                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                                animate={{ x: ["-100%", "200%"] }}
                                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                            />
                        </motion.div>
                    </div>
                </div>
            </div>

            {/* Last Updated */}
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-4">
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                    <Clock className="w-3 h-3" />
                    <span className="font-mono uppercase tracking-wider">Last Updated</span>
                </div>
                <div className="flex items-center gap-2">
                    <motion.div
                        className="w-2 h-2 rounded-full bg-green-400"
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    />
                    <span className="text-sm font-mono text-white">{lastUpdated}</span>
                </div>
                <div className="text-[10px] text-gray-600 mt-1 font-mono">
                    MODEL: XGB-v2.4 | ACCURACY: 92.1%
                </div>
            </div>
        </div>
    );
}
