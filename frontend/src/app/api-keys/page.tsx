'use client';

import { useState } from 'react';
import ProtectedPage from '@/components/ProtectedPage';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getApiKeys, createApiKey, revokeApiKey } from '@/lib/api';
import { useAccount } from 'wagmi';
import Link from 'next/link';
import { Loader2, Plus, Trash2, Key, Copy, Check, ArrowLeft } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function ApiKeysPage() {
    return (
        <ProtectedPage>
            <ApiKeysContent />
        </ProtectedPage>
    );
}

function ApiKeysContent() {
    const { address } = useAccount();
    const queryClient = useQueryClient();
    const [newKeyName, setNewKeyName] = useState('');
    const [createdKey, setCreatedKey] = useState<string | null>(null);
    const [copied, setCopied] = useState(false);

    const { data: keys, isLoading } = useQuery({
        queryKey: ['api-keys', address],
        queryFn: () => getApiKeys(address!),
        enabled: !!address,
    });

    const createMutation = useMutation({
        mutationFn: (name: string) => createApiKey(address!, name),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['api-keys'] });
            setCreatedKey(data.key);
            setNewKeyName('');
        },
    });

    const revokeMutation = useMutation({
        mutationFn: (id: string) => revokeApiKey(address!, id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['api-keys'] });
        },
    });

    const handleCreate = (e: React.FormEvent) => {
        e.preventDefault();
        if (newKeyName.trim()) {
            createMutation.mutate(newKeyName);
        }
    };
    const copyToClipboard = () => {
        if (createdKey) {
            navigator.clipboard.writeText(createdKey);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-8 flex justify-center">
            <div className="w-full max-w-4xl">
                <Link href="/dashboard" className="flex items-center text-sm text-slate-400 hover:text-white mb-6 transition group">
                    <ArrowLeft size={16} className="mr-2 group-hover:-translate-x-1 transition" />
                    Back to Dashboard
                </Link>

                <h1 className="text-3xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-500">
                    API Keys
                </h1>

                {/* Create Key Section */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 mb-8">
                    <h2 className="text-xl font-semibold mb-4 text-white">Create New Key</h2>
                    <form onSubmit={handleCreate} className="flex gap-4">
                        <input
                            type="text"
                            value={newKeyName}
                            onChange={(e) => setNewKeyName(e.target.value)}
                            placeholder="Key Name (e.g. Production App)"
                            className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-purple-500 transition"
                        />
                        <button
                            type="submit"
                            disabled={createMutation.isPending || !newKeyName}
                            className="px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-lg transition disabled:opacity-50 flex items-center gap-2"
                        >
                            {createMutation.isPending ? <Loader2 className="animate-spin" /> : <Plus size={20} />}
                            Generate
                        </button>
                    </form>

                    {/* New Key Display */}
                    {createdKey && (
                        <div className="mt-6 p-4 bg-green-900/20 border border-green-500/30 rounded-xl">
                            <p className="text-green-400 text-sm mb-2 font-bold">Key Created Successfully! Copy it now, you won't see it again.</p>
                            <div className="flex bg-slate-950 p-3 rounded-lg border border-slate-800 justify-between items-center">
                                <code className="text-green-300 font-mono">{createdKey}</code>
                                <button
                                    onClick={copyToClipboard}
                                    className="p-2 hover:bg-slate-800 rounded-md transition text-slate-400 hover:text-white"
                                >
                                    {copied ? <Check size={18} className="text-green-400" /> : <Copy size={18} />}
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Keys List */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                    <h2 className="text-xl font-semibold mb-6 text-white">Your Keys</h2>

                    {isLoading ? (
                        <div className="space-y-4">
                            {[1, 2].map(i => <div key={i} className="h-20 bg-slate-800/50 rounded-xl animate-pulse" />)}
                        </div>
                    ) : keys?.length === 0 ? (
                        <div className="text-center py-10 text-slate-500">
                            No API keys found. Create one to get started.
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {keys?.map((key: any) => (
                                <div key={key.id} className="flex items-center justify-between p-4 bg-slate-950 rounded-xl border border-slate-800 hover:border-slate-700 transition">
                                    <div className="flex items-center gap-4">
                                        <div className="p-3 bg-slate-900 rounded-lg text-purple-400">
                                            <Key size={20} />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-white">{key.name}</h3>
                                            <p className="text-xs text-slate-500 font-mono">
                                                Prefix: sk_live_... • Created {formatDistanceToNow(new Date(key.created_at))} ago
                                            </p>
                                        </div>
                                    </div>

                                    <button
                                        onClick={() => revokeMutation.mutate(key.id)}
                                        disabled={revokeMutation.isPending}
                                        className="p-2 text-red-400 hover:bg-red-900/20 rounded-lg transition"
                                        title="Revoke Key"
                                    >
                                        <Trash2 size={20} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
