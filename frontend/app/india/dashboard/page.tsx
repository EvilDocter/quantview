"use client";

import React from "react";
import { ArrowLeft, Layers, ShieldAlert, Brain, TrendingUp } from "lucide-react";
import { useRouter } from "next/navigation";

export default function InstitutionalDashboard() {
  const router = useRouter();

  const comparisonMatrix = [
    { metric: "Revenue (INR Cr)", tcs: "₹245,300", infy: "₹185,400", reliance: "₹910,200" },
    { metric: "Operating Margin", tcs: "24.5%", infy: "21.2%", reliance: "16.8%" },
    { metric: "ROE (%)", tcs: "45.2%", infy: "30.4%", reliance: "12.8%" },
    { metric: "Debt/Equity Ratio", tcs: "0.02x", infy: "0.05x", reliance: "0.85x" }
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
        <h2 className="text-md font-bold text-white">Institutional Analytics Portal</h2>
      </header>

      {/* Main container */}
      <main className="max-w-6xl w-full mx-auto px-6 py-12 space-y-8 z-10 animate-in fade-in duration-300">
        
        {/* Comparison matrix */}
        <div className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" /> Sector Peer Comparison Matrix
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-white/10 text-slate-400">
                  <th className="py-3">Financial Metric</th>
                  <th className="py-3">TCS</th>
                  <th className="py-3">Infosys</th>
                  <th className="py-3">Reliance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                {comparisonMatrix.map((row, idx) => (
                  <tr key={idx} className="hover:bg-white/[0.02]">
                    <td className="py-4 font-bold text-white">{row.metric}</td>
                    <td className="py-4">{row.tcs}</td>
                    <td className="py-4">{row.infy}</td>
                    <td className="py-4">{row.reliance}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </main>

    </div>
  );
}
