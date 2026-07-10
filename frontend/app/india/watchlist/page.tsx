"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  ArrowLeft, Star, Bell, History, 
  Settings, TrendingUp, Search, Plus 
} from "lucide-react";

export default function WatchlistPortal() {
  const router = useRouter();

  const [watchlist, setWatchlist] = useState([
    { symbol: "RELIANCE", name: "Reliance Industries", price: "₹2,450.00", change: "+2.15%", status: "up" },
    { symbol: "TATAMOTORS", name: "Tata Motors", price: "₹980.50", change: "+4.85%", status: "up" },
    { symbol: "TCS", name: "Tata Consultancy", price: "₹3,820.00", change: "-1.85%", status: "down" }
  ]);

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
        <h2 className="text-md font-bold text-white">Watchlists & Alerts Control</h2>
      </header>

      {/* Main container */}
      <main className="max-w-6xl w-full mx-auto px-6 py-12 flex flex-col lg:flex-row gap-8 z-10 animate-in fade-in duration-300">
        
        {/* Left Side: Watchlist Table */}
        <section className="flex-1 space-y-6">
          <div className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Star className="w-4 h-4 text-indigo-400" /> Watchlist Assets
              </h3>
              <button className="flex items-center gap-2 text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl transition">
                <Plus className="w-4 h-4" /> Add Asset
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400">
                    <th className="py-3">Symbol</th>
                    <th className="py-3">Company Name</th>
                    <th className="py-3">EOD Price</th>
                    <th className="py-3">Price Change</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-300">
                  {watchlist.map((asset, idx) => (
                    <tr 
                      key={idx} 
                      onClick={() => router.push(`/india/company/${asset.symbol}`)}
                      className="hover:bg-white/[0.02] cursor-pointer transition"
                    >
                      <td className="py-4 font-bold text-white">{asset.symbol}</td>
                      <td className="py-4">{asset.name}</td>
                      <td className="py-4">{asset.price}</td>
                      <td className={`py-4 font-bold ${asset.status === "up" ? "text-emerald-400" : "text-rose-400"}`}>
                        {asset.change}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Right Side: Alerts Configuration */}
        <aside className="w-full lg:w-80 space-y-6 flex-shrink-0">
          <div className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Bell className="w-4 h-4 text-indigo-400" /> Real-time Price Alerts
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Configure notifications to alert you when watched assets cross specific thresholds.
            </p>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center border-b border-white/5 pb-2">
                <span className="text-slate-400">Email Notifications</span>
                <span className="text-indigo-400 font-bold">Active</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Telegram Channel Alerts</span>
                <span className="text-slate-500 font-bold">Inactive</span>
              </div>
            </div>
          </div>
        </aside>

      </main>

    </div>
  );
}
