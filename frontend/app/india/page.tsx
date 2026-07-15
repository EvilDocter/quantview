"use client";

import React, { useState } from "react";
import { 
  Search, Brain, Activity, TrendingUp, TrendingDown, 
  Layers, Users, ArrowUpRight, Flame 
} from "lucide-react";

export default function IndianMarketHome() {
  const [searchQuery, setSearchQuery] = useState("");

  const quickPrompts = [
    "Should I invest in Tata Motors?",
    "Compare Infosys vs TCS.",
    "Explain Reliance Industries' Q4 profit margin.",
    "Find undervalued small-caps."
  ];
  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL_INDIA || "https://quantview-india.onrender.com";

  const [indices, setIndices] = useState<any[]>([
    { name: "NIFTY 50", value: "24,325.20", pct: "+1.26%", status: "up" },
    { name: "SENSEX", value: "79,850.50", pct: "+1.10%", status: "up" },
    { name: "BANK NIFTY", value: "52,100.10", pct: "-0.45%", status: "down" },
    { name: "NIFTY IT", value: "39,120.30", pct: "+1.68%", status: "up" }
  ]);

  const [gainers, setGainers] = useState<any[]>([
    { symbol: "TATAMOTORS", price: "₹980.50", change: "+4.85%" },
    { symbol: "INFY", price: "₹1,560.20", change: "+3.20%" },
    { symbol: "RELIANCE", price: "₹2,450.00", change: "+2.15%" }
  ]);

  const [losers, setLosers] = useState<any[]>([
    { symbol: "TCS", price: "₹3,820.00", change: "-1.85%" },
    { symbol: "HDFCBANK", price: "₹1,610.50", change: "-1.10%" },
    { symbol: "AXISBANK", price: "₹1,120.00", change: "-0.95%" }
  ]);

  const [fiiNet, setFiiNet] = useState("+₹550 Cr");
  const [diiNet, setDiiNet] = useState("+₹600 Cr");

  React.useEffect(() => {
    const fetchLiveData = async () => {
      try {
        // Fetch Live Indices
        const idxRes = await fetch(`${BACKEND_URL}/api/v1/market/indices`);
        if (idxRes.ok) {
          const data = await idxRes.json();
          if (data.indices && data.indices.length > 0) setIndices(data.indices);
        }

        // Fetch Top Gainers
        const gainRes = await fetch(`${BACKEND_URL}/api/v1/market/gainers`);
        if (gainRes.ok) {
          const data = await gainRes.json();
          if (data.gainers && data.gainers.length > 0) setGainers(data.gainers);
        }

        // Fetch Top Losers
        const loseRes = await fetch(`${BACKEND_URL}/api/v1/market/losers`);
        if (loseRes.ok) {
          const data = await loseRes.json();
          if (data.losers && data.losers.length > 0) setLosers(data.losers);
        }

        // Fetch FII/DII
        const instRes = await fetch(`${BACKEND_URL}/api/v1/market/fii-dii`);
        if (instRes.ok) {
          const data = await instRes.json();
          if (data.fii_net) setFiiNet(data.fii_net);
          if (data.dii_net) setDiiNet(data.dii_net);
        }
      } catch (err) {
        console.error("Failed to connect to India EOD tick API:", err);
      }
    };

    fetchLiveData();
    const interval = setInterval(fetchLiveData, 15000); // Poll EOD updates every 15s
    return () => clearInterval(interval);
  }, []);

  const sectors = [
    { name: "Automobile", perf: "+2.40%", trend: "up" },
    { name: "IT Services", perf: "+1.65%", trend: "up" },
    { name: "Private Banks", perf: "-0.85%", trend: "down" },
    { name: "Power", perf: "+0.90%", trend: "up" },
    { name: "FMCG", perf: "+0.15%", trend: "up" },
    { name: "Oil & Gas", perf: "+1.10%", trend: "up" }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      {/* Background Glow effects */}
      <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-indigo-500/5 rounded-full blur-[150px] pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-[400px] h-[400px] bg-purple-500/5 rounded-full blur-[120px] pointer-events-none" />

      {/* Header */}
      <header className="border-b border-white/5 bg-[#0e0e15]/50 backdrop-blur-md sticky top-0 z-40 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white shadow-lg">
            Q
          </div>
          <span className="font-black text-xl tracking-tight text-white">QuantView India</span>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-xs uppercase tracking-wider font-bold text-slate-400 hover:text-white transition">
            Research Portal
          </button>
          <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10" />
        </div>
      </header>

      {/* Content wrapper */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-12 flex flex-col space-y-12 z-10">
        
        {/* Research search engine interface */}
        <div className="text-center space-y-8 max-w-3xl mx-auto pt-6">
          <div className="space-y-3">
            <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white">
              AI Financial Research Platform
            </h2>
            <p className="text-sm text-slate-400">
              Assign comprehensive research tasks to autonomous agents running over deep financial data.
            </p>
          </div>

          {/* AI Search Bar */}
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-[24px] blur opacity-30 group-hover:opacity-40 transition duration-300" />
            <div className="relative bg-[#12121a] border border-white/10 rounded-[22px] flex items-center p-2 shadow-2xl">
              <Search className="w-5 h-5 text-slate-500 ml-4" />
              <input
                type="text"
                placeholder="Ask anything about Indian markets (e.g., 'Analyze Reliance Industries')..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none"
              />
              <button className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider px-6 py-3 rounded-xl transition shadow-lg">
                Ask Agent
              </button>
            </div>
          </div>

          {/* Quick Prompts */}
          <div className="flex flex-wrap justify-center gap-2">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => setSearchQuery(prompt)}
                className="px-4 py-2 rounded-full bg-white/[0.03] border border-white/5 text-xs text-slate-400 hover:text-white hover:bg-white/[0.06] transition"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Market Overview Dashboards Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          
          {/* Column 1: Market Pulse & Institutional */}
          <div className="space-y-6">
            {/* Index Levels */}
            <div className="bg-white/[0.02] border border-white/5 rounded-[24px] p-6 space-y-4 backdrop-blur-md">
              <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
                <Activity className="w-4 h-4 text-indigo-400" /> Market Pulse
              </h3>
              <div className="space-y-4">
                {indices.map((idx, i) => (
                  <div key={i} className="flex justify-between items-center border-b border-white/5 pb-2 last:border-0 last:pb-0">
                    <span className="text-xs text-slate-400 font-medium">{idx.name}</span>
                    <div className="text-right">
                      <div className="text-xs font-bold text-white">{idx.value}</div>
                      <div className={`text-[10px] font-semibold ${idx.status === "up" ? "text-emerald-400" : "text-rose-400"}`}>
                        {idx.pct}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* FII / DII net flows */}
            <div className="bg-white/[0.02] border border-white/5 rounded-[24px] p-6 space-y-4 backdrop-blur-md">
              <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
                <Users className="w-4 h-4 text-indigo-400" /> Institutional Activity
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-black/30 rounded-2xl p-3 border border-white/5 text-center">
                  <div className="text-[10px] text-slate-400 font-bold uppercase">FII Net Flow</div>
                  <div className="text-sm font-black text-emerald-400 mt-1">{fiiNet}</div>
                </div>
                <div className="bg-black/30 rounded-2xl p-3 border border-white/5 text-center">
                  <div className="text-[10px] text-slate-400 font-bold uppercase">DII Net Flow</div>
                  <div className="text-sm font-black text-emerald-400 mt-1">{diiNet}</div>
                </div>
              </div>
          </div>
          </div>

          {/* Column 2: Gainers & Losers */}
          <div className="space-y-6">
            {/* Top Gainers */}
            <div className="bg-white/[0.02] border border-white/5 rounded-[24px] p-6 space-y-4 backdrop-blur-md">
              <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
                <TrendingUp className="w-4 h-4 text-emerald-400" /> Top Gainers
              </h3>
              <div className="space-y-3">
                {gainers.map((stock, i) => (
                  <div key={i} className="flex justify-between items-center text-xs">
                    <span className="text-slate-300 font-semibold">{stock.symbol}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-400">{stock.price}</span>
                      <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full text-[10px]">
                        {stock.change}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Losers */}
            <div className="bg-white/[0.02] border border-white/5 rounded-[24px] p-6 space-y-4 backdrop-blur-md">
              <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
                <TrendingDown className="w-4 h-4 text-rose-400" /> Top Losers
              </h3>
              <div className="space-y-3">
                {losers.map((stock, i) => (
                  <div key={i} className="flex justify-between items-center text-xs">
                    <span className="text-slate-300 font-semibold">{stock.symbol}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-400">{stock.price}</span>
                      <span className="text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded-full text-[10px]">
                        {stock.change}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Column 3: Sector Heatmap & AI Insights */}
          <div className="space-y-6">
            {/* Sector Heatmap representation */}
            <div className="bg-white/[0.02] border border-white/5 rounded-[24px] p-6 space-y-4 backdrop-blur-md">
              <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
                <Layers className="w-4 h-4 text-indigo-400" /> Sector Performance
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {sectors.map((sec, i) => (
                  <div key={i} className="bg-black/20 rounded-xl p-3 border border-white/5 flex flex-col justify-between">
                    <span className="text-[10px] text-slate-400 truncate">{sec.name}</span>
                    <span className={`text-xs font-bold mt-1 ${sec.trend === "up" ? "text-emerald-400" : "text-rose-400"}`}>
                      {sec.perf}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Insights Card */}
            <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 rounded-[24px] p-6 space-y-3 backdrop-blur-md">
              <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
                <Brain className="w-4 h-4 text-indigo-400" /> Daily Market AI summary
              </h3>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Indian indices closed near record highs today supported by massive heavy-weights purchasing. Auto stocks rallied on sales numbers, while IT stocks stabilized despite foreign currency headwinds.
              </p>
            </div>
          </div>

        </div>

      </main>
    </div>
  );
}
