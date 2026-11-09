/**
 * Currency & Number Formatters for Uzbekistan Sum (UZS)
 */

export function formatUZS(amount: number | string): string {
  if (amount === undefined || amount === null) return "0 so'm";
  const num = typeof amount === 'number' ? amount : parseFloat(String(amount));
  if (isNaN(num)) return "0 so'm";
  return new Intl.NumberFormat('uz-UZ', {
    maximumFractionDigits: 0
  }).format(num) + " so'm";
}

export function formatCompactUZS(amount: number | string): string {
  if (amount === undefined || amount === null) return "0 so'm";
  const num = typeof amount === 'number' ? amount : parseFloat(String(amount));
  if (isNaN(num)) return "0 so'm";
  const abs = Math.abs(num);
  if (abs >= 1_000_000_000) {
    return (num / 1_000_000_000).toFixed(2) + " mlrd so'm";
  }
  if (abs >= 1_000_000) {
    return (num / 1_000_000).toFixed(1) + " mln so'm";
  }
  if (abs >= 1_000) {
    return (num / 1_000).toFixed(0) + " ming so'm";
  }
  return formatUZS(num);
}

export function formatPercent(value: number | string): string {
  if (value === undefined || value === null) return "0%";
  const num = typeof value === 'number' ? value : parseFloat(String(value));
  if (isNaN(num)) return "0%";
  return (num > 0 ? "+" : "") + num.toFixed(1) + "%";
}
