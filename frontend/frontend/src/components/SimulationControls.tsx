"use client";

import { useState, useEffect } from "react";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Zap, RotateCcw, CloudRain } from "lucide-react";

export interface SimulationState {
    circuit: string;
    laps: number;
    date: string;
    weatherSummary: string;
    airTemp: number;
    trackTemp: number;
    rainProb: number;
    humidity: number;
    tire: string;
    pitStops: number;
    safetyCar: string;
}

interface SimulationDefaults {
    laps: number;
    date: string;
    weather_summary: string;
    air_temp: number;
    track_temp: number;
    rain_prob: number;
    humidity: number;
    tire: string;
    pit_stops: number;
    safety_car: string;
}

interface SimulationControlsProps {
    onSimulate: (params: SimulationState) => void;
}

export default function SimulationControls({ onSimulate }: SimulationControlsProps) {
    const [params, setParams] = useState<SimulationState>({
        circuit: "lusail",
        laps: 44,
        date: "27 Jul 2025",
        weatherSummary: "Mixed Conditions",
        airTemp: 18,
        trackTemp: 28,
        rainProb: 45,
        humidity: 70,
        tire: "medium",
        pitStops: 2,
        safetyCar: "medium"
    });

    // Fetch defaults when circuit changes
    useEffect(() => {
        const fetchDefaults = async () => {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                const res = await fetch(`${apiUrl}/defaults/${params.circuit}`);
                if (res.ok) {
                    const defaults: SimulationDefaults = await res.json();
                    setParams(prev => ({
                        ...prev,
                        laps: defaults.laps || 50,
                        date: defaults.date || "TBD",
                        weatherSummary: defaults.weather_summary || "Unknown",
                        airTemp: defaults.air_temp,
                        trackTemp: defaults.track_temp,
                        rainProb: defaults.rain_prob,
                        humidity: defaults.humidity,
                        tire: defaults.tire,
                        pitStops: defaults.pit_stops,
                        safetyCar: defaults.safety_car
                    }));
                }
            } catch (error) {
                console.error("Failed to fetch defaults:", error);
            }
        };
        fetchDefaults();
    }, [params.circuit]);

    const handleSimulate = () => {
        onSimulate(params);
    };

    const handleReset = async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/defaults/${params.circuit}`);
            if (res.ok) {
                const defaults: SimulationDefaults = await res.json();
                setParams(prev => ({
                    ...prev,
                    airTemp: defaults.air_temp,
                    trackTemp: defaults.track_temp,
                    rainProb: defaults.rain_prob,
                    humidity: defaults.humidity,
                    tire: defaults.tire,
                    pitStops: defaults.pit_stops,
                    safetyCar: defaults.safety_car
                }));
            }
        } catch (error) {
            console.error("Failed to reset defaults:", error);
        }
    };

    const updateParam = (key: keyof SimulationState, value: string | number) => {
        setParams(prev => ({ ...prev, [key]: value }));
    };

    return (
        <div className="space-y-8 p-6 bg-[#111] border border-white/5 rounded-2xl h-full overflow-y-auto relative flex flex-col">
            <div className="flex justify-between items-start">
                <div>
                    <h2 className="text-xl font-bold mb-1 flex items-center gap-2">
                        <Zap className="w-5 h-5 text-[#E10600]" />
                        Simulation Parameters
                    </h2>
                    <p className="text-xs text-gray-500">Adjust variables to predict race outcome</p>
                </div>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleReset}
                    className="text-xs text-gray-400 hover:text-white hover:bg-white/10"
                >
                    <RotateCcw className="w-3 h-3 mr-1" /> Reset Normal
                </Button>
            </div>

            <div className="space-y-3">
                <Label className="text-xs font-mono text-gray-400 uppercase tracking-widest">Grand Prix (Remaining 2025)</Label>
                <Select value={params.circuit} onValueChange={(v) => updateParam("circuit", v)}>
                    <SelectTrigger className="bg-white/5 border-white/10 text-white h-12">
                        <SelectValue placeholder="Select Circuit" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1A1A1A] border-white/10 text-white">
                        <SelectItem value="lusail" className="focus:bg-white/10 focus:text-white cursor-pointer py-3">
                            <div className="flex items-center gap-3">
                                <span className="text-lg">🇶🇦</span>
                                <div className="flex flex-col">
                                    <span className="font-bold text-sm">Qatar Grand Prix</span>
                                    <span className="text-[10px] text-gray-400 font-mono">LUSAIL INTERNATIONAL CIRCUIT</span>
                                </div>
                            </div>
                        </SelectItem>
                        <SelectItem value="abudhabi" className="focus:bg-white/10 focus:text-white cursor-pointer py-3">
                            <div className="flex items-center gap-3">
                                <span className="text-lg">🇦🇪</span>
                                <div className="flex flex-col">
                                    <span className="font-bold text-sm">Abu Dhabi Grand Prix</span>
                                    <span className="text-[10px] text-gray-400 font-mono">YAS MARINA CIRCUIT</span>
                                </div>
                            </div>
                        </SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div className="space-y-6">
                <div className="flex items-center gap-2 text-xs font-mono text-gray-400 uppercase tracking-widest border-b border-white/5 pb-2">
                    <CloudRain className="w-3 h-3" /> Weather Conditions
                </div>

                <div className="space-y-4">
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                            <span className="text-gray-400">Air Temp</span>
                            <span className="font-mono font-bold">{params.airTemp}°C</span>
                        </div>
                        <Slider
                            value={[params.airTemp]}
                            min={10} max={45} step={1}
                            onValueChange={([v]) => updateParam("airTemp", v)}
                            className="[&>.relative>.absolute]:bg-[#E10600]"
                        />
                    </div>

                    <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                            <span className="text-gray-400">Track Temp</span>
                            <span className="font-mono font-bold">{params.trackTemp}°C</span>
                        </div>
                        <Slider
                            value={[params.trackTemp]}
                            min={15} max={60} step={1}
                            onValueChange={([v]) => updateParam("trackTemp", v)}
                            className="[&>.relative>.absolute]:bg-[#E10600]"
                        />
                    </div>

                    <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                            <span className="text-gray-400">Rain Probability</span>
                            <span className="font-mono font-bold text-blue-400">{params.rainProb}%</span>
                        </div>
                        <Slider
                            value={[params.rainProb]}
                            min={0} max={100} step={5}
                            onValueChange={([v]) => updateParam("rainProb", v)}
                            className="[&>.relative>.absolute]:bg-blue-500"
                        />
                    </div>
                </div>
            </div>

            <div className="space-y-6">
                <div className="flex items-center gap-2 text-xs font-mono text-gray-400 uppercase tracking-widest border-b border-white/5 pb-2">
                    <RotateCcw className="w-3 h-3" /> Strategy
                </div>

                <div className="space-y-4">
                    <div className="space-y-2">
                        <Label className="text-xs text-gray-400">Starting Tire</Label>
                        <div className="grid grid-cols-3 gap-2">
                            {['soft', 'medium', 'hard'].map((t) => (
                                <button
                                    key={t}
                                    onClick={() => updateParam("tire", t)}
                                    className={`px-3 py-2 rounded text-xs font-bold uppercase border transition-all ${params.tire === t
                                        ? t === 'soft' ? 'bg-red-500/20 border-red-500 text-red-500'
                                            : t === 'medium' ? 'bg-yellow-500/20 border-yellow-500 text-yellow-500'
                                                : 'bg-white/20 border-white text-white'
                                        : 'bg-white/5 border-transparent text-gray-500 hover:bg-white/10'
                                        }`}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-gray-400">Expected Pit Stops</Label>
                        <Select value={params.pitStops.toString()} onValueChange={(v) => updateParam("pitStops", parseInt(v))}>
                            <SelectTrigger className="bg-white/5 border-white/10 text-white">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent className="bg-[#1A1A1A] border-white/10 text-white">
                                <SelectItem value="1">1 Stop</SelectItem>
                                <SelectItem value="2">2 Stops</SelectItem>
                                <SelectItem value="3">3 Stops</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-xs text-gray-400">Safety Car Risk</Label>
                        <div className="flex items-center gap-2 bg-white/5 p-1 rounded-lg">
                            {['low', 'medium', 'high'].map((risk) => (
                                <button
                                    key={risk}
                                    onClick={() => updateParam("safetyCar", risk)}
                                    className={`flex-1 py-1.5 rounded text-[10px] font-bold uppercase transition-all ${params.safetyCar === risk
                                        ? 'bg-white/10 text-white shadow-sm'
                                        : 'text-gray-500 hover:text-gray-300'
                                        }`}
                                >
                                    {risk}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="sticky bottom-0 left-0 right-0 p-4 bg-[#111] border-t border-white/5 -mx-6 -mb-6 mt-auto">
                <Button
                    onClick={handleSimulate}
                    className="w-full bg-[#E10600] hover:bg-[#c40500] text-white font-bold py-6 text-lg tracking-wider uppercase shadow-[0_0_20px_rgba(225,6,0,0.3)] hover:shadow-[0_0_30px_rgba(225,6,0,0.5)] transition-all group relative overflow-hidden"
                >
                    <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                        animate={{ x: ["-100%", "200%"] }}
                        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    />
                    <span className="relative z-10 flex items-center justify-center gap-2">
                        <Zap className="w-5 h-5 group-hover:scale-110 transition-transform" />
                        Run Simulation
                    </span>
                </Button>
            </div>
        </div>
    );
}
