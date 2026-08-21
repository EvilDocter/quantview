"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Brain, Send, Sparkles, FileText, ChevronDown, ChevronUp,
  BarChart3, ShieldAlert, ArrowRight, CornerDownRight
} from "lucide-react";

interface Citation {
  id: string;
  document_name: string;
  page_number: number;
  section_name: string;
  snippet: string;
}

interface Message {
  id: string;
  sender: "user" | "copilot";
  query?: string;
  executive_insight?: string;
  full_analysis?: string;
  key_evidence?: Record<string, any>;
  chart_config?: any;
  citations?: Citation[];
  suggested_questions?: string[];
  timestamp: string;
}

interface CopilotChatProps {
  symbol: string;
  companyName: string;
}

export default function CopilotChat({ symbol, companyName }: CopilotChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init_msg",
      sender: "copilot",
      executive_insight: `Active AI Research Workspace created for ${companyName} (${symbol}). Grounded in PostgreSQL financials & Baidu Unlimited-OCR Annual Report data.`,
      full_analysis: `### Executive Institutional Thesis for ${symbol}
Welcome to your persistent research workspace. The AI Copilot has loaded complete historical statement ratios, quarterly filings, and Baidu Unlimited-OCR Annual Report sections for **${companyName}**.

Ask any deep analyst query, or select a suggested prompt below to begin your investigation.`,
      citations: [],
      suggested_questions: [
        `What am I missing in ${symbol}?`,
        `Explain ${symbol} cash flow & working capital trend`,
        `Compare ${symbol} margins against top sector peers`,
        `Build Bull / Base / Bear valuation scenario for ${symbol}`,
      ],
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({});

  const toggleCitation = (id: string) => {
    setExpandedCitations((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleSendQuery = async (queryToRun?: string) => {
    const activeQuery = queryToRun || inputQuery;
    if (!activeQuery.trim() || loading) return;

    const userMsgId = `user_${Date.now()}`;
    const userMessage: Message = {
      id: userMsgId,
      sender: "user",
      query: activeQuery,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputQuery("");
    setLoading(true);

    const isQuantviewDomain = typeof window !== "undefined" && window.location.hostname.includes("quantview.in");
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL_INDIA || "";

    // Use relative URL first — goes through Next.js rewrite proxy to backend:8001
    const endpoints = [
      "/api/v1/ai/copilot",
      `${window.location.protocol}//${window.location.hostname}:8001/api/v1/ai/copilot`,
    ];


    let resData: any = null;
    for (const ep of endpoints) {
      try {
        const res = await fetch(ep, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            symbol: symbol,
            query: activeQuery,
            chat_history: messages.map((m) => ({ sender: m.sender, content: m.full_analysis || m.query || "" })),
          }),
        });
        if (res.ok) {
          resData = await res.json();
          break;
        }
      } catch (err) {}
    }

    if (resData) {
      const copilotMsg: Message = {
        id: `copilot_${Date.now()}`,
        sender: "copilot",
        executive_insight: resData.executive_insight,
        full_analysis: resData.full_analysis,
        key_evidence: resData.key_evidence,
        chart_config: resData.chart_config,
        citations: resData.citations,
        suggested_questions: resData.suggested_questions,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, copilotMsg]);
    } else {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: "copilot",
          full_analysis: `⚠️ Could not reach AI Copilot backend server. Please verify backend service on port 8001 is active.`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[750px] bg-[#12121a]/90 border border-indigo-500/20 rounded-3xl backdrop-blur-md overflow-hidden shadow-2xl">
      {/* Copilot Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-white/[0.02] border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400">
            <Brain className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h2 className="text-sm font-black text-white tracking-wide uppercase">AI Research Copilot</h2>
            <p className="text-[10px] text-slate-400">
              Persistent Equity Workspace • Grounded in Baidu Unlimited-OCR
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            ● Grounded
          </span>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}>
            {msg.sender === "user" ? (
              <div className="max-w-[80%] bg-indigo-600 text-white rounded-2xl rounded-tr-none px-5 py-3.5 text-sm font-medium shadow-md">
                {msg.query}
              </div>
            ) : (
              <div className="w-full space-y-4">
                {/* Executive Insight Alert Banner */}
                {msg.executive_insight && (
                  <div className="bg-indigo-950/40 border border-indigo-500/30 rounded-2xl p-4 flex gap-3">
                    <Sparkles className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
                    <div>
                      <div className="text-[10px] uppercase tracking-wider font-bold text-indigo-300">Executive Insight</div>
                      <p className="text-xs text-slate-200 mt-1 leading-relaxed">{msg.executive_insight}</p>
                    </div>
                  </div>
                )}

                {/* Main Markdown Body */}
                <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6 text-slate-200 text-sm leading-relaxed prose prose-invert prose-indigo max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.full_analysis || ""}</ReactMarkdown>
                </div>

                {/* Key Evidence Table */}
                {msg.key_evidence && (
                  <div className="bg-white/[0.01] border border-white/5 rounded-2xl p-4 space-y-2">
                    <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1.5">
                      <BarChart3 className="w-3.5 h-3.5 text-indigo-400" /> PostgreSQL Key Financial Evidence
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                      {Object.entries(msg.key_evidence).map(([k, v]) => (
                        <div key={k} className="bg-white/[0.02] p-2.5 rounded-xl border border-white/5">
                          <div className="text-[10px] text-slate-400 uppercase font-semibold">{k.replace(/_/g, " ")}</div>
                          <div className="text-sm font-black text-white mt-0.5">{String(v)}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Inline Dynamic Chart Card */}
                {msg.chart_config && (
                  <div className="bg-white/[0.01] border border-white/5 rounded-2xl p-5 space-y-3">
                    <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <BarChart3 className="w-4 h-4 text-emerald-400" /> {msg.chart_config.title}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">5-Year Trend</span>
                    </div>
                    <div className="h-44 flex items-end justify-between gap-3 pt-6 pb-2 px-4 bg-black/30 rounded-xl border border-white/5">
                      {msg.chart_config.data?.map((d: any, idx: number) => {
                        const val1 = d[msg.chart_config.series[0]?.key] || 10;
                        const maxVal = Math.max(...msg.chart_config.data.map((x: any) => x[msg.chart_config.series[0]?.key] || 10));
                        const heightPct = Math.max(15, Math.min(100, (val1 / (maxVal || 1)) * 100));
                        return (
                          <div key={idx} className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                            <div className="text-[9px] text-slate-400 font-mono opacity-0 group-hover:opacity-100 transition">{val1}</div>
                            <div
                              style={{ height: `${heightPct}%` }}
                              className="w-full max-w-[28px] bg-gradient-to-t from-indigo-600 to-indigo-400 rounded-t-lg transition-all group-hover:brightness-125"
                            />
                            <div className="text-[10px] text-slate-400 font-bold">{d.year}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Annual Report OCR Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="bg-white/[0.01] border border-white/5 rounded-2xl p-4 space-y-2">
                    <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-indigo-400" /> Baidu Unlimited-OCR Citations ({msg.citations.length})
                    </div>
                    <div className="space-y-2">
                      {msg.citations.map((cit) => (
                        <div key={cit.id} className="border border-white/5 rounded-xl bg-white/[0.01] overflow-hidden">
                          <button
                            onClick={() => toggleCitation(cit.id)}
                            className="w-full flex items-center justify-between p-3 text-left hover:bg-white/[0.02] transition"
                          >
                            <span className="text-xs font-bold text-indigo-300 flex items-center gap-2">
                              <CornerDownRight className="w-3.5 h-3.5 text-slate-500" />
                              {cit.document_name} • Page {cit.page_number} ({cit.section_name})
                            </span>
                            {expandedCitations[cit.id] ? (
                              <ChevronUp className="w-4 h-4 text-slate-500" />
                            ) : (
                              <ChevronDown className="w-4 h-4 text-slate-500" />
                            )}
                          </button>
                          {expandedCitations[cit.id] && (
                            <div className="px-4 pb-3 text-xs text-slate-300 bg-black/30 border-t border-white/5 pt-2 font-mono">
                              "{cit.snippet}"
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggested Next Questions Chips */}
                {msg.suggested_questions && msg.suggested_questions.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                      Suggested Follow-Up Analysis:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {msg.suggested_questions.map((q, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSendQuery(q)}
                          disabled={loading}
                          className="px-3 py-1.5 rounded-full text-xs font-semibold bg-white/[0.03] hover:bg-indigo-600/30 border border-white/10 hover:border-indigo-500/40 text-slate-300 hover:text-white transition flex items-center gap-1.5"
                        >
                          {q} <ArrowRight className="w-3 h-3 text-indigo-400" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 p-4 rounded-2xl bg-white/[0.02] border border-white/5 w-fit">
            <Brain className="w-4 h-4 text-indigo-400 animate-spin" />
            <span className="text-xs font-medium text-slate-400">
              Copilot reasoning over local PostgreSQL & Baidu Unlimited-OCR evidence...
            </span>
          </div>
        )}
      </div>

      {/* Query Input Bar */}
      <div className="p-4 bg-white/[0.02] border-t border-white/5">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendQuery();
          }}
          className="flex items-center gap-2 bg-black/40 border border-white/10 rounded-2xl px-4 py-2 focus-within:border-indigo-500/50 transition"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder={`Ask AI Copilot about ${symbol} (e.g. "What am I missing?", "Explain debt")...`}
            className="flex-1 bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!inputQuery.trim() || loading}
            className="p-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-900 text-white transition disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
