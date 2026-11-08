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
  Legend,
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
      <div className="h-80 w-full flex items-center justify-center bg-slate-50 border border-slate-200 rounded-xl text-slate-400">
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
        <div className="bg-slate-900 text-white p-3 rounded-lg shadow-xl border border-slate-700 text-xs space-y-1.5 min-w-[200px]">
          <div className="font-semibold text-sm border-b border-slate-700 pb-1 text-agro-300">
            {p.fullName} oyi ko'rsatkichlari
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-400">Yalpi Tushum:</span>
            <span className="font-semibold text-emerald-400">{formatUZS(p.inflows)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-400">Jami Xarajat:</span>
            <span className="font-semibold text-rose-400">{formatUZS(p.outflows)}</span>
          </div>
          <div className="flex justify-between items-center border-t border-slate-800 pt-1">
            <span className="text-slate-400">Sof Kassa Oqimi:</span>
            <span className={`font-semibold ${p.netFlow >= 0 ? 'text-emerald-300' : 'text-amber-400'}`}>
              {formatUZS(p.netFlow)}
            </span>
          </div>
          <div className="flex justify-between items-center border-t border-slate-800 pt-1">
            <span className="text-slate-300 font-medium">Yakuniy Kassa:</span>
            <span className="font-bold text-sky-400">{formatUZS(p.closingBalance)}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 gap-2">
        <div>
          <h3 className="text-lg font-bold text-slate-900">{title}</h3>
          <p className="text-xs text-slate-500">
            Oylik tushumlar, xarajatlar va hisoblangan kassa qoldig'i (Closing Balance = Opening + Inflows - Outflows)
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="inline-flex items-center px-2 py-1 rounded bg-emerald-50 text-emerald-700 font-medium border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5"></span> Tushum
          </span>
          <span className="inline-flex items-center px-2 py-1 rounded bg-rose-50 text-rose-700 font-medium border border-rose-200">
            <span className="w-2 h-2 rounded-full bg-rose-500 mr-1.5"></span> Xarajat
          </span>
          <span className="inline-flex items-center px-2 py-1 rounded bg-sky-50 text-sky-700 font-medium border border-sky-200">
            <span className="w-2 h-2 rounded-full bg-sky-500 mr-1.5"></span> Kassa Qoldig'i
          </span>
        </div>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} />
            <YAxis
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => formatCompactUZS(v)}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
            <Bar dataKey="inflows" name="Tushumlar" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={32} />
            <Bar dataKey="outflows" name="Xarajatlar" fill="#f43f5e" radius={[4, 4, 0, 0]} maxBarSize={32} />
            <Line
              type="monotone"
              dataKey="closingBalance"
              name="Kassa Qoldig'i"
              stroke="#0284c7"
              strokeWidth={3}
              dot={{ r: 4, fill: "#0284c7" }}
              activeDot={{ r: 6 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
