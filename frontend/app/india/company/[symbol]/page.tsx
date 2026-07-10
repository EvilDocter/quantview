"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { 
  ArrowLeft, Activity, TrendingUp, AlertTriangle, Users, Layers, Newspaper, Calendar
} from "lucide-react";

export default function CompanyPortal() {
  const params = useParams();
  const router = useRouter();
  const symbol = params.symbol as string;

  const [activeTab, setActiveTab] = useState<"overview" | "financials" | "ratios" | "graph" | "news">("overview");
  const [selectedYear, setSelectedYear] = useState<number>(2026);

  // Load TradingView Widget
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;
    script.onload = () => {
      if (typeof window !== "undefined" && (window as any).TradingView) {
        new (window as any).TradingView.widget({
          width: "100%",
          height: 380,
          symbol: `BSE:${symbol}`,
          interval: "D",
          timezone: "Asia/Kolkata",
          theme: "dark",
          style: "1",
          locale: "en",
          toolbar_bg: "#f1f3f6",
          enable_publishing: false,
          hide_side_toolbar: false,
          allow_symbol_change: true,
          container_id: "tradingview_chart"
        });
      }
    };
    document.head.appendChild(script);
    return () => {
      script.remove();
    };
  }, [symbol]);

  const peers = [
    { name: "Reliance Industries", pe: "24.5", roe: "12.5%", price: "₹2,450.00" },
    { name: "Tata Motors", pe: "22.4", roe: "18.5%", price: "₹980.50" },
    { name: "Mahindra & Mahindra", pe: "26.1", roe: "15.8%", price: "₹2,120.00" }
  ];

  const newsItems = [
    { title: "Tata Motors Q4 net profit climbs 48% YoY; beats estimates.", sentiment: "positive", source: "Economic Times" },
    { title: "Promoters increase stake in Tata Motors as deliveries surge.", sentiment: "positive", source: "Mint" },
    { title: "Brokerages maintain bullish outlook post robust margins data.", sentiment: "positive", source: "Moneycontrol" }
  ];

  // Dynamic values depending on timeline selection
  const getTimelineMetrics = (year: number) => {
    const pe = (25.5 - (2026 - year) * 0.5).toFixed(1);
    const roe = (19.5 - (2026 - year) * 0.4).toFixed(1);
    const opm = (14.2 - (2026 - year) * 0.3).toFixed(1);
    return { pe, roe, opm };
  };

  const metrics = getTimelineMetrics(selectedYear);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      
      {/* Header */}
      <header className="border-b border-white/5 bg-[#0e0e15]/50 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <button 
          onClick={() => router.push("/india")}
          className="flex items-center gap-2 text-xs text-slate-400 hover:text-white font-bold uppercase tracking-wider"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Market
        </button>
        <div className="flex items-center gap-3">
          <span className="font-black text-xl tracking-tight text-white">{symbol}</span>
        </div>
      </header>

      {/* Main portal grid */}
      <main className="max-w-6xl w-full mx-auto px-6 py-8 space-y-8 flex-1 z-10 animate-in fade-in duration-300">
        
        {/* Stock info header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-white/[0.01] border border-white/5 rounded-3xl p-6 gap-4">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-white">{symbol} Industries</h1>
            <p className="text-xs text-slate-400 mt-1">Sector: Automobiles | Category: Large Cap</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-black text-white">₹980.50</div>
            <div className="text-xs text-emerald-400 font-bold mt-1">+₹45.50 (+4.85%)</div>
          </div>
        </div>

        {/* Timeline Slider Control */}
        <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-400" /> Historical Company Timeline
            </h3>
            <span className="text-xs font-black text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full">
              Viewing Year: {selectedYear}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-400 font-semibold">2016</span>
            <input
              type="range"
              min="2016"
              max="2026"
              value={selectedYear}
              onChange={e => setSelectedYear(Number(e.target.value))}
              className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
            <span className="text-xs text-white font-semibold">2026</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-2 border-b border-white/5 pb-2 overflow-x-auto">
          {["overview", "financials", "ratios", "graph", "news"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-6 py-2.5 rounded-full text-xs font-bold uppercase tracking-wider transition ${
                activeTab === tab 
                  ? "bg-indigo-600 text-white shadow-lg" 
                  : "text-slate-400 hover:text-white bg-white/[0.02]"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab 1: Overview */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Chart */}
            <div className="bg-white/[0.01] border border-white/5 rounded-3xl overflow-hidden p-6">
              <div id="tradingview_chart" className="w-full" />
            </div>

            {/* Quick Metrics (Dynamic depending on Year selector state) */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4 text-center">
                <div className="text-[10px] text-slate-400 uppercase font-bold">P/E Ratio</div>
                <div className="text-lg font-black text-white mt-1">{metrics.pe}x</div>
              </div>
              <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4 text-center">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Return on Equity</div>
                <div className="text-lg font-black text-white mt-1">{metrics.roe}%</div>
              </div>
              <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4 text-center">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Debt to Equity</div>
                <div className="text-lg font-black text-white mt-1">0.45x</div>
              </div>
              <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4 text-center">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Operating Margin</div>
                <div className="text-lg font-black text-white mt-1">{metrics.opm}%</div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Financials */}
        {activeTab === "financials" && (
          <div className="space-y-6 bg-white/[0.01] border border-white/5 rounded-3xl p-6">
            <h3 className="text-md font-bold text-white uppercase tracking-wider">Income Statement (Figures in ₹ Crores)</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400">
                    <th className="py-3">Financial Metric</th>
                    <th className="py-3">FY24</th>
                    <th className="py-3">FY23</th>
                    <th className="py-3">FY22</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-300">
                  <tr className="hover:bg-white/[0.02]">
                    <td className="py-4 font-bold text-white">Total Revenue</td>
                    <td className="py-4">₹124,500.50</td>
                    <td className="py-4">₹110,200.20</td>
                    <td className="py-4">₹98,100.10</td>
                  </tr>
                  <tr className="hover:bg-white/[0.02]">
                    <td className="py-4">Operating Expense</td>
                    <td className="py-4">₹108,550.00</td>
                    <td className="py-4">₹98,200.00</td>
                    <td className="py-4">₹88,000.00</td>
                  </tr>
                  <tr className="hover:bg-white/[0.02] font-bold text-emerald-400">
                    <td className="py-4">EBITDA</td>
                    <td className="py-4">₹15,950.50</td>
                    <td className="py-4">₹12,000.20</td>
                    <td className="py-4">₹10,100.10</td>
                  </tr>
                  <tr className="hover:bg-white/[0.02]">
                    <td className="py-4">Net Income</td>
                    <td className="py-4">₹9,800.50</td>
                    <td className="py-4">₹7,200.00</td>
                    <td className="py-4">₹6,100.00</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Ratios */}
        {activeTab === "ratios" && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Ratios Table */}
            <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
              <h3 className="text-md font-bold text-white uppercase tracking-wider">Historical Ratios</h3>
              <div className="space-y-3 text-xs">
                <div className="flex justify-between border-b border-white/5 pb-2">
                  <span className="text-slate-400">PE Ratio</span>
                  <span className="text-white font-bold">22.4x</span>
                </div>
                <div className="flex justify-between border-b border-white/5 pb-2">
                  <span className="text-slate-400">Return on Equity (ROE)</span>
                  <span className="text-white font-bold">18.5%</span>
                </div>
                <div className="flex justify-between border-b border-white/5 pb-2">
                  <span className="text-slate-400">Return on Asset (ROA)</span>
                  <span className="text-white font-bold">8.5%</span>
                </div>
                <div className="flex justify-between pb-2">
                  <span className="text-slate-400">Net Profit Margin</span>
                  <span className="text-white font-bold">7.87%</span>
                </div>
              </div>
            </div>

            {/* Peer Comparison */}
            <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
              <h3 className="text-md font-bold text-white uppercase tracking-wider">Peer Comparison</h3>
              <div className="space-y-4">
                {peers.map((peer, i) => (
                  <div key={i} className="flex justify-between items-center text-xs border-b border-white/5 pb-2 last:border-0 last:pb-0">
                    <span className="text-slate-300 font-semibold">{peer.name}</span>
                    <div className="text-right">
                      <span className="text-slate-400 pr-3">{peer.price}</span>
                      <span className="text-indigo-400 font-bold bg-indigo-500/10 px-2.5 py-1 rounded-full text-[10px]">
                        PE: {peer.pe}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 5: News */}
        {activeTab === "news" && (
          <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
            <h3 className="text-md font-bold text-white uppercase tracking-wider">Company News & Sentiment Feed</h3>
            <div className="space-y-4">
              {newsItems.map((item, i) => (
                <div key={i} className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex flex-col md:flex-row justify-between gap-3 text-xs">
                  <div className="space-y-1.5">
                    <h4 className="font-bold text-white leading-relaxed">{item.title}</h4>
                    <p className="text-[10px] text-slate-500">Source: {item.source}</p>
                  </div>
                  <span className="text-[10px] uppercase font-black text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full h-fit w-fit">
                    {item.sentiment}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

      </main>

    </div>
  );
}
