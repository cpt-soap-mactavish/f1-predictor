"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Zap, Radio, Gauge, Activity, Flag, Keyboard } from "lucide-react";
import SectorLegend from "@/components/SectorLegend";
import TrackMapLive from "@/components/TrackMapLive";
import PaceSparkline from "@/components/PaceSparkline";
import PositionChangeIndicator from "@/components/PositionChangeIndicator";
import ThemeToggle from "@/components/ThemeToggle";
import SoundToggle from "@/components/SoundToggle";
import ShortcutsModal from "@/components/ShortcutsModal";
import { useSound } from "@/hooks/useSound";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { useTheme } from "@/contexts/ThemeContext";

interface Prediction {
  position: number;
  driver_id: string;
  constructor_id: string;
  grid: number;
  win_probability: number;
  podium_probability: number;
  confidence: number;
}

const teamColors: Record<string, string> = {
  red_bull: "#3671C6", ferrari: "#E8002D", mercedes: "#27F4D2",
  mclaren: "#FF8000", alpine: "#FF87BC", aston_martin: "#229971",
  williams: "#64C4FF", haas: "#B6BABD", alphatauri: "#5E8FAA", sauber: "#52E252",
};

const tires = ["S", "M", "H", "I", "W"];

export default function Home() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentLap, setCurrentLap] = useState(1);
  const [hoveredRow, setHoveredRow] = useState<number | null>(null);
  const [fastestLapDriver, setFastestLapDriver] = useState<string | null>(null);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [positionChanges] = useState<Record<number, number>>({});
  // Hooks
  const { isMuted, toggleMute } = useSound();
  const { toggleTheme } = useTheme();

  // Keyboard shortcuts
  useKeyboardShortcuts([
    { key: " ", action: () => console.log("Simulate"), description: "Run Simulation" },
    { key: "t", action: toggleTheme, description: "Toggle Theme" },
    { key: "m", action: toggleMute, description: "Mute/Unmute" },
    { key: "?", shift: true, action: () => setShowShortcuts(true), description: "Show Shortcuts" },
    { key: "Escape", action: () => setShowShortcuts(false), description: "Close Modals" },
  ]);

  useEffect(() => {
    fetchPredictions();
    const interval = setInterval(() => setCurrentLap(prev => (prev % 44) + 1), 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchPredictions = async () => {
    try {
      const res = await fetch("/api/predict");
      const data = await res.json();
      const preds = data.predictions || [];
      setPredictions(preds);
      if (preds.length > 0) {
        setFastestLapDriver(preds[Math.floor(Math.random() * preds.length)].driver_id);
      }
    } catch (err) {
      console.error(err);
      // Fallback data for UI dev if API fails
      setPredictions(Array(20).fill(0).map((_, i) => ({
        position: i + 1,
        driver_id: ["verstappen", "norris", "leclerc", "piastri", "hamilton", "russell", "sainz", "alonso", "gasly", "ocon", "albon", "tsunoda", "stroll", "hulkenberg", "bearman", "lawson", "doohan", "antonelli", "colapinto", "hadjar"][i] || "driver",
        constructor_id: ["red_bull", "mclaren", "ferrari", "mclaren", "ferrari", "mercedes", "mercedes", "aston_martin", "alpine", "sauber", "williams", "rb", "aston_martin", "haas", "haas", "rb", "alpine", "mercedes", "williams", "rb"][i] || "haas",
        grid: i + 1,
        win_probability: i === 0 ? 45 : i === 1 ? 30 : 5,
        podium_probability: 80 - i * 5,
        confidence: 0.9
      })));
      setLoading(false);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Zap className="w-12 h-12 text-[#E10600]" />
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white font-sans selection:bg-[#E10600] selection:text-white overflow-x-hidden">
      {/* Cinematic Header */}
      <div className="border-b border-white/10 bg-black/60 backdrop-blur-xl sticky top-0 z-50">
        <div className="w-full max-w-[1900px] mx-auto px-4 md:px-6 py-3 md:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 md:gap-8">
              <div className="flex items-center gap-3 md:gap-4">
                <div className="w-1 h-8 md:h-10 bg-[#E10600] shadow-[0_0_15px_#E10600]" />
                <div>
                  <h1 className="text-lg md:text-xl font-bold tracking-tighter uppercase">Belgian GP</h1>
                  <div className="hidden md:flex items-center gap-2 text-[10px] text-gray-400 font-mono tracking-widest uppercase">
                    <span>Spa-Francorchamps</span>
                    <span className="w-1 h-1 rounded-full bg-gray-600" />
                    <span>Round 13</span>
                    <span className="w-1 h-1 rounded-full bg-gray-600" />
                    <span>2025</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 md:gap-4">
              {/* Theme & Sound Controls */}
              <div className="flex items-center gap-1 md:gap-2">
                <ThemeToggle />
                <SoundToggle isMuted={isMuted} onToggle={toggleMute} />
                <button
                  onClick={() => setShowShortcuts(true)}
                  className="hidden md:block p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
                  aria-label="Show keyboard shortcuts"
                >
                  <Keyboard className="w-5 h-5 text-gray-300" />
                </button>
              </div>

              <Link href="/predict">
                <button className="flex items-center gap-2 px-3 py-2 md:px-4 md:py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full transition-all group">
                  <Zap className="w-4 h-4 text-[#E10600] group-hover:scale-110 transition-transform" />
                  <span className="text-[10px] md:text-xs font-bold tracking-wider text-gray-200 whitespace-nowrap">SIM MODE</span>
                </button>
              </Link>

              {/* Race Control Messages */}
              <div className="hidden lg:flex items-center gap-2 px-4 py-1.5 bg-yellow-500/10 border border-yellow-500/20 rounded-full">
                <Flag className="w-3 h-3 text-yellow-500" />
                <span className="text-[10px] font-mono text-yellow-500 tracking-wider">SECTOR 2 YELLOW FLAG</span>
              </div>

              <div className="hidden xl:flex items-center gap-8 text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">AIR</span>
                  <span className="text-white font-bold">23°C</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">TRACK</span>
                  <span className="text-white font-bold">42°C</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">HUMIDITY</span>
                  <span className="text-white font-bold">45%</span>
                </div>
              </div>

              <div className="hidden md:flex items-center gap-4 pl-8 border-l border-white/10">
                <motion.div
                  className="flex items-center gap-2 px-3 py-1 rounded bg-[#E10600] text-white shadow-[0_0_10px_rgba(225,6,0,0.4)]"
                  animate={{ opacity: [1, 0.8, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                  <span className="text-[10px] font-bold tracking-wider">LIVE</span>
                </motion.div>
                <div className="text-2xl font-mono font-bold tabular-nums tracking-tight">
                  {currentLap}<span className="text-gray-600 text-lg">/44</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="w-full max-w-[1850px] mx-auto px-4 sm:px-6 py-6">
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">

          {/* Left Telemetry Column */}
          <div className="col-span-1 xl:col-span-3 space-y-6">

            {/* Track Map */}
            <div className="bg-[#111] rounded-2xl p-6 border border-white/5 relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none" />
              <div className="flex items-center justify-between mb-6">
                <div className="text-[10px] text-gray-400 font-mono tracking-widest flex items-center gap-2">
                  <Activity className="w-3 h-3 text-[#E10600]" />
                  CIRCUIT STATUS
                </div>
                <div className="px-2 py-0.5 rounded bg-green-500/20 text-green-400 text-[9px] font-mono border border-green-500/20">
                  TRACK CLEAR
                </div>
              </div>

              <div className="relative aspect-video flex items-center justify-center">
                <svg viewBox="0 0 300 200" className="w-full h-full drop-shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                  <defs>
                    <linearGradient id="trackGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#333" />
                      <stop offset="50%" stopColor="#555" />
                      <stop offset="100%" stopColor="#333" />
                    </linearGradient>
                  </defs>
                  {/* Track Path */}
                  <path d="M 40 100 L 80 60 L 140 50 L 200 70 L 250 90 L 270 140 L 240 180 L 180 190 L 120 175 L 70 150 L 40 100 Z"
                    fill="none" stroke="#222" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M 40 100 L 80 60 L 140 50 L 200 70 L 250 90 L 270 140 L 240 180 L 180 190 L 120 175 L 70 150 L 40 100 Z"
                    fill="none" stroke="url(#trackGradient)" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />

                  {/* Sectors */}
                  <path d="M 40 100 L 80 60 L 140 50" fill="none" stroke="#E10600" strokeWidth="8" strokeOpacity="0.2" />
                  <path d="M 140 50 L 200 70 L 250 90 L 270 140" fill="none" stroke="#4ade80" strokeWidth="8" strokeOpacity="0.2" />
                  <path d="M 270 140 L 240 180 L 180 190 L 120 175 L 70 150 L 40 100" fill="none" stroke="#fbbf24" strokeWidth="8" strokeOpacity="0.2" />

                  {/* Active Car */}
                  <circle cx="0" cy="0" r="4" fill="#fff" className="drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]">
                    <animateMotion
                      dur="6s"
                      repeatCount="indefinite"
                      path="M 40 100 L 80 60 L 140 50 L 200 70 L 250 90 L 270 140 L 240 180 L 180 190 L 120 175 L 70 150 L 40 100 Z"
                    />
                  </circle>
                </svg>
              </div>

              {/* Replace with new TrackMapLive */}
              <div className="bg-[#111] rounded-2xl p-5 border border-white/5">
                <div className="text-[10px] text-gray-400 font-mono tracking-widest mb-4">TRACK MAP</div>
                <TrackMapLive />
              </div>

              <div className="grid grid-cols-3 gap-px bg-white/5 rounded-lg overflow-hidden mt-6 border border-white/5">
                <div className="bg-[#151515] p-3 text-center">
                  <div className="text-[10px] text-gray-500 mb-1">LENGTH</div>
                  <div className="font-mono font-bold">7.004 <span className="text-[9px] text-gray-600">KM</span></div>
                </div>
                <div className="bg-[#151515] p-3 text-center">
                  <div className="text-[10px] text-gray-500 mb-1">DRS ZONES</div>
                  <div className="font-mono font-bold">2</div>
                </div>
                <div className="bg-[#151515] p-3 text-center">
                  <div className="text-[10px] text-gray-500 mb-1">TURNS</div>
                  <div className="font-mono font-bold">19</div>
                </div>
              </div>
            </div>

            {/* Live Data Cards */}
            <div className="grid grid-cols-1 gap-4">
              <div className="bg-[#111] rounded-2xl p-5 border border-white/5 relative overflow-hidden">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-[10px] text-gray-400 font-mono tracking-widest">SPEED TRAP</div>
                  <Gauge className="w-4 h-4 text-gray-600" />
                </div>
                <div className="flex items-baseline gap-2">
                  <div className="text-3xl md:text-4xl font-mono font-bold tabular-nums text-white">
                    {290 + Math.floor(Math.random() * 45)}
                  </div>
                  <div className="text-[10px] md:text-xs text-gray-500 font-mono">KM/H</div>
                </div>
                <div className="mt-4 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-blue-500 to-cyan-400"
                    animate={{ width: `${Math.random() * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-[#111] rounded-2xl p-4 md:p-5 border border-white/5">
                  <div className="text-[10px] text-gray-400 font-mono tracking-widest mb-2">GEAR</div>
                  <div className="text-2xl md:text-3xl font-mono font-bold text-white">{Math.floor(Math.random() * 8) + 1}</div>
                </div>
                <div className="bg-[#111] rounded-2xl p-4 md:p-5 border border-white/5">
                  <div className="text-[10px] text-gray-400 font-mono tracking-widest mb-2">RPM</div>
                  <div className="text-2xl md:text-3xl font-mono font-bold text-[#E10600]">
                    {(10 + Math.random() * 2).toFixed(1)}<span className="text-xs md:text-sm text-gray-500 ml-1">k</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Timing Board */}
          <div className="col-span-1 xl:col-span-9">
            <div className="bg-[#111] rounded-2xl border border-white/5 overflow-hidden shadow-2xl">
              <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                <div className="flex items-center gap-3">
                  <Radio className="w-4 h-4 text-[#E10600] animate-pulse" />
                  <span className="text-xs font-bold tracking-widest text-gray-300">LIVE TIMING</span>
                </div>
                <div className="flex items-center gap-4 text-[10px] font-mono text-gray-500">
                  <span>UPDATED: 0.042s</span>
                  <span>SOURCE: TRACK</span>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead className="bg-[#0A0A0F] border-b border-white/5">
                    <tr className="text-[9px] text-gray-500 uppercase tracking-wider font-mono">
                      <th className="px-4 py-3 text-left w-12">Pos</th>
                      <th className="px-4 py-3 text-left">Driver</th>
                      <th className="px-2 py-3 text-center w-12">Gap</th>
                      <th className="px-2 py-3 text-center w-12">Int</th>
                      <th className="px-3 py-3 text-center">Tire</th>
                      <th className="px-3 py-3 text-center">Pit</th>
                      <th className="px-4 py-3 text-right">Last Lap</th>
                      <th className="px-2 py-3 text-center w-16">S1</th>
                      <th className="px-2 py-3 text-center w-16">S2</th>
                      <th className="px-2 py-3 text-center w-16">S3</th>
                      <th className="px-4 py-3 text-right">Win %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {predictions.map((p, idx) => {
                      const tire = tires[Math.floor(Math.random() * 3)];
                      const isHovered = hoveredRow === idx;
                      const gap = idx === 0 ? "-" : `+${(idx * 2.4 + Math.random()).toFixed(1)}`;
                      const interval = idx === 0 ? "-" : `+${(Math.random() * 1.5).toFixed(1)}`;
                      const isFastest = p.driver_id === fastestLapDriver;

                      return (
                        <motion.tr
                          key={idx}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.02 }}
                          onMouseEnter={() => setHoveredRow(idx)}
                          onMouseLeave={() => setHoveredRow(null)}
                          className={cn(
                            "transition-colors duration-150 group",
                            isHovered ? "bg-white/[0.04]" : "bg-[#111]"
                          )}
                        >
                          <td className="px-4 py-3">
                            <div className={cn(
                              "w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold font-mono",
                              idx === 0 ? "bg-[#E10600] text-white" : "text-gray-400 bg-white/5"
                            )}>
                              {p.position}
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-3">
                              <div className="w-0.5 h-6 rounded-full" style={{ backgroundColor: teamColors[p.constructor_id] }} />
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <div className="font-bold text-white group-hover:text-[#E10600] transition-colors">
                                    {p.driver_id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                                  </div>
                                  <PaceSparkline data={[82, 80, 79, 81, 78]} />
                                  <PositionChangeIndicator change={positionChanges[idx] || 0} show={!!positionChanges[idx]} />
                                </div>
                                <div className="text-[9px] text-gray-600 uppercase hidden sm:block">
                                  {p.constructor_id.replace(/_/g, ' ')}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-2 py-3 text-center font-mono text-gray-400">{gap}</td>
                          <td className="px-2 py-3 text-center font-mono text-gray-500">{interval}</td>
                          <td className="px-3 py-3">
                            <div className="flex justify-center">
                              <div className={cn(
                                "w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold border-2",
                                tire === "S" && "border-red-500 text-red-500",
                                tire === "M" && "border-yellow-400 text-yellow-400",
                                tire === "H" && "border-white text-white"
                              )}>
                                {tire}
                              </div>
                            </div>
                          </td>
                          <td className="px-3 py-3 text-center font-mono text-gray-500">
                            {Math.random() > 0.8 ? "1" : "0"}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <div className={cn(
                              "font-mono tabular-nums",
                              isFastest ? "text-purple-400 font-bold" : "text-white"
                            )}>
                              1:{32 + idx}.{Math.floor(Math.random() * 999).toString().padStart(3, '0')}
                            </div>
                          </td>
                          {[1, 2, 3].map((s) => (
                            <td key={s} className="px-2 py-3 text-center">
                              <div className={cn(
                                "w-1.5 h-1.5 rounded-full mx-auto",
                                Math.random() > 0.7 ? "bg-purple-500 shadow-[0_0_8px_#a855f7]" :
                                  Math.random() > 0.3 ? "bg-green-500" : "bg-yellow-500"
                              )} />
                            </td>
                          ))}
                          <td className="px-4 py-3">
                            <div className="flex items-center justify-end gap-2">
                              <div className="w-16 h-1 bg-gray-800 rounded-full overflow-hidden">
                                <div
                                  className="h-full rounded-full"
                                  style={{
                                    width: `${p.win_probability}%`,
                                    backgroundColor: teamColors[p.constructor_id]
                                  }}
                                />
                              </div>
                              <span className="font-mono text-[10px] text-gray-400 w-8 text-right">
                                {p.win_probability.toFixed(0)}%
                              </span>
                            </div>
                          </td>
                        </motion.tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Shortcuts Modal */}
      <ShortcutsModal isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />

      {/* Sector Legend */}
      <SectorLegend />
    </div>
  );
}