"use client";

import React, { useState } from "react";
import { ArrowLeft, TrendingUp, ShieldAlert, Award, Play, Activity } from "lucide-react";
import { useRouter } from "next/navigation";

export default function QuantLabPortal() {
  const router = useRouter();
  const [symbol, setSymbol] = useState("TATAMOTORS");
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRunBacktest = (e: React.FormEvent) => {
    e.preventDefault();
    setRunning(true);
    setTimeout(() => {
      setResults({
        strategy: "50/200 MA Crossover",
        market_returns: "+15.20%",
        strategy_returns: "+28.45%",
        max_drawdown: "-8.50%"
      });
      setRunning(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      
      {/* Header */}
      <header className="border-b border-white/5 bg-[#0e0e15]/50 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <button 
          onClick={() => router.push("/india")}
          className="flex items-center gap-2 text-xs text-slate-400 hover:text-white font-bold uppercase tracking-wider"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </button>
        <h2 className="text-md font-bold text-white">Quantitative Analytics & Backtester</h2>
      </header>

      {/* Main container */}
      <main className="max-w-4xl w-full mx-auto px-6 py-12 space-y-8 z-10 animate-in fade-in duration-300">
        
        <div className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Activity className="w-4 h-4 text-indigo-400" /> Define Backtest Parameters
          </h3>
          <form onSubmit={handleRunBacktest} className="grid md:grid-cols-3 gap-6 text-xs">
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-400 uppercase font-bold">Select Symbol</label>
              <input 
                type="text" 
                value={symbol}
                onChange={e => setSymbol(e.target.value.toUpperCase())}
                className="w-full px-4 py-3 rounded-2xl bg-black/40 border border-white/10 text-white"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-400 uppercase font-bold">Strategy Type</label>
              <select className="w-full px-4 py-3 rounded-2xl bg-black/40 border border-white/10 text-white">
                <option>Moving Average Crossover</option>
                <option>Mean Reversion (RSI)</option>
              </select>
            </div>
            <div className="flex items-end">
              <button 
                type="submit" 
                className="w-full bg-indigo-600 hover:bg-indigo-500 py-3 rounded-2xl font-bold uppercase tracking-wider flex items-center justify-center gap-2"
              >
                {running ? "Simulating Strategy..." : <><Play className="w-4 h-4" /> Run Simulation</>}
              </button>
            </div>
          </form>
        </div>

        {/* Results viz card */}
        {results && (
          <div className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-6 animate-in slide-in-from-bottom duration-300">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Strategy Returns Performance</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Benchmark (Buy & Hold)</div>
                <div className="text-lg font-black text-white mt-1">{results.market_returns}</div>
              </div>
              <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Strategy Return</div>
                <div className="text-lg font-black text-emerald-400 mt-1">{results.strategy_returns}</div>
              </div>
              <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Max Drawdown</div>
                <div className="text-lg font-black text-rose-400 mt-1">{results.max_drawdown}</div>
              </div>
            </div>
          </div>
        )}

      </main>

    </div>
  );
}
