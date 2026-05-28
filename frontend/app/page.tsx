"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { HeroSection } from "../components/sections/HeroSection";
import { Bot, Brain, Star, Settings, Zap, Key, Info, Check, Loader2 } from "lucide-react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || (typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1:8000");

// Dynamic audio synthesizer using Web Audio API ($0 cost, 100% free offline audio generation)
const playSound = (type: "connect" | "trade" | "close" | "toggle") => {
  if (typeof window === "undefined") return;
  try {
    const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    const now = audioCtx.currentTime;
    
    if (type === "connect") {
      // Pleasant twin-tone chime
      osc.type = "sine";
      osc.frequency.setValueAtTime(523.25, now); // C5
      osc.frequency.setValueAtTime(659.25, now + 0.1); // E5
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc.start(now);
      osc.stop(now + 0.35);
    } else if (type === "trade") {
      // High tech rising execution sweep
      osc.type = "triangle";
      osc.frequency.setValueAtTime(300, now);
      osc.frequency.exponentialRampToValueAtTime(900, now + 0.25);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      osc.start(now);
      osc.stop(now + 0.25);
    } else if (type === "close") {
      // Lower descending sweep
      osc.type = "triangle";
      osc.frequency.setValueAtTime(600, now);
      osc.frequency.exponentialRampToValueAtTime(200, now + 0.3);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
      osc.start(now);
      osc.stop(now + 0.3);
    } else if (type === "toggle") {
      // High-pitched confirmation ping
      osc.type = "sine";
      osc.frequency.setValueAtTime(880, now); // A5
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
      osc.start(now);
      osc.stop(now + 0.2);
    }
  } catch (err) {
    console.warn("Audio Context failed to load", err);
  }
};

export default function Home() {
  const router = useRouter();
  
  // Persistence state loaders
  const [selectedMarket, setSelectedMarket] = useState<string>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("quantview_selected_category") || "Forex";
    }
    return "Forex";
  });
  
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"trader" | "analyser" | "watchlist" | "settings">("analyser");
  
  // Splash Screen States
  const [isLoading, setIsLoading] = useState(true);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingStatus, setLoadingStatus] = useState("Initializing QuantView Quant Engine...");
  
  // Market Engine state parameters
  const [data, setData] = useState<any[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [signals, setSignals] = useState<Record<string, any>>({});
  const [marketPrices, setMarketPrices] = useState<Record<string, any>>({});
  const [priceTrend, setPriceTrend] = useState<Record<string, "up" | "down" | "neutral">>({});
  const prevPricesRef = useRef<Record<string, number>>({});
  const wsRef = useRef<WebSocket | null>(null);
  const [news, setNews] = useState<any[]>([]);
  const [socialData, setSocialData] = useState<any>(null);
  const [expandedSignals, setExpandedSignals] = useState<string[]>([]);
  
  // cTrader & Shared Broker State parameters
  const [mt5Volume, setMt5Volume] = useState(0.01);
  const [mt5BrokerConnected, setMt5BrokerConnected] = useState(false);
  const [mt5AccountData, setMt5AccountData] = useState<any>(null);
  const [mt5Positions, setMt5Positions] = useState<any[]>([]);
  const [mt5Logs, setMt5Logs] = useState<any[]>([]);
  const [isAutoTradingActive, setIsAutoTradingActive] = useState(false);

  // cTrader State
  const [ctAccessToken, setCtAccessToken] = useState("");
  const [ctAccountId, setCtAccountId] = useState("");
  const [ctVolume, setCtVolume] = useState(0.01);
  const [ctConnecting, setCtConnecting] = useState(false);
  const [ctAccounts, setCtAccounts] = useState<any[]>([]);
  const [ctFetchingAccounts, setCtFetchingAccounts] = useState(false);
  
  // Settings Panel States
  const [aiRiskTolerance, setAiRiskTolerance] = useState<"conservative" | "moderate" | "aggressive">(() => {
    if (typeof window !== "undefined") {
      return (localStorage.getItem("quantview_ai_risk") as any) || "moderate";
    }
    return "moderate";
  });
  
  // Local Broker credentials loader
  useEffect(() => {
    const savedId = localStorage.getItem("quantview_ct_account_id");
    const savedToken = localStorage.getItem("quantview_ct_token");
    const savedVol = localStorage.getItem("quantview_mt5_volume") || "0.01";
    
    if (savedToken) setCtAccessToken(savedToken);
    if (savedId) setCtAccountId(savedId);
    setMt5Volume(Number(savedVol));
    
    if (savedId && savedToken) {
      // Attempt automated reconnect
      reconnectBroker();
    }
  }, []);
  
  // Category state synchronizer
  const handleMarketChange = (market: string) => {
    setSelectedMarket(market);
    setSelectedSymbol(null);
    setSearchQuery("");
    localStorage.setItem("quantview_selected_category", market);
  };
  

  
  const reconnectBroker = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/market/ctrader/account`);
      const json = await res.json();
      if (res.ok && json.connected) {
        setMt5BrokerConnected(true);
        setMt5AccountData(json.account);
        setIsAutoTradingActive(json.autoTradingActive || false);
        setMt5Volume(json.volume || 0.01);
        fetchBrokerStats();
      }
    } catch (err) {
      console.error(err);
    }
  };
  
  const fetchBrokerStats = async () => {
    try {
      // 1. Fetch live metrics
      const accRes = await fetch(`${BACKEND_URL}/market/ctrader/account`);
      const accJson = await accRes.json();
      if (accRes.ok && accJson.success) {
        setMt5AccountData(accJson.account);
        setIsAutoTradingActive(accJson.autoTradingActive);
      }
      
      // 2. Fetch positions
      const posRes = await fetch(`${BACKEND_URL}/market/ctrader/positions`);
      const posJson = await posRes.json();
      if (posRes.ok) {
        setMt5Positions(posJson);
      }
      
      // 3. Fetch trade logs
      const logRes = await fetch(`${BACKEND_URL}/market/ctrader/logs`);
      const logJson = await logRes.json();
      if (logRes.ok) {
        setMt5Logs(logJson);
      }
    } catch (err) {
      console.error("Broker fetch loop error", err);
    }
  };
  
  // Continuous sync loop for Live cTrader Account
  useEffect(() => {
    if (!mt5BrokerConnected) return;
    fetchBrokerStats();
    const interval = setInterval(fetchBrokerStats, 5000);
    return () => clearInterval(interval);
  }, [mt5BrokerConnected]);
  
  const toggleAutoTrading = async () => {
    const nextState = !isAutoTradingActive;
    try {
      const res = await fetch(`${BACKEND_URL}/market/ctrader/toggle-auto`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active: nextState })
      });
      if (res.ok) {
        setIsAutoTradingActive(nextState);
        playSound("toggle");
        fetchBrokerStats();
      }
    } catch (err) {
      console.error(err);
    }
  };
  
  const closePosition = async (positionId: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/market/ctrader/close`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ positionId })
      });
      if (res.ok) {
        playSound("close");
        fetchBrokerStats();
      } else {
        const json = await res.json();
        alert(json.detail || "Close order failed");
      }
    } catch (err) {
      console.error(err);
    }
  };
  
  const manualTrade = async (action: "BUY" | "SELL") => {
    const activeSymbol = selectedSymbol || displayedAssets[0] || "XAU/USD";
    try {
      const res = await fetch(`${BACKEND_URL}/market/ctrader/trade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: activeSymbol,
          action,
          volume: mt5Volume
        })
      });
      if (res.ok) {
        playSound("trade");
        fetchBrokerStats();
      } else {
        const json = await res.json();
        alert(json.detail || "Manual order execution failed");
      }
    } catch (err) {
      console.error(err);
    }
  };
  
  const handleRiskChange = (risk: "conservative" | "moderate" | "aggressive") => {
    setAiRiskTolerance(risk);
    localStorage.setItem("quantview_ai_risk", risk);
    playSound("toggle");
  };

  // Splash Screen progress bar simulation
  useEffect(() => {
    const statuses = [
      "Connecting to Twelve Data streaming nodes...",
      "Mapping active Forex and Commodity indices...",
      "Initializing Llama-3.3-70B quantitative reasoning models...",
      "Synergizing calculated Break of Structure (BOS) buffers...",
      "Establishing secure cTrader API broker handshake...",
      "Institutional QuantView AI Terminal active."
    ];
    
    let currentStep = 0;
    const interval = setInterval(() => {
      setLoadingProgress((prev) => {
        const next = prev + Math.floor(Math.random() * 12) + 8;
        if (next >= 100) {
          clearInterval(interval);
          setIsLoading(false);
          return 100;
        }
        
        // Dynamic status transition
        const idx = Math.min(Math.floor((next / 100) * statuses.length), statuses.length - 1);
        setLoadingStatus(statuses[idx]);
        return next;
      });
    }, 180);
    
    return () => clearInterval(interval);
  }, []);

  const toggleSignals = (symbol: string) => {
    setExpandedSignals((prev) => {
      if (prev.includes(symbol)) {
        return prev.filter((item) => item !== symbol);
      }
      return [...prev, symbol];
    });
  };

  const marketSymbols: Record<string, string[]> = {
    Forex: [
      "EUR/USD",
      "GBP/USD",
      "USD/JPY",
      "USD/CHF",
      "AUD/USD",
      "USD/CAD",
      "NZD/USD",
      "EUR/GBP",
      "EUR/JPY",
      "GBP/JPY",
      "EUR/AUD",
    ],
    Crypto: [
      "BTC/USD",
      "ETH/USD",
      "SOL/USD",
      "XRP/USD",
      "DOGE/USD",
      "ADA/USD",
      "BNB/USD",
    ],
    Stocks: [
      "AAPL",
      "TSLA",
      "NVDA",
      "MSFT",
      "AMZN",
      "META",
      "GOOGL",
      "NFLX",
      "AMD",
    ],
    Commodities: [
      "XAU/USD",
      "XAG/USD",
      "WTI",
      "COPPER",
    ],
  };

  const allAssets = Object.values(marketSymbols).flat();

  const getAssetLogo = (symbol: string) => {
    const clean = symbol.replace("/", "").replace("-", "");
    const logoMap: Record<string, string> = {
      BTCUSD: "https://s3-symbol-logo.tradingview.com/crypto/XTVCBTC--big.svg",
      ETHUSD: "https://s3-symbol-logo.tradingview.com/crypto/XTVCETH--big.svg",
      SOLUSD: "https://s3-symbol-logo.tradingview.com/crypto/XTVCSOL--big.svg",
      XRPUSD: "https://s3-symbol-logo.tradingview.com/crypto/XTVCXRP--big.svg",
      DOGEUSD: "https://s3-symbol-logo.tradingview.com/crypto/XTVCDOGE--big.svg",
      ADAUSD: "https://s3-symbol-logo.tradingview.com/crypto/XTVCADA--big.svg",
      BNBUSD: "https://s3-symbol-logo.tradingview.com/crypto/XTVCBNB--big.svg",
      AAPL: "https://s3-symbol-logo.tradingview.com/apple--big.svg",
      TSLA: "https://s3-symbol-logo.tradingview.com/tesla--big.svg",
      NVDA: "https://s3-symbol-logo.tradingview.com/nvidia--big.svg",
      MSFT: "https://s3-symbol-logo.tradingview.com/microsoft--big.svg",
      AMZN: "https://s3-symbol-logo.tradingview.com/amazon--big.svg",
      META: "https://s3-symbol-logo.tradingview.com/meta-platforms--big.svg",
      GOOGL: "https://s3-symbol-logo.tradingview.com/alphabet--big.svg",
      NFLX: "https://s3-symbol-logo.tradingview.com/netflix--big.svg",
      AMD: "https://s3-symbol-logo.tradingview.com/advanced-micro-devices--big.svg",
      EURUSD: "https://s3-symbol-logo.tradingview.com/country/US.svg",
      GBPUSD: "https://s3-symbol-logo.tradingview.com/country/GB.svg",
      USDJPY: "https://s3-symbol-logo.tradingview.com/country/JP.svg",
      XAUUSD: "https://s3-symbol-logo.tradingview.com/metal/gold--big.svg",
      XAGUSD: "https://s3-symbol-logo.tradingview.com/metal/silver--big.svg",
    };

    if (logoMap[clean]) return logoMap[clean];

    if (symbol.includes("/")) {
      const base = symbol.split("/")[0];
      const forexFlags: Record<string, string> = {
        EUR: "https://s3-symbol-logo.tradingview.com/country/EU.svg",
        USD: "https://s3-symbol-logo.tradingview.com/country/US.svg",
        GBP: "https://s3-symbol-logo.tradingview.com/country/GB.svg",
        JPY: "https://s3-symbol-logo.tradingview.com/country/JP.svg",
        CHF: "https://s3-symbol-logo.tradingview.com/country/CH.svg",
        AUD: "https://s3-symbol-logo.tradingview.com/country/AU.svg",
        CAD: "https://s3-symbol-logo.tradingview.com/country/CA.svg",
        NZD: "https://s3-symbol-logo.tradingview.com/country/NZ.svg",
      };
      if (forexFlags[base]) return forexFlags[base];
    }
    if (symbol.includes("XAU")) return "https://s3-symbol-logo.tradingview.com/metal/gold--big.svg";
    if (symbol.includes("XAG")) return "https://s3-symbol-logo.tradingview.com/metal/silver--big.svg";
    return "https://cdn-icons-png.flaticon.com/512/2830/2830284.png";
  };

  useEffect(() => {
    async function fetchVolatility() {
      try {
        const res = await fetch(`${BACKEND_URL}/market/volatility/top`);
        const json = await res.json();
        if (json?.top_volatile) setData(json.top_volatile);
      } catch (err) {
        console.error("Volatility fetch failed", err);
      }
    }
    fetchVolatility();
    const interval = setInterval(fetchVolatility, 30000);
    return () => clearInterval(interval);
  }, []);

  // Persistent Watchlist loader
  useEffect(() => {
    const stored = localStorage.getItem("quantview_watchlist");
    if (stored) setWatchlist(JSON.parse(stored));
  }, []);

  const displayedAssets = useMemo(() => {
    return searchQuery
      ? allAssets.filter((asset) => asset.toLowerCase().includes(searchQuery.toLowerCase()))
      : selectedSymbol
      ? [selectedSymbol]
      : marketSymbols[selectedMarket];
  }, [searchQuery, selectedSymbol, selectedMarket]);

  const filteredData = displayedAssets.map((symbol) => {
    const existing = data.find((d) => d.symbol === symbol);
    if (existing) return existing;
    return {
      symbol,
      volatility: { value: "--", level: "LOW", status: "STABLE" }
    };
  });

  const sortedData = [...filteredData];

  // Persistent Active WebSocket Engine
  useEffect(() => {
    if (wsRef.current) return;
    const ws = new WebSocket(`${BACKEND_URL.replace(/^http/, "ws")}/market/ws/live`);
    wsRef.current = ws;
    ws.onopen = () => {
      const visibleSymbols = sortedData.map((item) => item.symbol).filter(Boolean);
      if (visibleSymbols.length > 0) {
        try {
          ws.send(JSON.stringify({ type: "subscribe", symbols: visibleSymbols }));
        } catch (err) {
          console.error("Initial subscription failed", err);
        }
      }
    };
    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        const assets = parsed.assets || {};
        const formatted: any = {};
        const liveSignals: Record<string, any> = {};
        const newTrends: Record<string, "up" | "down" | "neutral"> = {};

        Object.entries(assets).forEach(([symbol, asset]: any) => {
          liveSignals[symbol] = asset?.signal || {};
          const price = Number(asset?.price || 0);
          const oldPrice = prevPricesRef.current[symbol] || 0;
          
          if (oldPrice > 0 && price > 0) {
            if (price > oldPrice) {
              newTrends[symbol] = "up";
            } else if (price < oldPrice) {
              newTrends[symbol] = "down";
            } else {
              newTrends[symbol] = priceTrend[symbol] || "neutral";
            }
          } else {
            newTrends[symbol] = "neutral";
          }
          
          if (price > 0) {
            prevPricesRef.current[symbol] = price;
          }

          formatted[symbol] = {
            rawPrice: price,
            price: price > 0 ? price.toLocaleString(undefined, {
              minimumFractionDigits: price < 10 ? 4 : 2,
              maximumFractionDigits: price < 10 ? 6 : 2
            }) : "--",
            change: asset?.signal?.price_change?.toFixed(2) || "0.00",
            signal: asset?.signal?.signal || "HOLD",
            confidence: asset?.signal?.confidence || 0,
            volatility: asset?.volatility?.value || 0,
            news: asset?.news || []
          };
        });

        setPriceTrend(prev => ({ ...prev, ...newTrends }));
        setMarketPrices(formatted);
        setSignals(liveSignals);
      } catch (err) {
        console.error("WebSocket message parse failed", err);
      }
    };
    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!sortedData.length || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    const visibleSymbols = sortedData.map((item) => item.symbol).filter(Boolean);
    if (visibleSymbols.length === 0) return;
    try {
      wsRef.current.send(JSON.stringify({ type: "subscribe", symbols: visibleSymbols }));
    } catch (err) {
      console.error(err);
    }
  }, [sortedData]);

  // news and social feed scraper triggers
  useEffect(() => {
    async function fetchNews() {
      try {
        const activeSymbol = selectedSymbol || displayedAssets[0] || "BTC/USD";
        const res = await fetch(`${BACKEND_URL}/market/news?symbol=${encodeURIComponent(activeSymbol)}`);
        const json = await res.json();
        setNews(json?.articles || []);
      } catch (err) {
        console.error(err);
      }
    }
    fetchNews();
  }, [selectedSymbol, selectedMarket]);

  if (isLoading) {
    return (
      <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#0f0f0f] text-slate-200">
        <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.05),transparent_60%)]" />
        
        <div className="relative z-10 flex flex-col items-center space-y-8 text-center max-w-lg px-6">
          {/* Logo animation */}
          <div className="relative mb-2">
            <div className="absolute -inset-10 rounded-full bg-neutral-500/10 blur-3xl animate-pulse" />
            <img
              src="/logo.png"
              alt="QuantView Logo"
              className="w-56 h-auto relative z-10 animate-pulse duration-[2000ms]"
            />
          </div>
          
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.3em] text-neutral-200 font-bold">
              Cognitive Algorithmic Desk
            </p>
          </div>
          
          {/* Pulsing loading bar */}
          <div className="w-64 h-1.5 rounded-full bg-slate-900 overflow-hidden border border-white/5 relative">
            <div 
              className="h-full bg-gradient-to-r from-neutral-600 to-neutral-200 transition-all duration-300 rounded-full"
              style={{ width: `${loadingProgress}%` }}
            />
          </div>
          
          {/* Real-time Loading Status log */}
          <div className="space-y-1">
            <p className="text-sm font-bold text-slate-300 font-mono tracking-tight animate-pulse">
              {loadingProgress}% Complete
            </p>
            <p className="text-[10px] uppercase font-mono tracking-widest text-slate-500">
              {loadingStatus}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#0f0f0f] text-slate-200 font-sans selection:bg-cyan-500/30">
      
      {/* 1. HERO SECTION */}
      <HeroSection />

      {/* 2. LIVE TERMINAL EXPERIENCE */}
      <div id="live-terminal" className="relative flex flex-col md:flex-row w-full max-w-[1600px] mx-auto min-h-screen border-t border-white/5 bg-[#0f0f0f] z-20 shadow-[0_-40px_100px_rgba(0,0,0,0.8)] pb-[72px] md:pb-0">
        
        {/* DESKTOP Sidebar — hidden on mobile */}
        <div className="hidden md:flex w-64 bg-[#121212]/80 backdrop-blur-xl border-r border-white/5 flex-col z-20 shrink-0 sticky top-0 h-screen overflow-y-auto">
        
          {/* Brand Banner */}
          <div className="p-6 border-b border-white/5 flex flex-col items-start gap-1">
            <img src="/logo.png" alt="QuantView Logo" className="w-40 h-auto" />
            <p className="text-[9px] uppercase tracking-widest text-neutral-200 font-bold pl-1 mt-1">AI Autobot Terminal</p>
          </div>

          <div className="p-4 flex-1 space-y-1.5 overflow-y-auto">
            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold px-3 mb-3">DESK TERMINALS</p>
            {[
              { id: "trader", label: "Auto Trader Bot", icon: <Bot className="w-4 h-4 shrink-0" />, badge: null },
              { id: "analyser", label: "AI Analyser", icon: <Brain className="w-4 h-4 shrink-0" />, badge: null },
              { id: "watchlist", label: "Watchlist Grid", icon: <Star className="w-4 h-4 shrink-0" />, badge: watchlist.length > 0 ? <span className="ml-auto text-xs px-2 py-0.5 rounded-md bg-purple-500/20 text-neutral-200 border border-neutral-500/20">{watchlist.length}</span> : null },
              { id: "settings", label: "Settings Panel", icon: <Settings className="w-4 h-4 shrink-0" />, badge: null },
            ].map((item) => (
              <button key={item.id} onClick={() => setActiveTab(item.id as any)}
                className={`w-full flex items-center gap-3.5 px-4 py-3.5 rounded-2xl transition-all duration-300 font-bold text-sm text-left border ${
                  activeTab === item.id ? "bg-neutral-500/10 border-white/10 text-neutral-200 shadow-[0_0_30px_rgba(168,85,247,0.15)]" : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]"
                }`}>
                {item.icon}<span>{item.label}</span>{item.badge}
              </button>
            ))}
          </div>

          <div className="p-4 border-t border-white/5 bg-[#121212] flex items-center gap-3 text-xs text-slate-400">
            <div className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse shrink-0" />
            <div className="truncate">
              <p className="font-bold text-white text-[10px] uppercase tracking-wider">WebSocket Link</p>
              <p className="text-[9px] text-slate-500">Live Tick Stream Connected</p>
            </div>
          </div>
        </div>

        {/* MOBILE Bottom Navigation Bar */}
        <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-[#121212]/95 backdrop-blur-2xl border-t border-white/10 flex items-stretch safe-area-inset-bottom">
          {[
            { id: "analyser", label: "Markets", icon: <Brain className="w-5 h-5" /> },
            { id: "watchlist", label: "Watchlist", icon: <Star className="w-5 h-5" /> },
            { id: "trader", label: "Trader", icon: <Bot className="w-5 h-5" /> },
            { id: "settings", label: "Settings", icon: <Settings className="w-5 h-5" /> },
          ].map((item) => (
            <button key={item.id} onClick={() => setActiveTab(item.id as any)}
              className={`flex-1 flex flex-col items-center justify-center py-2.5 gap-1 transition-all ${
                activeTab === item.id ? "text-neutral-200" : "text-slate-500"
              }`}>
              {item.icon}
              <span className="text-[9px] font-bold uppercase tracking-wide">{item.label}</span>
              {activeTab === item.id && <span className="w-1 h-1 rounded-full bg-purple-400" />}
            </button>
          ))}
        </div>

      {/* Main workspace (Displays only the active Sidebar SPA Tab) */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-neutral-500/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-white/10 rounded-full blur-[120px] pointer-events-none" />

        {activeTab === "trader" && (
          <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 custom-scrollbar z-10">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-white/5 pb-5">
              <div>
                <h1 className="text-3xl font-black tracking-tight text-white bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
                  cTrader Terminal
                </h1>
                <p className="text-sm text-slate-400 mt-1">
                  Secure local cTrader broker link with real-time execution
                </p>
              </div>
            </div>

            {!mt5BrokerConnected ? (
              // ── Broker Connect Card ──────────────────────────────────────────
              <div className="max-w-md mx-auto my-10 bg-[#161616] border border-white/10 rounded-[32px] p-8 shadow-[0_0_60px_rgba(0,0,0,0.5)] space-y-6">
                <div className="text-center space-y-2">
                  <div className="inline-flex p-4 rounded-3xl bg-emerald-500/10 border border-emerald-500/20 text-white">
                    <Zap className="w-8 h-8" />
                  </div>
                  <h2 className="text-xl font-bold text-white tracking-tight">Connect Trading Account</h2>
                  <p className="text-xs text-slate-400 leading-relaxed max-w-xs mx-auto">
                    Integrate your cTrader broker account. Enter your OAuth2 access token to connect.
                  </p>
                </div>

                {/* ── cTrader Form ─────────────────────────────────────────── */}
                <div className="space-y-4">
                  <div className="p-3 rounded-2xl bg-emerald-500/5 border border-emerald-500/15 text-emerald-300 text-[10px] leading-relaxed space-y-1">
                    <p className="font-bold flex items-center gap-1.5">
                      <Check className="w-3.5 h-3.5 text-white" />
                      Free — No Credits Required
                    </p>
                    <ol className="list-decimal pl-4 space-y-1 text-slate-400">
                      <li>Open an account with IC Markets, Pepperstone, or any cTrader broker</li>
                      <li>Go to <a href="https://openapi.ctrader.com/apps" target="_blank" rel="noreferrer" className="text-white underline font-bold">openapi.ctrader.com/apps</a> → create a free app</li>
                      <li>Visit the auth URL, approve access → paste your <strong>Access Token</strong> below</li>
                    </ol>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] uppercase tracking-wider text-white font-bold">cTrader Access Token</label>
                    <input
                      type="password"
                      value={ctAccessToken}
                      onChange={e => setCtAccessToken(e.target.value.trim())}
                      placeholder="Paste your OAuth2 Access Token"
                      className="w-full px-4 py-3 rounded-2xl bg-black/40 border border-white/10 text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 transition-all text-xs"
                    />
                  </div>

                  <button
                    type="button"
                    disabled={!ctAccessToken || ctConnecting}
                    onClick={async () => {
                      setCtConnecting(true);
                      try {
                        // 1. Fetch accounts
                        const resAcc = await fetch(`${BACKEND_URL}/market/ctrader/accounts/by-token?access_token=${encodeURIComponent(ctAccessToken)}`);
                        const jsonAcc = await resAcc.json();
                        if (jsonAcc.success && jsonAcc.accounts?.length) {
                          const firstAccount = jsonAcc.accounts[0];
                          const accountId = String(firstAccount.accountId || firstAccount.ctidTraderAccountId || "");
                          
                          // 2. Connect
                          const resConn = await fetch(`${BACKEND_URL}/market/ctrader/connect`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ access_token: ctAccessToken, account_id: accountId, volume: 0.01 }),
                          });
                          const jsonConn = await resConn.json();
                          if (resConn.ok && jsonConn.success) {
                            setMt5BrokerConnected(true);
                            setMt5AccountData(jsonConn.account);
                            localStorage.setItem("quantview_ct_token", ctAccessToken);
                            localStorage.setItem("quantview_ct_account_id", accountId);
                          } else {
                            alert(jsonConn.detail || jsonConn.error || "Connection failed");
                          }
                        } else {
                          alert("No accounts found — check your token.");
                        }
                      } catch(e) { alert("Backend connection error."); }
                      finally { setCtConnecting(false); }
                    }}
                    className="w-full py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase tracking-wider shadow-[0_0_30px_rgba(16,185,129,0.3)] transition-all disabled:opacity-40"
                  >
                    {ctConnecting ? (
                      <span className="flex items-center justify-center gap-1.5">
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        Connecting…
                      </span>
                    ) : (
                      "Connect cTrader Account"
                    )}
                  </button>
                </div>
              </div>
            ) : (
              // Live cTrader dashboard
              <div className="space-y-6 animate-in fade-in duration-300">
                {/* Broker account stats (Balance, Equity, Margin) */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                  <div className="rounded-[28px] border border-white/5 bg-[#161616]/80 p-6 relative overflow-hidden backdrop-blur-md">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-neutral-500/10 rounded-full blur-2xl" />
                    <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">cTrader Account Balance</p>
                    <h3 className="text-3xl font-black text-white mt-2 font-mono">
                      ${Number(mt5AccountData?.balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </h3>
                    <p className="text-[10px] text-neutral-200 font-semibold mt-1 uppercase tracking-wide">
                      Currency: {mt5AccountData?.currency || "USD"}
                    </p>
                  </div>

                  <div className="rounded-[28px] border border-white/5 bg-[#161616]/80 p-6 relative overflow-hidden backdrop-blur-md">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full blur-2xl" />
                    <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Account Equity</p>
                    <h3 className="text-3xl font-black text-white mt-2 font-mono">
                      ${Number(mt5AccountData?.equity || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </h3>
                    <p className="text-[10px] text-white font-semibold mt-1 uppercase tracking-wide">
                      Broker: {mt5AccountData?.broker || "cTrader Demo"}
                    </p>
                  </div>

                  <div className="rounded-[28px] border border-white/5 bg-[#161616]/80 p-6 relative overflow-hidden backdrop-blur-md">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl" />
                    <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Free Margin</p>
                    <h3 className="text-3xl font-black text-white mt-2 font-mono">
                      ${Number(mt5AccountData?.freeMargin || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </h3>
                    <p className="text-[10px] text-emerald-500 font-semibold mt-1 uppercase tracking-wide">
                      Margin Level: {Number(mt5AccountData?.marginLevel || 0).toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* Active Open positions */}
                <div className="rounded-[32px] border border-white/5 bg-[#161616] p-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-white">Active cTrader Positions</h3>
                      <p className="text-xs text-slate-400">Ticks live and syncs seamlessly with your cTrader app</p>
                    </div>
                    <span className="px-3 py-1 rounded-full bg-neutral-500/10 text-neutral-200 border border-neutral-500/20 text-[10px] uppercase tracking-wider font-bold">
                      {mt5Positions.length} Open Positions
                    </span>
                  </div>

                  {mt5Positions.length === 0 ? (
                    <div className="py-12 text-center text-slate-500 text-sm border border-dashed border-white/10 rounded-2xl">
                      No active trades currently running on your cTrader account.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {mt5Positions.map((pos) => {
                        const isWin = pos.profit >= 0;
                        return (
                          <div 
                            key={pos.id} 
                            className="bg-black/30 border border-white/5 rounded-2xl p-5 relative overflow-hidden flex flex-col justify-between"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className={`text-[10px] font-black px-2 py-1 rounded-md ${
                                  pos.type === "BUY" ? "bg-white/10 text-white border border-green-500/20" : "bg-neutral-600/10 text-neutral-400 border border-red-500/20"
                                }`}>
                                  {pos.type}
                                </span>
                                <span className="font-bold text-white">{pos.symbol}</span>
                                <span className="text-xs text-slate-500">x{pos.volume} Lots</span>
                              </div>
                              <span className={`text-xl font-black font-mono ${isWin ? "text-white" : "text-neutral-400"}`}>
                                ${pos.profit >= 0 ? "+" : ""}{pos.profit.toFixed(2)}
                              </span>
                            </div>

                            <div className="grid grid-cols-2 gap-2 text-xs text-slate-500 mt-4 pt-4 border-t border-white/5">
                              <div>Open: <span className="text-slate-300 font-mono">{pos.openPrice}</span></div>
                              <div>Current: <span className="text-slate-300 font-mono">{pos.currentPrice}</span></div>
                              <div>SL: <span className="text-slate-300 font-mono">{pos.stopLoss || "None"}</span></div>
                              <div>TP: <span className="text-slate-300 font-mono">{pos.takeProfit || "None"}</span></div>
                            </div>

                            <button
                              onClick={() => closePosition(pos.id)}
                              className="w-full py-2.5 bg-red-950/20 border border-red-500/20 hover:bg-red-900/20 text-neutral-400 font-bold text-xs uppercase rounded-xl transition-all mt-4"
                            >
                              Close Order
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* Quick Trade Desk (manual execution) */}
                <div className="rounded-[32px] border border-white/5 bg-[#161616] p-6 space-y-4">
                  <h3 className="text-md font-bold text-white">Quick Trade Desk</h3>
                  <p className="text-xs text-slate-400">Trigger standard execution orders directly from terminal screen</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex justify-between items-center bg-black/20 p-3.5 rounded-xl border border-white/5">
                      <span className="text-xs text-slate-400">Active Symbol</span>
                      <span className="text-xs font-black text-white">{selectedSymbol || displayedAssets[0] || "XAU/USD"}</span>
                    </div>
                    <div className="flex justify-between items-center bg-black/20 p-3.5 rounded-xl border border-white/5">
                      <span className="text-xs text-slate-400">Volume (Lots)</span>
                      <span className="text-xs font-black text-white">{mt5Volume} Lots</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 pt-2">
                    <button
                      onClick={() => manualTrade("BUY")}
                      className="py-4 bg-green-600/10 border border-green-500/20 hover:bg-green-500/20 text-white font-black text-xs uppercase rounded-2xl transition-all shadow-[0_0_30px_rgba(34,197,94,0.05)]"
                    >
                      Buy Long
                    </button>
                    <button
                      onClick={() => manualTrade("SELL")}
                      className="py-4 bg-red-600/10 border border-red-500/20 hover:bg-red-500/20 text-neutral-400 font-black text-xs uppercase rounded-2xl transition-all shadow-[0_0_30px_rgba(239,68,68,0.05)]"
                    >
                      Sell Short
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-end">
                  <button
                    onClick={() => {
                      localStorage.removeItem("quantview_ct_account_id");
                      localStorage.removeItem("quantview_ct_token");
                      setMt5BrokerConnected(false);
                      setMt5AccountData(null);
                      setMt5Positions([]);
                      playSound("close");
                    }}
                    className="px-4 py-2 bg-red-950/20 border border-red-500/10 hover:bg-red-900/20 text-neutral-400 text-xs font-bold uppercase rounded-xl transition-all"
                  >
                    Disconnect cTrader Broker Link
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: AI MARKET ANALYSER */}
        {activeTab === "analyser" && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header controls bar */}
            <div className="flex flex-col gap-3 px-4 md:px-6 py-4 border-b border-white/5 bg-[#121212]/80 backdrop-blur-xl z-10">
              <div className="flex items-center justify-between">
                <h1 className="text-lg md:text-xl font-bold tracking-tight text-white bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
                  Market Analyser
                </h1>
                <input
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    if (e.target.value.length > 0) setSelectedSymbol(null);
                  }}
                  className="bg-black/40 px-3 py-1.5 rounded-xl outline-none border border-white/10 focus:border-purple-500/50 transition-colors text-xs placeholder:text-slate-600 w-32 md:w-44 font-medium"
                />
              </div>
              {/* Market filter — horizontal scroll on mobile */}
              <div className="flex overflow-x-auto gap-1.5 pb-1 no-scrollbar">
                {["Forex", "Crypto", "Stocks", "Commodities"].map((market) => (
                  <button
                    key={market}
                    onClick={() => handleMarketChange(market)}
                    className={`shrink-0 px-3 py-2 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all border ${
                      selectedMarket === market
                        ? "bg-purple-500/20 text-neutral-200 border-neutral-500/20"
                        : "text-slate-400 border-white/5 bg-black/30"
                    }`}
                  >
                    {market}
                  </button>
                ))}
              </div>
            </div>

            {/* Content Body */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 custom-scrollbar z-10">
              
              {/* Volatility Status ring */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="bg-[#161616]/80 border border-white/5 rounded-2xl p-5 shadow-lg relative overflow-hidden backdrop-blur-md">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-neutral-500/10 rounded-full blur-2xl" />
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Market Category</p>
                  <h2 className="text-2xl font-black mt-1 text-white">{selectedMarket}</h2>
                </div>

                <div className="bg-[#161616]/80 border border-white/5 rounded-2xl p-5 shadow-lg relative overflow-hidden backdrop-blur-md">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full blur-2xl" />
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Analysis Resolution</p>
                  <h2 className="text-2xl font-black mt-1 text-white">5-Minute</h2>
                </div>

                <div className="bg-[#161616]/80 border border-white/5 rounded-2xl p-5 shadow-lg relative overflow-hidden backdrop-blur-md">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl" />
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Tracked Symbols</p>
                  <h2 className="text-2xl font-black mt-1 text-white">{sortedData.length} Assets</h2>
                </div>

                <div className="bg-[#161616]/80 border border-white/5 rounded-2xl p-5 shadow-lg relative overflow-hidden backdrop-blur-md">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-neutral-500/10 rounded-full blur-2xl" />
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Cognitive Engine</p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-purple-400 animate-ping" />
                    <h2 className="text-2xl font-black text-neutral-200 uppercase">LLAMA-3</h2>
                  </div>
                </div>
              </div>

              {/* Watchlist Quick add overlay */}
              {watchlist.length > 0 && (
                <div className="bg-[#161616]/60 border border-white/5 rounded-3xl p-6 space-y-4 shadow-xl backdrop-blur-md">
                  <div>
                    <h2 className="text-md font-bold text-white flex items-center gap-2">
                      <span className="text-amber-400">★</span> Pinned Watchlist Shortcuts
                    </h2>
                    <p className="text-xs text-slate-400 mt-0.5">Quickly select assets to trace technical analysis charts</p>
                  </div>

                  <div className="flex gap-2.5 flex-wrap">
                    {watchlist.map((asset) => {
                      const sig = signals[asset];
                      return (
                        <button
                          key={asset}
                          onClick={() => {
                            setSelectedSymbol(asset);
                            setSearchQuery("");
                          }}
                          className={`flex items-center gap-3.5 px-4.5 py-3 rounded-2xl transition-all duration-300 border ${
                            selectedSymbol === asset
                              ? "bg-neutral-500/10 border-white/10 text-neutral-200 shadow-[0_0_20px_rgba(168,85,247,0.1)]"
                              : "bg-black/30 border-white/5 text-slate-300 hover:bg-black/50"
                          }`}
                        >
                          <img
                            src={getAssetLogo(asset)}
                            alt={asset}
                            className="w-5 h-5 rounded-full bg-slate-900 object-contain p-[1px]"
                          />
                          <span className="font-bold text-xs">{asset}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Asset grid lists */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 items-start">
                {sortedData.map((item) => {
                  const signalData = signals[item.symbol];
                  const priceData = marketPrices[item.symbol];
                  const isPositive = Number(priceData?.change || 0) >= 0;
                  const isPinned = watchlist.includes(item.symbol);

                  return (
                    <div
                      key={item.symbol}
                      className="bg-[#161616]/80 border border-white/5 rounded-[24px] md:rounded-[32px] p-4 md:p-6 hover:border-neutral-500/30 hover:shadow-[0_0_40px_rgba(255,255,255,0.02)] transition-all duration-300 group relative overflow-hidden backdrop-blur-md"
                    >
                      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.01] to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

                      <div className="space-y-6 relative z-10">
                        {/* Header card elements */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <img
                              src={getAssetLogo(item.symbol)}
                              alt={item.symbol}
                              className="w-14 h-14 rounded-full bg-slate-950 object-contain p-1.5 ring-2 ring-slate-800 shadow-xl group-hover:scale-105 transition-transform"
                            />
                            <div>
                              <p className="text-2xl font-black tracking-tight text-white group-hover:text-neutral-200 transition-colors">
                                {item.symbol}
                              </p>
                              <p className="text-[10px] text-slate-500 mt-1 uppercase tracking-wider font-bold">
                                Volatility ATR: {Number(priceData?.volatility || item.volatility?.value || 0).toFixed(1)}%
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                const nextList = isPinned
                                  ? watchlist.filter((w) => w !== item.symbol)
                                  : [...watchlist, item.symbol];
                                setWatchlist(nextList);
                                localStorage.setItem("quantview_watchlist", JSON.stringify(nextList));
                                playSound("toggle");
                              }}
                              className={`p-2.5 rounded-xl border transition-all ${
                                isPinned
                                  ? "bg-amber-500/10 border-amber-500/20 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.15)]"
                                  : "bg-black/30 border-white/5 text-slate-500 hover:text-amber-400"
                              }`}
                            >
                              ★
                            </button>
                            
                            <button
                              onClick={() => router.push(`/asset/${encodeURIComponent(item.symbol.replace("/", "-"))}`)}
                              className="px-4 py-2.5 rounded-xl bg-neutral-500/10 hover:bg-purple-500/20 border border-neutral-500/20 text-neutral-200 font-bold text-xs uppercase transition-all"
                            >
                              Details Terminal
                            </button>
                          </div>
                        </div>

                        {/* Live ticking spot price */}
                        <div className="flex justify-between items-center bg-black/40 p-4 rounded-2xl border border-white/5 relative">
                          <div>
                            <p className="text-[9px] text-slate-500 uppercase tracking-widest font-bold">Realtime Spot Price</p>
                            <p className={`text-2xl md:text-3xl font-black mt-1 font-mono tracking-tighter transition-colors duration-300 ${
                              priceTrend[item.symbol] === "up" ? "text-emerald-400" :
                              priceTrend[item.symbol] === "down" ? "text-red-500" : "text-slate-200"
                            }`}>
                              {priceData?.price || "--"}
                            </p>
                          </div>

                          <div className="text-right">
                            <p className="text-[9px] text-slate-500 uppercase tracking-widest font-bold">Price Change</p>
                            <span className={`inline-flex px-3 py-1 rounded-lg text-xs font-bold mt-1 tracking-wide ${
                              isPositive ? "bg-emerald-500/10 text-white border border-emerald-500/20" : "bg-neutral-600/10 text-neutral-400 border border-red-500/20"
                            }`}>
                              {isPositive ? "+" : ""}{priceData?.change || "0.00"}%
                            </span>
                          </div>
                        </div>

                        {/* Scrolling News Marquee */}
                        {priceData?.news && priceData.news.length > 0 && (
                          <div className="overflow-hidden bg-black/40 border border-white/5 rounded-xl py-2 relative flex items-center">
                            <div className="absolute left-0 w-8 h-full bg-gradient-to-r from-[#0B1120] to-transparent z-10 pointer-events-none" />
                            <div className="absolute right-0 w-8 h-full bg-gradient-to-l from-[#0B1120] to-transparent z-10 pointer-events-none" />
                            
                            <div className="flex whitespace-nowrap animate-marquee">
                              {priceData.news.map((n: any, idx: number) => (
                                <a 
                                  key={idx} 
                                  href={n.link} 
                                  target="_blank" 
                                  rel="noreferrer"
                                  className="inline-flex items-center text-[10px] text-slate-400 hover:text-neutral-200 mx-4 transition-colors gap-1.5"
                                >
                                  <span className={`w-1.5 h-1.5 rounded-full ${
                                    n.sentiment === "Bullish" ? "bg-emerald-400" :
                                    n.sentiment === "Bearish" ? "bg-red-400" : "bg-blue-400"
                                  }`} />
                                  <span className="font-bold text-slate-300">{n.source}:</span>
                                  {n.title}
                                </a>
                              ))}
                              {/* Duplicate the items for seamless scrolling */}
                              {priceData.news.map((n: any, idx: number) => (
                                <a 
                                  key={`dup-${idx}`} 
                                  href={n.link} 
                                  target="_blank" 
                                  rel="noreferrer"
                                  className="inline-flex items-center text-[10px] text-slate-400 hover:text-neutral-200 mx-4 transition-colors gap-1.5"
                                >
                                  <span className={`w-1.5 h-1.5 rounded-full ${
                                    n.sentiment === "Bullish" ? "bg-emerald-400" :
                                    n.sentiment === "Bearish" ? "bg-red-400" : "bg-blue-400"
                                  }`} />
                                  <span className="font-bold text-slate-300">{n.source}:</span>
                                  {n.title}
                                </a>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Toggle Show Signal Parameters */}
                        {expandedSignals.includes(item.symbol) && (
                          <div className="grid grid-cols-2 gap-3 bg-black/20 p-4.5 rounded-2xl border border-white/5 animate-in fade-in duration-200">
                            <div className="bg-[#161616] border border-white/5 rounded-xl p-3">
                              <p className="text-[9px] uppercase tracking-wider text-slate-500 font-bold">Llama-3 Signal</p>
                              <h4 className={`text-md font-black mt-1 ${
                                signalData?.signal === "BUY" ? "text-white" : signalData?.signal === "SELL" ? "text-neutral-400" : "text-neutral-300"
                              }`}>
                                {signalData?.signal || "HOLD"}
                              </h4>
                            </div>

                            <div className="bg-[#161616] border border-white/5 rounded-xl p-3">
                              <p className="text-[9px] uppercase tracking-wider text-slate-500 font-bold">AI Confidence</p>
                              <h4 className="text-md font-black mt-1 text-white font-mono">
                                {signalData?.confidence || 50}%
                              </h4>
                            </div>

                            <div className="bg-[#161616] border border-white/5 rounded-xl p-3">
                              <p className="text-[9px] uppercase tracking-wider text-slate-500 font-bold">RSI (Momentum)</p>
                              <h4 className="text-md font-black mt-1 text-white font-mono">
                                {signalData?.rsi !== undefined ? Number(signalData.rsi).toFixed(2) : "0.00"}
                              </h4>
                            </div>

                            <div className="bg-[#161616] border border-white/5 rounded-xl p-3">
                              <p className="text-[9px] uppercase tracking-wider text-slate-500 font-bold">MACD Trend</p>
                              <h4 className={`text-md font-black mt-1 ${
                                signalData?.macd === "Bullish" ? "text-white" : signalData?.macd === "Bearish" ? "text-neutral-400" : "text-slate-400"
                              }`}>
                                {signalData?.macd || "Neutral"}
                              </h4>
                            </div>
                          </div>
                        )}

                        <div className="flex items-center justify-between border-t border-white/5 pt-4">
                          <div className="flex gap-3 text-[9px] text-slate-500 uppercase tracking-widest font-bold">
                            <span>● Live feeds</span>
                            <span>{selectedMarket}</span>
                          </div>

                          <button
                            onClick={() => toggleSignals(item.symbol)}
                            className={`px-3 py-2 rounded-xl border text-xs font-bold transition-all ${
                              expandedSignals.includes(item.symbol)
                                ? "bg-purple-500/20 text-neutral-200 border-white/10"
                                : "bg-black/40 border-white/10 hover:bg-black/60 text-slate-400"
                            }`}
                          >
                            {expandedSignals.includes(item.symbol) ? "Hide AI Parameters" : "Show AI Parameters"}
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: WATCHLIST GRID IN TRADINGVIEW STYLE */}
        {activeTab === "watchlist" && (
          <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 custom-scrollbar z-10">
            <div>
              <h1 className="text-3xl font-black tracking-tight text-white bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
                Watchlist Charts
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Your pinned institutional chart desks loaded inside customized TradingView grids
              </p>
            </div>

            {watchlist.length === 0 ? (
              <div className="max-w-md mx-auto my-12 text-center space-y-4 py-16 border border-dashed border-white/10 rounded-[32px] p-6 bg-black/10">
                <div className="text-3xl">★</div>
                <h3 className="text-lg font-bold text-white">Watchlist is Empty</h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Go to the <b>AI Analyser</b> page and click the star button next to any symbol to link their institutional charting setups directly to this screen!
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in fade-in duration-300">
                {watchlist.map((symbol) => {
                  const cleanTvSymbol = symbol.replace("/", "").replace("WTI", "USOIL");
                  return (
                    <div 
                      key={symbol}
                      className="rounded-[32px] border border-white/5 bg-[#161616] p-5 space-y-4 h-[440px] flex flex-col justify-between"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <img
                            src={getAssetLogo(symbol)}
                            alt={symbol}
                            className="w-8 h-8 rounded-full bg-slate-900 object-contain p-0.5"
                          />
                          <div>
                            <span className="font-black text-white text-md">{symbol}</span>
                            <span className="ml-2 text-[9px] uppercase tracking-wider font-bold bg-neutral-500/10 text-neutral-200 border border-neutral-500/20 px-2 py-0.5 rounded-md">
                              Live Chart
                            </span>
                          </div>
                        </div>

                        <button
                          onClick={() => {
                            const nextList = watchlist.filter((w) => w !== symbol);
                            setWatchlist(nextList);
                            localStorage.setItem("quantview_watchlist", JSON.stringify(nextList));
                            playSound("close");
                          }}
                          className="text-xs text-slate-500 hover:text-neutral-400 uppercase font-bold"
                        >
                          Remove
                        </button>
                      </div>

                      {/* Customized TradingView Mini widget chart */}
                      <div className="flex-1 w-full rounded-2xl overflow-hidden border border-white/5 bg-[#0f0f0f] relative">
                        <iframe
                          src={`https://s.tradingview.com/widgetembed/?symbol=${encodeURIComponent(cleanTvSymbol)}&interval=5&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=070b16&theme=dark`}
                          width="100%"
                          height="100%"
                          frameBorder="0"
                          className="relative z-10"
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: SETTINGS PANEL */}
        {activeTab === "settings" && (
          <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 custom-scrollbar z-10">
            <div className="border-b border-white/5 pb-5">
              <h1 className="text-3xl font-black tracking-tight text-white bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
                Settings Panel
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Configure execution parameters, Llama-3 quantitative risk limits, and broker connections
              </p>
            </div>

            <div className="max-w-2xl bg-[#161616] border border-white/5 rounded-[32px] p-8 space-y-8 animate-in fade-in duration-300">
              


              {/* Developer stats */}
              <div className="space-y-3 pt-4 border-t border-white/5">
                <h3 className="text-md font-bold text-white">System Diagnostics</h3>
                <div className="bg-black/40 border border-white/5 rounded-2xl p-4.5 font-mono text-[10px] text-slate-400 space-y-2">
                  <div className="flex justify-between">
                    <span>OS Platform:</span>
                    <span className="text-slate-300">macOS (Darwin x64)</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Python API Engine:</span>
                    <span className="text-neutral-200">TwelveData + tvDatafeed sync</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Llama-3 cognitive latency:</span>
                    <span className="text-white">~240ms (High-Speed Groq)</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Simulated Sound Driver:</span>
                    <span className="text-slate-300">HTML5 Web Audio API synthesizers active</span>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )}

      </div>
    </div>
    </div>
  );
}