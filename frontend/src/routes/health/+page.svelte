<script lang="ts">
  import { api } from "$lib/api/client";
  import type { HealthScore } from "$lib/api/types";
  import { app } from "$lib/app-state.svelte";

  const gradeColor = (grade: string) =>
    grade.startsWith("A") ? "var(--green)" : grade === "B" ? "#8ad4ff" : grade === "C" ? "var(--amber)" : "var(--red)";

  const sevClass = (s: string) => (s === "high" ? "unsuit" : s === "medium" ? "caution" : "suit");

  let h = $state<HealthScore | null>(null);

  $effect(() => {
    const id = app.investorId;
    void app.profileVersion;
    h = null;
    api.healthScore(id).then((r) => (h = r)).catch(() => {});
  });
</script>

{#if !h}
  <div class="loading">Grading your portfolio health…</div>
{:else}
  <div class="grid cols-2">
    <!-- Grade hero -->
    <div class="card" style="display: flex; align-items: center; gap: 26px">
      <div
        style="width: 130px; height: 130px; border-radius: 50%; flex-shrink: 0; display: grid; place-items: center; background: conic-gradient({gradeColor(h.grade)} {h.score * 3.6}deg, var(--panel-2) 0deg)"
      >
        <div
          style="width: 104px; height: 104px; border-radius: 50%; background: var(--panel); display: grid; place-items: center; flex-direction: column"
        >
          <div style="font-size: 40px; font-weight: 800; color: {gradeColor(h.grade)}; line-height: 1">{h.grade}</div>
          <div class="muted" style="font-size: 12px">{h.score}/100</div>
        </div>
      </div>
      <div>
        <h3 style="font-size: 18px">Portfolio Health Score</h3>
        <p style="font-size: 14px; line-height: 1.6; margin-top: 8px">{h.summary}</p>
      </div>
    </div>

    <!-- Components -->
    <div class="card">
      <h3>How it's scored</h3>
      <div class="sub">Four weighted lenses</div>
      {#each h.components as c (c.label)}
        <div style="margin-bottom: 14px">
          <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px">
            <span><b>{c.label}</b> <span class="muted">· {(c.weight * 100).toFixed(0)}%</span></span>
            <span style="font-weight: 700">{c.score.toFixed(0)}</span>
          </div>
          <div class="meter"><span style="width: {c.score}%"></span></div>
          <div class="muted" style="font-size: 11px; margin-top: 4px">{c.detail}</div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Protection alerts -->
  <div class="section-title">🛡 Investor Protection Alerts</div>
  {#if h.protection_alerts.length === 0}
    <div class="card">
      <div class="insight"><span class="dot up">✓</span> No protection alerts — your portfolio looks well-guarded.</div>
    </div>
  {:else}
    <div class="grid cols-1" style="gap: 12px">
      {#each h.protection_alerts as a, i (i)}
        <div
          class="card"
          style="border-left: 4px solid {a.severity === 'high'
            ? 'var(--red)'
            : a.severity === 'medium'
              ? 'var(--amber)'
              : 'var(--brand)'}"
        >
          <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px">
            <span class="pill {sevClass(a.severity)}">{a.severity.toUpperCase()}</span>
            <b style="font-size: 15px">{a.title}</b>
          </div>
          <div style="font-size: 13px; line-height: 1.6" class="muted">{a.detail}</div>
        </div>
      {/each}
    </div>
  {/if}
{/if}
