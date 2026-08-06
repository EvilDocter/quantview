"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { 
  Search, Sparkles, ArrowUpRight, Sliders 
} from "lucide-react";
import IndiaNavbar from "@/components/IndiaNavbar";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL_INDIA || "http://localhost:8000";

interface StockResult {
  symbol: string;
  name: string;
  sector: string;
  price: number;
  pe: number;
  roe: number;
  debt_to_equity: number;
  mcap: number;
  div_yield: number;
}

export default function SmartScreener() {
  const router = useRouter();
  const [nlQuery, setNlQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<StockResult[]>([]);
  const [interpretation, setInterpretation] = useState("");
  const [peMax, setPeMax] = useState(30);
  const [roeMin, setRoeMin] = useState(15);

  const presets = [
    { title: "High ROE Leaders", desc: "high roe" },
    { title: "Undervalued IT", desc: "undervalued it stocks" },
    { title: "Top Banking", desc: "bank" }
  ];

  const fetchFiltered = async (pe: number, roe: number) => {
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/screener/filter`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pe_max: pe, roe_min: roe })
      });
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
        setInterpretation(`Showing stocks with PE ≤ ${pe} and ROE ≥ ${roe}%`);
      }
    } catch (err) {
      console.error("Filter error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiltered(peMax, roeMin);
  }, []);

  const handleNlSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nlQuery.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/screener/natural-language`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: nlQuery })
      });
      if (res.ok) {
        const data = await res.json();
        setResults(data.companies || []);
        setInterpretation(data.query_interpretation || "");
      }
    } catch (err) {
      console.error("NL screener error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      
      {/* Shared Navbar */}
      <IndiaNavbar />

      {/* Main container */}
      <main className="max-w-6xl w-full mx-auto px-6 py-8 flex flex-col lg:flex-row gap-8 z-10">
        
        {/* Left Side: Parameters & Filters */}
        <aside className="w-full lg:w-80 space-y-6 flex-shrink-0">
          
          {/* Preset Buttons */}
          <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" /> Presets
            </h3>
            <div className="space-y-2">
              {presets.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setNlQuery(p.desc);
                    fetch(`${BACKEND_URL}/api/v1/screener/natural-language`, {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ query: p.desc })
                    }).then(r => r.json()).then(d => {
                      setResults(d.companies || []);
                      setInterpretation(d.query_interpretation || "");
                    });
                  }}
                  className="w-full text-left p-3.5 rounded-2xl bg-white/[0.02] border border-white/5 text-xs hover:bg-white/[0.05] transition"
                >
                  <div className="font-bold text-white">{p.title}</div>
                  <div className="text-[10px] text-slate-400 mt-1">Query: "{p.desc}"</div>
                </button>
              ))}
            </div>
          </div>

          {/* Traditional metric filters */}
          <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-indigo-400" /> Filter Criteria
            </h3>
            <div className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <div className="flex justify-between">
                  <label className="text-[10px] text-slate-400 uppercase font-bold">PE Max</label>
                  <span className="text-white font-bold">{peMax}x</span>
                </div>
                <input 
                  type="range" 
                  min="5" 
                  max="60" 
                  value={peMax} 
                  onChange={e => {
                    const v = Number(e.target.value);
                    setPeMax(v);
                    fetchFiltered(v, roeMin);
                  }}
                  className="w-full accent-indigo-500" 
                />
              </div>
              <div className="space-y-1.5">
                <div className="flex justify-between">
                  <label className="text-[10px] text-slate-400 uppercase font-bold">ROE Min (%)</label>
                  <span className="text-white font-bold">{roeMin}%</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="40" 
                  value={roeMin} 
                  onChange={e => {
                    const v = Number(e.target.value);
                    setRoeMin(v);
                    fetchFiltered(peMax, v);
                  }}
                  className="w-full accent-indigo-500" 
                />
              </div>
            </div>
          </div>

        </aside>

        {/* Right Side: Search Box & Table Results */}
        <section className="flex-1 space-y-6">
          
          {/* Search Box */}
          <form onSubmit={handleNlSearch} className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-[20px] blur opacity-25 group-hover:opacity-30 transition duration-300" />
            <div className="relative bg-[#12121a] border border-white/10 rounded-[18px] flex items-center p-2">
              <Search className="w-4 h-4 text-slate-500 ml-4" />
              <input
                type="text"
                placeholder="Query metrics, e.g., 'Undervalued IT stocks with high ROE'..."
                value={nlQuery}
                onChange={e => setNlQuery(e.target.value)}
                className="w-full bg-transparent px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none"
              />
              <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider px-6 py-2.5 rounded-xl transition">
                {loading ? "Searching..." : "Screen"}
              </button>
            </div>
          </form>

          {/* Results table */}
          <div className="bg-white/[0.01] border border-white/5 rounded-3xl overflow-hidden p-6">
            <div className="flex justify-between items-center border-b border-white/5 pb-4 mb-4">
              <div>
                <h3 className="text-sm font-bold text-white">Screener Results</h3>
                {interpretation && <p className="text-[10px] text-indigo-400 mt-0.5">{interpretation}</p>}
              </div>
              <span className="text-[10px] text-slate-400 font-bold uppercase">{results.length} companies matched</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400">
                    <th className="py-3">Symbol</th>
                    <th className="py-3">Sector</th>
                    <th className="py-3">Price</th>
                    <th className="py-3">P/E Ratio</th>
                    <th className="py-3">ROE</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-300">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-slate-500">Screening live universe...</td>
                    </tr>
                  ) : results.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-slate-500">No stocks matched the criteria.</td>
                    </tr>
                  ) : results.map((item, idx) => (
                    <tr 
                      key={idx} 
                      onClick={() => router.push(`/india/company/${item.symbol}`)}
                      className="hover:bg-white/[0.02] cursor-pointer transition"
                    >
                      <td className="py-4 font-bold text-white flex items-center gap-1">
                        {item.symbol} <ArrowUpRight className="w-3 h-3 text-indigo-400" />
                      </td>
                      <td className="py-4">{item.sector}</td>
                      <td className="py-4 font-bold text-white">₹{item.price?.toLocaleString("en-IN") || "—"}</td>
                      <td className="py-4 font-semibold text-emerald-400">{item.pe ? `${item.pe.toFixed(1)}x` : "—"}</td>
                      <td className="py-4">{item.roe ? `${item.roe.toFixed(1)}%` : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </section>

      </main>

    </div>
  );
}
