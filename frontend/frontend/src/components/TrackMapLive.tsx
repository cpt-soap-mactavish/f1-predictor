"use client";

import { motion } from "framer-motion";

export default function TrackMapLive() {
    return (
        <div className="relative w-full h-32">
            <svg viewBox="0 0 200 100" className="w-full h-full">
                <path
                    d="M 20 50 Q 50 20, 100 30 Q 150 40, 180 50 Q 150 60, 100 70 Q 50 80, 20 50 Z"
                    fill="none"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="8"
                />
                <motion.circle
                    cx="20"
                    cy="50"
                    r="4"
                    fill="#E10600"
                    filter="drop-shadow(0 0 8px #E10600)"
                    animate={{
                        offsetDistance: ["0%", "100%"],
                    }}
                    transition={{
                        duration: 8,
                        repeat: Infinity,
                        ease: "linear",
                    }}
                    style={{
                        offsetPath: "path('M 20 50 Q 50 20, 100 30 Q 150 40, 180 50 Q 150 60, 100 70 Q 50 80, 20 50 Z')",
                    }}
                >
                    <animate
                        attributeName="opacity"
                        values="1;0.3;1"
                        dur="1s"
                        repeatCount="indefinite"
                    />
                </motion.circle>
            </svg>
        </div>
    );
}
