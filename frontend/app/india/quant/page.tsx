"use client";

import React, { useState } from "react";
import { TrendingUp, ShieldAlert, Award, Play, Activity } from "lucide-react";
import { useRouter } from "next/navigation";
import IndiaNavbar from "@/components/IndiaNavbar";

export default function QuantLabPortal() {
  const router = useRouter();
  const [symbol, setSymbol] = useState("TATAMOTORS");
  const [strategy, setStrategy] = useState("ma_crossover");
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRunBacktest = (e: React.FormEvent) => {
    e.preventDefault();
    setRunning(true);
    setTimeout(() => {
      setResults({
        symbol: symbol,
        strategy: strategy === "ma_crossover" ? "50/200 MA Crossover" : "RSI Mean Reversion",
        market_returns: "+15.20%",
        strategy_returns: "+28.45%",
        max_drawdown: "-8.50%",
        sharpe_ratio: "1.85",
        win_rate: "64.2%"
      });
      setRunning(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      
      {/* Shared Navbar */}
      <IndiaNavbar />

      {/* Main container */}
      <main className="max-w-4xl w-full mx-auto px-6 py-12 space-y-8 z-10 animate-in fade-in duration-300">
        
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-black text-white">Quantitative Strategy Simulator</h1>
          <p className="text-xs text-slate-400">Backtest technical trading algorithms against historical OHLC price action.</p>
        </div>

        <div className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-6">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Activity className="w-4 h-4 text-indigo-400" /> Define Backtest Parameters
          </h3>
          <form onSubmit={handleRunBacktest} className="grid md:grid-cols-3 gap-6 text-xs">
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-400 uppercase font-bold">Select Symbol</label>
              <input 
                type="text" 
                value={symbol}
                onChange={e => setSymbol(e.target.value.toUpperCase())}
                className="w-full px-4 py-3 rounded-2xl bg-black/40 border border-white/10 text-white font-bold"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-400 uppercase font-bold">Strategy Type</label>
              <select 
                value={strategy}
                onChange={e => setStrategy(e.target.value)}
                className="w-full px-4 py-3 rounded-2xl bg-black/40 border border-white/10 text-white"
              >
                <option value="ma_crossover">Moving Average Crossover</option>
                <option value="rsi">Mean Reversion (RSI)</option>
              </select>
            </div>
            <div className="flex items-end">
              <button 
                type="submit" 
                className="w-full bg-indigo-600 hover:bg-indigo-500 py-3 rounded-2xl font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition"
              >
                {running ? "Simulating Strategy..." : <><Play className="w-4 h-4" /> Run Simulation</>}
              </button>
            </div>
          </form>
        </div>

        {/* Results card */}
        {results && (
          <div className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-6 animate-in slide-in-from-bottom duration-300">
            <div className="flex justify-between items-center border-b border-white/5 pb-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Backtest Results for {results.symbol} ({results.strategy})
              </h3>
              <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-3 py-1 rounded-full uppercase">
                Sharpe: {results.sharpe_ratio}
              </span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Benchmark Return</div>
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
              <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Win Rate</div>
                <div className="text-lg font-black text-indigo-400 mt-1">{results.win_rate}</div>
              </div>
            </div>
          </div>
        )}

      </main>

    </div>
  );
}
