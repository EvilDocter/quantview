"use client";

import { useEffect, useRef } from "react";

export default function TradingViewWidget({ symbol }: { symbol: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    // Clear previous widget
    ref.current.innerHTML = "";

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;

    const tvSymbolMap: Record<string, string> = {
      "EUR/USD": "FX:EURUSD",
      "USD/JPY": "FX:USDJPY",
      "GBP/USD": "FX:GBPUSD",
      "XAU/USD": "OANDA:XAUUSD",
    };

    const tvSymbol = tvSymbolMap[symbol] || "FX:EURUSD";

    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: tvSymbol,
      interval: "5",
      timezone: "Asia/Kolkata",
      theme: "dark",
      style: "1",
      locale: "en",
      hide_top_toolbar: false,
      allow_symbol_change: true,
    });

    ref.current.appendChild(script);
  }, [symbol]);

  return <div ref={ref} style={{ height: "100%", width: "100%" }} />;
}