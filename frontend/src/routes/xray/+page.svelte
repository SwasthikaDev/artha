<script lang="ts">
  import type { ChartConfiguration } from "chart.js/auto";
  import { api } from "$lib/api/client";
  import type { XRay } from "$lib/api/types";
  import { app } from "$lib/app-state.svelte";
  import { AXIS_TICK_COLOR, TOOLTIP_STYLE } from "$lib/charts";
  import Chart from "$lib/components/Chart.svelte";
  import { compactInr } from "$lib/format";

  let x = $state<XRay | null>(null);

  $effect(() => {
    const id = app.investorId;
    x = null;
    api.xray(id).then((r) => (x = r)).catch(() => {});
  });

  const chartData = $derived(
    x
      ? x.exposures
          .filter((e) => e.true_pct >= 1)
          .slice(0, 8)
          .map((e) => ({
            name: e.name,
            direct: e.apparent_pct,
            hidden: +(e.true_pct - e.apparent_pct).toFixed(2),
          }))
      : []
  );

  const stackedConfig = $derived<ChartConfiguration<"bar">>({
    type: "bar",
    data: {
      labels: chartData.map((d) => d.name),
      datasets: [
        {
          label: "Direct",
          data: chartData.map((d) => d.direct),
          backgroundColor: "#5b8cff",
        },
        {
          label: "Hidden (via funds)",
          data: chartData.map((d) => d.hidden),
          backgroundColor: "#7c5cff",
          borderRadius: { topRight: 6, bottomRight: 6, topLeft: 0, bottomLeft: 0 },
          borderSkipped: false,
        },
      ],
    },
    options: {
      indexAxis: "y",
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          grid: { display: false },
          border: { display: false },
          ticks: {
            color: AXIS_TICK_COLOR,
            font: { size: 12 },
            callback: (v) => `${v}%`,
          },
        },
        y: {
          stacked: true,
          grid: { display: false },
          border: { display: false },
          ticks: { color: AXIS_TICK_COLOR, font: { size: 11 } },
        },
      },
      plugins: {
        legend: { position: "bottom", labels: { color: AXIS_TICK_COLOR, boxWidth: 14, boxHeight: 14 } },
        tooltip: {
          ...TOOLTIP_STYLE,
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${(ctx.parsed.x as number).toFixed(1)}%`,
          },
        },
      },
    },
  });
</script>

{#if !x}
  <div class="loading">Looking through your funds to their underlying holdings…</div>
{:else}
  <div class="card" style="background: linear-gradient(135deg, #1a2547, #201a45); margin-bottom: 18px">
    <div class="sub" style="text-transform: uppercase; letter-spacing: 0.05em; color: var(--brand)">
      Portfolio X-Ray · Look-Through Analysis
    </div>
    <div style="font-size: 20px; font-weight: 800; line-height: 1.4; margin-top: 6px">{x.headline}</div>
    <div class="muted" style="font-size: 13px; margin-top: 8px">
      Your mutual funds &amp; ETFs hold underlying stocks. We decompose them to reveal your
      <b style="color: var(--text)"> true </b> concentration — the risk a surface view hides.
    </div>
  </div>

  <!-- Top hidden exposures -->
  <div class="grid cols-3">
    {#each x.top_hidden.slice(0, 3) as e (e.symbol)}
      <div class="card stat">
        <div class="label">{e.name}</div>
        <div class="value">
          {e.apparent_pct.toFixed(0)}% <span class="muted" style="font-size: 16px">→</span>{" "}
          <span class={e.flag ? "warn" : "up"}>{e.true_pct.toFixed(0)}%</span>
        </div>
        <div class="delta muted">
          +{compactInr(e.hidden_value)} hidden{e.via_funds.length ? ` via ${e.via_funds[0].split(" ")[0]}…` : ""}
        </div>
      </div>
    {/each}
  </div>

  <!-- Apparent vs true stacked bar -->
  <div class="section-title">Direct vs. Look-Through Exposure</div>
  <div class="card">
    <div class="sub">Blue = held directly · Purple = hidden inside your funds. Total bar = your TRUE exposure.</div>
    <Chart config={stackedConfig as ChartConfiguration} height={340} />
  </div>

  <!-- Insights -->
  <div class="section-title">What This Reveals</div>
  <div class="card">
    {#each x.insights as ins, i (i)}
      <div class="insight">
        <span class="dot">◆</span> {ins}
      </div>
    {/each}
  </div>

  <!-- Full table -->
  <div class="section-title">Full Look-Through Breakdown</div>
  <div class="card">
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Underlying</th>
            <th>Sector</th>
            <th class="num">Direct</th>
            <th class="num">True</th>
            <th class="num">Hidden</th>
            <th>Via funds</th>
          </tr>
        </thead>
        <tbody>
          {#each x.exposures.filter((e) => e.true_pct >= 0.5) as e (e.symbol)}
            <tr>
              <td><b>{e.name}</b></td>
              <td class="muted">{e.sector}</td>
              <td class="num">{e.apparent_pct.toFixed(1)}%</td>
              <td class="num {e.flag ? 'warn' : ''}"><b>{e.true_pct.toFixed(1)}%</b></td>
              <td class="num up">{e.hidden_value > 0 ? `+${(e.true_pct - e.apparent_pct).toFixed(1)}pp` : "—"}</td>
              <td class="muted" style="font-size: 11px">{e.via_funds.join(", ") || "—"}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
{/if}
