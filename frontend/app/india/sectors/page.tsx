"use client";

import React from "react";
import { Layers, TrendingUp, Sparkles, ArrowUpRight } from "lucide-react";
import { useRouter } from "next/navigation";
import IndiaNavbar from "@/components/IndiaNavbar";

export default function SectorsPortal() {
  const router = useRouter();

  const sectorOverview = [
    { name: "Automobiles", count: 48, return_3m: "+12.45%", momentum: "High", top_stock: "TATAMOTORS" },
    { name: "IT Services", count: 52, return_3m: "+8.20%", momentum: "Medium", top_stock: "INFY" },
    { name: "Private Banking", count: 28, return_3m: "-4.80%", momentum: "Low", top_stock: "HDFCBANK" },
    { name: "Energy & Utilities", count: 35, return_3m: "+6.10%", momentum: "Medium", top_stock: "RELIANCE" },
    { name: "FMCG", count: 40, return_3m: "+3.15%", momentum: "Low", top_stock: "ITC" },
    { name: "Pharmaceuticals", count: 30, return_3m: "+7.80%", momentum: "High", top_stock: "SUNPHARMA" }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      
      {/* Shared Navbar */}
      <IndiaNavbar />

      {/* Main container */}
      <main className="max-w-6xl w-full mx-auto px-6 py-8 flex flex-col gap-8 z-10 animate-in fade-in duration-300">
        
        <div className="text-center space-y-2 max-w-2xl mx-auto">
          <h1 className="text-3xl font-black text-white">Sectoral Performance & Rotations</h1>
          <p className="text-xs text-slate-400">Track capital flows, 3-month momentum, and sector benchmark leaders across Indian equities.</p>
        </div>

        {/* Sector Cards list */}
        <section className="space-y-6">
          <div className="grid md:grid-cols-3 gap-6 text-xs">
            {sectorOverview.map((sec, i) => (
              <div 
                key={i} 
                onClick={() => router.push(`/india/company/${sec.top_stock}`)}
                className="p-6 rounded-3xl bg-white/[0.01] border border-white/5 hover:border-indigo-500/30 space-y-4 cursor-pointer transition-all duration-200 hover:-translate-y-1 shadow-xl backdrop-blur-md"
              >
                <div className="flex justify-between items-center">
                  <h3 className="font-bold text-white text-base">{sec.name}</h3>
                  <span className="text-[10px] text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full font-bold uppercase">{sec.momentum} Momentum</span>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between items-center text-slate-400">
                    <span>3-Month Return</span>
                    <span className={`font-bold ${sec.return_3m.startsWith("+") ? "text-emerald-400" : "text-rose-400"}`}>
                      {sec.return_3m}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-slate-400">
                    <span>Universe Assets</span>
                    <span className="text-white font-bold">{sec.count} Companies</span>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-white/5 text-slate-300">
                    <span>Sector Leader</span>
                    <span className="text-indigo-400 font-bold flex items-center gap-1">
                      {sec.top_stock} <ArrowUpRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

      </main>

    </div>
  );
}
