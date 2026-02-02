'use client';

import { useLayoutEffect, useState } from 'react';
import ProtectedPage from '@/components/ProtectedPage';
import { useQuery } from '@tanstack/react-query';
import { getNews } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import { useAccount } from 'wagmi';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function Dashboard() {
    return (
        <ProtectedPage>
            <DashboardContent />
        </ProtectedPage>
    );
}

function DashboardContent() {
    const [selectedToken, setSelectedToken] = useState<string | undefined>(undefined);
    const { address } = useAccount();

    // Polling for news every 30 seconds
    const { data: news, isLoading } = useQuery({
        queryKey: ['news', selectedToken],
        queryFn: () => getNews(selectedToken),
        refetchInterval: 30000,
    });

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-8">
            <header className="flex justify-between items-center mb-10 max-w-7xl mx-auto">
                <div className="flex items-center gap-4">
                    <Link href="/" className="p-2 text-slate-400 hover:text-white bg-slate-800/50 hover:bg-slate-800 rounded-full transition" title="Back to Home">
                        <ArrowLeft size={20} />
                    </Link>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-500">
                        Live Feed
                    </h1>
                </div>
                <div className="flex gap-4">
                    <Link href="/api-keys" className="px-4 py-2 text-sm bg-slate-800 rounded-lg hover:bg-slate-700 transition">
                        Manage Keys
                    </Link>
                    <Link href="/billing" className="px-4 py-2 text-sm bg-indigo-900/40 text-indigo-300 rounded-lg hover:bg-indigo-900/60 transition">
                        Buy Credits
                    </Link>
                </div>
            </header>

            <div className="max-w-7xl mx-auto">
                <div className="flex gap-4 mb-8">
                    <button
                        onClick={() => setSelectedToken(undefined)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition ${!selectedToken ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400'}`}
                    >
                        All
                    </button>
                    <button
                        onClick={() => setSelectedToken('ethereum')}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition ${selectedToken === 'ethereum' ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400'}`}
                    >
                        Ethereum
                    </button>
                    <button
                        onClick={() => setSelectedToken('bitcoin')}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition ${selectedToken === 'bitcoin' ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400'}`}
                    >
                        Bitcoin
                    </button>
                </div>

                {isLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[1, 2, 3, 4, 5, 6].map(i => (
                            <div key={i} className="h-64 bg-slate-900/50 rounded-2xl animate-pulse"></div>
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {news?.map((item: any) => (
                            <NewsCard key={item.id} item={item} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function NewsCard({ item }: { item: any }) {
    const date = new Date(item.timestamp);

    return (
        <div className="group bg-slate-900/50 border border-slate-800 p-6 rounded-2xl hover:border-purple-500/50 transition-all hover:shadow-[0_0_20px_-5px_rgba(168,85,247,0.2)]">
            <div className="flex justify-between items-start mb-4">
                <span className="text-xs font-mono text-purple-400 bg-purple-400/10 px-2 py-1 rounded">
                    {item.token_id?.toUpperCase() || 'CRYPTO'}
                </span>
                <span className="text-xs text-slate-500">
                    {formatDistanceToNow(date, { addSuffix: true })}
                </span>
            </div>

            <h3 className="text-lg font-bold mb-3 text-white group-hover:text-purple-200 transition">
                {item.title}
            </h3>

            <p className="text-slate-400 text-sm leading-relaxed mb-4 line-clamp-4">
                {item.content}
            </p>

            {item.sources && item.sources.length > 0 && (
                <div className="pt-4 border-t border-slate-800/50 flex flex-wrap gap-2">
                    {item.sources.map((source: any, idx: number) => (
                        <a
                            key={idx}
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-indigo-400 hover:text-indigo-300 truncate max-w-[150px]"
                        >
                            {source.title || 'Source'} ↗
                        </a>
                    ))}
                </div>
            )}
        </div>
    );
}
