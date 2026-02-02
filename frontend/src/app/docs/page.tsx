'use client';

import Link from 'next/link';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ArrowLeft, Copy, Check } from 'lucide-react';
import { useState } from 'react';

export default function DocsPage() {
    return (
        <div className="min-h-screen bg-slate-950 text-slate-200">
            {/* Navigation */}
            <nav className="border-b border-slate-800 bg-slate-950/50 backdrop-blur sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="text-slate-400 hover:text-white transition">
                            <ArrowLeft size={20} />
                        </Link>
                        <h1 className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
                            API Documentation
                        </h1>
                    </div>
                    <div className="flex gap-4 text-sm">
                        <Link href="/dashboard" className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition">
                            Get API Key
                        </Link>
                    </div>
                </div>
            </nav>

            <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 lg:grid-cols-4 gap-12">
                {/* Sidebar */}
                <aside className="hidden lg:block space-y-8 sticky top-24 h-fit">
                    <div className="space-y-4">
                        <h3 className="font-bold text-white uppercase tracking-wider text-sm">Getting Started</h3>
                        <ul className="space-y-2 text-sm text-slate-400">
                            <li><a href="#introduction" className="hover:text-purple-400 transition">Introduction</a></li>
                            <li><a href="#authentication" className="hover:text-purple-400 transition">Authentication</a></li>
                            <li><a href="#base-url" className="hover:text-purple-400 transition">Base URL</a></li>
                        </ul>
                    </div>
                    <div className="space-y-4">
                        <h3 className="font-bold text-white uppercase tracking-wider text-sm">Endpoints</h3>
                        <ul className="space-y-2 text-sm text-slate-400">
                            <li><a href="#get-news" className="hover:text-purple-400 transition">Get News</a></li>
                            <li><a href="#get-usage" className="hover:text-purple-400 transition">Check Usage</a></li>
                            <li><a href="#get-status" className="hover:text-purple-400 transition">System Status</a></li>
                        </ul>
                    </div>
                </aside>

                {/* Content */}
                <main className="lg:col-span-3 space-y-16">

                    {/* Introduction */}
                    <section id="introduction" className="space-y-4">
                        <h2 className="text-3xl font-bold text-white">Introduction</h2>
                        <p className="text-lg text-slate-400 leading-relaxed">
                            The On-Chain News API provides real-time, algorithmic insights into cryptocurrency markets.
                            Our data is sourced directly from on-chain events and aggregated market signals, delivering low-latency updates for trading bots and analytics platforms.
                        </p>
                    </section>

                    {/* Authentication */}
                    <section id="authentication" className="space-y-6">
                        <h2 className="text-3xl font-bold text-white">Authentication</h2>
                        <p className="text-slate-400">
                            All API requests require an API key to be verified. You can generate a key in your <Link href="/api-keys" className="text-purple-400 hover:underline">Dashboard</Link>.
                            Pass this key in the <code className="text-purple-300">X-API-Key</code> header.
                        </p>

                        <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                            <div className="px-4 py-2 border-b border-slate-800 bg-slate-900/50 text-xs text-slate-500 font-mono">Example Request Header</div>
                            <CodeBlock language="bash" code={`curl -H "X-API-Key: sk_live_..." https://api.onchainnews.com/news`} />
                        </div>
                    </section>

                    {/* Endpoints */}
                    <section id="get-news" className="space-y-6">
                        <div className="flex items-center gap-3">
                            <span className="px-3 py-1 bg-green-500/20 text-green-400 text-sm font-bold rounded">GET</span>
                            <h2 className="text-3xl font-bold text-white">/news</h2>
                        </div>
                        <p className="text-slate-400">Retrieve the latest news insights. Results are paginated and sortable.</p>

                        <h3 className="text-xl font-bold text-white mt-8">Parameters</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm text-slate-400">
                                <thead className="text-xs uppercase bg-slate-900/50 text-slate-300">
                                    <tr>
                                        <th className="px-6 py-3">Parameter</th>
                                        <th className="px-6 py-3">Type</th>
                                        <th className="px-6 py-3">Description</th>
                                        <th className="px-6 py-3">Default</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800">
                                    <tr>
                                        <td className="px-6 py-4 font-mono text-purple-300">token_id</td>
                                        <td className="px-6 py-4">string</td>
                                        <td className="px-6 py-4">Filter by token slug (e.g. 'bitcoin', 'ethereum')</td>
                                        <td className="px-6 py-4">-</td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 font-mono text-purple-300">limit</td>
                                        <td className="px-6 py-4">integer</td>
                                        <td className="px-6 py-4">Number of items to return (max 100)</td>
                                        <td className="px-6 py-4">20</td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 font-mono text-purple-300">offset</td>
                                        <td className="px-6 py-4">integer</td>
                                        <td className="px-6 py-4">Pagination offset</td>
                                        <td className="px-6 py-4">0</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <h3 className="text-xl font-bold text-white mt-8">Response</h3>
                        <CodeBlock language="json" code={`[
  {
    "id": "ethereum_1701234567",
    "token_id": "ethereum",
    "timestamp": 1701234567,
    "title": "Large Whale Movement Detected",
    "content": "A wallet associated with... transferred 5000 ETH...",
    "source_count": 2,
    "sources": [
        { "url": "https://...", "title": "Etherscan Transaction" }
    ]
  }
]`} />
                    </section>

                    <section id="get-usage" className="space-y-6">
                        <div className="flex items-center gap-3">
                            <span className="px-3 py-1 bg-green-500/20 text-green-400 text-sm font-bold rounded">GET</span>
                            <h2 className="text-3xl font-bold text-white">/billing/usage</h2>
                        </div>
                        <p className="text-slate-400">Check your current API usage and plan limits.</p>

                        <h3 className="text-xl font-bold text-white mt-8">Response</h3>
                        <CodeBlock language="json" code={`{
  "total_requests": 1450,
  "plan": "Pro"
}`} />
                    </section>
                </main>
            </div>
        </div>
    );
}

function CodeBlock({ code, language }: { code: string, language: string }) {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative group rounded-xl overflow-hidden border border-slate-800">
            <button
                onClick={handleCopy}
                className="absolute right-4 top-4 p-2 bg-slate-800/80 rounded hover:bg-slate-700 text-slate-400 hover:text-white transition opacity-0 group-hover:opacity-100"
            >
                {copied ? <Check size={16} /> : <Copy size={16} />}
            </button>
            <SyntaxHighlighter
                language={language}
                style={vscDarkPlus}
                customStyle={{ margin: 0, padding: '1.5rem', background: '#0f172a' }}
            >
                {code}
            </SyntaxHighlighter>
        </div>
    );
}
