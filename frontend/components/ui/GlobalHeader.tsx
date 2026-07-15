"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, Home, X, ChevronRight } from "lucide-react";

const marketSymbols: Record<string, { symbol: string; name: string; exchange: string }[]> = {
  Forex: [
    { symbol: "EUR/USD", name: "Euro / US Dollar", exchange: "FX_IDC" },
    { symbol: "GBP/USD", name: "British Pound / US Dollar", exchange: "FX_IDC" },
    { symbol: "USD/JPY", name: "US Dollar / Japanese Yen", exchange: "FX_IDC" },
    { symbol: "USD/CHF", name: "US Dollar / Swiss Franc", exchange: "FX_IDC" },
    { symbol: "AUD/USD", name: "Australian Dollar / US Dollar", exchange: "FX_IDC" },
    { symbol: "USD/CAD", name: "US Dollar / Canadian Dollar", exchange: "FX_IDC" },
    { symbol: "NZD/USD", name: "New Zealand Dollar / US Dollar", exchange: "FX_IDC" },
    { symbol: "EUR/GBP", name: "Euro / British Pound", exchange: "FX_IDC" },
    { symbol: "EUR/JPY", name: "Euro / Japanese Yen", exchange: "FX_IDC" },
    { symbol: "GBP/JPY", name: "British Pound / Japanese Yen", exchange: "FX_IDC" },
    { symbol: "EUR/AUD", name: "Euro / Australian Dollar", exchange: "FX_IDC" },
  ],
  Crypto: [
    { symbol: "BTC/USD", name: "Bitcoin / US Dollar", exchange: "BINANCE" },
    { symbol: "ETH/USD", name: "Ethereum / US Dollar", exchange: "BINANCE" },
    { symbol: "SOL/USD", name: "Solana / US Dollar", exchange: "BINANCE" },
    { symbol: "XRP/USD", name: "Ripple / US Dollar", exchange: "BINANCE" },
    { symbol: "DOGE/USD", name: "Dogecoin / US Dollar", exchange: "BINANCE" },
    { symbol: "ADA/USD", name: "Cardano / US Dollar", exchange: "BINANCE" },
    { symbol: "BNB/USD", name: "Binance Coin / US Dollar", exchange: "BINANCE" },
  ],
  Stocks: [
    { symbol: "AAPL", name: "Apple Inc.", exchange: "NASDAQ" },
    { symbol: "TSLA", name: "Tesla Inc.", exchange: "NASDAQ" },
    { symbol: "NVDA", name: "NVIDIA Corporation", exchange: "NASDAQ" },
    { symbol: "MSFT", name: "Microsoft Corporation", exchange: "NASDAQ" },
    { symbol: "AMZN", name: "Amazon.com Inc.", exchange: "NASDAQ" },
    { symbol: "META", name: "Meta Platforms Inc.", exchange: "NASDAQ" },
    { symbol: "GOOGL", name: "Alphabet Inc.", exchange: "NASDAQ" },
    { symbol: "NFLX", name: "Netflix Inc.", exchange: "NASDAQ" },
    { symbol: "AMD", name: "Advanced Micro Devices", exchange: "NASDAQ" },
  ],
  Commodities: [
    { symbol: "XAU/USD", name: "Gold / US Dollar", exchange: "TVC" },
    { symbol: "XAG/USD", name: "Silver / US Dollar", exchange: "OANDA" },
    { symbol: "WTI", name: "Crude Oil WTI", exchange: "FX" },
    { symbol: "COPPER", name: "Copper Futures", exchange: "COMEX" },
  ],
};

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
  return "https://cdn-icons-png.flaticon.com/512/2830/2830284.png";
};

export function GlobalHeader() {
  const router = useRouter();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"All" | "Stocks" | "Forex" | "Crypto" | "Commodities">("All");
  
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isSearchOpen) {
      setTimeout(() => searchInputRef.current?.focus(), 100);
    }
  }, [isSearchOpen]);

  // Handle hotkey (Cmd+K or Ctrl+K) to open search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsSearchOpen(true);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const getFilteredAssets = () => {
    let list: { symbol: string; name: string; exchange: string; category: string }[] = [];
    
    Object.entries(marketSymbols).forEach(([category, items]) => {
      items.forEach(item => {
        list.push({ ...item, category });
      });
    });

    // Filter by tab
    if (activeTab !== "All") {
      list = list.filter(item => item.category === activeTab);
    }

    // Filter by search query
    if (searchQuery.trim() !== "") {
      const query = searchQuery.toLowerCase();
      list = list.filter(item => 
        item.symbol.toLowerCase().includes(query) || 
        item.name.toLowerCase().includes(query) ||
        item.exchange.toLowerCase().includes(query)
      );
    }

    return list;
  };

  const handleSelectAsset = (symbol: string) => {
    setIsSearchOpen(false);
    setSearchQuery("");
    router.push(`/asset/${encodeURIComponent(symbol.replace("/", "-"))}`);
  };

  return (
    <>
      {/* Global Header Bar */}
      <header className="fixed top-0 left-0 right-0 z-40 h-16 bg-[#0f0f0f]/70 backdrop-blur-md border-b border-white/5 px-6 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <button onClick={() => router.push("/")} className="flex items-center gap-2.5 focus:outline-none">
            <img src="/logo.png" alt="QuantView Logo" className="h-10 w-auto object-contain" />
          </button>
          
          <nav className="hidden md:flex items-center gap-6">
            <button 
              onClick={() => router.push("/")}
              className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-300 hover:text-white transition-colors"
            >
              <Home className="w-4 h-4" /> Home
            </button>
            <button 
              onClick={() => setIsSearchOpen(true)}
              className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-300 hover:text-white transition-colors"
            >
              <Search className="w-4 h-4" /> Search Assets
            </button>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsSearchOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-slate-400 text-xs transition-all"
          >
            <Search className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Search...</span>
            <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-black/40 border border-white/10 text-[9px] font-mono">
              ⌘K
            </kbd>
          </button>
        </div>
      </header>

      {/* TradingView-Style Search Dropdown Modal */}
      {isSearchOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-black/85 backdrop-blur-sm transition-all duration-300">
          {/* Modal Backdrop closer */}
          <div className="absolute inset-0" onClick={() => setIsSearchOpen(false)} />

          <div className="relative w-full max-w-2xl bg-[#161616] border border-white/10 rounded-2xl shadow-[0_30px_100px_rgba(0,0,0,0.8)] overflow-hidden flex flex-col max-h-[500px]">
            
            {/* Search Header */}
            <div className="p-4 border-b border-white/5 flex items-center gap-3 bg-black/20">
              <Search className="w-5 h-5 text-slate-400 shrink-0" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Symbol, Name, or Exchange..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent text-sm text-white placeholder-slate-500 outline-none"
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery("")} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Category Tab Selector */}
            <div className="flex px-4 py-2 border-b border-white/5 gap-1.5 overflow-x-auto no-scrollbar bg-black/10">
              {(["All", "Stocks", "Forex", "Crypto", "Commodities"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                    activeTab === tab 
                      ? "bg-purple-500/20 text-neutral-200 border border-neutral-500/20 shadow-lg"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Results list */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-0.5">
              {getFilteredAssets().length === 0 ? (
                <div className="py-12 text-center text-slate-500 text-xs font-medium">
                  No assets found matching "{searchQuery}"
                </div>
              ) : (
                getFilteredAssets().map((item) => (
                  <button
                    key={item.symbol}
                    onClick={() => handleSelectAsset(item.symbol)}
                    className="w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-white/[0.03] border border-transparent hover:border-white/5 text-left transition-all duration-200 group"
                  >
                    <div className="flex items-center gap-4 min-w-0">
                      <img
                        src={getAssetLogo(item.symbol)}
                        alt={item.symbol}
                        className="w-8 h-8 rounded-full bg-slate-900 object-contain p-0.5 border border-white/10 shrink-0"
                      />
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white group-hover:text-neutral-200 transition-colors text-sm">
                            {item.symbol}
                          </span>
                          <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-white/5 text-slate-500 tracking-wider">
                            {item.category}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 truncate mt-0.5">
                          {item.name}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <span className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">
                        {item.exchange}
                      </span>
                      <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-white transition-colors" />
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
