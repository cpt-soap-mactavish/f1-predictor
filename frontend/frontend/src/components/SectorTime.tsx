import { cn } from "@/lib/utils";

interface SectorTimeProps {
    sector: number;
    time: string;
    status: "fastest" | "personal-best" | "slower";
    delta?: string;
    className?: string;
}

export function SectorTime({
    sector,
    time,
    status,
    delta,
    className,
}: SectorTimeProps) {
    const statusStyles = {
        fastest: "bg-telemetry-purple/20 text-telemetry-purple border-telemetry-purple/50",
        "personal-best": "bg-telemetry-green/20 text-telemetry-green border-telemetry-green/50",
        slower: "bg-telemetry-yellow/20 text-telemetry-yellow border-telemetry-yellow/50",
    };

    return (
        <div className={cn("inline-flex flex-col gap-1", className)}>
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-mono">
                S{sector}
            </div>
            <div
                className={cn(
                    "px-3 py-1.5 rounded border font-mono text-sm font-bold",
                    statusStyles[status]
                )}
            >
                {time}
            </div>
            {delta && (
                <div className="text-[10px] font-mono text-muted-foreground text-center">
                    {delta}
                </div>
            )}
        </div>
    );
}
