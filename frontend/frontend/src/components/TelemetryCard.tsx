"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface TelemetryCardProps {
    title: string;
    value: string | number;
    delta?: string;
    status?: "fastest" | "personal-best" | "slower" | "neutral";
    unit?: string;
    icon?: React.ReactNode;
    className?: string;
}

export function TelemetryCard({
    title,
    value,
    delta,
    status = "neutral",
    unit,
    icon,
    className,
}: TelemetryCardProps) {
    const statusColors = {
        fastest: "text-telemetry-purple border-telemetry-purple/50 glow-purple",
        "personal-best": "text-telemetry-green border-telemetry-green/50 glow-green",
        slower: "text-telemetry-yellow border-telemetry-yellow/50",
        neutral: "text-muted-foreground border-border",
    };

    const deltaIcon = delta ? (
        delta.startsWith("+") ? (
            <TrendingUp className="w-4 h-4" />
        ) : delta.startsWith("-") ? (
            <TrendingDown className="w-4 h-4" />
        ) : (
            <Minus className="w-4 h-4" />
        )
    ) : null;

    return (
        <Card className={cn("telemetry-card", className)}>
            <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                    {icon}
                    {title}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex items-baseline justify-between">
                    <div className="flex items-baseline gap-1">
                        <span className={cn("telemetry-number", statusColors[status])}>
                            {value}
                        </span>
                        {unit && (
                            <span className="text-sm text-muted-foreground">{unit}</span>
                        )}
                    </div>
                    {delta && (
                        <div className={cn("flex items-center gap-1 text-sm", statusColors[status])}>
                            {deltaIcon}
                            <span className="font-mono">{delta}</span>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
