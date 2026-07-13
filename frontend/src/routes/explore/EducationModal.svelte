<script lang="ts">
  import type { AltAsset } from "$lib/api/types";
  import { compactInr, suitClass } from "$lib/format";
  import QuizSection from "./QuizSection.svelte";

  let { asset, onClose }: { asset: AltAsset; onClose: () => void } = $props();
</script>

<div
  role="presentation"
  onclick={onClose}
  style="position: fixed; inset: 0; background: rgba(4,8,20,0.7); display: grid; place-items: center; padding: 20px; z-index: 50"
>
  <div
    class="card"
    role="dialog"
    tabindex="-1"
    onclick={(e) => e.stopPropagation()}
    onkeydown={() => {}}
    style="max-width: 620px; width: 100%; max-height: 85vh; overflow-y: auto"
  >
    <div class="alt-head">
      <div>
        <h3 style="font-size: 20px">{asset.name}</h3>
        <div class="muted" style="font-size: 13px">{asset.category} · {asset.asset_class}</div>
      </div>
      <button class="btn ghost" onclick={onClose}>✕</button>
    </div>

    <div class="alt-meta" style="margin-top: 16px">
      {#if asset.yield_pct != null}<span>Yield <b class="up">{asset.yield_pct}%</b></span>{/if}
      <span>Risk <b>{asset.risk_level}</b></span>
      {#if asset.rating}<span>Rating <b>{asset.rating}</b></span>{/if}
      <span>Liquidity <b>{asset.liquidity}</b></span>
      {#if asset.tenure}<span>Tenure <b>{asset.tenure}</b></span>{/if}
      <span>Min <b>{compactInr(asset.min_investment)}</b></span>
    </div>

    <div class="section-title" style="margin-top: 22px">What is this?</div>
    <p style="line-height: 1.65; font-size: 14px">{asset.education}</p>

    {#if asset.highlights.length > 0}
      <div class="section-title">Highlights</div>
      {#each asset.highlights as h, i (i)}
        <div class="insight"><span class="dot">✓</span> {h}</div>
      {/each}
    {/if}

    <div class="section-title">Suitability for you</div>
    <div class="flag" style="background: var(--panel-2); border-color: var(--border)">
      <span
        class={suitClass(asset.suitability) === "suit" ? "up" : suitClass(asset.suitability) === "caution" ? "warn" : "down"}
      >
        {asset.suitability}
      </span>
      <span>— {asset.suitability_reason}</span>
    </div>

    <QuizSection assetId={asset.id} />

    <button class="btn" style="margin-top: 18px; width: 100%">
      Invest (demo) — routes to partner RTA / exchange
    </button>
  </div>
</div>
