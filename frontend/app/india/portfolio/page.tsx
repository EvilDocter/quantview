"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  ArrowLeft, Wallet, PieChart, Activity, 
  Sparkles, TrendingUp, RefreshCcw, Trash2 
} from "lucide-react";

export default function PortfolioDashboard() {
  const router = useRouter();
  
  const [holdings, setHoldings] = useState([
    { symbol: "RELIANCE", name: "Reliance Industries", qty: 10, buy: 2350.00, current: 2450.00 },
    { symbol: "TATAMOTORS", name: "Tata Motors", qty: 25, buy: 890.00, current: 980.50 }
  ]);

  const calculateTotals = () => {
    let totalInvested = 0;
    let currentValue = 0;

    holdings.forEach(h => {
      totalInvested += h.qty * h.buy;
      currentValue += h.qty * h.current;
    });

    const pnl = currentValue - totalInvested;
    const pnlPct = totalInvested > 0 ? (pnl / totalInvested) * 100 : 0;

    return {
      invested: totalInvested.toFixed(2),
      value: currentValue.toFixed(2),
      pnl: pnl.toFixed(2),
      pct: pnlPct.toFixed(2)
    };
  };

  const stats = calculateTotals();

  const handleAddAsset = (e: React.FormEvent) => {
    e.preventDefault();
    // In production, posts transaction to API /api/v1/portfolio
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
        <h2 className="text-md font-bold text-white">Capital Holdings Portfolio</h2>
      </header>

      {/* Main container */}
      <main className="max-w-6xl w-full mx-auto px-6 py-12 flex flex-col lg:flex-row gap-8 z-10 animate-in fade-in duration-300">
        
        {/* Left Side: Summary and Holdings */}
        <section className="flex-1 space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6">
              <div className="text-[10px] text-slate-400 uppercase font-bold">Total Invested</div>
              <div className="text-xl font-black text-white mt-1">₹{stats.invested}</div>
            </div>
            <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6">
              <div className="text-[10px] text-slate-400 uppercase font-bold">Current Valuation</div>
              <div className="text-xl font-black text-white mt-1">₹{stats.value}</div>
            </div>
            <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6">
              <div className="text-[10px] text-slate-400 uppercase font-bold">Total Profits (P&L)</div>
              <div className="text-xl font-black text-emerald-400 mt-1">₹{stats.pnl} ({stats.pct}%)</div>
            </div>
          </div>

          {/* Holdings List table */}
          <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Asset Allocation</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400">
                    <th className="py-3">Asset Symbol</th>
                    <th className="py-3">Quantity</th>
                    <th className="py-3">Buy Price</th>
                    <th className="py-3">EOD Price</th>
                    <th className="py-3">Unrealized profit</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-300">
                  {holdings.map((h, idx) => {
                    const profit = (h.current - h.buy) * h.qty;
                    return (
                      <tr key={idx} className="hover:bg-white/[0.02]">
                        <td className="py-4 font-bold text-white">{h.symbol}</td>
                        <td className="py-4">{h.qty}</td>
                        <td className="py-4">₹{h.buy.toFixed(2)}</td>
                        <td className="py-4">₹{h.current.toFixed(2)}</td>
                        <td className="py-4 font-bold text-emerald-400">₹{profit.toFixed(2)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Right Side: AI Allocation Advice */}
        <aside className="w-full lg:w-80 space-y-6 flex-shrink-0">
          <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 rounded-3xl p-6 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" /> AI Portfolio Intelligence
            </h3>
            <div className="space-y-3 text-xs leading-relaxed text-slate-300">
              <p>
                - Your portfolio beta is 0.95 relative to Nifty 50, showing market-average volatility.
              </p>
              <p>
                - Asset allocation is highly concentrated in Energy (52%) and Automobiles (48%). Consider diversifying into Banking or IT services.
              </p>
            </div>
          </div>
        </aside>

      </main>

    </div>
  );
}
