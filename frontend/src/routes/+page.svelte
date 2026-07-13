<script lang="ts">
  import type { ChartConfiguration } from "chart.js/auto";
  import { api } from "$lib/api/client";
  import type { HealthScore, Nudge, Portfolio } from "$lib/api/types";
  import { app } from "$lib/app-state.svelte";
  import { TOOLTIP_STYLE } from "$lib/charts";
  import Chart from "$lib/components/Chart.svelte";
  import { assetTagClass, compactInr, inr, PALETTE, pct, upDown } from "$lib/format";

  const gradeColor = (grade: string) =>
    grade?.startsWith("A") ? "var(--green)" : grade === "B" ? "#8ad4ff" : grade === "C" ? "var(--amber)" : "var(--red)";

  let p = $state<Portfolio | null>(null);
  let health = $state<HealthScore | null>(null);
  let nudges = $state<Nudge[]>([]);

  $effect(() => {
    const id = app.investorId;
    void app.profileVersion;
    p = null;
    api.portfolio(id).then((r) => (p = r)).catch(() => {});
    api.healthScore(id).then((r) => (health = r)).catch(() => {});
    api.nudges(id).then((r) => (nudges = r)).catch(() => {});
  });

  const pieData = $derived(
    p
      ? Object.values(
          p.holdings.reduce<Record<string, { name: string; value: number }>>((acc, h) => {
            acc[h.asset_class] ??= { name: h.asset_class, value: 0 };
            acc[h.asset_class].value += h.current_value;
            return acc;
          }, {})
        )
      : []
  );

  const donutConfig = $derived<ChartConfiguration<"doughnut">>({
    type: "doughnut",
    data: {
      labels: pieData.map((d) => d.name),
      datasets: [
        {
          data: pieData.map((d) => d.value),
          backgroundColor: pieData.map((_, i) => PALETTE[i % PALETTE.length]),
          borderWidth: 0,
          spacing: 2,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      cutout: "62%",
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            boxWidth: 14,
            boxHeight: 14,
            // Per-slice labels tinted with the slice color (Recharts-style legend).
            generateLabels: (chart) =>
              (chart.data.labels ?? []).map((label, i) => ({
                text: String(label),
                fillStyle: PALETTE[i % PALETTE.length],
                strokeStyle: "transparent",
                fontColor: PALETTE[i % PALETTE.length],
                lineWidth: 0,
                hidden: !chart.getDataVisibility(i),
                index: i,
              })),
          },
        },
        tooltip: {
          ...TOOLTIP_STYLE,
          callbacks: { label: (ctx) => `${ctx.label}: ${inr(ctx.parsed)}` },
        },
      },
    },
  });
</script>

{#if !p}
  <div class="loading">Aggregating your holdings across brokers &amp; depositories…</div>
{:else}
  {@const s = p.summary}
  <!-- KPI row -->
  <div class="grid cols-4">
    <div class="card stat">
      <div class="label">Total Value</div>
      <div class="value">{inr(s.total_current_value)}</div>
      <div class="delta {upDown(s.day_change)}">
        {pct(s.day_change_pct)} today ({inr(s.day_change)})
      </div>
    </div>
    <div class="card stat">
      <div class="label">Invested</div>
      <div class="value">{inr(s.total_invested)}</div>
      <div class="delta muted">Cost basis</div>
    </div>
    <div class="card stat">
      <div class="label">Total P&amp;L</div>
      <div class="value {upDown(s.total_pnl)}">{inr(s.total_pnl)}</div>
      <div class="delta {upDown(s.total_pnl)}">{pct(s.total_pnl_pct)} overall</div>
    </div>
    <a href="/health" class="card stat" style="text-decoration: none; color: inherit">
      <div class="label">Health Score</div>
      <div class="value" style={health ? `color: ${gradeColor(health.grade)}` : ""}>
        {health ? health.grade : "…"}
        {#if health}<span class="muted" style="font-size: 15px"> · {health.score}/100</span>{/if}
      </div>
      <div class="delta muted">{s.holdings_count} holdings · {s.accounts.length} accounts →</div>
    </a>
  </div>

  <!-- Smart nudges -->
  {#if nudges.length > 0}
    <div class="section-title">Smart Nudges</div>
    <div class="grid cols-3">
      {#each nudges.slice(0, 3) as n, i (i)}
        <div class="card" style="display: flex; flex-direction: column; gap: 8px">
          <span class="chip" style="align-self: flex-start; text-transform: capitalize">{n.kind}</span>
          <b style="font-size: 14px">{n.title}</b>
          <div class="muted" style="font-size: 12px; line-height: 1.5; flex: 1">{n.detail}</div>
          {#if n.cta}
            <a
              href={n.kind === "education" ? "/risk" : "/explore"}
              style="color: var(--brand); font-size: 12px; font-weight: 700"
            >
              {n.cta} →
            </a>
          {/if}
        </div>
      {/each}
    </div>
  {/if}

  <!-- Allocation + accounts -->
  <div class="grid cols-2" style="margin-top: 18px">
    <div class="card">
      <h3>Asset Allocation</h3>
      <div class="sub">Consolidated across all your accounts</div>
      <Chart config={donutConfig as ChartConfiguration} height={260} />
    </div>

    <div class="card">
      <h3>Linked Accounts</h3>
      <div class="sub">Simulated via Account Aggregator / NSDL-CDSL consent</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Broker</th>
              <th>Depository</th>
              <th class="num">Holdings</th>
              <th class="num">Value</th>
            </tr>
          </thead>
          <tbody>
            {#each s.accounts as a (a.broker)}
              <tr>
                <td><b>{a.broker}</b></td>
                <td><span class="chip">{a.depository}</span></td>
                <td class="num">{a.holdings_count}</td>
                <td class="num">{compactInr(a.current_value)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Holdings -->
  <div class="section-title">All Holdings</div>
  <div class="card">
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Instrument</th>
            <th>Class</th>
            <th>Broker</th>
            <th class="num">Qty</th>
            <th class="num">Avg</th>
            <th class="num">LTP</th>
            <th class="num">Value</th>
            <th class="num">P&amp;L</th>
          </tr>
        </thead>
        <tbody>
          {#each p.holdings as h (`${h.broker}-${h.symbol}`)}
            <tr>
              <td>
                <b>{h.symbol}</b>
                <div class="muted" style="font-size: 11px">{h.name}</div>
              </td>
              <td><span class="tag {assetTagClass(h.asset_class)}">{h.asset_class}</span></td>
              <td>{h.broker}</td>
              <td class="num">{h.quantity}</td>
              <td class="num">{inr(h.avg_cost)}</td>
              <td class="num">{inr(h.ltp)}</td>
              <td class="num">{inr(h.current_value)}</td>
              <td class="num {upDown(h.pnl)}">
                {inr(h.pnl)}
                <div style="font-size: 11px">{pct(h.pnl_pct)}</div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
{/if}
