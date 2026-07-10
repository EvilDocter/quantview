"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  ArrowLeft, Search, Filter, Sparkles, 
  ArrowUpRight, Sliders, ChevronDown 
} from "lucide-react";

export default function SmartScreener() {
  const router = useRouter();
  const [nlQuery, setNlQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const presets = [
    { title: "High ROE Leaders", desc: "ROE > 20%, Debt/Equity < 0.5" },
    { title: "Undervalued Growth", desc: "PE < 15, Revenue Growth > 15%" },
    { title: "Dividend Aristocrats", desc: "Yield > 4%, Cash Flow > 0" }
  ];

  const results = [
    { symbol: "TCS", sector: "IT Services", pe: "28.5", roe: "35.2%", mcap: "₹13.5L Cr" },
    { symbol: "INFY", sector: "IT Services", pe: "24.2", roe: "28.5%", mcap: "₹7.5L Cr" },
    { symbol: "TATAMOTORS", sector: "Automobiles", pe: "22.4", roe: "18.5%", mcap: "₹3.5L Cr" }
  ];

  const handleNlSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!nlQuery.trim()) return;
    setLoading(true);
    setTimeout(() => setLoading(false), 1200);
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
        <h2 className="text-md font-bold text-white">Smart Fundamental Screener</h2>
      </header>

      {/* Main container */}
      <main className="max-w-6xl w-full mx-auto px-6 py-12 flex flex-col lg:flex-row gap-8 z-10">
        
        {/* Left Side: Parameters & Filters */}
        <aside className="w-full lg:w-80 space-y-6 flex-shrink-0">
          
          {/* Preset Buttons */}
          <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" /> Presets
            </h3>
            <div className="space-y-2">
              {presets.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => setNlQuery(p.desc)}
                  className="w-full text-left p-3.5 rounded-2xl bg-white/[0.02] border border-white/5 text-xs hover:bg-white/[0.05] transition"
                >
                  <div className="font-bold text-white">{p.title}</div>
                  <div className="text-[10px] text-slate-400 mt-1">{p.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Traditional metric filters */}
          <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-indigo-400" /> Filter Criteria
            </h3>
            <div className="space-y-3 text-xs">
              <div className="space-y-1.5">
                <label className="text-[10px] text-slate-400 uppercase font-bold">PE Ratio Maximum</label>
                <input type="range" min="5" max="100" defaultValue="25" className="w-full accent-indigo-500" />
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] text-slate-400 uppercase font-bold">ROE Minimum (%)</label>
                <input type="range" min="0" max="50" defaultValue="15" className="w-full accent-indigo-500" />
              </div>
            </div>
          </div>

        </aside>

        {/* Right Side: Search Box & Table Results */}
        <section className="flex-1 space-y-6">
          
          {/* Search Box */}
          <form onSubmit={handleNlSearch} className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-[20px] blur opacity-25 group-hover:opacity-30 transition duration-300" />
            <div className="relative bg-[#12121a] border border-white/10 rounded-[18px] flex items-center p-2">
              <Search className="w-4 h-4 text-slate-500 ml-4" />
              <input
                type="text"
                placeholder="Query metrics, e.g., 'Companies in IT sector with PE under 30'..."
                value={nlQuery}
                onChange={e => setNlQuery(e.target.value)}
                className="w-full bg-transparent px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none"
              />
              <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider px-6 py-2.5 rounded-xl transition">
                Filter
              </button>
            </div>
          </form>

          {/* Results table */}
          <div className="bg-white/[0.01] border border-white/5 rounded-3xl overflow-hidden p-6">
            <div className="flex justify-between items-center border-b border-white/5 pb-4 mb-4">
              <h3 className="text-sm font-bold text-white">Screener Output</h3>
              <span className="text-[10px] text-slate-400 font-bold uppercase">{results.length} companies matched</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400">
                    <th className="py-3">Symbol</th>
                    <th className="py-3">Sector</th>
                    <th className="py-3">P/E Ratio</th>
                    <th className="py-3">Return on Equity</th>
                    <th className="py-3">Market Cap</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-300">
                  {results.map((item, idx) => (
                    <tr 
                      key={idx} 
                      onClick={() => router.push(`/india/company/${item.symbol}`)}
                      className="hover:bg-white/[0.02] cursor-pointer transition"
                    >
                      <td className="py-4 font-bold text-white flex items-center gap-1">
                        {item.symbol} <ArrowUpRight className="w-3 h-3 text-indigo-400" />
                      </td>
                      <td className="py-4">{item.sector}</td>
                      <td className="py-4 font-semibold text-emerald-400">{item.pe}x</td>
                      <td className="py-4">{item.roe}</td>
                      <td className="py-4">{item.mcap}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </section>

      </main>

    </div>
  );
}
