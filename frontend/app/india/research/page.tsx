"use client";

import React, { useState } from "react";
import { 
  ArrowLeft, Search, Brain, Loader2, Send, 
  BookOpen, Sparkles, AlertCircle, Bookmark 
} from "lucide-react";
import { useRouter } from "next/navigation";

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: any[];
}

export default function AIResearchPortal() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am your QuantView Financial Research Agent. Ask me to analyze any Nifty 500 company, extract risk factors from annual reports, or run valuations."
    }
  ]);
  const [loading, setLoading] = useState(false);

  const history = [
    "Should I buy Tata Motors?",
    "Infosys valuation multiples",
    "Reliance Industries capex details",
    "Nifty 50 margin trends"
  ];

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userText = query;
    setMessages(prev => [...prev, { role: "user", content: userText }]);
    setQuery("");
    setLoading(true);

    try {
      // In production, queries POST /api/v1/ai/research
      // We stub agentic response for UI testing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setMessages(prev => [...prev, {
        role: "assistant",
        content: `### Executive Analysis Summary for: ${userText}\n\nBased on the latest financial filings, we observe improving operating efficiencies. Operating margins expanded to 12.8% [Source: financial_agent].\n\n#### Key Catalysts:\n- Turnaround in luxury segments driving sales growth.\n- Strategic raw materials sourcing agreements minimizing pricing pressures.\n\n#### Risk Assessment:\n- Debt leverage metrics remain slightly elevated, though net debt-to-equity declined to 1.4x [Source: risk_agent].`,
        citations: [
          { agent: "financial_agent", source: "PostgreSQL P&L statements" },
          { agent: "risk_agent", source: "Financial ratio calculator" }
        ]
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Error fetching analysis. Please verify backend connections." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-100 flex font-sans relative overflow-hidden">
      
      {/* Sidebar: Research History */}
      <aside className="w-80 border-r border-white/5 bg-[#0e0e15]/50 backdrop-blur-md hidden md:flex flex-col p-6 space-y-6">
        <button 
          onClick={() => router.push("/india")}
          className="flex items-center gap-2 text-xs text-slate-400 hover:text-white font-bold uppercase tracking-wider"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </button>

        <div className="space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-indigo-400" /> Research Logs
          </h3>
          <div className="space-y-2">
            {history.map((item, idx) => (
              <button
                key={idx}
                onClick={() => setQuery(item)}
                className="w-full text-left px-4 py-3 rounded-xl bg-white/[0.02] border border-white/5 text-xs text-slate-400 hover:text-white hover:bg-white/[0.05] truncate transition"
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </aside>

      {/* Main chat window */}
      <section className="flex-1 flex flex-col h-screen">
        {/* Top bar */}
        <header className="border-b border-white/5 p-6 flex justify-between items-center bg-[#0e0e15]/30">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-indigo-400" />
            <div>
              <h2 className="text-md font-bold text-white">Autonomous Research Agent</h2>
              <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">QuantView Agent Graph Active</p>
            </div>
          </div>
        </header>

        {/* Message logs */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          {messages.map((msg, idx) => (
            <div 
              key={idx} 
              className={`flex gap-4 p-5 rounded-3xl border ${
                msg.role === "user" 
                  ? "bg-indigo-500/5 border-indigo-500/10 ml-12" 
                  : "bg-white/[0.02] border-white/5 mr-12"
              }`}
            >
              <div className="space-y-3 w-full">
                <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                  {msg.role === "user" ? "User Query" : "AI Research Report"}
                </div>
                <div className="text-sm leading-relaxed text-slate-300 whitespace-pre-line">
                  {msg.content}
                </div>
                
                {/* Citations panel */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-3 border-t border-white/5 space-y-2">
                    <div className="text-[10px] uppercase font-black text-indigo-400 tracking-wider flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" /> Cited Evidence Sources:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {msg.citations.map((cit, i) => (
                        <div key={i} className="text-[10px] bg-white/[0.04] border border-white/5 px-2.5 py-1 rounded-lg text-slate-400 flex items-center gap-1.5">
                          <span className="font-bold text-indigo-300">[{cit.agent}]</span> {cit.source}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-3 text-slate-400 text-xs p-6 bg-white/[0.02] border border-white/5 rounded-3xl mr-12">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
              Planner node orchestrating specialist agents (Financial, Filing, Risk)...
            </div>
          )}
        </div>

        {/* Input panel */}
        <footer className="p-6 border-t border-white/5 bg-[#0e0e15]/20">
          <form onSubmit={handleSearchSubmit} className="relative bg-[#12121a] border border-white/10 rounded-2xl flex items-center p-2">
            <input
              type="text"
              placeholder="Ask the Agent to compile an investment report..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="w-full bg-transparent px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none"
            />
            <button 
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold p-3 rounded-xl transition disabled:opacity-40"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </footer>
      </section>

    </div>
  );
}
