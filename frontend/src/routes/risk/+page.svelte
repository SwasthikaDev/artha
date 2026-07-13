<script lang="ts">
  import { goto } from "$app/navigation";
  import { api } from "$lib/api/client";
  import type { RiskProfileResult, RiskQuestion } from "$lib/api/types";
  import { app, bumpProfile } from "$lib/app-state.svelte";

  let questions = $state<RiskQuestion[]>([]);
  let answers = $state<Record<string, number>>({});
  let result = $state<RiskProfileResult | null>(null);
  let submitting = $state(false);

  $effect(() => {
    const id = app.investorId;
    api.riskQuestions().then((r) => (questions = r)).catch(() => {});
    api.getRiskProfile(id).then((r) => r && (result = r)).catch(() => {});
  });

  const allAnswered = $derived(questions.length > 0 && questions.every((q) => q.id in answers));

  const submit = async () => {
    submitting = true;
    try {
      const payload = questions.map((q) => ({ question_id: q.id, option_index: answers[q.id] }));
      result = await api.submitRiskProfile(app.investorId, payload);
      bumpProfile();
    } finally {
      submitting = false;
    }
  };

  const retake = () => {
    result = null;
    answers = {};
  };
</script>

{#if result}
  <div class="grid cols-2">
    <div class="card">
      <h3>Your Risk Profile</h3>
      <div class="sub">Based on your questionnaire responses</div>
      <div class="score-ring" style="margin-top: 10px">
        <div class="score-num">{result.score}</div>
        <div>
          <div style="font-size: 22px; font-weight: 800">{result.category}</div>
          <div class="muted" style="font-size: 13px">Recommended: {result.recommended_equity_band}</div>
        </div>
      </div>
      <div class="meter" style="margin-top: 18px">
        <span style="width: {result.score}%"></span>
      </div>
      <p style="margin-top: 16px; line-height: 1.6; font-size: 14px">{result.description}</p>
    </div>

    <div class="card">
      <h3>Suitable Asset Classes</h3>
      <div class="sub">These now personalize your Alt-Asset suitability tags</div>
      <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 12px">
        {#each result.suitable_asset_classes as c (c)}
          <span class="pill suit">{c}</span>
        {/each}
      </div>
      <div style="display: flex; gap: 10px; margin-top: 28px">
        <button class="btn" onclick={() => goto("/explore")}>
          Explore matched alt-assets →
        </button>
        <button class="btn ghost" onclick={retake}>Retake</button>
      </div>
    </div>
  </div>
{:else}
  <div class="card" style="max-width: 760px">
    <h3>Risk Profiling Questionnaire</h3>
    <div class="sub">
      Five quick questions. Your answers drive the suitability engine — every alt-asset
      gets tagged Suitable / Caution / Unsuitable for you.
    </div>

    {#each questions as q, qi (q.id)}
      <div class="q-block">
        <div class="q">{qi + 1}. {q.question}</div>
        <div class="options">
          {#each q.options as opt, oi (oi)}
            <div
              class="option {answers[q.id] === oi ? 'selected' : ''}"
              role="button"
              tabindex="0"
              onclick={() => (answers = { ...answers, [q.id]: oi })}
              onkeydown={(e) => e.key === "Enter" && (answers = { ...answers, [q.id]: oi })}
            >
              {opt.label}
            </div>
          {/each}
        </div>
      </div>
    {/each}

    <button class="btn" disabled={!allAnswered || submitting} onclick={submit}>
      {submitting ? "Scoring…" : "Get my risk profile"}
    </button>
  </div>
{/if}
