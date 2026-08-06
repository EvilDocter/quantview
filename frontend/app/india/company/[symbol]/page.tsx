"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Activity, TrendingUp, Brain, Building2,
  BarChart3, Newspaper, DollarSign, Shield
} from "lucide-react";
import IndiaNavbar from "@/components/IndiaNavbar";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL_INDIA || "http://localhost:8000";

interface CompanyData {
  symbol: string;
  name: string;
  sector: string;
  industry: string;
  market_cap: number;
  current_price: number;
  previous_close: number;
  day_high: number;
  day_low: number;
  fifty_two_week_high: number;
  fifty_two_week_low: number;
  pe_ratio: number;
  eps: number;
  book_value: number;
  dividend_yield: number;
  roe: number;
  debt_to_equity: number;
  revenue: number;
  net_income: number;
  ebitda: number;
  summary: string;
}

interface NewsItem {
  title: string;
  url: string;
  source: string;
  date: string;
  body: string;
}

function formatCurrency(val: number): string {
  if (!val) return "—";
  if (val >= 1e12) return `₹${(val / 1e12).toFixed(2)}T`;
  if (val >= 1e9) return `₹${(val / 1e9).toFixed(2)}B`;
  if (val >= 1e7) return `₹${(val / 1e7).toFixed(2)} Cr`;
  if (val >= 1e5) return `₹${(val / 1e5).toFixed(2)} L`;
  return `₹${val.toLocaleString("en-IN")}`;
}

function formatNum(val: number | undefined, suffix = ""): string {
  if (!val || val === 0) return "—";
  return `${Number(val).toFixed(2)}${suffix}`;
}

export default function CompanyPortal() {
  const params = useParams();
  const router = useRouter();
  const symbol = (params.symbol as string)?.toUpperCase() || "";

  const [company, setCompany] = useState<CompanyData | null>(null);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [aiReport, setAiReport] = useState<string>("");
  const [aiLoading, setAiLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "financials" | "news" | "ai">("overview");
  const [loading, setLoading] = useState(true);

  // Load TradingView Widget
  useEffect(() => {
    if (activeTab !== "overview") return;
    const container = document.getElementById("tradingview_chart");
    if (!container) return;
    container.innerHTML = "";
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
          toolbar_bg: "#0a0a0f",
          enable_publishing: false,
          hide_side_toolbar: false,
          allow_symbol_change: true,
          container_id: "tradingview_chart",
        });
      }
    };
    document.head.appendChild(script);
    return () => { script.remove(); };
  }, [symbol, activeTab]);

  // Fetch company data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [compRes, newsRes] = await Promise.all([
          fetch(`${BACKEND_URL}/api/v1/company/${symbol}`),
          fetch(`${BACKEND_URL}/api/v1/company/${symbol}/news?limit=5`),
        ]);
        if (compRes.ok) setCompany(await compRes.json());
        if (newsRes.ok) {
          const data = await newsRes.json();
          setNews(data.news || []);
        }
      } catch (err) {
        console.error("Failed to fetch company data:", err);
      } finally {
        setLoading(false);
      }
    };
    if (symbol) fetchData();
  }, [symbol]);

  const handleAiAnalysis = async () => {
    setAiLoading(true);
    setActiveTab("ai");
    setAiReport("Analyzing...");
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/ai/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: `Deep analysis of ${symbol} stock` }),
      });
      if (res.ok) {
        const data = await res.json();
        setAiReport(data.answer || "No report generated.");
      } else {
        setAiReport("Failed to generate AI report.");
      }
    } catch {
      setAiReport("Connection error. Is the backend running?");
    } finally {
      setAiLoading(false);
    }
  };

  const priceChange = company ? company.current_price - company.previous_close : 0;
  const pricePct = company && company.previous_close ? (priceChange / company.previous_close) * 100 : 0;

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-indigo-500/5 rounded-full blur-[150px] pointer-events-none" />

      {/* Shared Navbar */}
      <IndiaNavbar />

      <main className="max-w-6xl w-full mx-auto px-6 py-8 space-y-8 flex-1 z-10">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-pulse text-slate-400">Loading company data...</div>
          </div>
        ) : (
          <>
            {/* Price header card */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-white/[0.01] border border-white/5 rounded-3xl p-6 gap-4">
              <div>
                <h1 className="text-3xl font-black tracking-tight text-white">
                  {company?.name || symbol}
                </h1>
                <p className="text-xs text-slate-400 mt-1">
                  {company?.sector || "—"} • {company?.industry || "—"} • MCap: {formatCurrency(company?.market_cap || 0)}
                </p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-black text-white">
                  ₹{company?.current_price?.toLocaleString("en-IN") || "—"}
                </div>
                <div className={`text-xs font-bold mt-1 ${priceChange >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                  {priceChange >= 0 ? "+" : ""}₹{priceChange.toFixed(2)} ({pricePct >= 0 ? "+" : ""}{pricePct.toFixed(2)}%)
                </div>
              </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex gap-2 border-b border-white/5 pb-2 overflow-x-auto">
              {(["overview", "financials", "news", "ai"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => {
                    setActiveTab(tab);
                    if (tab === "ai" && !aiReport) handleAiAnalysis();
                  }}
                  className={`px-6 py-2.5 rounded-full text-xs font-bold uppercase tracking-wider transition ${
                    activeTab === tab
                      ? "bg-indigo-600 text-white shadow-lg"
                      : "text-slate-400 hover:text-white bg-white/[0.02]"
                  }`}
                >
                  {tab === "ai" ? "AI Analysis" : tab}
                </button>
              ))}
            </div>

            {/* Tab: Overview */}
            {activeTab === "overview" && (
              <div className="space-y-6">
                <div className="bg-white/[0.01] border border-white/5 rounded-3xl overflow-hidden p-6">
                  <div id="tradingview_chart" className="w-full" />
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: "P/E Ratio", value: formatNum(company?.pe_ratio, "x") },
                    { label: "EPS", value: formatNum(company?.eps) },
                    { label: "ROE", value: company?.roe ? `${(company.roe * 100).toFixed(1)}%` : "—" },
                    { label: "Debt/Equity", value: formatNum(company?.debt_to_equity) },
                    { label: "Book Value", value: formatNum(company?.book_value) },
                    { label: "Div Yield", value: company?.dividend_yield ? `${(company.dividend_yield * 100).toFixed(2)}%` : "—" },
                    { label: "52W High", value: company?.fifty_two_week_high ? `₹${company.fifty_two_week_high.toLocaleString("en-IN")}` : "—" },
                    { label: "52W Low", value: company?.fifty_two_week_low ? `₹${company.fifty_two_week_low.toLocaleString("en-IN")}` : "—" },
                  ].map((item, i) => (
                    <div key={i} className="bg-white/[0.02] border border-white/5 rounded-2xl p-4 text-center">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">{item.label}</div>
                      <div className="text-lg font-black text-white mt-1">{item.value}</div>
                    </div>
                  ))}
                </div>

                {company?.summary && (
                  <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-3">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-indigo-400" /> About {company.name}
                    </h3>
                    <p className="text-sm text-slate-300 leading-relaxed">{company.summary}</p>
                  </div>
                )}
              </div>
            )}

            {/* Tab: Financials */}
            {activeTab === "financials" && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { label: "Revenue", value: formatCurrency(company?.revenue || 0), icon: DollarSign },
                    { label: "Net Income", value: formatCurrency(company?.net_income || 0), icon: BarChart3 },
                    { label: "EBITDA", value: formatCurrency(company?.ebitda || 0), icon: TrendingUp },
                  ].map((item, i) => (
                    <div key={i} className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-2">
                      <div className="flex items-center gap-2">
                        <item.icon className="w-4 h-4 text-indigo-400" />
                        <span className="text-xs text-slate-400 uppercase font-bold">{item.label}</span>
                      </div>
                      <div className="text-2xl font-black text-white">{item.value}</div>
                    </div>
                  ))}
                </div>

                <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <Shield className="w-4 h-4 text-indigo-400" /> Key Ratios
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                    {[
                      { label: "P/E Ratio", value: formatNum(company?.pe_ratio, "x") },
                      { label: "EPS", value: `₹${formatNum(company?.eps)}` },
                      { label: "Book Value", value: `₹${formatNum(company?.book_value)}` },
                      { label: "Debt/Equity", value: formatNum(company?.debt_to_equity) },
                      { label: "ROE", value: company?.roe ? `${(company.roe * 100).toFixed(1)}%` : "—" },
                      { label: "Div Yield", value: company?.dividend_yield ? `${(company.dividend_yield * 100).toFixed(2)}%` : "—" },
                    ].map((item, i) => (
                      <div key={i} className="flex justify-between border-b border-white/5 pb-2">
                        <span className="text-slate-400">{item.label}</span>
                        <span className="text-white font-bold">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Tab: News */}
            {activeTab === "news" && (
              <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Newspaper className="w-4 h-4 text-indigo-400" /> Latest News
                </h3>
                {news.length === 0 ? (
                  <p className="text-sm text-slate-400">No news available.</p>
                ) : (
                  <div className="space-y-4">
                    {news.map((item, i) => (
                      <a
                        key={i}
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] transition"
                      >
                        <h4 className="font-bold text-white text-sm leading-relaxed">{item.title}</h4>
                        <p className="text-[10px] text-slate-500 mt-1">{item.source} • {item.date}</p>
                        {item.body && <p className="text-xs text-slate-400 mt-2 line-clamp-2">{item.body}</p>}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Tab: AI Analysis */}
            {activeTab === "ai" && (
              <div className="w-full bg-[#12121a]/80 border border-indigo-500/20 rounded-3xl p-8 shadow-2xl backdrop-blur-md relative overflow-hidden">
                {aiLoading && (
                  <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 animate-pulse" />
                )}
                <div className="flex items-center justify-between mb-6 border-b border-white/5 pb-4">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-wider">
                    <Brain className="w-5 h-5 text-indigo-400" /> AI Deep Analysis
                  </h3>
                  <button
                    onClick={handleAiAnalysis}
                    disabled={aiLoading}
                    className="text-[10px] uppercase tracking-wider font-bold px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-white transition"
                  >
                    {aiLoading ? "Analyzing..." : "Re-analyze"}
                  </button>
                </div>
                <div className="prose prose-invert prose-indigo max-w-none text-slate-200 text-sm leading-relaxed">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{aiReport}</ReactMarkdown>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
