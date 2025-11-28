
"use client";

import { motion } from "framer-motion";
import { Zap, CloudRain, Gauge } from "lucide-react";

const loadingSteps = [
    { icon: CloudRain, text: "Analyzing weather conditions...", delay: 0 },
    { icon: Gauge, text: "Calculating tire degradation...", delay: 0.5 },
    { icon: Zap, text: "Optimizing race strategy...", delay: 1 },
];

export default function SimulationLoader() {
    return (
        <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-8 max-w-md">
                {/* Animated Tire Icon */}
                <div className="relative w-32 h-32 mx-auto">
                    <motion.div
                        className="absolute inset-0 border-8 border-gray-800 rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                        {/* Tire tread marks */}
                        {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => (
                            <div
                                key={angle}
                                className="absolute w-1 h-4 bg-[#E10600] rounded"
                                style={{
                                    top: '50%',
                                    left: '50%',
                                    transform: `translate(-50%, -50%) rotate(${angle}deg) translateY(-40px)`,
                                }}
                            />
                        ))}
                    </motion.div>

                    {/* Center hub */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-12 h-12 bg-gradient-to-br from-gray-700 to-gray-900 rounded-full border-2 border-gray-600" />
                    </div>
                </div>

                {/* Loading Steps */}
                <div className="space-y-4">
                    {loadingSteps.map((step, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: step.delay, duration: 0.5 }}
                            className="flex items-center gap-3 text-sm font-mono text-gray-400"
                        >
                            <motion.div
                                animate={{ scale: [1, 1.2, 1] }}
                                transition={{ delay: step.delay, duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
                            >
                                <step.icon className="w-4 h-4 text-[#E10600]" />
                            </motion.div>
                            <span>{step.text}</span>
                            <motion.div
                                className="flex gap-1 ml-auto"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: step.delay + 0.3 }}
                            >
                                {[0, 1, 2].map((dot) => (
                                    <motion.div
                                        key={dot}
                                        className="w-1 h-1 bg-[#E10600] rounded-full"
                                        animate={{ opacity: [0.3, 1, 0.3] }}
                                        transition={{
                                            delay: step.delay + dot * 0.2,
                                            duration: 1,
                                            repeat: Infinity,
                                        }}
                                    />
                                ))}
                            </motion.div>
                        </motion.div>
                    ))}
                </div>

                {/* Progress Bar */}
                <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-gradient-to-r from-[#E10600] to-red-400"
                        initial={{ width: "0%" }}
                        animate={{ width: "100%" }}
                        transition={{ duration: 2, ease: "easeInOut" }}
                    />
                </div>

                {/* Status Text */}
                <motion.div
                    className="text-xs font-mono text-gray-500 uppercase tracking-wider"
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                >
                    Running Simulation...
                </motion.div>
            </div>
        </div>
    );
}
