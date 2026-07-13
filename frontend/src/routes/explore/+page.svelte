<script lang="ts">
  import { api } from "$lib/api/client";
  import type { AltAsset } from "$lib/api/types";
  import { app } from "$lib/app-state.svelte";
  import { compactInr, suitClass } from "$lib/format";
  import EducationModal from "./EducationModal.svelte";

  const FILTERS = ["All", "REIT", "InvIT", "Bond"];

  let assets = $state<AltAsset[]>([]);
  let filter = $state("All");
  let selected = $state<AltAsset | null>(null);
  let hasProfile = $state(true);

  $effect(() => {
    const id = app.investorId;
    void app.profileVersion;
    api.altAssets(id).then((r) => (assets = r)).catch(() => {});
    api.getRiskProfile(id).then((r) => (hasProfile = !!r)).catch(() => {});
  });

  const shown = $derived(filter === "All" ? assets : assets.filter((a) => a.asset_class === filter));
</script>

{#if !hasProfile}
  <div class="flag" style="margin-bottom: 18px">
    <span class="warn">◈</span>
    <span>
      Complete your <a href="/risk" style="color: var(--brand); font-weight: 700">Risk Profile</a>
      to see personalized suitability for each instrument.
    </span>
  </div>
{/if}

<div class="suggestions" style="margin-bottom: 18px">
  {#each FILTERS as f (f)}
    <div
      class="suggestion"
      style={filter === f ? "border-color: var(--brand); color: var(--text)" : ""}
      role="button"
      tabindex="0"
      onclick={() => (filter = f)}
      onkeydown={(e) => e.key === "Enter" && (filter = f)}
    >
      {f}
    </div>
  {/each}
</div>

<div class="grid cols-3">
  {#each shown as a (a.id)}
    <div class="card alt-card">
      <div class="alt-head">
        <div>
          <div style="font-weight: 800; font-size: 15px">{a.name}</div>
          <div class="muted" style="font-size: 12px">{a.category}</div>
        </div>
        {#if a.yield_pct != null}<div class="alt-yield">{a.yield_pct}%</div>{/if}
      </div>

      <span class="pill {suitClass(a.suitability)}" style="align-self: flex-start">
        {a.suitability === "Suitable" ? "✓" : a.suitability === "Caution" ? "!" : "✕"} {a.suitability}
      </span>

      <p class="muted" style="font-size: 13px; line-height: 1.5; margin: 0">{a.summary}</p>

      <div class="alt-meta">
        <span>Risk <b>{a.risk_level}</b></span>
        {#if a.rating}<span>Rating <b>{a.rating}</b></span>{/if}
        <span>Min <b>{compactInr(a.min_investment)}</b></span>
      </div>

      {#if a.suitability_reason}
        <div class="muted" style="font-size: 12px; font-style: italic">
          {a.suitability_reason}
        </div>
      {/if}

      <button class="btn ghost" style="margin-top: auto" onclick={() => (selected = a)}>
        Learn more
      </button>
    </div>
  {/each}
</div>

{#if selected}
  <EducationModal asset={selected} onClose={() => (selected = null)} />
{/if}
