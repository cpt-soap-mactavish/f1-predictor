"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Keyboard } from "lucide-react";

interface ShortcutsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const shortcuts = [
    { key: "Space", description: "Run Simulation" },
    { key: "T", description: "Toggle Theme" },
    { key: "M", description: "Mute/Unmute Sounds" },
    { key: "?", description: "Show This Help" },
    { key: "Esc", description: "Close Modals" },
];

export default function ShortcutsModal({ isOpen, onClose }: ShortcutsModalProps) {
    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9998]"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-[9999] w-full max-w-md"
                    >
                        <div className="bg-[#1A1A1A] border border-white/10 rounded-2xl p-6 shadow-2xl">
                            {/* Header */}
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-3">
                                    <Keyboard className="w-5 h-5 text-[#E10600]" />
                                    <h2 className="text-xl font-bold text-white">Keyboard Shortcuts</h2>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                                >
                                    <X className="w-5 h-5 text-gray-400" />
                                </button>
                            </div>

                            {/* Shortcuts List */}
                            <div className="space-y-3">
                                {shortcuts.map((shortcut, idx) => (
                                    <motion.div
                                        key={shortcut.key}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                        className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                                    >
                                        <span className="text-gray-300">{shortcut.description}</span>
                                        <kbd className="px-3 py-1 bg-black/40 border border-white/10 rounded text-white font-mono text-sm">
                                            {shortcut.key}
                                        </kbd>
                                    </motion.div>
                                ))}
                            </div>

                            {/* Footer */}
                            <div className="mt-6 pt-4 border-t border-white/10">
                                <p className="text-xs text-gray-500 text-center">
                                    Press <kbd className="px-2 py-0.5 bg-black/40 border border-white/10 rounded text-white font-mono">Esc</kbd> to close
                                </p>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
