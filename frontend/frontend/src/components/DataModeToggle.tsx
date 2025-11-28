"use client";

import { motion } from "framer-motion";
import { Radio } from "lucide-react";

interface DataModeToggleProps {
    isLive: boolean;
    onToggle: () => void;
}

export default function DataModeToggle({ isLive, onToggle }: DataModeToggleProps) {
    return (
        <button
            onClick={onToggle}
            className="flex items-center gap-2 bg-black/60 backdrop-blur-sm border border-white/10 rounded-lg px-4 py-2 text-xs font-mono hover:bg-white/5 transition-colors"
        >
            <motion.div
                animate={{ scale: isLive ? [1, 1.2, 1] : 1 }}
                transition={{ duration: 1, repeat: isLive ? Infinity : 0 }}
                className={`w-2 h-2 rounded-full ${isLive ? "bg-green-400" : "bg-red-400"}`}
            />


        </button>
    );
}
