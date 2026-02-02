'use client';

import { useState, useEffect } from 'react';
import ProtectedPage from '@/components/ProtectedPage';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getBalance, getUsage, verifyPayment } from '@/lib/api';
import { useAccount, useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { CreditCard, Activity, Zap, TrendingUp, ArrowLeft, Loader2, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';
import { parseUnits } from 'viem';

const USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"; // Base Mainnet
// Minimal ERC20 ABI
const USDC_ABI = [
    {
        inputs: [
            { name: "to", type: "address" },
            { name: "amount", type: "uint256" }
        ],
        name: "transfer",
        outputs: [{ name: "", type: "bool" }],
        stateMutability: "nonpayable",
        type: "function"
    }
] as const;

const TREASURY_ADDRESS = "0x6baeF23eeb7c09D731095bb5531da50b96b2D9B4"; // User Treasury Wallet

export default function BillingPage() {
    return (
        <ProtectedPage>
            <BillingContent />
        </ProtectedPage>
    );
}

function BillingContent() {
    const { address } = useAccount();
    const queryClient = useQueryClient();
    const [amount, setAmount] = useState('10');

    // Wagmi Hooks
    const { data: hash, isPending: isWritePending, writeContract, error: writeError } = useWriteContract();
    const { isLoading: isConfirming, isSuccess: isConfirmed } = useWaitForTransactionReceipt({
        hash,
    });

    const { data: balanceInfo } = useQuery({
        queryKey: ['billing', 'balance', address],
        queryFn: () => getBalance(address!),
        enabled: !!address,
    });

    const { data: usageInfo } = useQuery({
        queryKey: ['billing', 'usage', address],
        queryFn: () => getUsage(address!),
        enabled: !!address,
    });

    // Handle payment verification after confirmation
    useEffect(() => {
        if (isConfirmed && hash && address) {
            console.log("Transaction confirmed, verifying with backend...");
            verifyPayment(address, hash)
                .then((res) => {
                    console.log("Verification success:", res);
                    queryClient.invalidateQueries({ queryKey: ['billing'] });
                })
                .catch((err) => console.error("Verification failed:", err));
        }
    }, [isConfirmed, hash, address, queryClient]);

    const handlePay = () => {
        try {
            writeContract({
                address: USDC_ADDRESS,
                abi: USDC_ABI,
                functionName: 'transfer',
                args: [TREASURY_ADDRESS, parseUnits(amount, 6)],
            });
        } catch (err) {
            console.error(err);
        }
    };

    const isProcessing = isWritePending || isConfirming;

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-8 flex justify-center">
            <div className="w-full max-w-4xl">
                <Link href="/dashboard" className="flex items-center text-sm text-slate-400 hover:text-white mb-6 transition group">
                    <ArrowLeft size={16} className="mr-2 group-hover:-translate-x-1 transition" />
                    Back to Dashboard
                </Link>

                <h1 className="text-3xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-500">
                    Billing & Usage
                </h1>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
                    <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                        <div className="flex items-center gap-3 mb-2 text-purple-400">
                            <Zap size={24} />
                            <h3 className="font-semibold">Credits Available</h3>
                        </div>
                        <p className="text-4xl font-bold text-white">{balanceInfo?.credits ?? '...'}</p>
                        <p className="text-sm text-slate-500 mt-1">1 request = 1 credit</p>
                    </div>

                    <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                        <div className="flex items-center gap-3 mb-2 text-pink-400">
                            <Activity size={24} />
                            <h3 className="font-semibold">Total Requests</h3>
                        </div>
                        <p className="text-4xl font-bold text-white">{usageInfo?.total_requests ?? '...'}</p>
                        <p className="text-sm text-slate-500 mt-1">All time volume</p>
                    </div>

                    <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
                        <div className="flex items-center gap-3 mb-2 text-indigo-400">
                            <TrendingUp size={24} />
                            <h3 className="font-semibold">Current Plan</h3>
                        </div>
                        <p className="text-4xl font-bold text-white uppercase">{usageInfo?.plan ?? 'Free'}</p>
                        <p className="text-sm text-slate-500 mt-1">Starter Tier</p>
                    </div>
                </div>

                {/* Buy Credits Section */}
                <div className="bg-gradient-to-br from-indigo-900/20 to-purple-900/20 border border-indigo-500/30 rounded-3xl p-8 mb-10">
                    <div className="flex flex-col md:flex-row justify-between items-start gap-8">
                        <div>
                            <h2 className="text-2xl font-bold text-white mb-2">Top Up Credits (Base)</h2>
                            <p className="text-indigo-200/80 max-w-md mb-6">
                                Purchase credits instantly using USDC on Base.
                                <br />
                                <span className="font-bold text-white">1 USDC = 100 Credits</span>
                            </p>

                            <div className="flex flex-col gap-2">
                                <label className="text-sm text-slate-400 font-bold">Amount (USDC)</label>
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    className="bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white w-32 focus:outline-none focus:border-indigo-500 transition font-mono"
                                    min="1"
                                />
                                <p className="text-sm text-indigo-300">
                                    You will receive <span className="font-bold">{(parseFloat(amount || '0') * 100).toLocaleString()}</span> credits
                                </p>
                            </div>
                        </div>

                        <div className="flex flex-col gap-4 w-full md:w-auto items-end">
                            {isConfirmed ? (
                                <div className="p-6 bg-green-500/20 border border-green-500/50 rounded-xl flex flex-col items-center gap-2">
                                    <CheckCircle2 className="text-green-400" size={32} />
                                    <p className="font-bold text-green-300">Payment Successful!</p>
                                    <p className="text-xs text-green-400/80">Credits have been added to your account.</p>
                                    <button
                                        onClick={() => window.location.reload()}
                                        className="mt-2 text-xs underline text-green-300 hover:text-white"
                                    >
                                        Dismiss
                                    </button>
                                </div>
                            ) : (
                                <div className="p-6 bg-slate-950/50 rounded-xl border border-indigo-500/30 w-full md:w-80">
                                    <div className="flex justify-between mb-4 text-sm">
                                        <span className="text-slate-400">Total:</span>
                                        <span className="font-bold text-white">{amount} USDC</span>
                                    </div>
                                    <button
                                        onClick={handlePay}
                                        disabled={isProcessing || !amount || parseFloat(amount) <= 0}
                                        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                                    >
                                        {isProcessing ? <Loader2 className="animate-spin" /> : <CreditCard size={18} />}
                                        {isWritePending ? 'Check Wallet...' : isConfirming ? 'Confirming...' : 'Pay with Wallet'}
                                    </button>
                                    {writeError && (
                                        <p className="text-red-400 text-xs mt-3 text-center">
                                            {writeError.message.includes("User rejected") ? "Transaction rejected" : "Payment failed"}
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Usage History Table Placeholder */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-lg font-bold mb-4 text-white">Recent Activity</h3>
                    <div className="text-center py-8 text-slate-500 italic">
                        Detailed usage logs will appear here.
                    </div>
                </div>
            </div>
        </div>
    );
}
