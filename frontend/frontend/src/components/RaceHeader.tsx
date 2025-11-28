"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Flag, Trophy, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface RaceHeaderProps {
    raceName: string;
    circuit: string;
    date: string;
    round?: number;
    season?: number;
    className?: string;
}

export function RaceHeader({
    raceName,
    circuit,
    date,
    round,
    season = 2025,
    className,
}: RaceHeaderProps) {
    return (
        <Card className={cn("glass-effect border-f1-red/30", className)}>
            <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2">
                            <Flag className="w-5 h-5 text-f1-red" />
                            <CardTitle className="text-2xl font-bold text-gradient-red">
                                {raceName}
                            </CardTitle>
                        </div>
                        <p className="text-sm text-muted-foreground flex items-center gap-2">
                            <Zap className="w-4 h-4" />
                            {circuit}
                        </p>
                    </div>
                    <div className="text-right space-y-1">
                        {round && (
                            <div className="text-xs text-muted-foreground uppercase tracking-wider">
                                Round {round}
                            </div>
                        )}
                        <div className="text-sm font-mono text-foreground">{date}</div>
                        <div className="text-xs text-f1-gold font-bold">{season}</div>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="pt-0">
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                        <Trophy className="w-3 h-3" />
                        <span>AI Predictions</span>
                    </div>
                    <div className="h-3 w-px bg-border" />
                    <span>Powered by XGBoost ML</span>
                </div>
            </CardContent>
        </Card>
    );
}
