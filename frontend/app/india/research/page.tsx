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
  confidence?: number;
  processingTimeMs?: number;
}

export default function AIResearchPortal() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am your QuantView Financial Research Agent. Ask me to analyze any Nifty 500 company (e.g. INFY, RELIANCE, TCS, TATAMOTORS), extract risk factors from NSE annual reports, or evaluate your Zerodha portfolio holdings."
    }
  ]);
  const [loading, setLoading] = useState(false);

  const history = [
    "What are Infosys top risk factors in 2026 annual report?",
    "Should I buy Reliance Industries?",
    "Analyze Tata Motors luxury segment turnaround",
    "Evaluate my Zerodha portfolio health"
  ];

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userText = query;
    setMessages(prev => [...prev, { role: "user", content: userText }]);
    setQuery("");
    setLoading(true);

    try {
      // Connect to live FastAPI backend route: POST /api/v1/ai/research
      const response = await fetch("http://localhost:8000/api/v1/ai/research", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userText }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.answer || "No response content generated.",
        confidence: data.confidence,
        processingTimeMs: data.processing_time_ms,
        citations: data.citations || []
      }]);
    } catch (err: any) {
      console.error("AI Research fetch error:", err);
      // Try fallback to backend directly if origin differs
      try {
        const response = await fetch("/api/v1/ai/research", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: userText }),
        });
        if (response.ok) {
          const data = await response.json();
          setMessages(prev => [...prev, {
            role: "assistant",
            content: data.answer || "No response content generated.",
            confidence: data.confidence,
            processingTimeMs: data.processing_time_ms,
            citations: data.citations || []
          }]);
          return;
        }
      } catch (e2) {}

      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: "⚠️ Connection error contacting QuantView AI Backend (http://localhost:8000). Please ensure the backend server is running." 
      }]);
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
          className="flex items-center gap-2 text-xs text-slate-400 hover:text-white font-bold uppercase tracking-wider transition"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </button>

        <div className="space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-indigo-400" /> Suggested Research Prompts
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
              <h2 className="text-md font-bold text-white">Autonomous Financial Research Agent (RAG Active)</h2>
              <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">QuantView Knowledge Platform • Qdrant Vector DB • Qwen 2.5 14B</p>
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
                <div className="flex justify-between items-center">
                  <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                    {msg.role === "user" ? "User Query" : "QuantView AI Research Report"}
                  </div>
                  {msg.confidence !== undefined && (
                    <div className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold">
                      Confidence: {Math.round(msg.confidence * 100)}%
                    </div>
                  )}
                </div>

                <div className="text-sm leading-relaxed text-slate-300 whitespace-pre-line font-sans">
                  {msg.content}
                </div>
                
                {/* Citations panel */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-3 border-t border-white/5 space-y-2">
                    <div className="text-[10px] uppercase font-black text-indigo-400 tracking-wider flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" /> Verified RAG Evidence & Source Citations:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {msg.citations.map((cit: any, i: number) => (
                        <div key={i} className="text-[10px] bg-white/[0.04] border border-white/5 px-2.5 py-1 rounded-lg text-slate-400 flex items-center gap-1.5">
                          <span className="font-bold text-indigo-300">[{cit.source || "Knowledge RAG"}]</span> {cit.title || cit.content?.slice(0, 50)}
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
              Planner orchestrating Knowledge RAG (Qdrant Vector DB), Financial Agent, and Synthesis Agent...
            </div>
          )}
        </div>

        {/* Input box */}
        <div className="p-6 border-t border-white/5 bg-[#0e0e15]/50 backdrop-blur-md">
          <form onSubmit={handleSearchSubmit} className="relative flex items-center">
            <input 
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask QuantView AI to analyze annual report risks, company valuations, or portfolio impact..."
              className="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-4 pl-5 pr-14 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 transition"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute right-3 p-2.5 bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 text-white rounded-xl transition flex items-center justify-center"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </form>
        </div>
      </section>

    </div>
  );
}
