import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { base, mainnet } from 'wagmi/chains';

export const config = getDefaultConfig({
    appName: 'On-Chain News',
    projectId: process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID || 'YOUR_PROJECT_ID',
    chains: [base, mainnet],
    ssr: true,
});
