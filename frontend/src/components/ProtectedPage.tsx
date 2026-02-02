'use client';

import { useAccount } from 'wagmi';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useEffect, useState } from 'react';
import { ensureUser } from '@/lib/api';

export default function ProtectedPage({ children }: { children: React.ReactNode }) {
    const { isConnected, isConnecting, address } = useAccount();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    // Sync user with backend when connected
    useEffect(() => {
        if (isConnected && address) {
            ensureUser(address).catch(err => console.error("Failed to sync user:", err));
        }
    }, [isConnected, address]);

    if (!mounted) return null;

    if (isConnecting) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-slate-950 text-white">
                <div className="animate-pulse">Loading...</div>
            </div>
        );
    }

    if (!isConnected) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-white p-8">
                <h1 className="text-3xl font-bold mb-6">Access Restricted</h1>
                <p className="mb-8 text-slate-400">Please connect your wallet to access the dashboard.</p>
                <ConnectButton />
            </div>
        );
    }

    return <>{children}</>;
}
