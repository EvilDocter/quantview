"use client";

import React from "react";
import { ArrowLeft, Layers, TrendingUp, Sparkles, Activity } from "lucide-react";
import { useRouter } from "next/navigation";

export default function SectorsPortal() {
  const router = useRouter();

  const sectorOverview = [
    { name: "Automobile", count: 48, return_3m: "+12.45%", momentum: "High" },
    { name: "Information Technology", count: 52, return_3m: "+8.20%", momentum: "Medium" },
    { name: "Private Banking", count: 28, return_3m: "-4.80%", momentum: "Low" },
    { name: "Energy & Utilities", count: 35, return_3m: "+6.10%", momentum: "Medium" }
  ];

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
        <h2 className="text-md font-bold text-white">Sectoral Performance & Rotations</h2>
      </header>

      {/* Main container */}
      <main className="max-w-6xl w-full mx-auto px-6 py-12 flex flex-col lg:flex-row gap-8 z-10 animate-in fade-in duration-300">
        
        {/* Sector Cards list */}
        <section className="flex-1 space-y-6">
          <div className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Sector Overview matrices</h3>
            <div className="grid md:grid-cols-2 gap-4 text-xs">
              {sectorOverview.map((sec, i) => (
                <div key={i} className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                  <div className="flex justify-between items-center">
                    <h4 className="font-bold text-white text-sm">{sec.name}</h4>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">{sec.count} Assets</span>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="text-slate-400">3-Month Returns:</span>
                    <span className={`font-bold ${sec.return_3m.startsWith("+") ? "text-emerald-400" : "text-rose-400"}`}>
                      {sec.return_3m}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

      </main>

    </div>
  );
}
