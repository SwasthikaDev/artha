<script lang="ts">
  import { api } from "$lib/api/client";
  import type { QuizQuestion } from "$lib/api/types";

  let { assetId }: { assetId: string } = $props();

  let quiz = $state<QuizQuestion | null>(null);
  let picked = $state<number | null>(null);

  $effect(() => {
    const id = assetId;
    picked = null;
    quiz = null;
    api.quiz(id).then((r) => (quiz = r)).catch(() => (quiz = null));
  });
</script>

{#if quiz}
  <div class="section-title">Quick Check — Do you understand this?</div>
  <div class="q" style="font-weight: 700; font-size: 14px; margin-bottom: 10px">{quiz.question}</div>
  <div class="options">
    {#each quiz.options as opt, i (i)}
      {@const revealed = picked !== null}
      {@const isPicked = picked === i}
      {@const bg =
        revealed && opt.correct
          ? "rgba(62,207,142,0.14)"
          : revealed && isPicked && !opt.correct
            ? "rgba(255,107,107,0.14)"
            : undefined}
      {@const border =
        revealed && opt.correct ? "var(--green)" : revealed && isPicked && !opt.correct ? "var(--red)" : undefined}
      <div
        class="option"
        style="{bg ? `background: ${bg};` : ''} {border ? `border-color: ${border};` : ''}"
        role="button"
        tabindex="0"
        onclick={() => picked === null && (picked = i)}
        onkeydown={(e) => e.key === "Enter" && picked === null && (picked = i)}
      >
        {opt.label}
        {#if revealed && opt.correct}{" ✓"}{/if}
        {#if revealed && isPicked && !opt.correct}{" ✕"}{/if}
      </div>
    {/each}
  </div>
  {#if picked !== null}
    <div class="insight" style="margin-top: 12px">
      <span class="dot">💡</span> {quiz.explanation}
    </div>
  {/if}
{/if}
