"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { Activity, Zap, Shield, ChevronDown } from "lucide-react";

export function HeroSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  const y1 = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const y2 = useTransform(scrollYProgress, [0, 1], [0, -100]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 1], [1, 1.1]);

  return (
    <section 
      ref={containerRef} 
      className="relative min-h-[100vh] flex flex-col items-center justify-center overflow-hidden pt-20 pb-32"
    >
      {/* Background Ambient Glows */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-white/10 rounded-full blur-[120px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-neutral-500/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen" />
      
      {/* Subtle Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] pointer-events-none" />

      {/* Interactive Scrolling Brand Logo */}
      <motion.div
        style={{ 
          y: useTransform(scrollYProgress, [0, 1], [-80, 520]),
          scale: useTransform(scrollYProgress, [0, 1], [1.35, 0.65]),
          opacity: useTransform(scrollYProgress, [0, 0.85, 1], [1, 0.9, 0.8]), // Highly visible docking logo
        }}
        className="absolute top-[20%] z-30 pointer-events-none flex flex-col items-center justify-center"
      >
        {/* Dim Purple/Cyan Glow behind the logo */}
        <div className="absolute w-[360px] h-[140px] bg-purple-500/[0.06] rounded-full blur-[80px] pointer-events-none" />
        <div className="absolute w-[360px] h-[140px] bg-cyan-500/[0.04] rounded-full blur-[80px] pointer-events-none" />
        <img
          src="/logo.png"
          alt="QuantView Logo"
          className="w-72 md:w-[380px] h-auto relative z-10 filter drop-shadow-[0_0_30px_rgba(139,92,246,0.15)]"
        />
      </motion.div>

      {/* Main Content */}
      <motion.div 
        style={{ y: y1, opacity }} 
        className="relative z-10 flex flex-col items-center text-center max-w-5xl px-6"
      >
        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          className="text-4xl sm:text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-200 to-slate-500 leading-tight mb-6 mt-[240px] md:mt-[280px]"
        >
          The Future of
          <br />
          Intelligent Trading.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
          className="text-lg md:text-2xl text-slate-400 max-w-3xl leading-relaxed font-light mb-12"
        >
          Realtime AI-powered market analysis, liquidity mapping, and predictive trading infrastructure built for elite traders.
        </motion.p>

      </motion.div>

      {/* Floating UI Elements (Parallax) */}
      <motion.div 
        style={{ y: y2, scale }}
        className="absolute bottom-0 translate-y-1/2 w-full max-w-6xl px-6 pointer-events-none"
      >
        <div className="relative w-full aspect-[21/9] rounded-t-[40px] border-t border-x border-white/10 bg-[#121212]/80 backdrop-blur-2xl shadow-[0_-20px_100px_rgba(6,182,212,0.1)] overflow-hidden flex items-start justify-center p-8">
           {/* Faux Terminal Header */}
           <div className="absolute top-0 left-0 w-full h-12 border-b border-white/5 flex items-center px-6 gap-2 bg-white/[0.01]">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
           </div>

           {/* Animated Faux Chart Lines */}
           <div className="mt-12 w-full h-full relative">
              <div className="absolute inset-0 bg-gradient-to-t from-[#060B14] to-transparent z-10" />
              <svg className="w-full h-full opacity-30" viewBox="0 0 100 100" preserveAspectRatio="none">
                <motion.path 
                  d="M0,80 C20,60 40,90 60,40 C80,-10 100,50 100,50" 
                  fill="none" 
                  stroke="#06b6d4" 
                  strokeWidth="0.5"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 3, ease: "easeInOut" }}
                />
                <motion.path 
                  d="M0,90 C30,70 50,80 70,30 C90,0 100,20 100,20" 
                  fill="none" 
                  stroke="#8b5cf6" 
                  strokeWidth="0.5"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 4, ease: "easeInOut", delay: 0.5 }}
                />
              </svg>
           </div>
        </div>
      </motion.div>

      {/* Scroll Down Indicator */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 1 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-slate-500"
      >
        <span className="text-[10px] uppercase tracking-widest font-bold">Scroll to explore</span>
        <ChevronDown className="w-4 h-4 animate-bounce" />
      </motion.div>
    </section>
  );
}
