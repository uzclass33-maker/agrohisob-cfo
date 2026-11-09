/**
 * Currency & Number Formatters for Uzbekistan Sum (UZS)
 */

export function formatUZS(amount: number): string {
  if (amount === undefined || amount === null || isNaN(amount)) return "0 so'm";
  return new Intl.NumberFormat('uz-UZ', {
    maximumFractionDigits: 0
  }).format(amount) + " so'm";
}

export function formatCompactUZS(amount: number): string {
  if (amount === undefined || amount === null || isNaN(amount)) return "0";
  const abs = Math.abs(amount);
  if (abs >= 1_000_000_000) {
    return (amount / 1_000_000_000).toFixed(2) + " mlrd so'm";
  }
  if (abs >= 1_000_000) {
    return (amount / 1_000_000).toFixed(1) + " mln so'm";
  }
  if (abs >= 1_000) {
    return (amount / 1_000).toFixed(0) + " ming so'm";
  }
  return formatUZS(amount);
}

export function formatPercent(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return "0%";
  return (value > 0 ? "+" : "") + value.toFixed(1) + "%";
}
