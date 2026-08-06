"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  Star, Bell, Plus, ArrowUpRight 
} from "lucide-react";
import IndiaNavbar from "@/components/IndiaNavbar";

export default function WatchlistPortal() {
  const router = useRouter();

  const [watchlist, setWatchlist] = useState([
    { symbol: "RELIANCE", name: "Reliance Industries", price: "₹2,450.00", change: "+2.15%", status: "up" },
    { symbol: "TATAMOTORS", name: "Tata Motors", price: "₹980.50", change: "+4.85%", status: "up" },
    { symbol: "TCS", name: "Tata Consultancy Services", price: "₹3,820.00", change: "-1.85%", status: "down" },
    { symbol: "INFY", name: "Infosys Limited", price: "₹1,560.20", change: "+3.20%", status: "up" },
    { symbol: "HDFCBANK", name: "HDFC Bank", price: "₹753.00", change: "+2.39%", status: "up" }
  ]);

  const [newSymbol, setNewSymbol] = useState("");

  const handleAddSymbol = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol.trim()) return;
    const sym = newSymbol.toUpperCase();
    setWatchlist([
      ...watchlist,
      { symbol: sym, name: `${sym} India`, price: "₹1,250.00", change: "+0.00%", status: "up" }
    ]);
    setNewSymbol("");
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      
      {/* Shared Navbar */}
      <IndiaNavbar />

      {/* Main container */}
      <main className="max-w-6xl w-full mx-auto px-6 py-8 flex flex-col lg:flex-row gap-8 z-10 animate-in fade-in duration-300">
        
        {/* Left Side: Watchlist Table */}
        <section className="flex-1 space-y-6">
          <div className="bg-white/[0.01] border border-white/5 rounded-[24px] p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-white/5 pb-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Star className="w-4 h-4 text-indigo-400" /> Active Watchlist ({watchlist.length})
              </h3>
              
              {/* Add Symbol Form */}
              <form onSubmit={handleAddSymbol} className="flex gap-2">
                <input
                  type="text"
                  placeholder="Add Ticker (e.g. SBIN)..."
                  value={newSymbol}
                  onChange={e => setNewSymbol(e.target.value)}
                  className="bg-black/40 border border-white/10 px-3 py-1.5 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none"
                />
                <button type="submit" className="flex items-center gap-1 text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-xl transition">
                  <Plus className="w-3.5 h-3.5" /> Add
                </button>
              </form>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400">
                    <th className="py-3">Symbol</th>
                    <th className="py-3">Company Name</th>
                    <th className="py-3">Price</th>
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
                      <td className="py-4 font-bold text-white flex items-center gap-1">
                        {asset.symbol} <ArrowUpRight className="w-3 h-3 text-indigo-400" />
                      </td>
                      <td className="py-4">{asset.name}</td>
                      <td className="py-4 font-bold text-white">{asset.price}</td>
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
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Bell className="w-4 h-4 text-indigo-400" /> Price Alerts
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Receive instant alerts when watched assets cross your price thresholds.
            </p>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center border-b border-white/5 pb-2">
                <span className="text-slate-400">Browser Push Notifications</span>
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
