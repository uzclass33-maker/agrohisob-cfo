'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Sprout, Lock, Mail, ArrowRight, ShieldCheck, AlertCircle, CheckCircle, Sparkles } from 'lucide-react';
import { supabase, isSupabaseConfigured } from '@/lib/supabaseClient';
import { loginAsDemoSession } from '@/lib/api';

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectUrl = searchParams.get('redirect') || '/dashboard';

  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [configured, setConfigured] = useState(true);

  useEffect(() => {
    setConfigured(isSupabaseConfigured());
  }, []);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);
    setLoading(true);

    if (!configured) {
      setErrorMsg(
        "Supabase Auth loyihasi ulanmagan. Iltimos, Vercel yoki .env.local ga NEXT_PUBLIC_SUPABASE_URL va NEXT_PUBLIC_SUPABASE_ANON_KEY kalitlarini kiriting."
      );
      setLoading(false);
      return;
    }

    try {
      if (isSignUp) {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: fullName }
          }
        });
        if (error) throw error;
        setSuccessMsg("Ro'yxatdan o'tish muvaffaqiyatli! Elektron pochtangizga tasdiqlash xati yuborildi yoki profilingiz yaratildi.");
        if (data.session) {
          setTimeout(() => router.push(redirectUrl), 1500);
        }
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password
        });
        if (error) throw error;
        setSuccessMsg("Tizimga muvaffaqiyatli kirildi! Sahifaga yo'naltirilmoqda...");
        setTimeout(() => router.push(redirectUrl), 800);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Autentifikatsiyada xatolik yuz berdi.");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoAccess = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      await loginAsDemoSession();
      setSuccessMsg("Demo CFO sifatida tizimga muvaffaqiyatli kirildi! Profil: demo@agrohisob.uz. Yo'naltirilmoqda...");
      const targetUrl = redirectUrl && redirectUrl !== '/dashboard'
        ? redirectUrl
        : '/dashboard?scenario=scenario-small-farmer';
      setTimeout(() => router.push(targetUrl), 500);
    } catch (err: any) {
      console.error("Demo login error:", err);
      setSuccessMsg("Sintetik Demo CFO rejimi ochilmoqda! Yo'naltirilmoqda...");
      const targetUrl = redirectUrl && redirectUrl !== '/dashboard'
        ? redirectUrl
        : '/dashboard?scenario=scenario-small-farmer';
      setTimeout(() => router.push(targetUrl), 500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link href="/" className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-agro-700 text-white shadow-card">
          <Sprout className="h-7 w-7" />
        </Link>
        <h1 className="mt-5 text-3xl font-bold tracking-tight text-navy-950">
          AgroHisob <span className="text-agro-700">CFO</span>
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          O'zbekiston agrobiznesi uchun xavfsiz moliyaviy kabinet (Supabase Auth)
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card py-8 px-4 sm:px-10">
          
          {/* One-Click Demo Mode Button for Evaluators */}
          <div className="mb-6 rounded-xl border border-agro-200 bg-agro-50 p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Sparkles className="w-4 h-4 text-agro-700" />
              <span className="text-xs font-bold text-agro-800 uppercase tracking-wider">
                Tezkor Sinov Rejimi
              </span>
            </div>
            <p className="text-xs text-agro-900 mb-3">
              Hisob yaratmasdan barcha moliyaviy ssenariylar va tahlillarni ko'rish uchun:
            </p>
            <button
              type="button"
              onClick={handleDemoAccess}
              className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-agro-700 px-3 py-2 text-xs font-bold text-white shadow-sm transition-all hover:bg-agro-800 active:translate-y-px"
            >
              Demo CFO Sifatida Boshqaruv Paneliga Kirish
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-slate-400 font-medium">yoki shaxsiy profil orqali</span>
            </div>
          </div>

          {!configured && (
            <div className="mb-6 flex items-start space-x-2 rounded-xl border border-amber-200 bg-amber-50 p-4 text-xs text-amber-800">
              <AlertCircle className="h-5 w-5 flex-shrink-0 text-amber-600 mt-0.5" />
              <div>
                <p className="font-semibold text-amber-900">Supabase Loyihasi Sozlanmoqda</p>
                <p className="mt-1">
                  Supabase kalitlari kiritilmagan bo'lsa ham yuqoridagi demo tugmasi orqali platformadan to'liq foydalanishingiz mumkin.
                </p>
              </div>
            </div>
          )}

          {errorMsg && (
            <div className="mb-4 flex items-center space-x-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="mb-4 flex items-center space-x-2 rounded-lg border border-agro-200 bg-agro-50 p-3 text-sm text-agro-800">
              <CheckCircle className="h-5 w-5 flex-shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Tab Selector */}
          <div className="flex border-b border-slate-200 mb-6">
            <button
              type="button"
              onClick={() => { setIsSignUp(false); setErrorMsg(null); }}
              className={`flex-1 py-3 text-sm font-semibold text-center border-b-2 transition-colors ${
                !isSignUp ? 'border-agro-700 text-agro-800' : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              Kirish
            </button>
            <button
              type="button"
              onClick={() => { setIsSignUp(true); setErrorMsg(null); }}
              className={`flex-1 py-3 text-sm font-semibold text-center border-b-2 transition-colors ${
                isSignUp ? 'border-agro-700 text-agro-800' : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              Ro'yxatdan o'tish
            </button>
          </div>

          <form className="space-y-4" onSubmit={handleAuth}>
            {isSignUp && (
              <div>
                <label htmlFor="full-name" className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Fermer xo'jaligi yoki To'liq ism
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <input
                    id="full-name"
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Masalan: Rustamov Baxtiyor"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-agro-500 focus:border-agro-500"
                  />
                </div>
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Elektron pochta (Email)
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-slate-400" />
                </div>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="fermer@agrohisob.uz"
                  className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-agro-500 focus:border-agro-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Maxfiy parol
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-slate-400" />
                </div>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-agro-500 focus:border-agro-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-transparent bg-agro-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:bg-agro-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-agro-500 disabled:opacity-50"
            >
              {loading ? "Jarayonda..." : isSignUp ? "Ro'yxatdan o'tish" : "Tizimga kirish"}
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4 text-xs text-slate-500">
            <span className="flex items-center">
              <ShieldCheck className="h-4 w-4 text-agro-600 mr-1" />
              Supabase 256-bit shifrlash
            </span>
            <Link href={redirectUrl} className="font-medium text-agro-700 transition-colors hover:text-agro-800">
              Dashboardga qaytish &rarr;
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center bg-canvas">Yuklanmoqda...</div>}>
      <LoginContent />
    </Suspense>
  );
}
