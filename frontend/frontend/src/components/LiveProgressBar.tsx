"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface LiveProgressBarProps {
    value: number;
    max?: number;
    color?: string;
    label?: string;
    showValue?: boolean;
    animated?: boolean;
    showSparks?: boolean;
    className?: string;
}

export function LiveProgressBar({
    value,
    max = 100,
    color = "#E10600",
    label,
    showValue = true,
    animated = true,
    showSparks = true,
    className,
}: LiveProgressBarProps) {
    const percentage = (value / max) * 100;
    const ProgressBar = animated ? motion.div : "div";

    return (
        <div className={cn("space-y-1", className)}>
            {label && (
                <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground uppercase tracking-wider">
                        {label}
                    </span>
                    {showValue && (
                        <span className="font-mono font-bold">{value.toFixed(1)}%</span>
                    )}
                </div>
            )}
            <div className="relative h-3 bg-secondary rounded-full overflow-hidden">
                <ProgressBar
                    className={cn(
                        "h-full rounded-full",
                        showSparks && "progress-bar-sparks"
                    )}
                    style={{
                        width: `${percentage}%`,
                        backgroundColor: color
                    }}
                    initial={animated ? { width: 0 } : undefined}
                    animate={animated ? { width: `${percentage}%` } : undefined}
                    transition={animated ? { duration: 1, ease: "easeOut" } : undefined}
                />
                {/* Glow effect */}
                <div
                    className="absolute inset-0 opacity-30"
                    style={{
                        background: `linear-gradient(90deg, transparent, ${color}40, transparent)`,
                        animation: "shimmer 2s linear infinite",
                    }}
                />
            </div>
        </div>
    );
}
