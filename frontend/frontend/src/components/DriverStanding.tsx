"use client";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface DriverStandingProps {
    position: number;
    driver: string;
    team: string;
    probability: number;
    teamColor?: string;
    animated?: boolean;
    className?: string;
}

export function DriverStanding({
    position,
    driver,
    team,
    probability,
    teamColor = "#E10600",
    animated = true,
    className,
}: DriverStandingProps) {
    const positionColors = {
        1: "bg-f1-gold text-black",
        2: "bg-f1-silver text-black",
        3: "bg-orange-600 text-white",
    };

    const ProgressBar = animated ? motion.div : "div";

    return (
        <Card className={cn("telemetry-card p-3", className)}>
            <div className="flex items-center gap-3">
                {/* Position Badge */}
                <div
                    className={cn(
                        "flex items-center justify-center w-8 h-8 rounded-md font-bold text-sm",
                        position <= 3 ? positionColors[position as 1 | 2 | 3] : "bg-secondary text-foreground"
                    )}
                >
                    {position}
                </div>

                {/* Driver Info */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                        <span className="font-bold text-sm truncate">{driver}</span>
                        <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: teamColor }}
                        />
                    </div>
                    <p className="text-xs text-muted-foreground truncate">{team}</p>
                </div>

                {/* Probability Bar */}
                <div className="flex items-center gap-2 min-w-[120px]">
                    <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                        <ProgressBar
                            className="h-full rounded-full progress-bar-sparks"
                            style={{
                                width: `${probability}%`,
                                backgroundColor: teamColor
                            }}
                            initial={animated ? { width: 0 } : undefined}
                            animate={animated ? { width: `${probability}%` } : undefined}
                            transition={animated ? { duration: 0.8, ease: "easeOut" } : undefined}
                        />
                    </div>
                    <span className="telemetry-number text-sm min-w-[45px] text-right">
                        {probability.toFixed(1)}%
                    </span>
                </div>
            </div>
        </Card>
    );
}
