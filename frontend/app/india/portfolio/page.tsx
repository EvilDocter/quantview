"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { 
  Shield, Sparkles, TrendingUp, RefreshCw, 
  CheckCircle2, AlertTriangle, Building, ChevronRight, Activity, Wallet, PieChart
} from "lucide-react";
import IndiaNavbar from "@/components/IndiaNavbar";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL_INDIA || "http://localhost:8000";

interface Holding {
  quantview_symbol: string;
  trading_symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  pnl: number;
  pnl_percentage: number;
  current_value: number;
  investment_value: number;
}

interface PortfolioData {
  connection_id: string;
  broker_code: string;
  account_id: string;
  total_investment: number;
  total_current_value: number;
  total_pnl: number;
  total_pnl_percentage: number;
  funds: {
    net_available: number;
    cash_balance: number;
    utilised_margin: number;
  };
  holdings: Holding[];
}

interface IntelligenceData {
  portfolio_health_score: number;
  portfolio_beta: number;
  top_holding_concentration: {
    symbol: string;
    percentage: number;
  };
  sector_allocation: Record<string, number>;
  risk_penalties: string[];
  ai_verdict: string;
}

const BROKERS = [
  { id: "zerodha", name: "Zerodha Kite", connId: "conn_zerodha_01", logo: "Z", color: "from-amber-500 to-orange-500" },
  { id: "angel", name: "Angel One", connId: "conn_angel_01", logo: "A", color: "from-blue-500 to-indigo-500" },
  { id: "fyers", name: "FYERS", connId: "conn_fyers_01", logo: "F", color: "from-teal-500 to-emerald-500" },
  { id: "upstox", name: "Upstox", connId: "conn_upstox_01", logo: "U", color: "from-purple-500 to-indigo-500" },
  { id: "dhan", name: "DhanHQ", connId: "conn_dhan_01", logo: "D", color: "from-rose-500 to-pink-500" },
];

function fmtVal(val: any, decimals = 2): string {
  if (val === undefined || val === null) return "0.00";
  const n = Number(val);
  return isNaN(n) ? "0.00" : n.toFixed(decimals);
}

function fmtCurr(val: any): string {
  if (val === undefined || val === null) return "0";
  const n = Number(val);
  return isNaN(n) ? "0" : n.toLocaleString("en-IN");
}

export default function PortfolioDashboard() {
  const router = useRouter();
  
  const [selectedBroker, setSelectedBroker] = useState(BROKERS[0]);
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [intelligence, setIntelligence] = useState<IntelligenceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showConnectModal, setShowConnectModal] = useState(false);

  const fetchPortfolio = async (broker = selectedBroker) => {
    setLoading(true);
    try {
      const [portRes, intelRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/v1/broker-gateway/portfolio?broker=${broker.id}&connection_id=${broker.connId}`),
        fetch(`${BACKEND_URL}/api/v1/broker-gateway/portfolio/intelligence?broker=${broker.id}&connection_id=${broker.connId}`)
      ]);

      if (portRes.ok) setPortfolio(await portRes.json());
      if (intelRes.ok) {
        const intelData = await intelRes.json();
        setIntelligence(intelData.intelligence);
      }
    } catch (err) {
      console.error("Failed to fetch broker portfolio:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio(selectedBroker);
  }, [selectedBroker]);

  const totalPnlNum = Number(portfolio?.total_pnl || 0);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex flex-col font-sans relative overflow-hidden">
      
      {/* Shared Navbar */}
      <IndiaNavbar />

      {/* Main container */}
      <main className="max-w-6xl w-full mx-auto px-6 py-8 space-y-8 flex-1 z-10">
        
        {/* Top Controls: Broker Selector */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-white/[0.01] border border-white/5 rounded-3xl p-6 gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-3">
              <Shield className="w-6 h-6 text-indigo-400" /> Non-Custodial Broker Gateway
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Connect your authorized Indian broker account to stream live holdings, positions, and AI portfolio intelligence.
            </p>
          </div>
          
          <div className="flex items-center gap-3 w-full md:w-auto">
            <button
              onClick={() => setShowConnectModal(true)}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider px-5 py-2.5 rounded-xl shadow-lg transition"
            >
              + Connect Broker
            </button>
          </div>
        </div>

        {/* Broker Account Tabs */}
        <div className="flex gap-3 overflow-x-auto pb-2 border-b border-white/5">
          {BROKERS.map((b) => (
            <button
              key={b.id}
              onClick={() => setSelectedBroker(b)}
              className={`flex items-center gap-2.5 px-5 py-3 rounded-2xl text-xs font-bold transition border ${
                selectedBroker.id === b.id
                  ? "bg-indigo-600/10 border-indigo-500 text-white shadow-md"
                  : "bg-white/[0.02] border-white/5 text-slate-400 hover:text-white"
              }`}
            >
              <div className={`w-6 h-6 rounded-lg bg-gradient-to-tr ${b.color} flex items-center justify-center text-[10px] font-black text-white`}>
                {b.logo}
              </div>
              <span>{b.name}</span>
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-pulse text-slate-400 flex items-center gap-2">
              <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" /> Loading broker portfolio...
            </div>
          </div>
        ) : (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
              <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-5">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Invested Capital</div>
                <div className="text-xl font-black text-white mt-1">₹{fmtCurr(portfolio?.total_investment)}</div>
              </div>
              <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-5">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Current Valuation</div>
                <div className="text-xl font-black text-white mt-1">₹{fmtCurr(portfolio?.total_current_value)}</div>
              </div>
              <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-5">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Total P&L</div>
                <div className={`text-xl font-black mt-1 ${totalPnlNum >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                  {totalPnlNum >= 0 ? "+" : ""}₹{fmtCurr(portfolio?.total_pnl)} ({fmtVal(portfolio?.total_pnl_percentage)}%)
                </div>
              </div>
              <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-5">
                <div className="text-[10px] text-slate-400 uppercase font-bold">Cash Funds Available</div>
                <div className="text-xl font-black text-indigo-400 mt-1">₹{fmtCurr(portfolio?.funds?.net_available)}</div>
              </div>
            </div>

            {/* Main Portal Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Left 2 Cols: Normalized Holdings Table */}
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
                  <div className="flex justify-between items-center border-b border-white/5 pb-4">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Wallet className="w-4 h-4 text-indigo-400" /> Normalized Delivery Holdings ({portfolio?.holdings?.length || 0})
                    </h3>
                    <span className="text-[10px] text-slate-400 font-mono">UCC: {portfolio?.account_id}</span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-white/10 text-slate-400">
                          <th className="py-3">Symbol</th>
                          <th className="py-3">Qty</th>
                          <th className="py-3">Avg Price</th>
                          <th className="py-3">LTP</th>
                          <th className="py-3">Valuation</th>
                          <th className="py-3">P&L</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5 text-slate-300">
                        {portfolio?.holdings?.map((h, idx) => {
                          const pnlNum = Number(h.pnl || 0);
                          return (
                            <tr 
                              key={idx} 
                              onClick={() => router.push(`/india/company/${h.trading_symbol}`)}
                              className="hover:bg-white/[0.02] cursor-pointer transition"
                            >
                              <td className="py-4 font-bold text-white">{h.trading_symbol}</td>
                              <td className="py-4">{h.quantity}</td>
                              <td className="py-4">₹{fmtCurr(h.average_price)}</td>
                              <td className="py-4 font-semibold text-white">₹{fmtCurr(h.current_price)}</td>
                              <td className="py-4 font-bold text-slate-200">₹{fmtCurr(h.current_value)}</td>
                              <td className={`py-4 font-bold ${pnlNum >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                                {pnlNum >= 0 ? "+" : ""}₹{fmtCurr(h.pnl)} ({fmtVal(h.pnl_percentage)}%)
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Right 1 Col: AI Portfolio Intelligence */}
              <div className="space-y-6">
                
                {/* Health Score Card */}
                <div className="bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-transparent border border-indigo-500/20 rounded-3xl p-6 space-y-5 shadow-2xl backdrop-blur-md">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-indigo-400" /> QuantView Health Score
                    </h3>
                    <span className="text-[10px] uppercase font-bold text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full">
                      {intelligence?.ai_verdict}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-5xl font-black text-white">
                      {intelligence?.portfolio_health_score}<span className="text-xl text-slate-500">/100</span>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Portfolio Beta</div>
                      <div className="text-lg font-black text-indigo-400">{fmtVal(intelligence?.portfolio_beta, 2)}x</div>
                    </div>
                  </div>

                  {/* Risk Penalties */}
                  {intelligence?.risk_penalties && intelligence.risk_penalties.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-white/5">
                      <div className="text-[10px] uppercase font-bold text-amber-400 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> Risk Factors Detected
                      </div>
                      {intelligence.risk_penalties.map((penalty, i) => (
                        <p key={i} className="text-xs text-slate-300 leading-relaxed bg-amber-500/5 border border-amber-500/10 p-2.5 rounded-xl">
                          {penalty}
                        </p>
                      ))}
                    </div>
                  )}
                </div>

                {/* Sector Allocation Breakdown */}
                {intelligence?.sector_allocation && (
                  <div className="bg-white/[0.01] border border-white/5 rounded-3xl p-6 space-y-4">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <PieChart className="w-4 h-4 text-indigo-400" /> Sector Distribution
                    </h3>
                    <div className="space-y-3 text-xs">
                      {Object.entries(intelligence.sector_allocation).map(([sector, pct], i) => (
                        <div key={i} className="space-y-1">
                          <div className="flex justify-between">
                            <span className="text-slate-300">{sector}</span>
                            <span className="text-white font-bold">{fmtVal(pct, 1)}%</span>
                          </div>
                          <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${pct}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            </div>
          </>
        )}
      </main>

      {/* Connect Broker Modal */}
      {showConnectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-[#12121a] border border-white/10 rounded-3xl p-6 max-w-md w-full space-y-6 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center border-b border-white/5 pb-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Connect Broker Account</h3>
              <button onClick={() => setShowConnectModal(false)} className="text-slate-400 hover:text-white text-xs font-bold">✕</button>
            </div>
            
            <p className="text-xs text-slate-400 leading-relaxed">
              Select your Indian broker to authenticate securely. QuantView uses your authorized session to access holdings non-custodially.
            </p>

            <div className="space-y-2">
              {BROKERS.map((b) => (
                <button
                  key={b.id}
                  onClick={() => {
                    setSelectedBroker(b);
                    setShowConnectModal(false);
                  }}
                  className="w-full flex items-center justify-between p-3.5 rounded-2xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.05] transition text-left"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-xl bg-gradient-to-tr ${b.color} flex items-center justify-center text-xs font-black text-white`}>
                      {b.logo}
                    </div>
                    <div>
                      <div className="font-bold text-white text-xs">{b.name}</div>
                      <div className="text-[10px] text-slate-400">OAuth 2.0 / TOTP Auth</div>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-500" />
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
