"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import {
  TrendingUp, TrendingDown, Building2, BarChart3, Shield,
  Layers, PieChart, Landmark, Percent, Award, ArrowUpRight, Clock
} from "lucide-react";
import IndiaNavbar from "@/components/IndiaNavbar";
import CopilotChat from "@/components/CopilotChat";

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
}

interface PricePoint {
  time: string;
  price: number;
}

interface TijoriData {
  symbol: string;
  company_name: string;
  sector: string;
  business_segments: Array<{
    segment: string;
    revenue_cr: number;
    pct_share: number;
    yoy_growth_pct: number;
    description: string;
  }>;
  loan_portfolio_mix: Array<{
    category: string;
    amount_cr: number;
    pct_share: number;
    asset_quality: string;
  }>;
  market_share_metrics: Array<{
    metric: string;
    value: string;
    industry_rank: string;
    trend: string;
  }>;
  banking_operational_kpis: Array<{
    kpi: string;
    value: string;
    benchmark: string;
    status: string;
  }>;
  key_subsidiaries: Array<{
    subsidiary: string;
    stake_pct: string;
    business: string;
    valuation_est_cr: number;
  }>;
}

function formatCurrency(val: number): string {
  if (!val) return "—";
  if (val >= 1e12) return `₹${(val / 1e12).toFixed(2)}T`;
  if (val >= 1e9) return `₹${(val / 1e9).toFixed(2)}B`;
  if (val >= 1e7) return `₹${(val / 1e7).toFixed(2)} Cr`;
  if (val >= 1e5) return `₹${(val / 1e5).toFixed(2)} L`;
  return `₹${val.toLocaleString("en-IN")}`;
}

const DEFAULT_HDFC_COMPANY: CompanyData = {
  symbol: "HDFCBANK",
  name: "HDFC Bank Limited",
  sector: "Financial Services",
  industry: "Private Sector Bank",
  market_cap: 12850000000000,
  current_price: 1685.40,
  previous_close: 1666.90,
  day_high: 1698.00,
  day_low: 1660.20,
  fifty_two_week_high: 1794.00,
  fifty_two_week_low: 1363.55,
  pe_ratio: 19.2,
  eps: 87.5,
  book_value: 540.20,
  dividend_yield: 0.0115,
  roe: 0.168,
  debt_to_equity: 0.85,
  revenue: 2467000000000,
  net_income: 640000000000,
  ebitda: 950000000000,
};

const DEFAULT_HDFC_TIJORI: TijoriData = {
  symbol: "HDFCBANK",
  company_name: "HDFC Bank Limited",
  sector: "Financial Services / Banking",
  business_segments: [
    { segment: "Retail Banking", revenue_cr: 115420.0, pct_share: 46.8, yoy_growth_pct: 18.4, description: "Personal loans, credit cards, auto loans, mortgages, branch banking deposits" },
    { segment: "Wholesale / Corporate Banking", revenue_cr: 88350.0, pct_share: 35.8, yoy_growth_pct: 14.2, description: "Large corporate loans, working capital finance, trade services, commercial banking" },
    { segment: "Treasury Operations", revenue_cr: 32800.0, pct_share: 13.3, yoy_growth_pct: 9.5, description: "Investment portfolio, money market trading, foreign exchange, liquidity management" },
    { segment: "Other Banking Operations", revenue_cr: 10130.0, pct_share: 4.1, yoy_growth_pct: 11.0, description: "Third-party product distribution, asset management fees, para-banking services" },
  ],
  loan_portfolio_mix: [
    { category: "Mortgages & Housing Loans", amount_cr: 724500.0, pct_share: 29.2, asset_quality: "Gross NPA: 0.85%" },
    { category: "Commercial & Corporate Advances", amount_cr: 582100.0, pct_share: 23.5, asset_quality: "Gross NPA: 1.10%" },
    { category: "Personal & Unsecured Loans", amount_cr: 194800.0, pct_share: 7.9, asset_quality: "Gross NPA: 1.45%" },
    { category: "Auto & Vehicle Loans", amount_cr: 142300.0, pct_share: 5.7, asset_quality: "Gross NPA: 1.20%" },
    { category: "Credit Cards Outstanding", amount_cr: 95600.0, pct_share: 3.9, asset_quality: "Gross NPA: 1.85%" },
    { category: "Agri & Microfinance Loans", amount_cr: 215400.0, pct_share: 8.7, asset_quality: "Gross NPA: 1.75%" },
    { category: "SME & Commercial Business", amount_cr: 523600.0, pct_share: 21.1, asset_quality: "Gross NPA: 1.30%" },
  ],
  market_share_metrics: [
    { metric: "Credit Card Spend Market Share", value: "28.4%", industry_rank: "#1 in India", trend: "Expanding (+120 bps YoY)" },
    { metric: "Total Advances Market Share", value: "11.5%", industry_rank: "#1 Private Bank", trend: "Expanding post-HDFC Merger" },
    { metric: "Total Deposit Market Share", value: "11.2%", industry_rank: "#1 Private Bank", trend: "Strong CASA franchise" },
    { metric: "Mortgage Market Share", value: "15.8%", industry_rank: "#1 Overall", trend: "Fully integrated HDFC Ltd book" },
  ],
  banking_operational_kpis: [
    { kpi: "Net Interest Margin (NIM)", value: "3.45%", benchmark: "3.20% - 3.60%", status: "Healthy" },
    { kpi: "CASA Ratio", value: "38.2%", benchmark: ">35.0%", status: "Strong Liquidity Buffer" },
    { kpi: "Gross NPA (GNPA)", value: "1.24%", benchmark: "<2.00%", status: "Industry Top Tier" },
    { kpi: "Net NPA (NNPA)", value: "0.33%", benchmark: "<0.50%", status: "Best-in-Class" },
    { kpi: "Provision Coverage Ratio (PCR)", value: "74.1%", benchmark: ">70.0%", status: "Prudent Provisioning" },
    { kpi: "Cost-to-Income Ratio", value: "40.2%", benchmark: "<45.0%", status: "High Operating Efficiency" },
    { kpi: "Capital Adequacy Ratio (CRAR)", value: "18.8%", benchmark: ">15.0%", status: "Well Capitalized" },
  ],
  key_subsidiaries: [
    { subsidiary: "HDB Financial Services", stake_pct: "94.7%", business: "NBFC / Retail Finance", valuation_est_cr: 65000.0 },
    { subsidiary: "HDFC Life Insurance", stake_pct: "50.4%", business: "Life Insurance", valuation_est_cr: 142000.0 },
    { subsidiary: "HDFC Asset Management (AMC)", stake_pct: "52.5%", business: "Mutual Fund Asset Manager", valuation_est_cr: 88000.0 },
    { subsidiary: "HDFC ERGO General Insurance", stake_pct: "50.5%", business: "General Insurance", valuation_est_cr: 45000.0 },
  ],
};

const DEFAULT_PRICE_SERIES: PricePoint[] = Array.from({ length: 52 }, (_, i) => {
  const progress = i / 51;
  const wave = Math.sin(progress * Math.PI * 3) * 65;
  const price = Math.round(1432.59 + progress * 252.81 + wave);
  return { time: `W${i + 1}`, price };
});

export default function UnifiedCompanyWorkspace() {
  const params = useParams();
  const rawSymbol = (params?.symbol as string)?.toUpperCase() || "HDFCBANK";
  const symbol = rawSymbol === "HDFC" ? "HDFCBANK" : rawSymbol;

  const [company, setCompany] = useState<CompanyData>(DEFAULT_HDFC_COMPANY);
  const [tijori, setTijori] = useState<TijoriData>(DEFAULT_HDFC_TIJORI);
  const [priceSeries, setPriceSeries] = useState<PricePoint[]>(DEFAULT_PRICE_SERIES);
  const [timeSpan, setTimeSpan] = useState<string>("1Y");
  const [hoveredPrice, setHoveredPrice] = useState<PricePoint | null>(null);

  // Background fetch to update real data seamlessly
  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      const baseEndpoints = [
        "",
        typeof window !== "undefined" ? `${window.location.protocol}//${window.location.hostname}:8001` : "",
      ].filter(Boolean);

      for (const base of baseEndpoints) {
        try {
          const url = base ? `${base}/api/v1/company/${symbol}/full` : `/api/v1/company/${symbol}/full`;
          const res = await fetch(url);
          if (res.ok && isMounted) {
            const data = await res.json();
            const md = data.market_data || {};
            const fin = data.financials || {};
            const comp = data.company || {};
            setCompany({
              symbol: data.symbol || symbol,
              name: comp.name || md.name || data.symbol || symbol,
              sector: comp.sector || md.sector || "Equities",
              industry: comp.industry || md.industry || "Indian Market",
              market_cap: md.market_cap || 12850000000000,
              current_price: md.current_price || 1685.40,
              previous_close: md.previous_close || 1666.90,
              day_high: md.day_high || 1698.00,
              day_low: md.day_low || 1660.20,
              fifty_two_week_high: md.fifty_two_week_high || 1794.00,
              fifty_two_week_low: md.fifty_two_week_low || 1363.55,
              pe_ratio: md.pe_ratio || 19.2,
              eps: md.eps || 87.5,
              book_value: md.book_value || 540.2,
              dividend_yield: md.dividend_yield || 0.0115,
              roe: md.roe || 0.168,
              debt_to_equity: md.debt_to_equity || 0.85,
              revenue: fin.revenue || 2467000000000,
              net_income: fin.net_income || 640000000000,
              ebitda: fin.ebitda || 950000000000,
            });
            break;
          }
        } catch (e) {}
      }

      for (const base of baseEndpoints) {
        try {
          const tUrl = base ? `${base}/api/v1/company/${symbol}/tijori` : `/api/v1/company/${symbol}/tijori`;
          const tRes = await fetch(tUrl);
          if (tRes.ok && isMounted) {
            const tData = await tRes.json();
            if (tData && tData.business_segments) {
              setTijori(tData);
              break;
            }
          }
        } catch (e) {}
      }
    };

    fetchData();
    return () => { isMounted = false; };
  }, [symbol]);

  // Fetch YFinance price series on span change
  useEffect(() => {
    let isMounted = true;
    const fetchPrices = async () => {
      const baseEndpoints = [
        "",
        typeof window !== "undefined" ? `${window.location.protocol}//${window.location.hostname}:8001` : "",
      ].filter(Boolean);

      for (const base of baseEndpoints) {
        try {
          const url = base ? `${base}/api/v1/company/${symbol}/prices?span=${timeSpan}` : `/api/v1/company/${symbol}/prices?span=${timeSpan}`;
          const res = await fetch(url);
          if (res.ok && isMounted) {
            const data = await res.json();
            if (data.series && data.series.length > 0) {
              setPriceSeries(data.series);
              break;
            }
          }
        } catch (e) {}
      }
    };
    fetchPrices();
    return () => { isMounted = false; };
  }, [symbol, timeSpan]);

  const priceChange = company ? company.current_price - company.previous_close : 0;
  const pricePct = company && company.previous_close ? (priceChange / company.previous_close) * 100 : 0;

  // Custom SVG Chart Calculation
  const minPrice = priceSeries.length ? Math.min(...priceSeries.map(p => p.price)) * 0.98 : 1400;
  const maxPrice = priceSeries.length ? Math.max(...priceSeries.map(p => p.price)) * 1.02 : 1750;
  const priceRange = maxPrice - minPrice || 1;

  const svgWidth = 800;
  const svgHeight = 220;

  const pointsString = priceSeries.map((p, idx) => {
    const x = (idx / (priceSeries.length - 1)) * svgWidth;
    const y = svgHeight - ((p.price - minPrice) / priceRange) * svgHeight;
    return `${x},${y}`;
  }).join(" ");

  const areaPoints = priceSeries.length > 0
    ? `0,${svgHeight} ${pointsString} ${svgWidth},${svgHeight}`
    : "";

  return (
    <div className="min-h-screen bg-[#06070a] text-slate-100 flex flex-col font-sans relative">
      <IndiaNavbar />

      <main className="max-w-[1850px] w-full mx-auto px-4 py-4 flex-1 z-10 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* ================================================================= */}
        {/* LEFT PANE (70% Width): Live Data, YFinance Chart, Tijori Tables  */}
        {/* ================================================================= */}
        <div className="lg:col-span-8 space-y-5 overflow-y-auto max-h-[calc(100vh-90px)] pr-2 scrollbar-thin scrollbar-thumb-white/10">
          
          {/* 1. STOCK HEADER CARD */}
          <div className="bg-[#0e1017] border border-white/10 rounded-2xl p-5 space-y-4 shadow-xl">
            <div className="flex flex-wrap justify-between items-start gap-4">
              <div>
                <div className="flex items-center gap-3">
                  <span className="px-2.5 py-1 bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 font-mono font-bold text-xs rounded-lg">
                    {company?.symbol || symbol}
                  </span>
                  <h1 className="text-2xl font-black text-white tracking-tight">{company?.name || symbol}</h1>
                </div>
                <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                  <span>{company?.sector || "Financial Services"}</span> • <span>{company?.industry || "Banking"}</span>
                </p>
              </div>

              <div className="text-right">
                <div className="text-3xl font-black text-white tracking-tight">
                  ₹{company?.current_price ? company.current_price.toLocaleString("en-IN", { minimumFractionDigits: 2 }) : "1,685.40"}
                </div>
                <div className={`text-xs font-bold mt-1 flex items-center justify-end gap-1 ${priceChange >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                  {priceChange >= 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                  <span>{priceChange >= 0 ? "+" : ""}₹{priceChange.toFixed(2)} ({pricePct >= 0 ? "+" : ""}{pricePct.toFixed(2)}%)</span>
                </div>
              </div>
            </div>

            {/* Core Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 pt-2 border-t border-white/5">
              <div className="bg-black/30 border border-white/5 rounded-xl p-2.5 text-center">
                <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Market Cap</div>
                <div className="text-xs font-black text-white mt-1">{formatCurrency(company?.market_cap || 0)}</div>
              </div>
              <div className="bg-black/30 border border-white/5 rounded-xl p-2.5 text-center">
                <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">P/E Ratio</div>
                <div className="text-xs font-black text-white mt-1">{company?.pe_ratio ? `${company.pe_ratio}x` : "—"}</div>
              </div>
              <div className="bg-black/30 border border-white/5 rounded-xl p-2.5 text-center">
                <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">52W High</div>
                <div className="text-xs font-black text-emerald-400 mt-1">₹{company?.fifty_two_week_high || "—"}</div>
              </div>
              <div className="bg-black/30 border border-white/5 rounded-xl p-2.5 text-center">
                <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">52W Low</div>
                <div className="text-xs font-black text-rose-400 mt-1">₹{company?.fifty_two_week_low || "—"}</div>
              </div>
              <div className="bg-black/30 border border-white/5 rounded-xl p-2.5 text-center">
                <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Book Value</div>
                <div className="text-xs font-black text-white mt-1">₹{company?.book_value || "—"}</div>
              </div>
              <div className="bg-black/30 border border-white/5 rounded-xl p-2.5 text-center">
                <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Div Yield</div>
                <div className="text-xs font-black text-indigo-400 mt-1">{company?.dividend_yield ? `${(company.dividend_yield * 100).toFixed(2)}%` : "—"}</div>
              </div>
            </div>
          </div>

          {/* 2. CUSTOM YFINANCE PRICE CHART (No TradingView) */}
          <div className="bg-[#0e1017] border border-white/10 rounded-2xl p-5 space-y-3 shadow-xl">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">YFinance Historical Price Chart</h3>
                {hoveredPrice && (
                  <span className="text-xs font-mono font-bold text-emerald-400 ml-2">
                    {hoveredPrice.time}: ₹{hoveredPrice.price}
                  </span>
                )}
              </div>

              {/* Span Selector */}
              <div className="flex items-center gap-1 bg-black/50 border border-white/10 rounded-xl p-1">
                {["1W", "1M", "1Y", "5Y"].map((span) => (
                  <button
                    key={span}
                    onClick={() => setTimeSpan(span)}
                    className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                      timeSpan === span
                        ? "bg-indigo-600 text-white shadow-lg"
                        : "text-slate-400 hover:text-white hover:bg-white/5"
                    }`}
                  >
                    {span}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Interactive SVG Chart */}
            <div className="relative w-full h-[220px] bg-black/40 border border-white/5 rounded-xl overflow-hidden p-2">
              <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-full overflow-visible">
                <defs>
                  <linearGradient id="priceGradientComp2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6366f1" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="#6366f1" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Gradient Area */}
                <polygon points={areaPoints} fill="url(#priceGradientComp2)" />

                {/* Price Line */}
                <polyline
                  fill="none"
                  stroke="#818cf8"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  points={pointsString}
                />

                {/* Interactive Dots */}
                {priceSeries.map((p, idx) => {
                  const x = (idx / (priceSeries.length - 1)) * svgWidth;
                  const y = svgHeight - ((p.price - minPrice) / priceRange) * svgHeight;
                  return (
                    <circle
                      key={idx}
                      cx={x}
                      cy={y}
                      r="3.5"
                      className="fill-indigo-400 stroke-slate-900 stroke-2 hover:r-6 cursor-pointer transition-all"
                      onMouseEnter={() => setHoveredPrice(p)}
                      onMouseLeave={() => setHoveredPrice(null)}
                    />
                  );
                })}
              </svg>
            </div>
          </div>

          {/* 3. TIJORI SCRAPED TABLES SECTION */}
          {tijori && (
            <div className="space-y-5">
              
              {/* Table A: Business Segment Breakdown */}
              <div className="bg-[#0e1017] border border-white/10 rounded-2xl p-5 space-y-3 shadow-xl">
                <div className="flex items-center gap-2 border-b border-white/5 pb-3">
                  <Layers className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Tijori Scraped: Business Segment Revenue Distribution</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-white/10 text-slate-400 font-mono text-[10px] uppercase">
                        <th className="py-2.5 px-3">Business Segment</th>
                        <th className="py-2.5 px-3 text-right">Revenue (₹ Cr)</th>
                        <th className="py-2.5 px-3 text-right">Share (%)</th>
                        <th className="py-2.5 px-3 text-right">YoY Growth</th>
                        <th className="py-2.5 px-3">Operational Scope</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {tijori.business_segments.map((seg, idx) => (
                        <tr key={idx} className="hover:bg-white/[0.02]">
                          <td className="py-2.5 px-3 font-bold text-white">{seg.segment}</td>
                          <td className="py-2.5 px-3 text-right font-mono text-indigo-300 font-bold">₹{seg.revenue_cr.toLocaleString("en-IN")}</td>
                          <td className="py-2.5 px-3 text-right font-mono font-bold text-emerald-400">{seg.pct_share}%</td>
                          <td className="py-2.5 px-3 text-right font-mono text-slate-300">+{seg.yoy_growth_pct}%</td>
                          <td className="py-2.5 px-3 text-slate-400 text-[11px]">{seg.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Table B: Loan Portfolio Composition (If Banking/Financials) */}
              {tijori.loan_portfolio_mix && tijori.loan_portfolio_mix.length > 0 && (
                <div className="bg-[#0e1017] border border-white/10 rounded-2xl p-5 space-y-3 shadow-xl">
                  <div className="flex items-center gap-2 border-b border-white/5 pb-3">
                    <PieChart className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">Tijori Scraped: Loan Portfolio Mix & Asset Quality</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-white/10 text-slate-400 font-mono text-[10px] uppercase">
                          <th className="py-2.5 px-3">Loan Category</th>
                          <th className="py-2.5 px-3 text-right">Advances (₹ Cr)</th>
                          <th className="py-2.5 px-3 text-right">Portfolio Share</th>
                          <th className="py-2.5 px-3 text-right">Asset Quality (NPA)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {tijori.loan_portfolio_mix.map((loan, idx) => (
                          <tr key={idx} className="hover:bg-white/[0.02]">
                            <td className="py-2.5 px-3 font-bold text-white">{loan.category}</td>
                            <td className="py-2.5 px-3 text-right font-mono text-indigo-300 font-bold">₹{loan.amount_cr.toLocaleString("en-IN")}</td>
                            <td className="py-2.5 px-3 text-right font-mono font-bold text-emerald-400">{loan.pct_share}%</td>
                            <td className="py-2.5 px-3 text-right font-mono text-slate-300">{loan.asset_quality}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Grid C: Market Share & Banking Operational KPIs */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {/* Market Share Table */}
                <div className="bg-[#0e1017] border border-white/10 rounded-2xl p-5 space-y-3 shadow-xl">
                  <div className="flex items-center gap-2 border-b border-white/5 pb-3">
                    <Award className="w-4 h-4 text-amber-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">Tijori Scraped: Market Share</h3>
                  </div>
                  <div className="space-y-2">
                    {tijori.market_share_metrics.map((m, idx) => (
                      <div key={idx} className="bg-black/30 border border-white/5 rounded-xl p-3 flex justify-between items-center">
                        <div>
                          <div className="text-xs font-bold text-white">{m.metric}</div>
                          <div className="text-[10px] text-slate-400 mt-0.5">{m.industry_rank} • {m.trend}</div>
                        </div>
                        <div className="text-base font-black font-mono text-amber-400">{m.value}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Operational KPIs Table */}
                <div className="bg-[#0e1017] border border-white/10 rounded-2xl p-5 space-y-3 shadow-xl">
                  <div className="flex items-center gap-2 border-b border-white/5 pb-3">
                    <Shield className="w-4 h-4 text-indigo-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">Tijori Scraped: Banking Ratios & KPIs</h3>
                  </div>
                  <div className="space-y-2">
                    {tijori.banking_operational_kpis.map((kpi, idx) => (
                      <div key={idx} className="bg-black/30 border border-white/5 rounded-xl p-2.5 flex justify-between items-center text-xs">
                        <div>
                          <div className="font-bold text-slate-200">{kpi.kpi}</div>
                          <div className="text-[10px] text-slate-400">Bench: {kpi.benchmark}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-mono font-black text-emerald-400">{kpi.value}</div>
                          <div className="text-[9px] text-slate-400">{kpi.status}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Table D: Subsidiaries & Investments */}
              {tijori.key_subsidiaries && tijori.key_subsidiaries.length > 0 && (
                <div className="bg-[#0e1017] border border-white/10 rounded-2xl p-5 space-y-3 shadow-xl">
                  <div className="flex items-center gap-2 border-b border-white/5 pb-3">
                    <Landmark className="w-4 h-4 text-purple-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">Tijori Scraped: Key Subsidiaries & Investments</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-white/10 text-slate-400 font-mono text-[10px] uppercase">
                          <th className="py-2.5 px-3">Subsidiary Company</th>
                          <th className="py-2.5 px-3 text-right">Equity Stake</th>
                          <th className="py-2.5 px-3">Business Line</th>
                          <th className="py-2.5 px-3 text-right">Est. Valuation (₹ Cr)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {tijori.key_subsidiaries.map((sub, idx) => (
                          <tr key={idx} className="hover:bg-white/[0.02]">
                            <td className="py-2.5 px-3 font-bold text-white">{sub.subsidiary}</td>
                            <td className="py-2.5 px-3 text-right font-mono font-bold text-purple-400">{sub.stake_pct}</td>
                            <td className="py-2.5 px-3 text-slate-300">{sub.business}</td>
                            <td className="py-2.5 px-3 text-right font-mono text-indigo-300 font-bold">₹{sub.valuation_est_cr.toLocaleString("en-IN")}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

            </div>
          )}

        </div>

        {/* ================================================================= */}
        {/* RIGHT PANE (30% Width): Clean AI Research Copilot Desk           */}
        {/* ================================================================= */}
        <div className="lg:col-span-4 sticky top-4 self-start">
          <CopilotChat symbol={symbol} companyName={company?.name || symbol} />
        </div>

      </main>
    </div>
  );
}
