<script lang="ts">
  import type { ChartConfiguration } from "chart.js/auto";
  import { api } from "$lib/api/client";
  import type { Analytics } from "$lib/api/types";
  import { app } from "$lib/app-state.svelte";
  import { AXIS_TICK_COLOR, TOOLTIP_STYLE } from "$lib/charts";
  import Chart from "$lib/components/Chart.svelte";
  import { PALETTE } from "$lib/format";

  let a = $state<Analytics | null>(null);

  $effect(() => {
    const id = app.investorId;
    a = null;
    api.analytics(id).then((r) => (a = r)).catch(() => {});
  });

  const sectorData = $derived(a ? a.allocation_by_sector.map((s) => ({ name: s.label, pct: s.pct })) : []);

  const sectorConfig = $derived<ChartConfiguration<"bar">>({
    type: "bar",
    data: {
      labels: sectorData.map((d) => d.name),
      datasets: [
        {
          data: sectorData.map((d) => d.pct),
          backgroundColor: sectorData.map((_, i) => PALETTE[i % PALETTE.length]),
          borderRadius: { topRight: 6, bottomRight: 6, topLeft: 0, bottomLeft: 0 },
          borderSkipped: false,
        },
      ],
    },
    options: {
      indexAxis: "y",
      maintainAspectRatio: false,
      scales: {
        x: { display: false },
        y: {
          grid: { display: false },
          border: { display: false },
          ticks: { color: AXIS_TICK_COLOR, font: { size: 12 } },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          ...TOOLTIP_STYLE,
          callbacks: { label: (ctx) => `${(ctx.parsed.x as number).toFixed(1)}%` },
        },
      },
    },
  });
</script>

{#if !a}
  <div class="loading">Computing allocation, concentration &amp; risk metrics…</div>
{:else}
  {@const rm = a.risk_metrics}
  <!-- Risk metric KPIs -->
  <div class="grid cols-4">
    <div class="card stat">
      <div class="label">Diversification</div>
      <div class="value">{rm.diversification_score.toFixed(0)}<span style="font-size: 16px">/100</span></div>
      <div class="meter" style="margin-top: 10px">
        <span style="width: {rm.diversification_score}%"></span>
      </div>
    </div>
    <div class="card stat">
      <div class="label">Concentration (HHI)</div>
      <div class="value">{rm.hhi.toFixed(0)}</div>
      <div class="delta muted">{rm.hhi_rating}</div>
    </div>
    <div class="card stat">
      <div class="label">Equity Exposure</div>
      <div class="value {rm.equity_pct >= 75 ? 'warn' : ''}">{rm.equity_pct.toFixed(0)}%</div>
      <div class="delta muted">of portfolio</div>
    </div>
    <div class="card stat">
      <div class="label">Est. Volatility</div>
      <div class="value">{rm.est_volatility.toFixed(0)}%</div>
      <div class="delta muted">annualized</div>
    </div>
  </div>

  <!-- Concentration flags -->
  {#if rm.concentration_flags.length > 0}
    <div class="section-title">Concentration Alerts</div>
    <div class="card">
      {#each rm.concentration_flags as f, i (i)}
        <div class="flag">
          <span class="warn">⚠</span> {f}
        </div>
      {/each}
    </div>
  {/if}

  <div class="grid cols-2" style="margin-top: 18px">
    <!-- Sector exposure -->
    <div class="card">
      <h3>Sector Exposure</h3>
      <div class="sub">Where your money is concentrated</div>
      <Chart config={sectorConfig as ChartConfiguration} height={280} />
    </div>

    <!-- Top holdings concentration -->
    <div class="card">
      <h3>Top Holdings</h3>
      <div class="sub">Single-holding concentration (flagged above 15%)</div>
      <div style="margin-top: 8px">
        {#each a.top_holdings as t (t.label)}
          <div class="alloc-row">
            <div class="lbl" style="width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">
              {t.label}
            </div>
            <div class="bar">
              <div class="meter">
                <span
                  style="width: {Math.min(t.pct * 3, 100)}%; {t.flag
                    ? 'background: linear-gradient(90deg,#ffb454,#ff6b6b)'
                    : ''}"
                ></span>
              </div>
            </div>
            <div class="pct {t.flag ? 'warn' : ''}">{t.pct.toFixed(1)}%</div>
          </div>
        {/each}
      </div>
    </div>
  </div>

  <!-- Insights -->
  <div class="section-title">Portfolio Insights</div>
  <div class="card">
    {#each a.insights as ins, i (i)}
      <div class="insight">
        <span class="dot">•</span> {ins}
      </div>
    {/each}
  </div>

  <!-- Broker split -->
  <div class="section-title">Allocation by Broker</div>
  <div class="card">
    {#each a.allocation_by_broker as b (b.label)}
      <div class="alloc-row">
        <div class="lbl">{b.label}</div>
        <div class="bar"><div class="meter"><span style="width: {b.pct}%"></span></div></div>
        <div class="pct">{b.pct.toFixed(1)}%</div>
      </div>
    {/each}
  </div>
{/if}
