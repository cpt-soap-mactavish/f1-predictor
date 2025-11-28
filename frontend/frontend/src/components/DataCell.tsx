"use client";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface DataCellProps {
    label: string;
    value: string | number;
    unit?: string;
    status?: "good" | "warning" | "critical" | "neutral";
    mono?: boolean;
    size?: "sm" | "md" | "lg";
    className?: string;
}

export function DataCell({
    label,
    value,
    unit,
    status = "neutral",
    mono = true,
    size = "md",
    className,
}: DataCellProps) {
    const statusColors = {
        good: "text-telemetry-green",
        warning: "text-telemetry-yellow",
        critical: "text-f1-red",
        neutral: "text-foreground",
    };

    const sizes = {
        sm: "text-lg",
        md: "text-2xl",
        lg: "text-3xl",
    };

    return (
        <Card className={cn("bg-secondary/30 border-border/50", className)}>
            <CardContent className="p-3">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 font-mono">
                    {label}
                </div>
                <div className="flex items-baseline gap-1">
                    <span
                        className={cn(
                            "font-bold",
                            mono && "font-mono",
                            sizes[size],
                            statusColors[status]
                        )}
                    >
                        {value}
                    </span>
                    {unit && (
                        <span className="text-sm text-muted-foreground font-mono">
                            {unit}
                        </span>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
