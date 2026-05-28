"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: "cyan" | "blue" | "purple" | "emerald" | "gold" | "none";
}

const glowMap = {
  cyan: "group-hover:shadow-[0_0_40px_rgba(6,182,212,0.15)] hover:border-cyan-500/30",
  blue: "group-hover:shadow-[0_0_40px_rgba(255,255,255,0.04)] hover:border-blue-500/30",
  purple: "group-hover:shadow-[0_0_40px_rgba(139,92,246,0.15)] hover:border-neutral-500/30",
  emerald: "group-hover:shadow-[0_0_40px_rgba(16,185,129,0.15)] hover:border-emerald-500/30",
  gold: "group-hover:shadow-[0_0_40px_rgba(251,191,36,0.15)] hover:border-amber-500/30",
  none: "",
};

export function GlassCard({ children, className, glowColor = "cyan" }: GlassCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ type: "spring", stiffness: 400, damping: 30 }}
      className={cn(
        "group relative rounded-[32px] border border-white/5 bg-[#161616]/80 p-6 backdrop-blur-md overflow-hidden transition-all duration-500",
        glowMap[glowColor],
        className
      )}
    >
      {/* Subtle interior glow layer */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      
      {/* Content wrapper to stay above background layers */}
      <div className="relative z-10 h-full w-full">
        {children}
      </div>
    </motion.div>
  );
}
