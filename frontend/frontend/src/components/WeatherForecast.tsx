import { CloudRain, Thermometer, Droplets, Sun, Calendar } from "lucide-react";

interface WeatherForecastProps {
    date?: string;
    summary?: string;
    airTemp: number;
    trackTemp: number;
    rainProb: number;
    humidity: number;
}

export default function WeatherForecast({ date, summary, airTemp, trackTemp, rainProb, humidity }: WeatherForecastProps) {
    return (
        <div className="bg-white/[0.02] border border-white/5 rounded-xl p-6 h-full flex flex-col gap-6">
            {/* Header Section */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-[#E10600] animate-pulse" />
                    <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">Forecast</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-mono text-gray-500">
                    <Calendar className="w-3 h-3" />
                    <span>{date || "RACE DAY"}</span>
                </div>
            </div>

            {/* Main Weather Summary */}
            <div className="text-center py-2">
                <div className="text-2xl font-bold text-white uppercase tracking-wider">
                    {summary || "CONDITIONS LOADING..."}
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-4 mt-auto">
                {/* Air Temp */}
                <div className="flex flex-col items-center justify-center p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="flex items-center gap-2 mb-1">
                        <Thermometer className="w-4 h-4 text-orange-500" />
                        <span className="text-[10px] font-mono text-gray-500">AIR</span>
                    </div>
                    <div className="text-lg font-bold text-white">{airTemp}°C</div>
                </div>

                {/* Track Temp */}
                <div className="flex flex-col items-center justify-center p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="flex items-center gap-2 mb-1">
                        <Sun className="w-4 h-4 text-red-500" />
                        <span className="text-[10px] font-mono text-gray-500">TRACK</span>
                    </div>
                    <div className="text-lg font-bold text-white">{trackTemp}°C</div>
                </div>

                {/* Rain Probability */}
                <div className="flex flex-col items-center justify-center p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="flex items-center gap-2 mb-1">
                        <CloudRain className={`w-4 h-4 ${rainProb > 40 ? 'text-blue-400' : 'text-gray-400'}`} />
                        <span className="text-[10px] font-mono text-gray-500">RAIN</span>
                    </div>
                    <div className={`text-lg font-bold ${rainProb > 40 ? 'text-blue-400' : 'text-white'}`}>
                        {rainProb}%
                    </div>
                </div>

                {/* Humidity */}
                <div className="flex flex-col items-center justify-center p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="flex items-center gap-2 mb-1">
                        <Droplets className="w-4 h-4 text-cyan-500" />
                        <span className="text-[10px] font-mono text-gray-500">HUMIDITY</span>
                    </div>
                    <div className="text-lg font-bold text-white">{humidity}%</div>
                </div>
            </div>
        </div>
    );
}
