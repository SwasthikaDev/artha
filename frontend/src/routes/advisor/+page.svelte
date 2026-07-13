<script lang="ts">
  import { api } from "$lib/api/client";
  import { app } from "$lib/app-state.svelte";

  interface Msg {
    role: "user" | "assistant";
    content: string;
    grounded?: string[];
    source?: string;
  }

  const SUGGESTIONS: Record<string, string[]> = {
    en: [
      "Am I over-concentrated in IT?",
      "How diversified is my portfolio?",
      "How am I performing overall?",
      "Should I look at REITs or bonds?",
    ],
    hi: [
      "क्या मैं IT में ज़्यादा केंद्रित हूँ?",
      "मेरा पोर्टफोलियो कितना विविध है?",
      "मेरा प्रदर्शन कैसा है?",
      "क्या मुझे REITs या बॉन्ड देखने चाहिए?",
    ],
  };

  const LANGS = ["en", "hi"] as const;

  let messages = $state<Msg[]>([]);
  let input = $state("");
  let busy = $state(false);
  let lang = $state<"en" | "hi">("en");
  let logEl: HTMLDivElement | undefined = $state();

  $effect(() => {
    void app.investorId;
    messages = [
      {
        role: "assistant",
        content:
          lang === "hi"
            ? "नमस्ते! मैं आपका Artha सलाहकार हूँ। मैं आपके सभी खातों का समेकित पोर्टफोलियो देख सकता हूँ। एकाग्रता, विविधता, प्रदर्शन या वैकल्पिक निवेश के बारे में पूछें।"
            : "Hi! I'm your Artha advisor. I can see your consolidated portfolio across all your accounts. Ask me about concentration, diversification, performance, or alternate assets.",
      },
    ];
  });

  $effect(() => {
    void messages.length;
    void busy;
    logEl?.scrollTo({ top: logEl.scrollHeight, behavior: "smooth" });
  });

  const send = async (text: string) => {
    const q = text.trim();
    if (!q || busy) return;
    const history = messages
      .filter((m) => m.content)
      .map((m) => ({ role: m.role, content: m.content }));
    messages = [...messages, { role: "user", content: q }];
    input = "";
    busy = true;
    try {
      const res = await api.advisor(app.investorId, q, history, lang);
      messages = [
        ...messages,
        { role: "assistant", content: res.reply, grounded: res.grounded_on, source: res.source },
      ];
    } catch {
      messages = [...messages, { role: "assistant", content: "Sorry — I couldn't reach the advisor service." }];
    } finally {
      busy = false;
    }
  };
</script>

<div class="card chat">
  <div class="chat-log" bind:this={logEl}>
    {#each messages as m, i (i)}
      <div class="msg {m.role === 'user' ? 'user' : 'bot'}">
        {m.content}
        {#if m.grounded && m.grounded.length > 0}
          <div class="grounded">
            Grounded on: {m.grounded.join(", ")}
            {m.source ? ` · ${m.source === "claude" ? "Claude AI" : "rule-based"}` : ""}
          </div>
        {/if}
      </div>
    {/each}
    {#if busy}<div class="msg bot muted">Analyzing your portfolio…</div>{/if}
  </div>

  <div style="margin-top: 14px">
    <div class="suggestions" style="justify-content: space-between; align-items: center">
      <div style="display: flex; flex-wrap: wrap; gap: 8px">
        {#each SUGGESTIONS[lang] as s (s)}
          <div
            class="suggestion"
            role="button"
            tabindex="0"
            onclick={() => send(s)}
            onkeydown={(e) => e.key === "Enter" && send(s)}
          >
            {s}
          </div>
        {/each}
      </div>
      <div
        style="display: flex; gap: 4px; background: var(--panel); border: 1px solid var(--border); border-radius: 999px; padding: 3px"
      >
        {#each LANGS as l (l)}
          <div
            role="button"
            tabindex="0"
            onclick={() => (lang = l)}
            onkeydown={(e) => e.key === "Enter" && (lang = l)}
            style="padding: 5px 12px; border-radius: 999px; cursor: pointer; font-size: 12px; font-weight: 700; background: {lang === l
              ? 'linear-gradient(135deg, var(--brand), var(--brand-2))'
              : 'transparent'}; color: {lang === l ? '#fff' : 'var(--muted)'}"
          >
            {l === "en" ? "English" : "हिंदी"}
          </div>
        {/each}
      </div>
    </div>
    <div class="chat-input">
      <input
        bind:value={input}
        onkeydown={(e) => e.key === "Enter" && send(input)}
        placeholder={lang === "hi" ? "अपने पोर्टफोलियो के बारे में पूछें…" : "Ask about your portfolio…"}
      />
      <button class="btn" onclick={() => send(input)} disabled={busy}>Send</button>
    </div>
  </div>
</div>
