'use client';

import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine
} from 'recharts';
import { MonthlyFinancialData } from '@/lib/types';
import { formatCompactUZS, formatUZS } from '@/lib/formatters';

interface Props {
  data: MonthlyFinancialData[];
  title?: string;
}

export default function CashFlowChart({ data, title = "12 Oylik Pul Oqimi va Kassa Qoldig'i Dinamikasi" }: Props) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !data || data.length === 0) {
    return (
      <div className="flex h-80 w-full items-center justify-center rounded-xl border border-slate-200/80 bg-slate-50 text-sm text-slate-400">
        Grafik yuklanmoqda...
      </div>
    );
  }

  const chartData = data.map((item) => ({
    name: item.month_name.slice(0, 3),
    fullName: item.month_name,
    inflows: item.total_inflows,
    outflows: item.total_outflows,
    closingBalance: item.closing_balance,
    netFlow: item.net_cash_flow,
    debtService: item.debt_service,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const p = payload[0].payload;
      return (
        <div className="min-w-[210px] space-y-1.5 rounded-lg border border-navy-700 bg-navy-950 p-3.5 text-xs shadow-xl">
          <div className="border-b border-navy-800 pb-1.5 text-sm font-semibold text-harvest-300">
            {p.fullName} oyi ko'rsatkichlari
          </div>
          <div className="flex items-center justify-between gap-6">
            <span className="text-slate-400">Yalpi tushum:</span>
            <span className="num font-semibold text-emerald-400">{formatUZS(p.inflows)}</span>
          </div>
          <div className="flex items-center justify-between gap-6">
            <span className="text-slate-400">Jami xarajat:</span>
            <span className="num font-semibold text-rose-400">{formatUZS(p.outflows)}</span>
          </div>
          <div className="flex items-center justify-between gap-6 border-t border-navy-800 pt-1.5">
            <span className="text-slate-400">Sof kassa oqimi:</span>
            <span className={`num font-semibold ${p.netFlow >= 0 ? 'text-emerald-300' : 'text-harvest-300'}`}>
              {formatUZS(p.netFlow)}
            </span>
          </div>
          <div className="flex items-center justify-between gap-6 border-t border-navy-800 pt-1.5">
            <span className="font-medium text-slate-300">Yakuniy kassa:</span>
            <span className="num font-bold text-sky-400">{formatUZS(p.closingBalance)}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  const LegendChip = ({ color, label }: { color: string; label: string }) => (
    <span className="inline-flex items-center rounded border border-slate-200 bg-white px-2 py-1 text-[11px] font-semibold text-slate-600">
      <span className="mr-1.5 h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
      {label}
    </span>
  );

  return (
    <div className="card p-5 sm:p-6">
      <div className="flex flex-col gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-base font-semibold tracking-tight text-navy-950">{title}</h3>
          <p className="mt-0.5 text-xs text-slate-500">
            Oylik tushumlar, xarajatlar va hisoblangan kassa qoldig'i (Closing Balance = Opening + Inflows - Outflows)
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-1.5">
          <LegendChip color="#2e9e6b" label="Tushum" />
          <LegendChip color="#e0566a" label="Xarajat" />
          <LegendChip color="#25304d" label="Kassa qoldig'i" />
        </div>
      </div>

      <div className="mt-4 h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eef2ee" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <YAxis
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              width={64}
              tickFormatter={(v) => formatCompactUZS(v)}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(16, 33, 26, 0.04)' }} />
            <ReferenceLine y={0} stroke="#cbd5e1" strokeDasharray="3 3" />
            <Bar
              dataKey="inflows"
              name="Tushumlar"
              fill="#2e9e6b"
              radius={[3, 3, 0, 0]}
              maxBarSize={30}
              isAnimationActive
              animationDuration={900}
              animationEasing="ease-out"
            />
            <Bar
              dataKey="outflows"
              name="Xarajatlar"
              fill="#e0566a"
              radius={[3, 3, 0, 0]}
              maxBarSize={30}
              isAnimationActive
              animationDuration={900}
              animationEasing="ease-out"
            />
            <Line
              type="monotone"
              dataKey="closingBalance"
              name="Kassa Qoldig'i"
              stroke="#25304d"
              strokeWidth={2.5}
              dot={{ r: 3.5, fill: '#25304d', strokeWidth: 0 }}
              activeDot={{ r: 5.5 }}
              isAnimationActive
              animationDuration={1200}
              animationEasing="ease-out"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
