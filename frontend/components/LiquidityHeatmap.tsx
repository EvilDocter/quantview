

"use client";

interface HeatmapProps {
  signal?: any;
  projection?: any;
}

export default function LiquidityHeatmap({
  signal,
  projection,
}: HeatmapProps) {

  const bullish = projection?.probability_map?.bullish || 50;
  const bearish = projection?.probability_map?.bearish || 50;

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-[32px] z-0">

      <div className="absolute inset-0 opacity-[0.08] bg-[linear-gradient(to_right,rgba(255,255,255,0.08)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.08)_1px,transparent_1px)] bg-[size:60px_60px]" />

      <div className="absolute top-[12%] left-0 right-0 h-[12%] bg-gradient-to-r from-transparent via-red-500/20 to-transparent blur-2xl animate-pulse" />

      <div className="absolute bottom-[18%] left-0 right-0 h-[14%] bg-gradient-to-r from-transparent via-green-500/20 to-transparent blur-2xl animate-pulse" />

      <div className="absolute left-[8%] top-[28%] w-[22%] h-[22%] rounded-[40px] border border-red-500/20 bg-neutral-600/10 backdrop-blur-md shadow-[0_0_80px_rgba(239,68,68,0.16)] overflow-hidden">

        <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />

        <div className="relative z-10 p-5 h-full flex flex-col justify-between">

          <div>
            <p className="text-[10px] uppercase tracking-[0.25em] text-red-300/70 mb-2">
              Sell Liquidity
            </p>

            <div className="text-2xl font-black text-neutral-400">
              HEAVY OFFLOAD
            </div>
          </div>

          <div>
            <div className="w-full h-2 rounded-full bg-white/5 overflow-hidden mb-3">
              <div
                className="h-full rounded-full bg-gradient-to-r from-red-400 to-pink-500"
                style={{ width: `${bearish}%` }}
              />
            </div>

            <div className="text-xs text-red-200/70">
              Institutional sell-side liquidity detected.
            </div>
          </div>

        </div>
      </div>

      <div className="absolute right-[8%] bottom-[24%] w-[24%] h-[24%] rounded-[40px] border border-green-500/20 bg-white/10 backdrop-blur-md shadow-[0_0_80px_rgba(255,255,255,0.03)] overflow-hidden animate-pulse">

        <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />

        <div className="relative z-10 p-5 h-full flex flex-col justify-between">

          <div>
            <p className="text-[10px] uppercase tracking-[0.25em] text-green-300/70 mb-2">
              Buy Liquidity
            </p>

            <div className="text-2xl font-black text-white">
              ACCUMULATION
            </div>
          </div>

          <div>
            <div className="w-full h-2 rounded-full bg-white/5 overflow-hidden mb-3">
              <div
                className="h-full rounded-full bg-gradient-to-r from-green-400 to-emerald-500"
                style={{ width: `${bullish}%` }}
              />
            </div>

            <div className="text-xs text-green-200/70">
              Smart money accumulation cluster active.
            </div>
          </div>

        </div>
      </div>

      <div className="absolute left-[20%] top-[50%] w-[18%] h-[1px] bg-gradient-to-r from-cyan-400 to-transparent rotate-[14deg] opacity-80" />

      <div className="absolute left-[28%] top-[54%] w-[22%] h-[1px] bg-gradient-to-r from-purple-400 to-transparent -rotate-[12deg] opacity-60" />

      <div className="absolute right-[18%] top-[38%] w-[20%] h-[1px] bg-gradient-to-r from-yellow-400 to-transparent rotate-[18deg] opacity-70" />

      <div className="absolute top-[42%] left-[50%] -translate-x-1/2 -translate-y-1/2">

        <div className="relative w-56 h-56 rounded-full border border-cyan-500/20 bg-cyan-500/5 backdrop-blur-2xl flex items-center justify-center shadow-[0_0_120px_rgba(255,255,255,0.05)]">

          <div className="absolute inset-0 rounded-full border border-cyan-400/20 animate-ping" />
          <div className="absolute inset-6 rounded-full border border-purple-400/20 animate-spin [animation-duration:12s]" />

          <div className="text-center relative z-10">

            <p className="text-[10px] uppercase tracking-[0.25em] text-gray-500 mb-2">
              Orderflow Energy
            </p>

            <div className="text-5xl font-black text-white">
              {signal?.confidence || 0}%
            </div>

            <div className="text-sm text-gray-400 mt-2 uppercase tracking-wide">
              Liquidity Active
            </div>

          </div>

        </div>

      </div>

      <div className="absolute bottom-[8%] left-[8%] right-[8%] grid grid-cols-1 md:grid-cols-3 gap-4">

        <div className="rounded-3xl border border-white/10 bg-black/40 backdrop-blur-2xl p-5 overflow-hidden relative">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />

          <div className="relative z-10 space-y-3">
            <p className="text-[10px] uppercase tracking-[0.25em] text-gray-500">
              Sell Pressure
            </p>

            <div className="text-3xl font-black text-neutral-400">
              {bearish}%
            </div>

            <div className="text-xs text-gray-400">
              Aggressive institutional sell-side flow.
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-black/40 backdrop-blur-2xl p-5 overflow-hidden relative">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />

          <div className="relative z-10 space-y-3">
            <p className="text-[10px] uppercase tracking-[0.25em] text-gray-500">
              Liquidity Pulse
            </p>

            <div className="flex items-center gap-2 text-white font-black text-2xl">
              <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse" />
              ACTIVE
            </div>

            <div className="text-xs text-gray-400">
              Live orderflow mapping enabled.
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-black/40 backdrop-blur-2xl p-5 overflow-hidden relative">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.05),transparent_45%)]" />

          <div className="relative z-10 space-y-3">
            <p className="text-[10px] uppercase tracking-[0.25em] text-gray-500">
              Buy Pressure
            </p>

            <div className="text-3xl font-black text-white">
              {bullish}%
            </div>

            <div className="text-xs text-gray-400">
              Institutional accumulation intensity rising.
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}