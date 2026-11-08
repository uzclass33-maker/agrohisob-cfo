import './globals.css';
import type { Metadata } from 'next';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

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
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 antialiased">
        <Navbar />
        <main className="flex-1">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
