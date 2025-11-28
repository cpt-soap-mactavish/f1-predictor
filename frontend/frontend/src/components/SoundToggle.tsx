"use client";

import { motion } from "framer-motion";
import { Volume2, VolumeX } from "lucide-react";

interface SoundToggleProps {
    isMuted: boolean;
    onToggle: () => void;
}

export default function SoundToggle({ isMuted, onToggle }: SoundToggleProps) {
    return (
        <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onToggle}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
            aria-label={isMuted ? "Unmute sounds" : "Mute sounds"}
        >
            {isMuted ? (
                <VolumeX className="w-5 h-5 text-gray-400" />
            ) : (
                <Volume2 className="w-5 h-5 text-[#E10600]" />
            )}
        </motion.button>
    );
}
