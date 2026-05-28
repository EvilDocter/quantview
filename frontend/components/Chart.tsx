"use client";

import { useEffect, useRef, useState } from "react";
import {
  createChart,
  ColorType,
  CandlestickSeries,
} from "lightweight-charts";

export default function Chart({
  symbol,
  interval,
}: {
  symbol: string;
  interval: string;
}) {
  const chartContainerRef = useRef<HTMLDivElement | null>(null);
  const [isMarketClosed, setIsMarketClosed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 420,
      layout: {
        background: {
          type: ColorType.Solid,
          color: "#020617",
        },
        textColor: "#d1d5db",
      },
      grid: {
        vertLines: { color: "#1e293b" },
        horzLines: { color: "#1e293b" },
      },
      rightPriceScale: {
        autoScale: true,
        borderColor: "#334155",
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
      timeScale: {
        borderColor: "#334155",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 5,
        barSpacing: 12,
      },
      localization: {
        priceFormatter: (price: number) => {
          if (price > 1000) {
            return price.toFixed(2);
          }

          if (price > 1) {
            return price.toFixed(4);
          }

          return price.toFixed(6);
        },
      },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
      priceLineVisible: false,
    });

    async function fetchData() {
      setIsLoading(true);
      try {
        setHasError(false);
        const intervalMap: Record<string, string> = {
          "1m": "1min",
          "5m": "5min",
          "15m": "15min",
          "1H": "1h",
        };
        const apiInterval = intervalMap[interval] || "5min";
        const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || (typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1:8000");
        const res = await fetch(
          `${BACKEND_URL}/market/candles?symbol=${encodeURIComponent(symbol)}&interval=${apiInterval}`
        );

        const json = await res.json();

        if (!json?.data || json.data.length === 0) {
          setHasError(true);
          setIsLoading(false);
          return;
        }

        const formatted = (json.data || [])
          .map((candle: any) => ({
            time: Math.floor(
              new Date(candle.datetime).getTime() / 1000
            ) as any,
            open: Number(candle.open),
            high: Number(candle.high),
            low: Number(candle.low),
            close: Number(candle.close),
          }))
          .filter(
            (candle: any) =>
              !isNaN(candle.open) &&
              !isNaN(candle.high) &&
              !isNaN(candle.low) &&
              !isNaN(candle.close)
          )
          .sort((a: any, b: any) => a.time - b.time);

        if (formatted.length === 0) {
          setHasError(true);
          setIsLoading(false);
          return;
        }

        const avgMovement =
          formatted.reduce(
            (acc: number, candle: any) =>
              acc + Math.abs(candle.open - candle.close),
            0
          ) / Math.max(formatted.length, 1);

        const isFlat = avgMovement < 0.00005;

        setIsMarketClosed(isFlat && interval !== "1m");

        setIsLoading(false);
        series.setData(formatted as any);
        chart.timeScale().fitContent();
      } catch (err) {
        setHasError(true);
        setIsLoading(false);
        console.error("Chart fetch error:", err);
      }
    }

    fetchData();

    const intervalId = setInterval(fetchData, 600000);

    const handleResize = () => {
      if (!chartContainerRef.current) return;
      chart.applyOptions({
        width: chartContainerRef.current.clientWidth,
        height: chartContainerRef.current.clientHeight,
      });
      chart.timeScale().fitContent();
    };

    window.addEventListener("resize", handleResize);
    handleResize();

    return () => {
      clearInterval(intervalId);
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [symbol, interval]);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "420px",
        overflow: "hidden",
        borderRadius: "14px",
      }}
    >
      {isLoading && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(2,6,23,0.75)",
            backdropFilter: "blur(6px)",
            color: "#d1d5db",
            zIndex: 20,
            fontSize: "14px",
          }}
        >
          Loading chart...
        </div>
      )}

      {hasError && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(2,6,23,0.85)",
            backdropFilter: "blur(6px)",
            color: "#ef4444",
            zIndex: 20,
            fontSize: "14px",
            textAlign: "center",
            padding: "20px",
          }}
        >
          Unable to load realtime candles.<br />
          API quota or market feed issue.
        </div>
      )}

      {isMarketClosed && (
        <div
          style={{
            position: "absolute",
            top: 10,
            right: 10,
            background: "#ef4444",
            color: "white",
            padding: "4px 10px",
            borderRadius: "6px",
            fontSize: "12px",
            zIndex: 10,
          }}
        >
          Low Volatility
        </div>
      )}

      <div
        ref={chartContainerRef}
        style={{
          width: "100%",
          height: "100%",
        }}
      />
    </div>
  );
}