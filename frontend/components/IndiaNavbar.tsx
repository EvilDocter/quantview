"use client";

import React from "react";
import { useRouter, usePathname } from "next/navigation";
import { 
  Brain, Wallet, Sliders, Activity, 
  Star, Layers, Sparkles, ArrowLeft
} from "lucide-react";

export default function IndiaNavbar() {
  const router = useRouter();
  const pathname = usePathname();

  const navItems = [
    { label: "AI Research", path: "/india", icon: Brain },
    { label: "Broker Portfolio", path: "/india/portfolio", icon: Wallet },
    { label: "Smart Screener", path: "/india/screener", icon: Sliders },
    { label: "Quant Lab", path: "/india/quant", icon: Activity },
    { label: "Watchlist", path: "/india/watchlist", icon: Star },
    { label: "Sectors", path: "/india/sectors", icon: Layers },
  ];

  return (
    <header className="border-b border-white/5 bg-[#0e0e15]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between shadow-2xl">
      {/* Brand & Market Selector */}
      <div className="flex items-center gap-6">
        <button 
          onClick={() => router.push("/")}
          className="flex items-center gap-2.5 group text-left"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-indigo-600 flex items-center justify-center font-black text-white shadow-lg text-sm group-hover:scale-105 transition-transform duration-200">
            Q
          </div>
          <div>
            <div className="font-black text-sm tracking-tight text-white flex items-center gap-1.5">
              QuantView <span className="text-[10px] bg-indigo-500/20 text-indigo-400 font-bold px-2 py-0.5 rounded-full border border-indigo-500/30 uppercase">India</span>
            </div>
            <div className="text-[10px] text-slate-400">Autonomous Financial Intelligence</div>
          </div>
        </button>
      </div>

      {/* Primary Navigation Links */}
      <nav className="hidden md:flex items-center gap-1.5 bg-white/[0.02] border border-white/5 p-1.5 rounded-2xl">
        {navItems.map((item) => {
          const isActive = pathname === item.path || (item.path !== "/india" && pathname.startsWith(item.path));
          const Icon = item.icon;
          return (
            <button
              key={item.path}
              onClick={() => router.push(item.path)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all duration-200 ${
                isActive
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20"
                  : "text-slate-400 hover:text-white hover:bg-white/[0.04]"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.push("/india/portfolio")}
          className="hidden sm:flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs uppercase tracking-wider px-4 py-2 rounded-xl shadow-lg transition"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Connect Broker</span>
        </button>
      </div>
    </header>
  );
}
