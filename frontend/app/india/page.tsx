"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useRouter } from "next/navigation";
import { 
  Search, Brain, Activity, TrendingUp, TrendingDown, 
  Layers, Users, ArrowUpRight, Flame, Sparkles
} from "lucide-react";
import IndiaNavbar from "@/components/IndiaNavbar";
import CopilotChat from "@/components/CopilotChat";

export default function IndianMarketHome() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [activeSymbol, setActiveSymbol] = useState("RELIANCE");
  const [showCopilot, setShowCopilot] = useState(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const quickPrompts = [
    "Analyze Reliance Industries",
    "Should I invest in Tata Motors?",
    "Compare Infosys vs TCS",
    "Explain VRL Logistics cash flow",
  ];

  const detectCompanySymbol = (q: string): string => {
    const qUpper = q.toUpperCase();
    
    // Explicit Alias Mappings
    if (qUpper.includes("INFOSYS") || qUpper.includes("INFY")) return "INFY";
    if (qUpper.includes("TATA CONSULTANCY") || qUpper.includes("TCS")) return "TCS";
    if (qUpper.includes("TATA MOTORS") || qUpper.includes("TATAMOTORS")) return "TATAMOTORS";
    if (qUpper.includes("RELIANCE")) return "RELIANCE";
    if (qUpper.includes("VRL LOGISTICS") || qUpper.includes("VRLLOG") || qUpper.includes("VRL")) return "VRLLOG";
    if (qUpper.includes("HINDUSTAN AERONAUTICS") || qUpper.includes("HAL")) return "HAL";
    if (qUpper.includes("HDFC BANK") || qUpper.includes("HDFCBANK")) return "HDFCBANK";
    if (qUpper.includes("ICICI BANK") || qUpper.includes("ICICIBANK")) return "ICICIBANK";
    if (qUpper.includes("STATE BANK") || qUpper.includes("SBIN")) return "SBIN";
    if (qUpper.includes("ZOMATO")) return "ZOMATO";
    if (qUpper.includes("SUZLON")) return "SUZLON";
    if (qUpper.includes("MRF")) return "MRF";
    if (qUpper.includes("CDSL")) return "CDSL";

    // Dynamic Extraction: Remove common prompt words and extract ticker candidate
    const cleaned = qUpper
      .replace(/\b(ANALYZE|EXPLAIN|COMPARE|VS|SHOULD|INVEST|IN|CASH|FLOW|MARGIN|VALUATION|SCENARIO|BULL|BEAR|FOR|STOCK|SHARE|COMPANY|LIMITED|LTD|WHAT|AM|I|MISSING|THE|TREND|AND)\b/g, " ")
      .trim();

    const matches = cleaned.match(/\b[A-Z0-9]{2,12}\b/g);
    if (matches && matches.length > 0) {
      return matches[0];
    }

    return "RELIANCE";
  };


  const handleSearch = (queryToSubmit?: string) => {
    const activeQuery = queryToSubmit || searchQuery;
    if (!activeQuery.trim()) return;

    const sym = detectCompanySymbol(activeQuery);
    setActiveSymbol(sym);
    setShowCopilot(true);

    // If searching explicit company query, navigate directly to company workspace
    if (activeQuery.toLowerCase().includes("analyze") || activeQuery.toLowerCase().includes("company") || activeQuery.length < 10) {
      router.push(`/india/company/${sym}`);
    }
  };

  const [indices, setIndices] = useState<any[]>([]);
  const [gainers, setGainers] = useState<any[]>([]);
  const [losers, setLosers] = useState<any[]>([]);
  const [sectors, setSectors] = useState<any[]>([]);
  const [fiiNet, setFiiNet] = useState("Loading...");
  const [diiNet, setDiiNet] = useState("Loading...");

  React.useEffect(() => {
    const fetchLiveData = async () => {
      // Use relative URL first (Next.js proxy -> backend:8001), then same-host direct
      const baseEndpoints = [
        "",
        `${window.location.protocol}//${window.location.hostname}:8001`,
      ];


      const fetchEndpoint = async (path: string) => {
        for (const base of baseEndpoints) {
          try {
            const url = base ? `${base}${path}` : path;
            const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
            if (res.ok) return await res.json();
          } catch (e) {}
        }
        return null;
      };

      const [indData, gainData, loseData, secData, fiiData] = await Promise.all([
        fetchEndpoint("/api/v1/market/indices"),
        fetchEndpoint("/api/v1/market/top-gainers"),
        fetchEndpoint("/api/v1/market/top-losers"),
        fetchEndpoint("/api/v1/market/sectors"),
        fetchEndpoint("/api/v1/market/fii-dii-activity"),
      ]);

      if (indData?.indices) setIndices(indData.indices);
      if (gainData?.gainers) setGainers(gainData.gainers);
      if (loseData?.losers) setLosers(loseData.losers);
      if (secData?.sectors) setSectors(secData.sectors);
      if (fiiData?.fii_net) setFiiNet(fiiData.fii_net);
      if (fiiData?.dii_net) setDiiNet(fiiData.dii_net);
    };

    fetchLiveData();
  }, []);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-indigo-500/5 rounded-full blur-[150px] pointer-events-none" />

      {/* Shared Navbar */}
      <IndiaNavbar />

      {/* Content wrapper */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-8 flex flex-col space-y-10 z-10">
        
        {/* Research search engine interface */}
        <div className="text-center space-y-6 max-w-3xl mx-auto pt-4">
          <div className="space-y-2">
            <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white">
              AI Financial Research Copilot
            </h1>
            <p className="text-xs md:text-sm text-slate-400">
              Persistent AI equity research copilot analyzing 5,000+ Indian listed equities with Baidu Unlimited-OCR.
            </p>
          </div>

          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-[24px] blur opacity-30 group-hover:opacity-40 transition duration-300" />
            <div className="relative bg-[#12121a] border border-white/10 rounded-[22px] flex items-center p-2 shadow-2xl">
              <Search className="w-5 h-5 text-slate-500 ml-4" />
              <input
                type="text"
                placeholder="Ask anything about Indian markets (e.g., 'Analyze Reliance Industries', 'VRLLOG')..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") handleSearch(); }}
                className="w-full bg-transparent px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none"
              />
              <button
                onClick={() => handleSearch()}
                disabled={isLoading}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-white font-bold text-xs uppercase tracking-wider px-6 py-3 rounded-xl transition shadow-lg"
              >
                Launch Copilot
              </button>
            </div>
          </div>

          {/* Quick Prompts */}
          <div className="flex flex-wrap justify-center gap-2">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setSearchQuery(prompt);
                  handleSearch(prompt);
                }}
                className="px-4 py-2 rounded-full bg-white/[0.03] border border-white/5 text-xs text-slate-400 hover:text-white hover:bg-white/[0.06] transition"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Phase IX Embedded Copilot Research Workspace */}
        {showCopilot && (
          <div className="w-full max-w-5xl mx-auto">
            <CopilotChat symbol={activeSymbol} companyName={activeSymbol} />
          </div>
        )}

        {/* Market Data Grid */}
        {!showCopilot && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Market Pulse Card */}
            <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4 text-indigo-400" /> Market Pulse
              </h3>
              <div className="space-y-3">
                {indices.length === 0 ? (
                  <p className="text-xs text-slate-500">Loading benchmark indices...</p>
                ) : (
                  indices.map((ind, i) => (
                    <div key={i} className="flex justify-between items-center border-b border-white/5 pb-2">
                      <span className="text-xs font-bold text-white">{ind.name}</span>
                      <span className={`text-xs font-mono font-bold ${ind.change >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                        {ind.price?.toLocaleString("en-IN")} ({ind.change >= 0 ? "+" : ""}{ind.change_pct}%)
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Top Gainers Card */}
            <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" /> Top Gainers
              </h3>
              <div className="space-y-3">
                {gainers.length === 0 ? (
                  <p className="text-xs text-slate-500">Loading market gainers...</p>
                ) : (
                  gainers.slice(0, 5).map((g, i) => (
                    <button
                      key={i}
                      onClick={() => router.push(`/india/company/${g.symbol}`)}
                      className="w-full flex justify-between items-center border-b border-white/5 pb-2 hover:bg-white/[0.02] transition text-left"
                    >
                      <span className="text-xs font-bold text-white">{g.symbol}</span>
                      <span className="text-xs font-mono font-bold text-emerald-400">+{g.change_pct}%</span>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Top Losers Card */}
            <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <TrendingDown className="w-4 h-4 text-rose-400" /> Top Losers
              </h3>
              <div className="space-y-3">
                {losers.length === 0 ? (
                  <p className="text-xs text-slate-500">Loading market losers...</p>
                ) : (
                  losers.slice(0, 5).map((l, i) => (
                    <button
                      key={i}
                      onClick={() => router.push(`/india/company/${l.symbol}`)}
                      className="w-full flex justify-between items-center border-b border-white/5 pb-2 hover:bg-white/[0.02] transition text-left"
                    >
                      <span className="text-xs font-bold text-white">{l.symbol}</span>
                      <span className="text-xs font-mono font-bold text-rose-400">{l.change_pct}%</span>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
