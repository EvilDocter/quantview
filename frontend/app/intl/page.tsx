"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Shield, Globe } from "lucide-react";

export default function MarketChoicePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex flex-col items-center justify-center p-6 font-sans relative overflow-hidden">
      {/* Decorative gradients */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-4xl w-full text-center space-y-12 z-10">
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-black tracking-tight text-white bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
            QuantView
          </h1>
          <p className="text-md md:text-lg text-slate-400 max-w-lg mx-auto">
            Choose your market platform to begin trading or analyzing financial intelligence.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
          {/* Card 1: Indian Market */}
          <div 
            onClick={() => router.push("/india")}
            className="group relative bg-white/[0.02] hover:bg-white/[0.05] border border-white/5 hover:border-indigo-500/30 rounded-[32px] p-8 cursor-pointer transition-all duration-300 transform hover:-translate-y-1 shadow-2xl backdrop-blur-md flex flex-col justify-between text-left"
          >
            <div className="space-y-6">
              <div className="inline-flex p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 group-hover:scale-110 transition-transform duration-300">
                <Shield className="w-8 h-8" />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-white group-hover:text-indigo-400 transition-colors">
                  Indian Market
                </h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  AI-powered financial research platform. Specialized autonomous agents analyzing filings, corporate actions, and portfolios.
                </p>
              </div>
            </div>
            <div className="mt-8 text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1">
              Enter Platform →
            </div>
          </div>

          {/* Card 2: International Markets */}
          <div 
            onClick={() => router.push("/intl")}
            className="group relative bg-white/[0.02] hover:bg-white/[0.05] border border-white/5 hover:border-purple-500/30 rounded-[32px] p-8 cursor-pointer transition-all duration-300 transform hover:-translate-y-1 shadow-2xl backdrop-blur-md flex flex-col justify-between text-left"
          >
            <div className="space-y-6">
              <div className="inline-flex p-4 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-400 group-hover:scale-110 transition-transform duration-300">
                <Globe className="w-8 h-8" />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-white group-hover:text-purple-400 transition-colors">
                  International Markets
                </h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Real-time trading terminal. Forex, indices, commodities, and crypto execution with cTrader/MT5 broker connections.
                </p>
              </div>
            </div>
            <div className="mt-8 text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1">
              Enter Terminal →
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}