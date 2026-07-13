<script lang="ts">
  import { page } from "$app/state";
  import { api } from "$lib/api/client";
  import { app } from "$lib/app-state.svelte";
  import "../styles.css";

  let { children } = $props();

  const NAV = [
    { to: "/", label: "Dashboard", ico: "◧", end: true },
    { to: "/analytics", label: "Analytics", ico: "◑" },
    { to: "/xray", label: "Portfolio X-Ray", ico: "◎" },
    { to: "/health", label: "Health Score", ico: "🛡" },
    { to: "/risk", label: "Risk Profile", ico: "◈" },
    { to: "/explore", label: "Alt-Assets", ico: "◆" },
    { to: "/advisor", label: "AI Advisor", ico: "✦" },
  ];

  const TITLES: Record<string, [string, string]> = {
    "/": ["Unified Dashboard", "Your entire portfolio across every broker & depository, in one view"],
    "/analytics": ["Portfolio Analytics", "Allocation, concentration, and risk intelligence"],
    "/xray": ["Portfolio X-Ray", "Look through your funds to reveal your TRUE hidden concentration"],
    "/health": ["Portfolio Health", "Your A–F health grade and investor-protection alerts"],
    "/risk": ["Risk Profile", "Assess your risk appetite to personalize suitability"],
    "/explore": ["Alt-Asset Explorer", "Discover & learn REITs, InvITs, and bonds — matched to you"],
    "/advisor": ["AI Advisor", "Ask anything about your portfolio, in plain language"],
  };

  const [title, sub] = $derived(TITLES[page.url.pathname] ?? TITLES["/"]);

  const isActive = (to: string, end?: boolean) =>
    end ? page.url.pathname === to : page.url.pathname.startsWith(to);

  $effect(() => {
    api.investors().then((r) => (app.investors = r)).catch(() => {});
    api.status().then((r) => (app.status = r)).catch(() => {});
  });
</script>

<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <span class="logo">◈</span>
      <div>
        Artha
        <small>Multi-asset super app</small>
      </div>
    </div>
    {#each NAV as n (n.to)}
      <a href={n.to} class="nav-item {isActive(n.to, n.end) ? 'active' : ''}">
        <span class="ico">{n.ico}</span>
        {n.label}
      </a>
    {/each}
    <div class="sidebar-foot">
      {#if app.status}
        Market data: {app.status.market_data}
        <br />
        AI advisor: {app.status.ai_advisor}
        <br />
      {/if}
      SEBI GFF Hackathon · PS3
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <div>
        <h1>{title}</h1>
        <p>{sub}</p>
      </div>
      <div class="investor-select">
        <span class="muted" style="font-size: 12px">Investor</span>
        <select bind:value={app.investorId}>
          {#each app.investors as i (i.id)}
            <option value={i.id}>{i.name}</option>
          {/each}
        </select>
      </div>
    </div>

    {@render children()}
  </main>
</div>
