"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Brain, Settings, TrendingUp, TrendingDown, Scale, Star, MousePointerClick, Lock, Unlock } from "lucide-react";
import { motion } from "framer-motion";

export default function AssetPage() {
  const router = useRouter();
  const params = useParams<{ symbol: string }>();
  const rawSymbol = params?.symbol ? decodeURIComponent(params.symbol) : "EUR/USD";
  const symbol = rawSymbol.includes("-") && !rawSymbol.includes("/") ? rawSymbol.replace("-", "/") : rawSymbol;

  const scrollReveal = {
    initial: { opacity: 0, y: 30 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, margin: "-100px" },
    transition: { duration: 0.6, ease: "easeOut" as any }
  };

  const getTradingViewSymbol = (raw: string) => {
    const clean = raw.replace("/", "");

    const forexPairs = [
      "EURUSD",
      "GBPUSD",
      "USDJPY",
      "USDCHF",
      "AUDUSD",
      "USDCAD",
      "NZDUSD",
      "EURGBP",
      "EURJPY",
      "GBPJPY",
      "EURAUD",
      "EURCAD",
      "CHFJPY",
      "AUDJPY",
      "CADJPY",
      "NZDJPY",
    ];

    const cryptoPairs = [
      "BTCUSD",
      "ETHUSD",
      "SOLUSD",
      "XRPUSD",
      "DOGEUSD",
      "ADAUSD",
      "BNBUSD",
      "AVAXUSD",
      "DOTUSD",
      "LINKUSD",
      "MATICUSD",
    ];

    const commodities: Record<string, string> = {
      BRENT: "TVC:UKOIL",
      WTI: "TVC:USOIL",
      NATGAS: "TVC:NATGAS",
      COPPER: "COMEX:HG1!",
      PLATINUM: "TVC:PLATINUM",
      PALLADIUM: "TVC:PALLADIUM",
      XAUUSD: "OANDA:XAUUSD",
      XAGUSD: "OANDA:XAGUSD",
    };

    if (forexPairs.includes(clean)) {
      return `OANDA:${clean}`;
    }

    if (cryptoPairs.includes(clean)) {
      return `BINANCE:${clean.replace("USD", "USDT")}`;
    }

    if (commodities[clean as keyof typeof commodities]) {
      return commodities[clean as keyof typeof commodities];
    }

    return `NASDAQ:${clean}`;
  };

  const tradingViewSymbol = getTradingViewSymbol(symbol);

  const getAssetLogo = (raw: string) => {
    const clean = raw.replace("/", "").replace("-", "");

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
      INTC: "https://s3-symbol-logo.tradingview.com/intel--big.svg",
      UBER: "https://s3-symbol-logo.tradingview.com/uber-technologies--big.svg",
      COIN: "https://s3-symbol-logo.tradingview.com/coinbase--big.svg",
      XAUUSD: "https://s3-symbol-logo.tradingview.com/metal/gold--big.svg",
      XAGUSD: "https://s3-symbol-logo.tradingview.com/metal/silver--big.svg",
    };

    if (logoMap[clean]) {
      return logoMap[clean];
    }

    // forex fallback logos
    if (clean.includes("USD") || clean.includes("JPY") || clean.includes("EUR")) {
      return "https://s3-symbol-logo.tradingview.com/country/US--big.svg";
    }

    // commodity fallback
    if (clean.includes("XAU") || clean.includes("XAG")) {
      return "https://s3-symbol-logo.tradingview.com/metal/gold--big.svg";
    }

    // stock fallback
    return "https://s3-symbol-logo.tradingview.com/apple--big.svg";
  };

  const getAssetType = (asset: string) => {
    if (
      asset.includes("BTC") ||
      asset.includes("ETH") ||
      asset.includes("SOL")
    ) {
      return "Crypto";
    }

    if (
      asset.includes("XAU") ||
      asset.includes("XAG") ||
      asset === "BRENT"
    ) {
      return "Commodity";
    }

    return "Forex";
  };

  const isLiveAsset = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "XAU/USD",
    "BTC/USD",
    "ETH/USD",
  ].includes(symbol);

  const relatedAssets: Record<string, string[]> = {
    "EUR/USD": ["GBP/USD", "USD/JPY", "XAU/USD", "EUR/JPY"],
    "GBP/USD": ["EUR/USD", "USD/JPY", "GBP/JPY", "XAU/USD"],
    "USD/JPY": ["EUR/USD", "GBP/JPY", "XAU/USD", "AUD/JPY"],
    "BTC/USD": ["ETH/USD", "SOL/USD", "XRP/USD", "DOGE/USD"],
    "ETH/USD": ["BTC/USD", "SOL/USD", "ADA/USD", "BNB/USD"],
    "XAU/USD": ["XAG/USD", "EUR/USD", "USD/JPY", "BTC/USD"],
  };

  const suggestedAssets =
    relatedAssets[symbol] || [
      "EUR/USD",
      "BTC/USD",
      "XAU/USD",
      "ETH/USD",
    ];

  const [assetData, setAssetData] = useState<any>(null);
  const [priceTrend, setPriceTrend] = useState<"up" | "down" | "neutral">("neutral");
  const prevPriceRef = useRef<number>(0);
  const [visibleNewsCount, setVisibleNewsCount] = useState(3);
  const [visibleEventsCount, setVisibleEventsCount] = useState(3);
  const [isLoading, setIsLoading] = useState(true);
  const [chartLocked, setChartLocked] = useState(true);
  const [fetchFailed, setFetchFailed] = useState(false);
  const signal = assetData?.signal;
  const formattedRsi = signal?.rsi !== undefined && signal?.rsi !== null
    ? parseFloat(signal.rsi).toFixed(2)
    : "0.00";
  const bullishScore = signal?.signal === "BUY"
    ? signal?.confidence || 75
    : signal?.signal === "SELL"
    ? 100 - (signal?.confidence || 75)
    : 50;

  const gaugeRotation = (bullishScore / 100) * 180 - 90;
  const news = assetData?.news || [];
  const marketPulse = assetData?.market_pulse;
  const volatility = assetData?.volatility;
  const economicEvents = assetData?.economic_events || [];
  const positioning = assetData?.positioning;

  const socialPosts = assetData?.social_posts?.length
    ? assetData.social_posts
    : assetData?.social_feed?.posts || [];
  const [selectedTimeframe, setSelectedTimeframe] = useState("5m");
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [isSaved, setIsSaved] = useState(false);
  const [customLayoutId, setCustomLayoutId] = useState<string>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("quantview_custom_layout_id") || "";
    }
    return "";
  });
  const [isLayoutModalOpen, setIsLayoutModalOpen] = useState(false);

  // Unified asset refresh
  useEffect(() => {
    let isMounted = true;

    async function fetchAssetData() {
      const intervalMap: Record<string, string> = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "1H": "1h",
      };

      const apiInterval = intervalMap[selectedTimeframe] || "5min";

      try {
        const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || (typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1:8000");
        const res = await fetch(
          `${BACKEND_URL}/market/asset/details?symbol=${encodeURIComponent(symbol)}&interval=${apiInterval}`,
          {
            cache: "no-store",
          }
        );

        if (!res.ok) {
          throw new Error("Asset fetch failed");
        }

        const json = await res.json();

        if (!isMounted) return;

        const price = Number(json.price || 0);
        const oldPrice = prevPriceRef.current;
        if (oldPrice > 0 && price > 0) {
          if (price > oldPrice) {
            setPriceTrend("up");
          } else if (price < oldPrice) {
            setPriceTrend("down");
          }
        }
        if (price > 0) {
          prevPriceRef.current = price;
        }

        setFetchFailed(false);
        setAssetData(json);
        setIsLoading(false);
      } catch (err) {
        if (!isMounted) return;

        setFetchFailed(true);
        setIsLoading(false);
        console.error(err);
      }
    }

    setIsLoading(true);
    fetchAssetData();

    const intervalId = setInterval(() => {
      fetchAssetData();
    }, 15000);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [symbol, selectedTimeframe]);

  // Watchlist persistence
  useEffect(() => {
    const stored = localStorage.getItem("quantview_watchlist");

    if (stored) {
      const parsed = JSON.parse(stored);
      setWatchlist(parsed);
      setIsSaved(parsed.includes(symbol));
    }
  }, [symbol]);

  const toggleWatchlist = () => {
    let updated = [...watchlist];

    if (updated.includes(symbol)) {
      updated = updated.filter((item) => item !== symbol);
      setIsSaved(false);
    } else {
      updated.push(symbol);
      setIsSaved(true);
    }

    setWatchlist(updated);
    localStorage.setItem(
      "quantview_watchlist",
      JSON.stringify(updated)
    );
  };

  return (
    <div className="min-h-screen bg-[#0f0f0f] text-white p-3 md:p-6 space-y-6 overflow-x-hidden">
      {isLoading && (
        <div className="fixed top-4 right-4 z-50 px-4 py-2 rounded-xl bg-blue-500/20 border border-white/10 text-neutral-200 text-sm backdrop-blur-md">
          Loading market data...
        </div>
      )}

      {/* Header */}
      <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-[#161616]/90 backdrop-blur-3xl p-6 md:p-8 lg:p-10 shadow-[0_0_120px_rgba(255,255,255,0.03)]">

        <div
          className="absolute inset-0 opacity-40 pointer-events-none bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.06),transparent_40%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.02),transparent_35%)]"
        />

        <div className="absolute -top-32 -right-20 w-80 h-80 rounded-full blur-3xl opacity-5 bg-white pointer-events-none" />
        <div className="absolute -bottom-32 -left-20 w-80 h-80 rounded-full blur-3xl opacity-5 bg-white pointer-events-none" />

        <div className="relative z-10 flex flex-col gap-8">
          
          {/* Top Row: Info and Buttons */}
          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-8">
            
            {/* Logo and Titles */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-6 md:gap-8">
              <div className="relative w-24 h-24 md:w-32 md:h-32 rounded-[30px] bg-white/95 p-5 flex items-center justify-center shadow-[0_0_60px_rgba(255,255,255,0.14)] shrink-0 overflow-hidden border border-white/20">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.4),transparent_45%)]" />
                <img
                  src={getAssetLogo(symbol)}
                  alt={symbol}
                  className="w-full h-full object-contain relative z-10"
                  onError={(e) => {
                    (e.currentTarget as HTMLImageElement).src =
                      "https://s3-symbol-logo.tradingview.com/country/US--big.svg";
                  }}
                />
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex items-center gap-3 flex-wrap mb-2">
                    <span className="px-3 py-1 rounded-full border border-cyan-500/20 bg-white/10 text-white text-[11px] uppercase tracking-[0.25em] font-semibold">
                      {getAssetType(symbol)} MARKET
                    </span>
                    <span className="px-3 py-1 rounded-full border border-neutral-500/20 bg-neutral-500/10 text-neutral-200 text-[11px] uppercase tracking-[0.25em] font-semibold animate-pulse">
                      AI ACTIVE
                    </span>
                  </div>

                  <h1 className="text-3xl sm:text-5xl md:text-7xl font-black tracking-tight leading-none bg-gradient-to-r from-white via-neutral-200 to-neutral-400 bg-clip-text text-transparent">
                    {symbol}
                  </h1>
                  {assetData?.price !== undefined && (
                    <div className="flex items-center gap-2 mt-3">
                      <span className="text-xs uppercase tracking-[0.2em] text-slate-400 font-semibold">Spot Price:</span>
                      <span className={`text-2xl sm:text-3xl font-black font-mono transition-colors duration-300 ${
                        priceTrend === "up" ? "text-white" :
                        priceTrend === "down" ? "text-neutral-400" : "text-slate-200"
                      }`}>
                        {assetData.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 5 })}
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-4 flex-wrap">
                  <div
                    className={`px-4 py-2 rounded-2xl text-sm font-semibold border backdrop-blur-xl shadow-lg ${
                      isLiveAsset
                        ? "bg-white/10 text-white border-white/10 shadow-[0_0_30px_rgba(255,255,255,0.05)]"
                        : "bg-neutral-500/10 text-neutral-300 border-white/10 shadow-[0_0_30px_rgba(255,255,255,0.05)]"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-2 h-2 rounded-full animate-pulse ${
                          isLiveAsset ? "bg-green-400" : "bg-yellow-400"
                        }`}
                      />
                      {isLiveAsset ? "LIVE MARKET" : "DELAYED FEED"}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex items-center gap-4 sm:ml-auto">
              <button
                onClick={toggleWatchlist}
                className={`px-6 py-3.5 rounded-2xl border transition-all duration-300 font-semibold backdrop-blur-xl hover:scale-[1.02] whitespace-nowrap flex items-center gap-2 ${
                  isSaved
                    ? "bg-neutral-500/10 text-neutral-300 border-white/10 shadow-[0_0_20px_rgba(250,204,21,0.15)]"
                    : "bg-[#161616] text-slate-300 border-white/5 hover:bg-[#262626] hover:text-white"
                }`}
              >
                <Star className={`w-4 h-4 ${isSaved ? "fill-yellow-400 text-neutral-300" : "text-slate-400"}`} />
                {isSaved ? "Watchlisted" : "Add Watchlist"}
              </button>

              <button
                onClick={() => window.history.back()}
                className="px-6 py-3.5 rounded-2xl bg-black/30 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-300 backdrop-blur-xl hover:scale-[1.02] text-slate-300 hover:text-white whitespace-nowrap"
              >
                Back
              </button>
            </div>
            
          </div>

          {/* Bottom Row: Info Pills and Stats Grid */}
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-end">
            
            {/* Info Pills */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 xl:col-span-5 w-full">
              <div className="rounded-2xl border border-white/5 bg-black/40 backdrop-blur-xl p-4 transition-colors hover:bg-black/60">
                <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-semibold">
                  Intelligence Engine
                </p>
                <div className="text-sm font-bold text-white truncate">
                  Institutional AI
                </div>
              </div>

              <div className="rounded-2xl border border-white/5 bg-black/40 backdrop-blur-xl p-4 transition-colors hover:bg-black/60">
                <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-semibold">
                  Data Feed
                </p>
                <div className="text-sm font-bold text-white truncate">
                  {isLiveAsset ? "Live WebSocket" : "Delayed API"}
                </div>
              </div>

              <div className="rounded-2xl border border-white/5 bg-black/40 backdrop-blur-xl p-4 transition-colors hover:bg-black/60 col-span-2 sm:col-span-1">
                <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-semibold">
                  Active Timeframe
                </p>
                <div className="text-sm font-bold text-white truncate">
                  {selectedTimeframe}
                </div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 xl:col-span-7 w-full">
              <div className="rounded-[24px] border border-white/10 bg-[#161616]/80 backdrop-blur-2xl p-5 overflow-hidden relative shadow-lg group hover:border-white/10 transition-colors">
                <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_50%)] group-hover:opacity-40 transition-opacity" />
                <div className="relative z-10">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400 mb-2 font-semibold">
                    Market Bias
                  </p>
                  <div className={`text-2xl sm:text-3xl font-black tracking-tight ${
                    signal?.signal === "BUY"
                      ? "text-white drop-shadow-[0_0_10px_rgba(34,197,94,0.3)]"
                      : signal?.signal === "SELL"
                      ? "text-neutral-400 drop-shadow-[0_0_10px_rgba(239,68,68,0.3)]"
                      : "text-neutral-300 drop-shadow-[0_0_10px_rgba(250,204,21,0.3)]"
                  }`}>
                    {signal?.signal || "HOLD"}
                  </div>
                </div>
              </div>

              <div className="rounded-[24px] border border-white/10 bg-[#161616]/80 backdrop-blur-2xl p-5 overflow-hidden relative shadow-lg group hover:border-white/10 transition-colors">
                <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_50%)] group-hover:opacity-40 transition-opacity" />
                <div className="relative z-10">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400 mb-2 font-semibold">
                    AI Confidence
                  </p>
                  <div className="text-2xl sm:text-3xl font-black text-white tracking-tight drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]">
                    {signal?.confidence || 0}%
                  </div>
                </div>
              </div>

              <div className="rounded-[24px] border border-white/10 bg-[#161616]/80 backdrop-blur-2xl p-5 overflow-hidden relative shadow-lg group hover:border-neutral-500/30 transition-colors">
                <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_50%)] group-hover:opacity-40 transition-opacity" />
                <div className="relative z-10">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400 mb-2 font-semibold">
                    Momentum
                  </p>
                  <div className="text-2xl sm:text-3xl font-black text-neutral-200 tracking-tight drop-shadow-[0_0_10px_rgba(168,85,247,0.3)]">
                    {formattedRsi}
                  </div>
                </div>
              </div>
              
              <div className="rounded-[24px] border border-white/10 bg-[#161616]/80 backdrop-blur-2xl p-5 overflow-hidden relative shadow-lg group transition-colors">
                <div className="relative z-10">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400 mb-2 font-semibold">
                    Market State
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-400 animate-pulse shadow-[0_0_10px_rgba(250,204,21,0.5)]" />
                    <div className="text-sm font-bold text-neutral-300 uppercase tracking-widest drop-shadow-[0_0_10px_rgba(250,204,21,0.3)]">
                      ACTIVE
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>

      {/* Scrolling News Marquee */}
      {news && news.length > 0 && (
        <div className="overflow-hidden bg-[#161616]/80 border border-white/10 rounded-2xl py-3 px-4 relative flex items-center shadow-[0_0_50px_rgba(255,255,255,0.02)] backdrop-blur-3xl">
          <div className="absolute left-0 w-16 h-full bg-gradient-to-r from-[#0f0f0f] to-transparent z-10 pointer-events-none" />
          <div className="absolute right-0 w-16 h-full bg-gradient-to-l from-[#0f0f0f] to-transparent z-10 pointer-events-none" />
          
          <div className="flex whitespace-nowrap animate-marquee">
            {news.map((n: any, idx: number) => (
              <a 
                key={idx} 
                href={n.link || "#"} 
                target="_blank" 
                rel="noreferrer"
                className="inline-flex items-center text-xs text-slate-400 hover:text-neutral-200 mx-6 transition-colors gap-2"
              >
                <span className={`w-2 h-2 rounded-full shrink-0 ${
                  n.sentiment === "Bullish" ? "bg-emerald-400" :
                  n.sentiment === "Bearish" ? "bg-red-400" : "bg-blue-400"
                }`} />
                <span className="font-bold text-slate-200">{n.source || "Finance News"}:</span>
                <span>{n.title}</span>
              </a>
            ))}
            {/* Duplicate the items for seamless scrolling */}
            {news.map((n: any, idx: number) => (
              <a 
                key={`dup-${idx}`} 
                href={n.link || "#"} 
                target="_blank" 
                rel="noreferrer"
                className="inline-flex items-center text-xs text-slate-400 hover:text-neutral-200 mx-6 transition-colors gap-2"
              >
                <span className={`w-2 h-2 rounded-full shrink-0 ${
                  n.sentiment === "Bullish" ? "bg-emerald-400" :
                  n.sentiment === "Bearish" ? "bg-red-400" : "bg-blue-400"
                }`} />
                <span className="font-bold text-slate-200">{n.source || "Finance News"}:</span>
                <span>{n.title}</span>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Timeframe Selector */}
      <div className="flex gap-2 flex-wrap">
        {["1m", "5m", "15m", "1H"].map((tf) => (
          <button
            key={tf}
            onClick={() => setSelectedTimeframe(tf)}
            className={`px-3 py-2 rounded-lg border border-white/5 text-sm transition-colors ${
              selectedTimeframe === tf
                ? "bg-blue-500/20 text-neutral-200"
                : "bg-[#121212] hover:bg-[#262626]"
            }`}
          >
            {tf}
          </button>
        ))}
      </div>

      {/* Watchlist Preview */}
      {watchlist.length > 0 && (
        <div className="bg-[#121212] border border-white/5 rounded-xl p-4 space-y-3">

          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Quick Watchlist</h2>
            <p className="text-xs text-gray-500">
              Persistent local trading workspace
            </p>
          </div>

          <div className="flex gap-2 flex-wrap">
            {watchlist.map((item) => (
              <button
                key={item}
                onClick={() => {
                  router.push(`/asset/${encodeURIComponent(item.replace("/", "-"))}`);
                }}
                className={`px-4 py-2 rounded-lg border text-sm transition-colors ${
                  item === symbol
                    ? "bg-blue-500/20 text-neutral-200 border-white/10"
                    : "bg-[#161616] border-white/5 hover:bg-[#262626]"
                }`}
              >
                {item}
              </button>
            ))}
          </div>

        </div>
      )}

      {/* Signal Cards */}
      <motion.div {...scrollReveal} className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">

        <div className="relative overflow-hidden rounded-[30px] border border-white/10 bg-[#161616]/90 backdrop-blur-2xl p-6 shadow-[0_0_60px_rgba(255,255,255,0.02)]">

          <div
            className={`absolute inset-0 opacity-50 ${
              signal?.signal === "BUY"
                ? "bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_40%)]"
                : signal?.signal === "SELL"
                ? "bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_40%)]"
                : "bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_40%)]"
            }`}
          />

          <div className="relative z-10 flex items-start justify-between">

            <div>
              <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                AI SIGNAL
              </p>

              <h2
                className={`text-3xl sm:text-4xl md:text-5xl font-bold mt-5 ${
                  signal?.signal === "BUY"
                    ? "text-white"
                    : signal?.signal === "SELL"
                    ? "text-neutral-400"
                    : "text-neutral-300"
                }`}
              >
                {signal?.signal || "HOLD"}
              </h2>
            </div>

            <div
              className={`w-14 h-14 rounded-2xl border flex items-center justify-center text-2xl ${
                signal?.signal === "BUY"
                  ? "bg-white/10 border-green-500/20 text-white"
                  : signal?.signal === "SELL"
                  ? "bg-neutral-600/10 border-red-500/20 text-neutral-400"
                  : "bg-neutral-500/10 border-yellow-500/20 text-neutral-300"
              }`}
            >
              {signal?.signal === "BUY"
                ? "↑"
                : signal?.signal === "SELL"
                ? "↓"
                : "→"}
            </div>

          </div>

          <div className="relative z-10 mt-8 flex items-center justify-between text-sm text-gray-500 border-t border-white/5 pt-4">
            <span>Institutional AI Engine</span>
            <span className="text-white">LIVE</span>
          </div>

        </div>

        <div className="relative overflow-hidden rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6">

          <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_40%)]" />

          <div className="relative z-10 flex items-center justify-center h-full">

            <div className="relative w-52 h-52 rounded-full overflow-hidden flex items-center justify-center border border-neutral-500/20 shadow-[0_0_60px_rgba(255,255,255,0.03)]">

              <div
                className="absolute inset-0 rounded-full"
                style={{
                  background: `conic-gradient(#ffffff ${(signal?.confidence || 0) * 3.6}deg, rgba(255,255,255,0.06) 0deg)`,
                }}
              />

              <div className="absolute inset-[18px] rounded-full bg-[#050816] border border-white/5 backdrop-blur-xl" />

              <div className="relative z-10 text-center space-y-2">
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  Confidence
                </p>

                <div className="text-3xl sm:text-4xl md:text-5xl font-bold text-white">
                  {signal?.confidence || 0}%
                </div>

                <div className="text-xs text-neutral-200">
                  AI Probability
                </div>
              </div>

            </div>

          </div>

        </div>

        <div className="relative overflow-hidden rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6">

          <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_40%)]" />

          <div className="relative z-10 space-y-8">

            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  RSI MOMENTUM
                </p>

                <div className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mt-4">
                  {formattedRsi}
                </div>
              </div>

              <div className="w-14 h-14 rounded-2xl bg-white/10 border border-blue-500/20 flex items-center justify-center text-neutral-200 text-2xl">
                ≋
              </div>
            </div>

            <div className="space-y-3">

              <div className="flex items-center justify-between text-xs text-gray-500 uppercase tracking-wide">
                <span>Momentum Strength</span>
                <span>{formattedRsi}/100</span>
              </div>

              <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-neutral-800 via-neutral-400 to-white"
                  style={{
                    width: `${formattedRsi}%`,
                  }}
                />
              </div>

            </div>

          </div>

        </div>

        <div className="relative overflow-hidden rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6">

          <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_40%)]" />

          <div className="relative z-10 flex flex-col justify-between h-full">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  MACD TREND
                </p>

                <div className="text-4xl font-bold text-white mt-4 leading-tight">
                  {signal?.macd || "Neutral"}
                </div>
              </div>

              <div className="w-14 h-14 rounded-2xl bg-white/10 border border-cyan-500/20 flex items-center justify-center text-white text-2xl">
                ∿
              </div>

            </div>

            <div className="mt-8 rounded-2xl border border-white/5 bg-black/20 p-4 backdrop-blur-xl">
              <div className="flex items-center justify-between text-xs text-gray-500 uppercase tracking-wide mb-3">
                <span>Trend Energy</span>
                <span>Realtime</span>
              </div>

              <div className="flex items-end gap-1 h-16">
                {[35, 52, 44, 70, 58, 80, 65, 90].map((bar, idx) => (
                  <div
                    key={idx}
                    className="flex-1 rounded-t-xl bg-gradient-to-t from-neutral-600 to-neutral-200 animate-pulse"
                    style={{
                      height: `${bar}%`,
                      animationDelay: `${idx * 0.1}s`,
                    }}
                  />
                ))}
              </div>
            </div>

          </div>

        </div>

      </motion.div>

      {/* AI Reasoning Container */}
      {signal?.is_real_ai && signal?.ai_reasoning && (
        <motion.div {...scrollReveal} className="relative overflow-hidden rounded-[30px] border border-blue-500/20 bg-[#161616]/90 backdrop-blur-2xl p-6 md:p-8 shadow-[0_0_60px_rgba(255,255,255,0.04)] group transition-all hover:border-blue-400/40">
          <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.04),transparent_70%)] group-hover:opacity-60 transition-opacity" />
          
          <div className="relative z-10 flex flex-col md:flex-row md:items-start gap-6">
            <div className="w-16 h-16 shrink-0 rounded-2xl bg-white/10 border border-blue-500/20 flex items-center justify-center">
              <Brain className="w-8 h-8 text-neutral-200" />
            </div>
            
            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-3">
                <p className="text-[11px] uppercase tracking-[0.25em] text-neutral-200 font-bold">
                  Groq Llama-3 AI Engine
                </p>
                <span className="px-2 py-0.5 rounded-full bg-white/10 text-neutral-200 text-[10px] font-bold uppercase tracking-wider border border-blue-500/20 animate-pulse">
                  Active
                </span>
              </div>
              
              <h3 className="text-xl md:text-2xl font-medium text-white leading-relaxed">
                "{signal.ai_reasoning}"
              </h3>
            </div>
          </div>
        </motion.div>
      )}

      {/* Bullish Bearish Speedometer */}
      <motion.div {...scrollReveal} className="bg-[#121212] border border-white/5 rounded-2xl p-6 space-y-6 overflow-hidden">

        <div className="flex items-center justify-between flex-wrap gap-3">

          <div>
            <h2 className="text-2xl font-semibold tracking-tight">
              Market Direction Gauge
            </h2>

            <p className="text-sm text-gray-400 mt-1">
              AI-powered bullish vs bearish directional momentum
            </p>
          </div>

          <div
            className={`px-4 py-2 rounded-xl border text-sm font-semibold ${
              bullishScore >= 65
                ? "bg-white/10 text-white border-white/20"
                : bullishScore <= 35
                ? "bg-neutral-600/10 text-neutral-300 border-neutral-600/20"
                : "bg-neutral-500/10 text-neutral-400 border-neutral-500/20"
            }`}
          >
            {bullishScore >= 65
              ? "Bullish Momentum"
              : bullishScore <= 35
              ? "Bearish Momentum"
              : "Neutral Momentum"}
          </div>
        </div>

        <div className="flex flex-col items-center justify-center p-6 bg-black/40 rounded-[24px] border border-white/5 relative overflow-hidden">
          
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.03),transparent_70%)] pointer-events-none" />

          {/* Semi-circle Gauge Container */}
          <div className="relative w-[280px] h-[140px] overflow-hidden flex items-end justify-center mt-6">
            
            {/* Speedometer Background Track */}
            <div className="absolute top-0 left-0 w-[280px] h-[280px] rounded-full border-[18px] border-white/5" />
            
            {/* Active Colored Bias Fill */}
            <div 
              className={`absolute top-0 left-0 w-[280px] h-[280px] rounded-full border-[18px] transition-all duration-1000 ${
                signal?.signal === "BUY" 
                  ? "border-white/10 border-b-transparent border-r-transparent"
                  : signal?.signal === "SELL"
                  ? "border-white/10 border-b-transparent border-l-transparent"
                  : "border-white/10 border-b-transparent"
              }`}
              style={{
                transform: `rotate(${gaugeRotation}deg)`,
                transformOrigin: 'center center'
              }}
            />

            {/* Needle indicator pin */}
            <div className="absolute left-1/2 bottom-0 w-[220px] h-[110px] bg-[#121212] rounded-t-full -translate-x-1/2" />
            
            {/* Rotating Arrow Indicator */}
            <div 
              className="absolute bottom-0 w-2.5 h-[115px] origin-bottom bg-gradient-to-t from-cyan-400 to-blue-500 rounded-t-full transition-transform duration-1000"
              style={{
                transform: `translateX(-50%) rotate(${gaugeRotation}deg)`,
                left: "50%"
              }}
            />

            <div className="absolute left-0 bottom-0 text-neutral-400 text-sm font-semibold">
              Bearish
            </div>

            <div className="absolute right-0 bottom-0 text-white text-sm font-semibold">
              Bullish
            </div>

            <div className="absolute left-1/2 bottom-10 -translate-x-1/2 text-center space-y-1">
              <div className="text-4xl font-bold text-white">
                {bullishScore}%
              </div>

              <div className="text-sm text-gray-400">
                AI Confidence
              </div>
            </div>

          </div>

        </div>

      </motion.div>
      {/* Volatility Analytics */}
      {volatility && (
        <div className="relative overflow-hidden rounded-[32px] border border-white/10 bg-[#161616]/90 backdrop-blur-2xl p-6 md:p-8 space-y-8 shadow-[0_0_80px_rgba(59,130,246,0.08)]">
          <div className="absolute inset-0 opacity-50 pointer-events-none bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.03),transparent_35%)]" />

          <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">

            <div>
              <h2 className="text-2xl font-semibold tracking-tight">
                Market Energy System
              </h2>

              <p className="text-sm text-gray-400 mt-1">
                Institutional liquidity movement, volatility pressure, and realtime market energy analysis
              </p>
            </div>

            <div
              className={`px-4 py-2 rounded-xl border text-sm font-semibold w-fit ${
                volatility.status === "ACTIVE"
                  ? "bg-white/10 text-white border-white/20"
                  : volatility.status === "WATCH"
                  ? "bg-neutral-500/10 text-neutral-400 border-neutral-500/20"
                  : "bg-neutral-600/10 text-neutral-300 border-neutral-600/20"
              }`}
            >
              {volatility.status}
            </div>

          </div>

          <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">

            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 space-y-4 hover:scale-[1.02] transition-transform duration-500">
              <p className="text-sm text-gray-400">Volatility Level</p>
              <h2 className="text-xl font-bold text-neutral-200">
                {volatility.level || "Moderate"}
              </h2>
            </div>

            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 space-y-4 hover:scale-[1.02] transition-transform duration-500">
              <p className="text-sm text-gray-400">Movement Intensity</p>
              <h2 className="text-xl font-bold text-neutral-200">
                {typeof volatility?.value === "number"
                  ? `${volatility.value.toFixed(1)}%`
                  : "12.0%"}
              </h2>
            </div>

            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 space-y-4 hover:scale-[1.02] transition-transform duration-500">
              <p className="text-sm text-gray-400">Market Condition</p>
              <h2
                className={`text-xl font-bold ${
                  volatility.status === "ACTIVE"
                    ? "text-white"
                    : volatility.status === "WATCH"
                    ? "text-neutral-300"
                    : "text-neutral-400"
                }`}
              >
                {volatility.status}
              </h2>
            </div>

            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 space-y-4 hover:scale-[1.02] transition-transform duration-500">
              <p className="text-sm text-gray-400">Feed Type</p>
              <h2
                className={`text-xl font-bold ${
                  isLiveAsset ? "text-white" : "text-neutral-300"
                }`}
              >
                {isLiveAsset ? "LIVE" : "DELAYED"}
              </h2>
            </div>

          </div>

          <div className="relative z-10 rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6 space-y-5 overflow-hidden">
            <div className="flex items-center justify-between text-sm text-gray-400">
              <span>Market Energy Pressure</span>
              <span>
                {typeof volatility?.value === "number"
                  ? `${volatility.value.toFixed(1)}%`
                  : "12.0%"}
              </span>
            </div>

            <div className="w-full h-4 rounded-full bg-white/5 overflow-hidden shadow-inner">
              <div
                className={`h-full rounded-full ${
                  volatility.status === "ACTIVE"
                    ? "bg-gradient-to-r from-green-500 via-emerald-400 to-cyan-400"
                    : volatility.status === "WATCH"
                    ? "bg-gradient-to-r from-yellow-500 to-orange-400"
                    : "bg-gradient-to-r from-red-500 to-pink-500"
                }`}
                style={{
                  width:
                    volatility.status === "ACTIVE"
                      ? "92%"
                      : volatility.status === "WATCH"
                      ? "63%"
                      : "35%",
                }}
              />
            </div>
          </div>

        </div>
      )}

      {/* Main Chart */}
      <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-[#161616]/90 backdrop-blur-3xl p-4 md:p-6 space-y-6 shadow-[0_0_120px_rgba(255,255,255,0.02)]">

        <div
          className={`absolute inset-0 opacity-50 pointer-events-none ${
            signal?.signal === "BUY"
              ? "bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.03),transparent_35%)]"
              : signal?.signal === "SELL"
              ? "bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.03),transparent_35%)]"
              : "bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.03),transparent_35%)]"
          }`}
        />

        <div className="absolute -top-24 right-0 w-72 h-72 rounded-full blur-3xl opacity-20 bg-cyan-500" />
        <div className="absolute -bottom-24 left-0 w-72 h-72 rounded-full blur-3xl opacity-20 bg-purple-500" />

        <div className="relative z-10 flex flex-col xl:flex-row xl:items-center xl:justify-between gap-6">

          <div className="space-y-4">

            <div className="flex items-center gap-3 flex-wrap">

              <span className="px-3 py-1 rounded-full border border-cyan-500/20 bg-white/10 text-white text-[11px] uppercase tracking-[0.25em] font-semibold">
                LIVE CHART INTELLIGENCE
              </span>

              <span className="px-3 py-1 rounded-full border border-neutral-500/20 bg-neutral-500/10 text-neutral-200 text-[11px] uppercase tracking-[0.25em] font-semibold animate-pulse">
                AI OVERLAY ACTIVE
              </span>

            </div>

            <div>
              <h2 className="text-3xl md:text-4xl font-black tracking-tight bg-gradient-to-r from-white via-cyan-200 to-blue-300 bg-clip-text text-transparent">
                Institutional Chart Terminal
              </h2>

              <p className="text-sm md:text-base text-gray-400 mt-3 max-w-3xl leading-relaxed">
                AI-enhanced institutional market visualization with realtime momentum analysis, macro event overlays, smart-money positioning, and volatility intelligence.
              </p>
            </div>

          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsLayoutModalOpen(true)}
              className="px-6 py-4 rounded-2xl border border-neutral-500/20 bg-neutral-500/10 text-neutral-200 hover:bg-purple-500/20 transition-all duration-300 text-sm font-semibold backdrop-blur-xl hover:scale-[1.02] shadow-[0_0_40px_rgba(168,85,247,0.12)] flex items-center gap-2"
            >
              <Settings className="w-4 h-4" /> Link Pine Script
            </button>

            <button
              onClick={() => {
                window.open(
                  `https://www.tradingview.com/chart/?symbol=${encodeURIComponent(tradingViewSymbol)}`,
                  "_blank"
                );
              }}
              className="px-6 py-4 rounded-2xl border border-cyan-500/20 bg-white/10 text-white hover:bg-cyan-500/20 transition-all duration-300 text-sm font-semibold backdrop-blur-xl hover:scale-[1.02] shadow-[0_0_40px_rgba(255,255,255,0.03)]"
            >
              Open TradingView
            </button>
          </div>

        </div>

        <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">

          <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
            <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.03),transparent_45%)]" />
            <div className="relative z-10">
              <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500 mb-3">
                AI Bias
              </p>

              <div className={`text-4xl font-black ${
                signal?.signal === "BUY"
                  ? "text-white"
                  : signal?.signal === "SELL"
                  ? "text-neutral-400"
                  : "text-neutral-300"
              }`}>
                {signal?.signal || "HOLD"}
              </div>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
            <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.03),transparent_45%)]" />
            <div className="relative z-10">
              <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500 mb-3">
                Momentum Energy
              </p>

              <div className="text-4xl font-black text-white">
                {formattedRsi}
              </div>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
            <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.03),transparent_45%)]" />
            <div className="relative z-10">
              <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500 mb-3">
                AI Confidence
              </p>

              <div className="text-4xl font-black text-white">
                {signal?.confidence || 0}%
              </div>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
            <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.03),transparent_45%)]" />
            <div className="relative z-10">
              <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500 mb-3">
                Market Feed
              </p>

              <div className="flex items-center gap-2 text-neutral-300 font-bold text-lg">
                <div className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
                ACTIVE
              </div>
            </div>
          </div>

        </div>

        <div className="relative z-10 h-[420px] md:h-[700px] w-full rounded-[32px] overflow-hidden border border-white/10 bg-[#0f0f0f] shadow-[0_0_100px_rgba(59,130,246,0.08)]">

          {/* Unlock Overlay for Smooth Page Scroll on Hover */}
          {chartLocked && (
            <div 
              onClick={() => setChartLocked(false)}
              className="absolute inset-0 bg-black/40 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center cursor-pointer group transition-all duration-300 hover:bg-black/20"
            >
              <div className="bg-slate-900/90 border border-cyan-500/30 text-white px-6 py-4 rounded-2xl flex items-center gap-3 shadow-2xl hover:scale-105 hover:bg-slate-950 hover:border-cyan-400 transition-all duration-300">
                <MousePointerClick className="w-5 h-5 animate-pulse" />
                <span className="text-xs uppercase tracking-widest font-black">Click to Unlock Chart Controls</span>
              </div>
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mt-3 font-semibold">
                Prevents mouse wheel zoom from trapping page scroll
              </p>
            </div>
          )}

          {/* Quick Lock Button when Interacting with Chart */}
          {!chartLocked && (
            <button
              onClick={() => setChartLocked(true)}
              className="absolute top-4 right-4 z-30 bg-red-500/20 hover:bg-red-500/30 text-neutral-400 hover:text-white border border-white/10 hover:border-red-500/50 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-300 shadow-xl flex items-center gap-2 backdrop-blur-md"
            >
              <Lock className="w-3.5 h-3.5" />
              Lock Scroll
            </button>
          )}

          {!fetchFailed ? (
            <iframe
              className={`relative z-10 w-full h-full transition-all duration-300 ${
                chartLocked ? "pointer-events-none opacity-80" : "pointer-events-auto"
              }`}
              key={`${symbol}-${selectedTimeframe}-${customLayoutId}`}
              src={customLayoutId 
                ? `https://s.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol=${encodeURIComponent(tradingViewSymbol)}&interval=${selectedTimeframe === "1m"
                  ? "1"
                  : selectedTimeframe === "5m"
                  ? "5"
                  : selectedTimeframe === "15m"
                  ? "15"
                  : "60"}&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=0f172a&theme=dark&workspace=${encodeURIComponent(customLayoutId)}`
                : `https://s.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol=${encodeURIComponent(tradingViewSymbol)}&interval=${selectedTimeframe === "1m"
                  ? "1"
                  : selectedTimeframe === "5m"
                  ? "5"
                  : selectedTimeframe === "15m"
                  ? "15"
                  : "60"}&hidesidetoolbar=1&symboledit=1&saveimage=0&toolbarbg=0f172a&theme=dark`
              }
              width="100%"
              height="100%"
              frameBorder="0"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400 text-sm bg-black/20 backdrop-blur-2xl">
              <div className="text-center space-y-4">
                <div className="text-5xl">📡</div>
                <div>
                  <p className="text-lg font-semibold text-white mb-2">
                    Institutional Chart Feed Offline
                  </p>
                  <p className="text-sm text-gray-500">
                    Reconnecting to realtime market intelligence...
                  </p>
                </div>
              </div>
            </div>
          )}

        </div>

        <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-4">

          <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
            <div className="relative z-10 space-y-3">
              <p className="text-[11px] uppercase tracking-[0.25em] text-neutral-200 font-bold">
                Smart Money Concepts
              </p>

              {signal?.choch_bullish || signal?.bos_bullish ? (
                <div className="text-2xl font-black text-white flex items-center gap-2">
                  BULLISH SHIFT <TrendingUp className="w-5 h-5 text-white" />
                </div>
              ) : signal?.choch_bearish || signal?.bos_bearish ? (
                <div className="text-2xl font-black text-neutral-400 flex items-center gap-2">
                  BEARISH SHIFT <TrendingDown className="w-5 h-5 text-neutral-400" />
                </div>
              ) : (
                <div className="text-2xl font-black text-slate-400 flex items-center gap-2">
                  ACCUMULATION <Scale className="w-5 h-5 text-slate-400" />
                </div>
              )}

              <div className="space-y-1.5 text-xs text-gray-400 pt-1">
                <div className="flex justify-between items-center border-b border-white/5 pb-1">
                  <span>Structure Break (BOS):</span>
                  <span className={signal?.bos_bullish ? "text-white font-bold" : signal?.bos_bearish ? "text-neutral-400 font-bold" : "text-gray-600"}>
                    {signal?.bos_bullish ? "Bullish BOS" : signal?.bos_bearish ? "Bearish BOS" : "Inactive"}
                  </span>
                </div>
                <div className="flex justify-between items-center border-b border-white/5 pb-1">
                  <span>Character Shift (CHoCH):</span>
                  <span className={signal?.choch_bullish ? "text-white font-bold" : signal?.choch_bearish ? "text-neutral-400 font-bold" : "text-gray-600"}>
                    {signal?.choch_bullish ? "Bullish CHoCH" : signal?.choch_bearish ? "Bearish CHoCH" : "Inactive"}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Fair Value Gap (FVG):</span>
                  <span className={signal?.fvg_bullish ? "text-white font-bold" : signal?.fvg_bearish ? "text-neutral-400 font-bold" : "text-gray-600"}>
                    {signal?.fvg_bullish ? `Bullish FVG (+${signal.fvg_gap})` : signal?.fvg_bearish ? `Bearish FVG (-${signal.fvg_gap})` : "None"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
            <div className="relative z-10 space-y-3">
              <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                Macro Risk Layer
              </p>

              <div className="text-3xl font-black text-neutral-400">
                ELEVATED
              </div>

              <p className="text-sm text-gray-400 leading-relaxed">
                High-impact macroeconomic narratives increasing volatility compression probability.
              </p>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
            <div className="relative z-10 space-y-3">
              <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                AI Projection
              </p>

              <div className="text-3xl font-black text-white">
                {signal?.signal || "HOLD"}
              </div>

              <p className="text-sm text-gray-400 leading-relaxed">
                AI confidence engine projecting directional continuation based on realtime structure analysis.
              </p>
            </div>
          </div>

        </div>

      </div>

      {/* Market Pulse */}
      {/* Institutional Positioning */}
      {positioning && (
        <div className="relative overflow-hidden rounded-[32px] border border-white/10 bg-[#161616]/90 backdrop-blur-2xl p-6 md:p-8 space-y-8 shadow-[0_0_80px_rgba(59,130,246,0.08)]">
          <div className="absolute inset-0 pointer-events-none opacity-60 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_30%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.03),transparent_30%)]" />

          <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 className="text-2xl font-semibold tracking-tight">
                Institutional Positioning
              </h2>
              <p className="text-sm text-gray-400 mt-1">
                Retail crowd exposure, smart money flow, and squeeze analytics
              </p>
            </div>
            <div
              className={`px-4 py-2 rounded-xl border text-sm font-semibold w-fit ${
                positioning.crowd_bias === "BULLISH"
                  ? "bg-white/10 text-white border-white/20"
                  : positioning.crowd_bias === "BEARISH"
                  ? "bg-neutral-600/10 text-neutral-300 border-neutral-600/20"
                  : "bg-neutral-500/10 text-neutral-400 border-neutral-500/20"
              }`}
            >
              Crowd Bias: {positioning.crowd_bias}
            </div>
          </div>

          <div className="relative z-10 grid grid-cols-1 xl:grid-cols-[1.1fr_0.9fr] gap-6">
            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6 space-y-6">
              <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_top_right,rgba(34,197,94,0.14),transparent_35%)] pointer-events-none" />
              <div className="relative z-10 flex items-center justify-between">
                <h3 className="text-lg font-semibold">
                  Retail Positioning
                </h3>
                <span className="text-xs px-3 py-1 rounded-full bg-white/10 text-white border border-cyan-500/20">
                  LIVE POSITIONING
                </span>
              </div>
              <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
                <div className="flex items-center justify-center">
                  <div className="relative w-52 h-52 rounded-full flex items-center justify-center border border-green-500/20 bg-green-500/[0.04] shadow-[0_0_50px_rgba(34,197,94,0.12)] overflow-hidden">
                    <div
                      className="absolute inset-0 rounded-full"
                      style={{
                        background: `conic-gradient(#22c55e ${positioning.retail_long * 3.6}deg, rgba(255,255,255,0.06) 0deg)`,
                      }}
                    />
                    <div className="absolute inset-[18px] rounded-full bg-[#050816] border border-white/5 backdrop-blur-xl" />
                    <div className="relative z-10 text-center space-y-1">
                      <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                        Retail Long
                      </p>
                      <div className="text-5xl font-bold text-white">
                        {positioning.retail_long}%
                      </div>
                      <div className="text-xs text-gray-500">
                        Crowd Exposure
                      </div>
                    </div>
                  </div>
                </div>
                <div className="space-y-5">
                  <div className="rounded-3xl border border-red-500/20 bg-red-500/[0.04] p-5 backdrop-blur-xl shadow-[0_0_40px_rgba(239,68,68,0.08)]">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                          Retail Short
                        </p>
                        <div className="text-3xl font-bold text-neutral-400 mt-2">
                          {positioning.retail_short}%
                        </div>
                      </div>
                      <div className="w-12 h-12 rounded-2xl bg-neutral-600/10 border border-red-500/20 flex items-center justify-center text-neutral-400 text-xl">
                        ↓
                      </div>
                    </div>
                    <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-red-500 to-orange-400"
                        style={{
                          width: `${positioning.retail_short}%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 gap-4">
                    <div className="rounded-xl border border-neutral-500/20 bg-purple-500/5 p-4">
                      <p className="text-xs text-gray-500 mb-2">
                        Smart Money Bias
                      </p>
                      <p className="text-sm font-semibold text-neutral-200 leading-relaxed">
                        {positioning.smart_money_bias}
                      </p>
                    </div>
                    <div className="rounded-xl border border-orange-500/20 bg-orange-500/5 p-4">
                      <p className="text-xs text-gray-500 mb-2">
                        Institutional Activity
                      </p>
                      <p className="text-sm font-semibold text-white leading-relaxed">
                        {positioning.institutional_activity?.activity}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6 space-y-6">
              <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_top_right,rgba(239,68,68,0.16),transparent_35%)] pointer-events-none" />
              <div className="relative z-10 flex items-center justify-between">
                <h3 className="text-lg font-semibold">
                  Squeeze Risk Analysis
                </h3>
                <span
                  className={`text-xs px-3 py-1 rounded-full border ${
                    positioning.squeeze_risk?.risk >= 75
                      ? "bg-neutral-600/10 text-neutral-300 border-neutral-600/20"
                      : positioning.squeeze_risk?.risk >= 50
                      ? "bg-neutral-500/10 text-neutral-400 border-neutral-500/20"
                      : "bg-white/10 text-white border-white/20"
                  }`}
                >
                  {positioning.squeeze_risk?.type}
                </span>
              </div>
              <div className="relative z-10 flex flex-col items-center justify-center py-4 space-y-6">
                <div className="relative w-64 h-64 rounded-full flex items-center justify-center overflow-hidden border border-white/10 bg-black/20 shadow-[0_0_70px_rgba(239,68,68,0.12)]">
                  <div
                    className="absolute inset-0 rounded-full"
                    style={{
                      background: `conic-gradient(${positioning.squeeze_risk?.risk >= 75 ? '#ef4444' : positioning.squeeze_risk?.risk >= 50 ? '#facc15' : '#22c55e'} ${positioning.squeeze_risk?.risk * 3.6}deg, rgba(255,255,255,0.05) 0deg)`,
                    }}
                  />
                  <div className="absolute inset-[18px] rounded-full bg-[#050816] border border-white/5 backdrop-blur-xl" />
                  <div className="relative z-10 text-center space-y-2">
                    <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                      Liquidation Risk
                    </p>
                    <div className="text-6xl font-bold text-white">
                      {positioning.squeeze_risk?.risk}%
                    </div>
                    <div className="text-sm text-gray-500">
                      Squeeze Probability
                    </div>
                  </div>
                </div>
              </div>
              <div className="relative z-10 rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6 space-y-5 overflow-hidden">
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">
                    Institutional Flow Insight
                  </p>
                  <p className="text-sm text-gray-300 leading-relaxed">
                    {positioning.institutional_activity?.description}
                  </p>
                </div>
                <div className="border-t border-white/5 pt-4">
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">
                    AI Positioning Summary
                  </p>
                  <p className="text-sm text-gray-300 leading-relaxed">
                    {positioning.ai_summary}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Market Pulse */}
      {marketPulse && (
        <div className="relative overflow-hidden rounded-[32px] border border-white/10 bg-[#161616]/90 backdrop-blur-2xl p-6 md:p-8 space-y-8 shadow-[0_0_80px_rgba(168,85,247,0.08)]">
          <div className="absolute inset-0 opacity-50 pointer-events-none bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.03),transparent_35%)]" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 className="text-2xl font-semibold tracking-tight">
                Market Pulse
              </h2>
              <p className="text-sm text-gray-400 mt-1">
                Aggregated crowd sentiment and social trading analytics
              </p>
            </div>
            <div
              className={`px-4 py-2 rounded-xl border text-sm font-semibold w-fit ${
                marketPulse.overall_sentiment === "Bullish"
                  ? "bg-white/10 text-white border-white/20"
                  : marketPulse.overall_sentiment === "Bearish"
                  ? "bg-neutral-600/10 text-neutral-300 border-neutral-600/20"
                  : "bg-neutral-500/10 text-neutral-400 border-neutral-500/20"
              }`}
            >
              Overall: {marketPulse.overall_sentiment}
            </div>
          </div>
          <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 space-y-4 hover:scale-[1.02] transition-transform duration-500">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-400">Bullish</p>
                <p className="text-lg font-bold text-white">
                  {marketPulse.bullish_percentage}%
                </p>
              </div>
              <div className="w-full h-2 rounded-full bg-[#262626] overflow-hidden">
                <div
                  className="h-full bg-green-400 rounded-full"
                  style={{ width: `${marketPulse.bullish_percentage}%` }}
                />
              </div>
            </div>
            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 space-y-4 hover:scale-[1.02] transition-transform duration-500">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-400">Bearish</p>
                <p className="text-lg font-bold text-neutral-400">
                  {marketPulse.bearish_percentage}%
                </p>
              </div>
              <div className="w-full h-2 rounded-full bg-[#262626] overflow-hidden">
                <div
                  className="h-full bg-red-400 rounded-full"
                  style={{ width: `${marketPulse.bearish_percentage}%` }}
                />
              </div>
            </div>
            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 space-y-4 hover:scale-[1.02] transition-transform duration-500">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-400">Neutral</p>
                <p className="text-lg font-bold text-neutral-300">
                  {marketPulse.neutral_percentage}%
                </p>
              </div>
              <div className="w-full h-2 rounded-full bg-[#262626] overflow-hidden">
                <div
                  className="h-full bg-yellow-400 rounded-full"
                  style={{ width: `${marketPulse.neutral_percentage}%` }}
                />
              </div>
            </div>
          </div>
          <div className="relative z-10 flex items-center justify-between text-sm text-gray-500 pt-3 border-t border-white/5">
            <span>Total Institutional Narratives Analysed</span>
            <span>{marketPulse.total_articles || 0}</span>
          </div>
        </div>
      )}

      {/* AI Intelligence Terminal */}
      {assetData?.ai_analysis && (
        <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-[#161616]/90 backdrop-blur-3xl p-6 md:p-8 space-y-8 shadow-[0_0_120px_rgba(255,255,255,0.02)]">

          <div className="absolute inset-0 opacity-50 pointer-events-none bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.03),transparent_35%)]" />

          <div className="absolute -top-32 right-0 w-80 h-80 rounded-full blur-3xl opacity-20 bg-cyan-500" />
          <div className="absolute -bottom-32 left-0 w-80 h-80 rounded-full blur-3xl opacity-20 bg-purple-500" />

          <div className="relative z-10 flex flex-col xl:flex-row xl:items-center xl:justify-between gap-6">

            <div className="space-y-4">

              <div className="flex items-center gap-3 flex-wrap">

                <span className="px-3 py-1 rounded-full border border-cyan-500/20 bg-white/10 text-white text-[11px] uppercase tracking-[0.25em] font-semibold">
                  AI INTELLIGENCE CORE
                </span>

                <span className="px-3 py-1 rounded-full border border-neutral-500/20 bg-neutral-500/10 text-neutral-200 text-[11px] uppercase tracking-[0.25em] font-semibold animate-pulse">
                  LIVE ANALYSIS
                </span>

              </div>

              <div>
                <h2 className="text-3xl md:text-4xl font-black tracking-tight bg-gradient-to-r from-white via-cyan-200 to-neutral-400 bg-clip-text text-transparent">
                  Institutional AI Intelligence
                </h2>

                <p className="text-sm md:text-base text-gray-400 mt-3 max-w-3xl leading-relaxed">
                  Realtime AI-powered market regime detection, smart-money interpretation, liquidity mapping, and institutional macro analysis.
                </p>
              </div>

            </div>

            <div className="rounded-3xl border border-cyan-500/20 bg-white/10 px-6 py-5 backdrop-blur-2xl shadow-[0_0_50px_rgba(255,255,255,0.03)]">
              <p className="text-[11px] uppercase tracking-[0.25em] text-white mb-2">
                Market Regime
              </p>

              <div className="text-2xl font-black text-white">
                {assetData.ai_analysis.market_regime?.name}
              </div>
            </div>

          </div>

          <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">

            <div className="rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
              <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
              <div className="relative z-10 space-y-3">
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  Smart Money Flow
                </p>

                <div className="text-2xl font-black text-white leading-tight">
                  {assetData.ai_analysis.smart_money?.flow}
                </div>
              </div>
            </div>

            <div className="rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
              <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
              <div className="relative z-10 space-y-3">
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  Event Risk
                </p>

                <div className="text-2xl font-black text-neutral-400">
                  {assetData.ai_analysis.volatility_forecast?.event_risk}
                </div>
              </div>
            </div>

            <div className="rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
              <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
              <div className="relative z-10 space-y-3">
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  Liquidity State
                </p>

                <div className="text-2xl font-black text-neutral-200 leading-tight">
                  {assetData.ai_analysis.liquidity_state?.state}
                </div>
              </div>
            </div>

            <div className="rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
              <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
              <div className="relative z-10 space-y-3">
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  Breakout Probability
                </p>

                <div className="text-4xl font-black text-white">
                  {assetData.ai_analysis.volatility_forecast?.breakout_probability}%
                </div>
              </div>
            </div>

          </div>

          <div className="relative z-10 grid grid-cols-1 xl:grid-cols-[1.2fr_0.8fr] gap-6">

            <div className="rounded-[32px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6 overflow-hidden relative">

              <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />

              <div className="relative z-10 space-y-5">

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                      AI Narrative Engine
                    </p>

                    <h3 className="text-2xl font-black text-white mt-3 leading-tight">
                      {assetData.ai_analysis.ai_narrative?.headline}
                    </h3>
                  </div>

                  <div className="w-14 h-14 rounded-2xl bg-white/10 border border-cyan-500/20 flex items-center justify-center text-white text-2xl shadow-[0_0_30px_rgba(255,255,255,0.03)]">
                    ◎
                  </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-black/20 backdrop-blur-xl p-5">
                  <p className="text-sm text-gray-300 leading-relaxed">
                    {assetData.ai_analysis.ai_narrative?.summary}
                  </p>
                </div>

              </div>

            </div>

            <div className="rounded-[32px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6 overflow-hidden relative">

              <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />

              <div className="relative z-10 space-y-6">

                <div>
                  <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                    Confidence Evolution
                  </p>

                  <div className="text-4xl font-black text-white mt-3">
                    {signal?.confidence || 0}%
                  </div>
                </div>

                <div className="space-y-4">

                  {(assetData.ai_analysis.confidence_evolution || []).map((point: any, idx: number) => (
                    <div key={idx} className="space-y-2">

                      <div className="flex items-center justify-between text-xs text-gray-500 uppercase tracking-wide">
                        <span>{point.interval}</span>
                        <span>{point.confidence}%</span>
                      </div>

                      <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500"
                          style={{
                            width: `${point.confidence}%`,
                          }}
                        />
                      </div>

                    </div>
                  ))}

                </div>

              </div>

            </div>

          </div>

        </div>
      )}
      {/* AI Projection Engine */}
      {assetData?.ai_projection && (
        <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-[#161616]/90 backdrop-blur-3xl p-6 md:p-8 space-y-8 shadow-[0_0_120px_rgba(34,197,94,0.10)]">

          <div className="absolute inset-0 opacity-50 pointer-events-none bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.03),transparent_35%)]" />

          <div className="absolute -top-32 right-0 w-80 h-80 rounded-full blur-3xl opacity-20 bg-green-500" />
          <div className="absolute -bottom-32 left-0 w-80 h-80 rounded-full blur-3xl opacity-20 bg-cyan-500" />

          <div className="relative z-10 flex flex-col xl:flex-row xl:items-center xl:justify-between gap-6">

            <div>
              <div className="flex items-center gap-3 flex-wrap mb-4">
                <span className="px-3 py-1 rounded-full border border-green-500/20 bg-white/10 text-white text-[11px] uppercase tracking-[0.25em] font-semibold">
                  AI PROJECTION ENGINE
                </span>

                <span className="px-3 py-1 rounded-full border border-cyan-500/20 bg-white/10 text-white text-[11px] uppercase tracking-[0.25em] font-semibold animate-pulse">
                  LIVE FORECAST
                </span>
              </div>

              <h2 className="text-3xl md:text-4xl font-black tracking-tight bg-gradient-to-r from-white via-green-200 to-cyan-300 bg-clip-text text-transparent">
                Institutional Projection Matrix
              </h2>

              <p className="text-sm md:text-base text-gray-400 mt-3 max-w-3xl leading-relaxed">
                AI-generated breakout targets, institutional liquidity zones, directional probability analysis, and realtime market projection intelligence.
              </p>
            </div>

            <div className="rounded-3xl border border-green-500/20 bg-white/10 px-6 py-5 backdrop-blur-2xl shadow-[0_0_50px_rgba(34,197,94,0.12)]">
              <p className="text-[11px] uppercase tracking-[0.25em] text-white mb-2">
                Preferred Direction
              </p>

              <div className={`text-3xl font-black ${
                assetData.ai_projection.projected_move?.direction === "BUY"
                  ? "text-white"
                  : assetData.ai_projection.projected_move?.direction === "SELL"
                  ? "text-neutral-400"
                  : "text-neutral-300"
              }`}>
                {assetData.ai_projection.projected_move?.direction}
              </div>
            </div>

          </div>

          <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">

            <div className="rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 relative overflow-hidden">
              <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
              <div className="relative z-10 space-y-3">
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  AI Target Price
                </p>

                <div className="text-4xl font-black text-white">
                  {assetData.ai_projection.projected_move?.target_price}
                </div>
              </div>
            </div>

            <div className="rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 relative overflow-hidden">
              <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
              <div className="relative z-10 space-y-3">
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  Breakout Probability
                </p>

                <div className="text-4xl font-black text-white">
                  {assetData.ai_projection.breakout_projection?.breakout_probability}%
                </div>
              </div>
            </div>

            <div className="rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 relative overflow-hidden">
              <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
              <div className="relative z-10 space-y-3">
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  Volatility State
                </p>

                <div className="text-2xl font-black text-neutral-200 leading-tight">
                  {assetData.ai_projection.breakout_projection?.volatility_state}
                </div>
              </div>
            </div>

            <div className="rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 relative overflow-hidden">
              <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
              <div className="relative z-10 space-y-3">
                <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                  Projected Move
                </p>

                <div className="text-4xl font-black text-neutral-300">
                  {assetData.ai_projection.projected_move?.move_percent}%
                </div>
              </div>
            </div>

          </div>

          <div className="relative z-10 grid grid-cols-1 xl:grid-cols-2 gap-6">

            <div className="rounded-[32px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6 overflow-hidden relative">

              <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />

              <div className="relative z-10 space-y-6">

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                      Institutional Zones
                    </p>

                    <h3 className="text-2xl font-black text-white mt-3">
                      {assetData.ai_projection.institutional_zones?.dominant_zone}
                    </h3>
                  </div>

                  <div className="w-14 h-14 rounded-2xl bg-white/10 border border-blue-500/20 flex items-center justify-center text-white text-2xl">
                    ◈
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                  <div className="rounded-3xl border border-green-500/20 bg-green-500/5 p-5 space-y-3">
                    <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500">
                      Accumulation Zone
                    </p>

                    <div className="text-xl font-black text-white">
                      {assetData.ai_projection.institutional_zones?.accumulation_zone?.low}
                    </div>

                    <div className="text-sm text-gray-400">
                      to {assetData.ai_projection.institutional_zones?.accumulation_zone?.high}
                    </div>
                  </div>

                  <div className="rounded-3xl border border-red-500/20 bg-red-500/5 p-5 space-y-3">
                    <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500">
                      Distribution Zone
                    </p>

                    <div className="text-xl font-black text-neutral-400">
                      {assetData.ai_projection.institutional_zones?.distribution_zone?.low}
                    </div>

                    <div className="text-sm text-gray-400">
                      to {assetData.ai_projection.institutional_zones?.distribution_zone?.high}
                    </div>
                  </div>

                </div>

              </div>

            </div>

            <div className="rounded-[32px] border border-white/10 bg-black/20 backdrop-blur-2xl p-6 overflow-hidden relative">

              <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />

              <div className="relative z-10 space-y-6">

                <div>
                  <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
                    AI Probability Engine
                  </p>

                  <div className="text-4xl font-black text-white mt-3">
                    {assetData.ai_projection.probability_map?.bullish}%
                  </div>
                </div>

                <div className="space-y-5">

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs text-gray-500 uppercase tracking-wide">
                      <span>Bullish Probability</span>
                      <span>{assetData.ai_projection.probability_map?.bullish}%</span>
                    </div>

                    <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-green-400 to-emerald-500"
                        style={{
                          width: `${assetData.ai_projection.probability_map?.bullish || 0}%`,
                        }}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs text-gray-500 uppercase tracking-wide">
                      <span>Bearish Probability</span>
                      <span>{assetData.ai_projection.probability_map?.bearish}%</span>
                    </div>

                    <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-red-400 to-pink-500"
                        style={{
                          width: `${assetData.ai_projection.probability_map?.bearish || 0}%`,
                        }}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs text-gray-500 uppercase tracking-wide">
                      <span>Neutral Probability</span>
                      <span>{assetData.ai_projection.probability_map?.neutral}%</span>
                    </div>

                    <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-yellow-400 to-orange-500"
                        style={{
                          width: `${assetData.ai_projection.probability_map?.neutral || 0}%`,
                        }}
                      />
                    </div>
                  </div>

                </div>

              </div>

            </div>

          </div>

        </div>
      )}
      {/* Economic Calendar */}
      <div id="live-timeline-section" className="bg-[#121212] border border-white/5 rounded-2xl p-5 space-y-5 overflow-hidden">

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

          <div>
            <h2 className="text-2xl font-semibold tracking-tight">
              Institutional Macro Timeline
            </h2>

            <p className="text-sm text-gray-400 mt-1">
              Premium macroeconomic event intelligence and institutional impact timeline
            </p>
          </div>

          <span className="text-xs px-3 py-1 rounded-full bg-white/10 text-white border border-orange-500/20 w-fit">
            LIVE MACRO EVENTS
          </span>

        </div>

        {economicEvents.length === 0 && (
          <div className="p-5 rounded-xl bg-[#161616] border border-white/5 text-sm text-gray-400">
            No high-impact economic events currently available for this asset.
          </div>
        )}

        <div className="relative space-y-6 before:absolute before:left-[30px] before:top-0 before:h-full before:w-[2px] before:bg-gradient-to-b before:from-white/40 before:via-neutral-400/30 before:to-neutral-800/10">

          {(() => {
            const sortedEvents = [...economicEvents].sort((a: any, b: any) => {
              const impactOrder: Record<string, number> = { HIGH: 3, MEDIUM: 2, LOW: 1 };
              const valA = impactOrder[a.impact?.toUpperCase()] || 0;
              const valB = impactOrder[b.impact?.toUpperCase()] || 0;
              return valB - valA;
            });
            return sortedEvents.slice(0, visibleEventsCount).map((event: any, idx: number) => {
              const isHigh = event.impact === "HIGH";
              const isMedium = event.impact === "MEDIUM";

              return (
                <div
                  key={idx}
                  className={`relative ml-16 rounded-3xl border overflow-hidden backdrop-blur-xl shadow-2xl transition-all duration-500 hover:scale-[1.015] hover:-translate-y-1 ${
                    isHigh
                      ? "bg-red-500/5 border-red-500/20"
                      : isMedium
                      ? "bg-yellow-500/5 border-yellow-500/20"
                      : "bg-[#161616] border-white/5"
                  }`}
                >

                  <div
                    className={`absolute -left-[52px] top-10 w-6 h-6 rounded-full border-4 shadow-[0_0_30px_rgba(255,255,255,0.3)] ${
                      isHigh
                        ? "bg-red-400 border-red-300"
                        : isMedium
                        ? "bg-yellow-400 border-yellow-300"
                        : "bg-blue-400 border-blue-300"
                    }`}
                  />

                  <div
                    className={`absolute inset-0 opacity-40 pointer-events-none ${
                      isHigh
                        ? "bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]"
                        : isMedium
                        ? "bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]"
                        : "bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]"
                    }`}
                  />

                  <div className="relative z-10 flex items-start justify-between gap-4 p-6">

                    <div className="space-y-3 flex-1">

                      <div className="flex items-center gap-2 flex-wrap">

                        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-white/10 text-neutral-200 border border-blue-500/20">
                          {event.currency}
                        </span>

                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold border ${
                            isHigh
                              ? "bg-neutral-600/10 text-neutral-300 border-neutral-600/20"
                              : isMedium
                              ? "bg-neutral-500/10 text-neutral-400 border-neutral-500/20"
                              : "bg-white/10 text-white border-white/20"
                          }`}
                        >
                          {event.impact} IMPACT
                        </span>

                      </div>

                      <div className="space-y-1">
                        <h3 className="text-lg font-semibold text-white leading-relaxed">
                          {event.event}
                        </h3>
                        <p className="text-xs text-gray-500">
                          Scheduled macroeconomic release affecting {symbol}
                        </p>
                      </div>

                    </div>

                    <div className="text-right shrink-0">

                      <div className="text-xs text-gray-500 mb-2">
                        EVENT TIME
                      </div>

                      <div className="text-sm font-semibold text-white">
                        {event.time || "TBD"}
                      </div>

                      <div className="mt-4 w-3 h-3 rounded-full animate-pulse bg-orange-400 ml-auto" />

                      <div className="mt-5 space-y-2">

                        <p className="text-xs text-gray-500 uppercase tracking-wide">
                          Affected Markets
                        </p>

                        <div className="flex flex-wrap justify-end gap-2 max-w-[220px] ml-auto">

                          {(event.affected_assets || []).map(
                            (asset: string, assetIdx: number) => (
                              <span
                                key={assetIdx}
                                className="px-2 py-1 rounded-lg text-[10px] font-medium bg-white/10 text-white border border-cyan-500/20"
                              >
                                {asset}
                              </span>
                            )
                          )}

                        </div>

                      </div>

                    </div>

                  </div>

                </div>
              );
            });
          })()}

        </div>

        {economicEvents.length > 3 && (
          <div className="flex justify-center gap-4 pt-4 border-t border-white/5">
            {visibleEventsCount < economicEvents.length ? (
              <button
                onClick={() => setVisibleEventsCount((prev) => prev + 3)}
                className="px-6 py-3 rounded-xl bg-neutral-500/10 hover:bg-purple-500/20 border border-neutral-500/20 text-neutral-200 font-bold text-xs uppercase tracking-widest transition-all"
              >
                View More Events
              </button>
            ) : (
              <button
                onClick={() => {
                  setVisibleEventsCount(3);
                  document.getElementById("live-timeline-section")?.scrollIntoView({ behavior: "smooth" });
                }}
                className="px-6 py-3 rounded-xl bg-neutral-600/10 hover:bg-red-500/20 border border-red-500/20 text-neutral-400 font-bold text-xs uppercase tracking-widest transition-all"
              >
                Show Less Events
              </button>
            )}
          </div>
        )}

      </div>

      {visibleEventsCount > 3 && (
        <button
          onClick={() => {
            setVisibleEventsCount(3);
            document.getElementById("live-timeline-section")?.scrollIntoView({ behavior: "smooth" });
          }}
          className="fixed bottom-24 right-6 z-50 bg-[#0f0f0f]/90 hover:bg-neutral-600/10 border border-white/10 text-neutral-400 font-bold text-xs uppercase tracking-widest px-4 py-3 rounded-full shadow-[0_10px_30px_rgba(0,0,0,0.5)] transition-all flex items-center gap-2 backdrop-blur-md"
        >
          <span>✕ Show Less Events</span>
        </button>
      )}
      {/* Macro News Intelligence */}
      {(() => {
        const redFolderNews = news.filter((item: any) => item.sentiment === "Bearish" || item.impact === "HIGH");
        const yellowFolderNews = news.filter((item: any) => item.sentiment === "Neutral" && item.impact !== "HIGH");
        const greenFolderNews = news.filter((item: any) => item.sentiment === "Bullish" && item.impact !== "HIGH");
        const hasMoreNews = redFolderNews.length > visibleNewsCount || 
                            yellowFolderNews.length > visibleNewsCount || 
                            greenFolderNews.length > visibleNewsCount;

        const renderNewsCard = (item: any, idx: number) => (
          <a
            key={idx}
            href={item.link || "#"}
            target="_blank"
            rel="noopener noreferrer"
            className={`group relative overflow-hidden block rounded-[24px] border backdrop-blur-2xl transition-all duration-300 hover:-translate-y-1.5 hover:scale-[1.01] hover:shadow-lg ${
              item.impact === "HIGH"
                ? "bg-red-500/[0.04] border-red-500/20 hover:border-red-500/40"
                : item.sentiment === "Bullish"
                ? "bg-green-500/[0.04] border-green-500/20 hover:border-green-500/40"
                : item.sentiment === "Bearish"
                ? "bg-red-500/[0.04] border-red-500/20 hover:border-red-500/40"
                : "bg-white/[0.01] border-white/5 hover:border-neutral-500/30"
            }`}
          >
            <div className="relative z-10 flex flex-col gap-4 p-5">
              <div className="flex items-center gap-2 flex-wrap text-[10px]">
                <span
                  className={`px-2 py-0.5 rounded-full font-bold border ${
                    item.sentiment === "Bullish"
                      ? "bg-white/10 text-white border-white/20"
                      : item.sentiment === "Bearish"
                      ? "bg-neutral-600/10 text-neutral-300 border-neutral-600/20"
                      : "bg-neutral-500/10 text-neutral-400 border-neutral-500/20"
                  }`}
                >
                  {item.sentiment}
                </span>
                <span className="text-gray-500 font-semibold">{item.source || "Finance News"}</span>
                <span
                  className={`px-2 py-0.5 rounded-full font-bold border ${
                    item.impact === "HIGH"
                      ? "bg-neutral-600/10 text-neutral-300 border-neutral-600/20"
                      : "bg-white/10 text-neutral-200 border-blue-500/20"
                  }`}
                >
                  {item.impact || "LOW"}
                </span>
              </div>
              
              <h3 className="text-sm font-bold text-white group-hover:text-neutral-200 transition-colors line-clamp-2">
                {item.title}
              </h3>
              
              <p className="text-xs text-gray-400 leading-relaxed line-clamp-3">
                {item.summary}
              </p>

              {item.ai_summary && (
                <div className="rounded-xl border border-white/5 bg-black/30 p-3.5 space-y-1.5 mt-1">
                  <p className="text-[9px] uppercase tracking-[0.2em] text-gray-500 font-bold">
                    AI Macro Narrative
                  </p>
                  <p className="text-xs text-gray-300 leading-relaxed font-light">
                    {item.ai_summary}
                  </p>
                </div>
              )}

              <div className="flex items-center justify-between pt-3 border-t border-white/5 text-[10px]">
                <span className="text-gray-500 font-medium">
                  {item.published ? new Date(item.published).toLocaleDateString() : "Recent"}
                </span>
                <span className="text-neutral-200 font-bold group-hover:translate-x-1 transition-transform">
                  Open ↗
                </span>
              </div>
            </div>
          </a>
        );

        return (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-white/5 pb-4">
              <div>
                <h2 className="text-2xl font-black tracking-tight text-white bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
                  Macro News Intelligence
                </h2>
                <p className="text-sm text-gray-400 mt-1">
                  Institutional-grade macroeconomic intelligence grouped by market impact folders
                </p>
              </div>
              <span className="text-xs px-3 py-1 rounded-full bg-white/10 text-neutral-200 border border-blue-500/20 w-fit font-bold">
                LIVE IMPACT ROTATION
              </span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
              {/* Column 1: Red Folder News */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 px-2 pb-2 border-b border-red-500/20">
                  <span className="w-3 h-3 rounded bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
                  <h3 className="text-sm font-bold text-neutral-400 uppercase tracking-widest">Red Folder (High Risk)</h3>
                  <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-neutral-600/10 text-neutral-400 border border-red-500/15">
                    {redFolderNews.length}
                  </span>
                </div>
                {redFolderNews.length === 0 ? (
                  <div className="p-6 text-center text-xs text-gray-500 border border-dashed border-white/5 rounded-2xl">
                    No high risk events currently.
                  </div>
                ) : (
                  redFolderNews.slice(0, visibleNewsCount).map((item: any, idx: number) => renderNewsCard(item, idx))
                )}
              </div>

              {/* Column 2: Yellow Folder News */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 px-2 pb-2 border-b border-yellow-500/20">
                  <span className="w-3 h-3 rounded bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]" />
                  <h3 className="text-sm font-bold text-neutral-300 uppercase tracking-widest">Yellow Folder (Medium Risk)</h3>
                  <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-neutral-500/10 text-neutral-300 border border-yellow-500/15">
                    {yellowFolderNews.length}
                  </span>
                </div>
                {yellowFolderNews.length === 0 ? (
                  <div className="p-6 text-center text-xs text-gray-500 border border-dashed border-white/5 rounded-2xl">
                    No medium risk events currently.
                  </div>
                ) : (
                  yellowFolderNews.slice(0, visibleNewsCount).map((item: any, idx: number) => renderNewsCard(item, idx))
                )}
              </div>

              {/* Column 3: Green Folder News */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 px-2 pb-2 border-b border-green-500/20">
                  <span className="w-3 h-3 rounded bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-widest">Green Folder (Low Risk)</h3>
                  <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-white/10 text-white border border-green-500/15">
                    {greenFolderNews.length}
                  </span>
                </div>
                {greenFolderNews.length === 0 ? (
                  <div className="p-6 text-center text-xs text-gray-500 border border-dashed border-white/5 rounded-2xl">
                    No low risk events currently.
                  </div>
                ) : (
                  greenFolderNews.slice(0, visibleNewsCount).map((item: any, idx: number) => renderNewsCard(item, idx))
                )}
              </div>
            </div>

            {hasMoreNews && (
              <div className="flex justify-center pt-4">
                <button
                  onClick={() => setVisibleNewsCount((prev) => prev + 3)}
                  className="px-6 py-3 rounded-xl bg-neutral-500/10 hover:bg-purple-500/20 border border-neutral-500/20 text-neutral-200 font-bold text-xs uppercase tracking-widest transition-all"
                >
                  View More News
                </button>
              </div>
            )}
          </div>
        );
      })()}


    {/* Related Assets */}
    <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-[#161616]/90 backdrop-blur-3xl p-6 md:p-8 space-y-8 shadow-[0_0_120px_rgba(255,255,255,0.02)]">

      <div className="absolute inset-0 opacity-50 pointer-events-none bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.03),transparent_35%)]" />

      <div className="absolute -top-32 -right-16 w-80 h-80 rounded-full blur-3xl opacity-20 bg-purple-500" />
      <div className="absolute -bottom-32 -left-16 w-80 h-80 rounded-full blur-3xl opacity-20 bg-cyan-500" />

      <div className="relative z-10 flex flex-col xl:flex-row xl:items-center xl:justify-between gap-6">

        <div className="space-y-4">

          <div className="flex items-center gap-3 flex-wrap">

            <span className="px-3 py-1 rounded-full border border-cyan-500/20 bg-white/10 text-white text-[11px] uppercase tracking-[0.25em] font-semibold">
              CORRELATION MATRIX
            </span>

            <span className="px-3 py-1 rounded-full border border-neutral-500/20 bg-neutral-500/10 text-neutral-200 text-[11px] uppercase tracking-[0.25em] font-semibold animate-pulse">
              AI FLOW ACTIVE
            </span>

          </div>

          <div>
            <h2 className="text-3xl md:text-4xl font-black tracking-tight bg-gradient-to-r from-white via-purple-200 to-cyan-300 bg-clip-text text-transparent">
              Institutional Correlation Explorer
            </h2>

            <p className="text-sm md:text-base text-gray-400 mt-3 max-w-3xl leading-relaxed">
              AI-driven correlated asset discovery engine with institutional liquidity mapping, macro rotation analysis, and realtime cross-market intelligence.
            </p>
          </div>

        </div>

        <div className="relative z-10 flex items-center gap-3 flex-wrap">

          <div className="px-4 py-2 rounded-2xl border border-neutral-500/20 bg-neutral-500/10 text-neutral-200 text-sm font-semibold backdrop-blur-xl shadow-[0_0_30px_rgba(168,85,247,0.12)]">
            SMART DISCOVERY ACTIVE
          </div>

          <div className="px-4 py-2 rounded-2xl border border-cyan-500/20 bg-white/10 text-white text-sm font-semibold backdrop-blur-xl shadow-[0_0_30px_rgba(255,255,255,0.03)]">
            LIVE CORRELATIONS
          </div>

        </div>

      </div>

      <div className="relative z-10 grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">

        {suggestedAssets.map((asset) => (
          <button
            key={asset}
            onClick={() => {
              router.push(`/asset/${encodeURIComponent(asset.replace("/", "-"))}`);
            }}
            className="group relative overflow-hidden rounded-[30px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 text-left hover:border-cyan-500/30 transition-all duration-500 hover:-translate-y-1 hover:scale-[1.02] hover:shadow-[0_0_60px_rgba(255,255,255,0.03)]"
          >
            <div className="absolute inset-0 opacity-40 pointer-events-none bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.03),transparent_45%)]" />
            <div className="relative z-10 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3 min-w-0">
                <div className="relative w-16 h-16 rounded-2xl bg-white/95 p-3 shrink-0 overflow-hidden border border-white/20 shadow-[0_0_30px_rgba(255,255,255,0.12)]">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.4),transparent_45%)]" />
                  <img
                    src={getAssetLogo(asset)}
                    alt={asset}
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      (e.currentTarget as HTMLImageElement).src =
                        "https://s3-symbol-logo.tradingview.com/country/US--big.svg";
                    }}
                  />
                </div>
                <div className="min-w-0">
                  <h3 className="text-lg font-bold truncate text-white">
                    {asset}
                  </h3>
                  <p className="text-xs text-white mt-2 uppercase tracking-[0.2em] font-semibold">
                    {getAssetType(asset)} MARKET
                  </p>
                </div>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-white/10 border border-cyan-500/20 flex items-center justify-center text-white text-xl shrink-0 group-hover:scale-110 transition-transform duration-300 shadow-[0_0_30px_rgba(255,255,255,0.03)]">
                ↗
              </div>
            </div>
            <div className="relative z-10 mt-6 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-2xl border border-white/10 bg-black/20 backdrop-blur-xl p-3">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500 mb-2">
                    Correlation
                  </p>
                  <div className="text-lg font-black text-white">
                    {85 + (asset.charCodeAt(0) % 15)}%
                  </div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/20 backdrop-blur-xl p-3">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500 mb-2">
                    Flow State
                  </p>
                  <div className="flex items-center gap-2 text-white text-sm font-semibold">
                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                    ACTIVE
                  </div>
                </div>
              </div>
              <div className="rounded-2xl border border-neutral-500/20 bg-purple-500/5 p-4 backdrop-blur-xl">
                <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-gray-500 mb-3">
                  <span>Institutional Rotation</span>
                  <span>LIVE</span>
                </div>
                <div className="w-full h-2 rounded-full bg-white/5 overflow-hidden mb-3">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500"
                    style={{
                      width: `${70 + (asset.charCodeAt(asset.length - 1) % 25)}%`,
                    }}
                  />
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">
                  AI engine detecting institutional cross-market liquidity alignment.
                </p>
              </div>
            </div>
          </button>
        ))}

      </div>

      <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-4">

        <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
          <div className="relative z-10 space-y-3">
            <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
              Risk-On Flow
            </p>

            <div className="text-3xl font-black text-white">
              ACCELERATING
            </div>

            <p className="text-sm text-gray-400 leading-relaxed">
              Cross-market liquidity rotation currently favoring high-beta institutional exposure.
            </p>
          </div>
        </div>

        <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
          <div className="relative z-10 space-y-3">
            <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
              Safe Haven Rotation
            </p>

            <div className="text-3xl font-black text-neutral-300">
              MODERATE
            </div>

            <p className="text-sm text-gray-400 leading-relaxed">
              Defensive capital flows remain balanced despite elevated macro volatility conditions.
            </p>
          </div>
        </div>

        <div className="rounded-[28px] border border-white/10 bg-black/20 backdrop-blur-2xl p-5 overflow-hidden relative">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />
          <div className="relative z-10 space-y-3">
            <p className="text-[11px] uppercase tracking-[0.25em] text-gray-500">
              AI Correlation Engine
            </p>

            <div className="text-3xl font-black text-white">
              SYNCHRONIZED
            </div>

            <p className="text-sm text-gray-400 leading-relaxed">
              QuantView AI actively mapping realtime institutional liquidity relationships.
            </p>
          </div>
        </div>

      </div>

      {/* Premium Pine Script / Layout Modal */}
      {isLayoutModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md transition-all duration-300">
          <div className="relative w-full max-w-lg overflow-hidden rounded-[32px] border border-white/10 bg-[#161616] p-8 shadow-[0_0_80px_rgba(168,85,247,0.25)] space-y-6">
            <div className="absolute top-0 right-0 p-6">
              <button
                onClick={() => setIsLayoutModalOpen(false)}
                className="text-gray-400 hover:text-white transition-colors text-2xl font-semibold focus:outline-none"
              >
                ×
              </button>
            </div>

            <div className="space-y-2">
              <div className="inline-flex p-3 rounded-2xl bg-neutral-500/10 border border-neutral-500/20 text-neutral-200">
                <TrendingUp className="w-6 h-6" />
              </div>
              <h3 className="text-2xl font-bold text-white tracking-tight">
                Link Pine Script Chart Layout
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                Standard web chart widgets cannot run local Pine Scripts directly because Pine's compiler is fully proprietary to TradingView. 
                Instead, you can load your custom indicators in three steps:
              </p>
            </div>

            <div className="space-y-3.5 text-xs text-gray-300">
              <div className="flex gap-3">
                <span className="flex items-center justify-center w-5 h-5 shrink-0 rounded-full bg-neutral-500/10 text-neutral-200 text-[10px] font-bold border border-neutral-500/20">
                  1
                </span>
                <p>
                  Add your custom indicator (like <b>Price Action Concepts</b>) onto your chart inside your TradingView account.
                </p>
              </div>

              <div className="flex gap-3">
                <span className="flex items-center justify-center w-5 h-5 shrink-0 rounded-full bg-neutral-500/10 text-neutral-200 text-[10px] font-bold border border-neutral-500/20">
                  2
                </span>
                <p>
                  Click <b>Save</b> on your TradingView chart (top-right), enable <b>Chart Sharing</b>, and copy the Layout ID from the URL (e.g. the string after <code>/chart/</code>, e.g. <code>p3d9a7v8</code>).
                </p>
              </div>

              <div className="flex gap-3">
                <span className="flex items-center justify-center w-5 h-5 shrink-0 rounded-full bg-neutral-500/10 text-neutral-200 text-[10px] font-bold border border-neutral-500/20">
                  3
                </span>
                <p>
                  Enter the Layout ID below to embed your personalized Pine Script drawings directly into this terminal screen!
                </p>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <label className="text-[10px] uppercase tracking-wider text-neutral-200 font-bold">
                TradingView Chart Layout ID
              </label>
              <input
                type="text"
                value={customLayoutId}
                onChange={(e) => {
                  const val = e.target.value.trim();
                  setCustomLayoutId(val);
                  localStorage.setItem("quantview_custom_layout_id", val);
                }}
                placeholder="e.g. p3d9a7v8"
                className="w-full px-5 py-3 rounded-2xl bg-black/40 border border-white/10 text-white placeholder-gray-600 focus:outline-none focus:border-purple-500 transition-all font-mono text-sm"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => {
                  setCustomLayoutId("");
                  localStorage.removeItem("quantview_custom_layout_id");
                }}
                className="px-4 py-2.5 rounded-xl border border-white/5 text-gray-400 hover:text-white transition-all text-[10px] uppercase font-bold"
              >
                Clear Layout
              </button>
              <button
                onClick={() => setIsLayoutModalOpen(false)}
                className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white transition-all text-[10px] uppercase font-bold shadow-[0_0_30px_rgba(168,85,247,0.3)]"
              >
                Apply & Reload Chart
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    </div>
  );
}