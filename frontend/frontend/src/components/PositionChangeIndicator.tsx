"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ArrowUp, ArrowDown } from "lucide-react";

interface PositionChangeIndicatorProps {
    change: number;
    show: boolean;
}

export default function PositionChangeIndicator({
    change,
    show,
}: PositionChangeIndicatorProps) {
    if (!show || change === 0) return null;

    const isGain = change < 0;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, scale: 0.5, x: -10 }}
                animate={{ opacity: 1, scale: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.5 }}
                className={`flex items-center gap-1 text-xs font-bold ${isGain ? "text-green-400" : "text-red-400"
                    }`}
            >
                {isGain ? (
                    <ArrowUp className="w-3 h-3" />
                ) : (
                    <ArrowDown className="w-3 h-3" />
                )}
                <span>{Math.abs(change)}</span>
            </motion.div>
        </AnimatePresence>
    );
}
