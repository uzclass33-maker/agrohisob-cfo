import './globals.css';
import type { Metadata } from 'next';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import BackendWarmup from '@/components/BackendWarmup';

export const metadata: Metadata = {
  title: "AgroHisob CFO — O'zbekiston Agrobiznesi Uchun AI-CFO Platformasi",
  description: "Agro-klasterlar, meva-sabzavot eksportyorlari va fermerlar uchun Soliq E-faktura, 12 oylik Cash-Flow, DSCR kredit riski va VMQ-613 yer ijarasi garov baholash tizimi.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uz">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="flex min-h-screen flex-col bg-canvas text-slate-900 antialiased">
        <BackendWarmup />
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
