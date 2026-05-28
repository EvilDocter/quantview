import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { LenisProvider } from "../components/providers/LenisProvider";
import { GlobalHeader } from "../components/ui/GlobalHeader";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "QuantView | Institutional AI Terminal",
  description: "Realtime AI-powered market analysis and predictive trading infrastructure.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#0f0f0f] text-slate-50 selection:bg-cyan-500/30 pt-16">
        <LenisProvider>
          <GlobalHeader />
          {children}
        </LenisProvider>
      </body>
    </html>
  );
}
