'use client';

import { ConnectButton } from '@rainbow-me/rainbowkit';
import Link from 'next/link';
import { ArrowRight, Terminal, BarChart2, Zap, Database } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      {/* Navigation */}
      <nav className="w-full border-b border-slate-800 bg-slate-950/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
            On-Chain News
          </div>
          <div className="flex gap-6 items-center">
            <Link href="/docs" className="text-sm text-slate-400 hover:text-white transition">API Docs</Link>
            <ConnectButton showBalance={false} accountStatus="address" chainStatus="none" />
          </div>
        </div>
      </nav>

      <main className="flex flex-col items-center">

        {/* HERO SECTION */}
        <section className="w-full max-w-5xl px-6 py-24 md:py-32 flex flex-col items-center text-center">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 text-white">
            On-Chain News, <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              Distilled Into Actionable Signals
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-slate-400 mb-6 max-w-3xl leading-relaxed">
            Real-time crypto insights from on-chain data, market events, and ecosystem signals — summarized, structured, and API-ready.
          </p>

          <p className="text-indigo-300 font-medium mb-10 text-lg">
            Not noise. Not speculation. Just what actually moved the market.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <Link
              href="/dashboard"
              className="px-8 py-4 bg-white text-slate-950 font-bold rounded-lg hover:bg-slate-200 transition flex items-center justify-center gap-2"
            >
              Get API Access <ArrowRight size={18} />
            </Link>
            <Link
              href="/dashboard"
              className="px-8 py-4 border border-slate-700 bg-slate-900/50 text-white font-medium rounded-lg hover:bg-slate-800 transition flex items-center justify-center"
            >
              View Live Signals
            </Link>
          </div>
        </section>

        {/* WHAT THIS IS */}
        <section className="w-full bg-slate-900/30 border-y border-slate-800 py-24">
          <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-sm font-bold text-purple-400 uppercase tracking-wider mb-2">What is this platform?</h2>
              <h3 className="text-3xl md:text-4xl font-bold text-white mb-6">
                We track on-chain activity, protocol updates, market structure changes, and ecosystem events.
              </h3>
              <p className="text-lg text-slate-400 leading-relaxed mb-6">
                We turn raw data into short, human-readable insights like:
              </p>

              <ul className="space-y-4 mb-8">
                <li className="flex gap-4 p-4 bg-slate-950 rounded-xl border border-slate-800">
                  <div className="w-1 bg-green-500 rounded-full h-full"></div>
                  <p className="font-mono text-green-300 text-sm">"HYPE gained 34% in 7 days, showing inverse correlation with Bitcoin."</p>
                </li>
                <li className="flex gap-4 p-4 bg-slate-950 rounded-xl border border-slate-800">
                  <div className="w-1 bg-blue-500 rounded-full h-full"></div>
                  <p className="font-mono text-blue-300 text-sm">"HIP-3 went live, requiring 500,000 HYPE staking — increasing token demand."</p>
                </li>
              </ul>

              <div className="flex gap-8 text-slate-500 font-medium pt-4 border-t border-slate-800/50">
                <span className="flex items-center gap-2"><div className="w-2 h-2 bg-red-500 rounded-full"></div> No scrolling Twitter</span>
                <span className="flex items-center gap-2"><div className="w-2 h-2 bg-red-500 rounded-full"></div> No reading 10 articles</span>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent blur-3xl rounded-full"></div>
              <div className="relative bg-slate-950 border border-slate-800 rounded-2xl p-8 shadow-2xl">
                <div className="flex items-center gap-3 mb-6 border-b border-slate-800 pb-4">
                  <Terminal size={20} className="text-slate-500" />
                  <span className="text-sm font-mono text-slate-500">api_response.json</span>
                </div>
                <pre className="font-mono text-xs md:text-sm text-slate-300 overflow-x-auto">
                  {`{
  "id": "hyp_8293",
  "token": "HYPE",
  "signal": "staking_requirement_increase",
  "impact": "high_demand",
  "summary": "HIP-3 requires 500k HYPE staking.",
  "sources": 3,
  "confidence": 0.98
}`}
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* EXAMPLE INSIGHTS */}
        <section className="w-full max-w-7xl mx-auto px-6 py-24">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Example Signals</h2>
            <p className="text-slate-400">See exactly what you get.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Card 1 */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 hover:border-purple-500/30 transition group">
              <h3 className="text-xl font-bold text-white mb-3 group-hover:text-purple-300 transition">Hyperliquid Grows Perpetuals Market Share</h3>
              <p className="text-slate-400 mb-6 leading-relaxed">
                Hyperliquid’s perpetuals market share is rising against Bybit, OKX, and Binance — signaling increased adoption and revenue potential for HYPE.
              </p>
              <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                2 sources · 6 hours ago
              </div>
            </div>

            {/* Card 2 */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 hover:border-purple-500/30 transition group">
              <h3 className="text-xl font-bold text-white mb-3 group-hover:text-purple-300 transition">HIP-4 Introduces On-Chain Prediction Markets</h3>
              <p className="text-slate-400 mb-6 leading-relaxed">
                Hyperliquid announced HIP-4, adding prediction markets and bounded options — expanding product scope and fee generation.
              </p>
              <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                3 sources · 7 hours ago
              </div>
            </div>

            {/* Card 3 */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 hover:border-purple-500/30 transition group">
              <h3 className="text-xl font-bold text-white mb-3 group-hover:text-purple-300 transition">HIP-3 Goes Live, Requires HYPE Staking</h3>
              <p className="text-slate-400 mb-6 leading-relaxed">
                Permissionless market creation now requires staking 500,000 HYPE, increasing token utility and long-term demand.
              </p>
              <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                3 sources · 8 hours ago
              </div>
            </div>

            {/* Card 4 */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 hover:border-purple-500/30 transition group">
              <h3 className="text-xl font-bold text-white mb-3 group-hover:text-purple-300 transition">HYPE Gains 34%, Shows Inverse BTC Correlation</h3>
              <p className="text-slate-400 mb-6 leading-relaxed">
                HYPE was the only DEX token up in the last 7 days, with a −0.49 correlation to Bitcoin — indicating independent momentum.
              </p>
              <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                3 sources · 9 hours ago
              </div>
            </div>
          </div>
        </section>

        {/* WHO THIS IS FOR */}
        <section className="w-full bg-slate-900 border-t border-slate-800 py-24">
          <div className="max-w-5xl mx-auto px-6 text-center">
            <h2 className="text-3xl font-bold text-white mb-12">Built for people who need signal, not hype</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="p-6">
                <div className="w-12 h-12 bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-4 text-purple-400">
                  <BarChart2 size={24} />
                </div>
                <h3 className="font-bold text-white mb-2">Traders</h3>
                <p className="text-sm text-slate-400">Understand why a token moved</p>
              </div>

              <div className="p-6">
                <div className="w-12 h-12 bg-pink-900/30 rounded-full flex items-center justify-center mx-auto mb-4 text-pink-400">
                  <Database size={24} />
                </div>
                <h3 className="font-bold text-white mb-2">Funds & Analysts</h3>
                <p className="text-sm text-slate-400">Track ecosystem-level changes</p>
              </div>

              <div className="p-6">
                <div className="w-12 h-12 bg-indigo-900/30 rounded-full flex items-center justify-center mx-auto mb-4 text-indigo-400">
                  <Zap size={24} />
                </div>
                <h3 className="font-bold text-white mb-2">Crypto Apps</h3>
                <p className="text-sm text-slate-400">Enrich dashboards with real-time insights</p>
              </div>

              <div className="p-6">
                <div className="w-12 h-12 bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4 text-green-400">
                  <Terminal size={24} />
                </div>
                <h3 className="font-bold text-white mb-2">AI Agents</h3>
                <p className="text-sm text-slate-400">Feed structured market intelligence</p>
              </div>
            </div>

            <div className="mt-16 bg-slate-950 border border-slate-800 p-8 rounded-2xl max-w-2xl mx-auto">
              <p className="text-lg text-slate-300 font-medium">
                "If your product or strategy depends on knowing what just happened, this is for you."
              </p>
              <div className="mt-6">
                <Link href="/dashboard" className="text-purple-400 hover:text-white font-bold text-sm uppercase tracking-wider transition">
                  Get Started Now &rarr;
                </Link>
              </div>
            </div>
          </div>
        </section>

      </main>

      <footer className="border-t border-slate-800 bg-slate-950 py-12 text-center text-slate-600 text-sm">
        <p>&copy; 2026 On-Chain News. All rights reserved.</p>
      </footer>
    </div>
  );
}
