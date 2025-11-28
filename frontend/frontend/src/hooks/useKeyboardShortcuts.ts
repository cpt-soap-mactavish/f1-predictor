"use client";

import { useEffect, useCallback } from "react";

interface KeyboardShortcut {
    key: string;
    ctrl?: boolean;
    shift?: boolean;
    action: () => void;
    description: string;
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]) {
    const handleKeyPress = useCallback(
        (event: KeyboardEvent) => {
            // Don't trigger if user is typing in an input
            if (
                event.target instanceof HTMLInputElement ||
                event.target instanceof HTMLTextAreaElement
            ) {
                return;
            }

            shortcuts.forEach((shortcut) => {
                const ctrlMatch = shortcut.ctrl ? event.ctrlKey || event.metaKey : !event.ctrlKey && !event.metaKey;
                const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey;
                const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();

                if (ctrlMatch && shiftMatch && keyMatch) {
                    event.preventDefault();
                    shortcut.action();
                }
            });
        },
        [shortcuts]
    );

    useEffect(() => {
        window.addEventListener("keydown", handleKeyPress);
        return () => window.removeEventListener("keydown", handleKeyPress);
    }, [handleKeyPress]);
}

export const SHORTCUTS = {
    SIMULATE: { key: " ", description: "Run Simulation" },
    THEME: { key: "t", description: "Toggle Theme" },
    MUTE: { key: "m", description: "Mute/Unmute Sounds" },
    HELP: { key: "?", shift: true, description: "Show Shortcuts" },
};
