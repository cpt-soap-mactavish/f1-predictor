import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";

interface ShapChartProps {
  driverId: string;
}

interface ShapData {
  driver_id: string;
  features: string[];
  shap_values: number[];
  base_value: number;
}

export default function ShapChart({ driverId }: ShapChartProps) {
  const [shapData, setShapData] = useState<ShapData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchShapData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/shap/${driverId}`);
        if (!response.ok) throw new Error("Failed to fetch SHAP data");
        const data = await response.json();
        setShapData(data);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };
    fetchShapData();
  }, [driverId]);

  if (loading || !shapData) {
    return (
      <Card className="card-f1">
        <CardContent className="p-6">
          <p className="text-f1silver">Loading SHAP data...</p>
        </CardContent>
      </Card>
    );
  }

  const chartData = shapData.features
    .map((feature, index) => ({
      feature: feature.replace(/_/g, " "),
      value: Math.abs(shapData.shap_values[index]),
      impact: shapData.shap_values[index] > 0 ? "positive" : "negative",
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10); // Top 10 features

  return (
    <Card className="card-f1">
      <CardContent className="p-6">
        <svg width="100%" height={chartData.length * 30 + 20}>
          {chartData.map((item, index) => (
            <g key={index}>
              <rect
                x="150"
                y={index * 30 + 10}
                width={Math.min(item.value * 100, 300)} // Cap width for readability
                height="20"
                fill={item.impact === "positive" ? "#10b981" : "#ef4444"}
                className="rounded"
              />
              <text x="10" y={index * 30 + 25} fill="#fff" fontSize="12">
                {item.feature}
              </text>
              <text x="120" y={index * 30 + 25} fill="#fff" fontSize="12">
                {item.value.toFixed(3)}
              </text>
            </g>
          ))}
        </svg>
      </CardContent>
    </Card>
  );
}