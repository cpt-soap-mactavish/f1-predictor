"use client";

import { cn } from "@/lib/utils";

interface TireCompoundProps {
    compound: "soft" | "medium" | "hard" | "intermediate" | "wet";
    laps?: number;
    age?: number;
    className?: string;
}

export function TireCompound({
    compound,
    laps,
    age,
    className,
}: TireCompoundProps) {
    const compoundStyles = {
        soft: "bg-red-500 text-white",
        medium: "bg-yellow-400 text-black",
        hard: "bg-white text-black",
        intermediate: "bg-green-500 text-white",
        wet: "bg-blue-500 text-white",
    };

    const compoundLabels = {
        soft: "S",
        medium: "M",
        hard: "H",
        intermediate: "I",
        wet: "W",
    };

    return (
        <div className={cn("inline-flex items-center gap-2", className)}>
            <div
                className={cn(
                    "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold",
                    compoundStyles[compound]
                )}
            >
                {compoundLabels[compound]}
            </div>
            {(laps !== undefined || age !== undefined) && (
                <div className="flex flex-col text-[10px] font-mono">
                    {laps !== undefined && (
                        <span className="text-foreground">{laps} laps</span>
                    )}
                    {age !== undefined && (
                        <span className="text-muted-foreground">Age: {age}</span>
                    )}
                </div>
            )}
        </div>
    );
}
