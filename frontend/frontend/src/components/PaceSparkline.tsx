"use client";

import { LineChart, Line } from "recharts";

interface PaceSparklineProps {
    data: number[];
}

export default function PaceSparkline({ data }: PaceSparklineProps) {
    const chartData = data.map((value, index) => ({ value }));

    return (
        <LineChart width={40} height={16} data={chartData}>
            <Line
                type="monotone"
                dataKey="value"
                stroke="#E10600"
                strokeWidth={1.5}
                dot={false}
            />
        </LineChart>
    );
}
