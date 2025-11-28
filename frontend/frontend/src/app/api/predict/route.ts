import { NextResponse } from 'next/server';

// Mock predictions data - replace with actual backend API call
const mockPredictions = [
    {
        position: 1,
        driver_id: "max_verstappen",
        constructor_id: "red_bull",
        grid: 1,
        win_probability: 87.3,
        podium_probability: 95.8,
        confidence: 92.1
    },
    {
        position: 2,
        driver_id: "lando_norris",
        constructor_id: "mclaren",
        grid: 2,
        win_probability: 72.5,
        podium_probability: 91.2,
        confidence: 88.4
    },
    {
        position: 3,
        driver_id: "charles_leclerc",
        constructor_id: "ferrari",
        grid: 3,
        win_probability: 65.8,
        podium_probability: 87.6,
        confidence: 85.3
    },
    {
        position: 4,
        driver_id: "lewis_hamilton",
        constructor_id: "mercedes",
        grid: 4,
        win_probability: 58.2,
        podium_probability: 82.1,
        confidence: 81.7
    },
    {
        position: 5,
        driver_id: "oscar_piastri",
        constructor_id: "mclaren",
        grid: 5,
        win_probability: 52.3,
        podium_probability: 76.5,
        confidence: 78.9
    },
    {
        position: 6,
        driver_id: "george_russell",
        constructor_id: "mercedes",
        grid: 6,
        win_probability: 45.7,
        podium_probability: 71.3,
        confidence: 75.2
    },
    {
        position: 7,
        driver_id: "carlos_sainz",
        constructor_id: "ferrari",
        grid: 7,
        win_probability: 38.9,
        podium_probability: 65.8,
        confidence: 71.5
    },
    {
        position: 8,
        driver_id: "fernando_alonso",
        constructor_id: "aston_martin",
        grid: 8,
        win_probability: 32.1,
        podium_probability: 58.4,
        confidence: 67.8
    },
    {
        position: 9,
        driver_id: "pierre_gasly",
        constructor_id: "alpine",
        grid: 9,
        win_probability: 25.6,
        podium_probability: 51.2,
        confidence: 64.3
    },
    {
        position: 10,
        driver_id: "lance_stroll",
        constructor_id: "aston_martin",
        grid: 10,
        win_probability: 18.4,
        podium_probability: 43.7,
        confidence: 60.1
    }
];

export async function GET() {
    // TODO: Replace with actual backend API call
    // const response = await fetch('http://localhost:8000/api/predict');
    // const data = await response.json();

    return NextResponse.json({
        predictions: mockPredictions,
        race: "Belgian Grand Prix",
        circuit: "Spa-Francorchamps",
        date: "2025-07-27"
    });
}
