import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import '@rainbow-me/rainbowkit/styles.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'On-Chain News API',
    description: 'Real-time crypto insights and API platform',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.className} bg-slate-950 text-white min-h-screen`}>
                <Providers>{children}</Providers>
            </body>
        </html>
    );
}
