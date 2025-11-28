"use client";

import { useCallback, useEffect, useRef, useState } from "react";

interface UseSoundReturn {
    play: (soundName: string) => void;
    isMuted: boolean;
    toggleMute: () => void;
    setVolume: (volume: number) => void;
}

export function useSound(): UseSoundReturn {
    const [isMuted, setIsMuted] = useState(true); // Muted by default
    const [volume, setVolume] = useState(0.5);
    const audioRefs = useRef<Record<string, HTMLAudioElement>>({});

    useEffect(() => {
        // Preload sounds
        const sounds = {
            engineStart: "/sounds/engine-start.mp3",
            pitStop: "/sounds/pit-stop.mp3",
            positionUp: "/sounds/position-up.mp3",
            positionDown: "/sounds/position-down.mp3",
        };

        Object.entries(sounds).forEach(([key, src]) => {
            const audio = new Audio(src);
            audio.volume = volume;
            audioRefs.current[key] = audio;
        });

        // Load mute preference from localStorage
        const savedMute = localStorage.getItem("f1-sound-muted");
        if (savedMute !== null) {
            setIsMuted(savedMute === "true");
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        // Update volume for all audio elements
        Object.values(audioRefs.current).forEach((audio) => {
            audio.volume = isMuted ? 0 : volume;
        });
    }, [volume, isMuted]);
    const play = useCallback(
        (soundName: string) => {
            if (isMuted) return;

            const audio = audioRefs.current[soundName];
            if (audio) {
                audio.currentTime = 0;
                audio.play().catch((err) => console.log("Audio play failed:", err));
            }
        },
        [isMuted]
    );

    const toggleMute = useCallback(() => {
        setIsMuted((prev) => {
            const newValue = !prev;
            localStorage.setItem("f1-sound-muted", String(newValue));
            return newValue;
        });
    }, []);

    return { play, isMuted, toggleMute, setVolume };
}
