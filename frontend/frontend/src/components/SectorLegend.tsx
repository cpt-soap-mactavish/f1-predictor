"use client";

import { motion } from "framer-motion";

export default function SectorLegend() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-6 right-6 bg-black/80 backdrop-blur-sm border border-white/10 rounded-lg p-3 text-xs font-mono z-50"
        >
            <div className="text-gray-400 uppercase tracking-wider mb-2 text-[10px]">Sector Colors</div>
            <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-400" />
                    <span className="text-gray-300">Personal Best</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-purple-400" />
                    <span className="text-gray-300">Session Best</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-yellow-400" />
                    <span className="text-gray-300">Slow Sector</span>
                </div>
            </div>
        </motion.div>
    );
}
