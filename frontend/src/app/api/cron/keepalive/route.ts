import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://agrohisob-backend.onrender.com';
  try {
    const res = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      headers: { 'User-Agent': 'AgroHisob-Vercel-Cron/1.0' },
      cache: 'no-store',
    });
    const data = await res.json().catch(() => ({}));
    return NextResponse.json({
      status: 'ok',
      backendStatus: res.status,
      timestamp: new Date().toISOString(),
      backendResponse: data,
    });
  } catch (error: any) {
    return NextResponse.json(
      { 
        status: 'error', 
        message: error?.message || 'Failed to ping backend', 
        timestamp: new Date().toISOString() 
      },
      { status: 500 }
    );
  }
}
