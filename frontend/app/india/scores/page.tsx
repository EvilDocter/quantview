"use client";

import React from "react";
import { ArrowLeft, Brain, Shield, Award, Sparkles, TrendingUp } from "lucide-react";
import { useRouter } from "next/navigation";

export default function AIScoresPortal() {
  const router = useRouter();

  const scoreCategories = [
    { title: "Financial Health", score: "8.5/10", desc: "Low debt levels, high interest coverage parameters.", color: "text-emerald-400" },
    { title: "Competitive Moat", score: "7.8/10", desc: "Sustainable operating profit margin advantages.", color: "text-indigo-400" },
    { title: "Earnings Quality", score: "9.0/10", desc: "Strong accrual metrics matching cash inflows.", color: "text-purple-400" },
    { title: "Corporate Governance", score: "8.2/10", desc: "Excellent board independent variables.", color: "text-blue-400" }
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
        <h2 className="text-md font-bold text-white">AI Quantitative Scores</h2>
      </header>

      {/* Main container */}
      <main className="max-w-4xl w-full mx-auto px-6 py-12 space-y-12 z-10 animate-in fade-in duration-300">
        
        <div className="text-center space-y-4">
          <div className="inline-flex p-4 rounded-3xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Brain className="w-8 h-8" />
          </div>
          <h1 className="text-4xl font-black tracking-tight text-white">Company Quality Scoring Matrices</h1>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            10 fundamental metrics calculated and explained continuously using underlying P&L, balance sheets, and transcripts.
          </p>
        </div>

        {/* Scores Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {scoreCategories.map((sc, idx) => (
            <div key={idx} className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-3 backdrop-blur-md">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-white">{sc.title}</h3>
                <span className={`text-md font-black ${sc.color}`}>{sc.score}</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">{sc.desc}</p>
            </div>
          ))}
        </div>

      </main>

    </div>
  );
}
