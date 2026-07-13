// Shared investor context — the Svelte 5 equivalent of the React AppCtx.
import type { Investor, SystemStatus } from "$lib/api/types";

export const app = $state({
  investorId: "INV001",
  investors: [] as Investor[],
  status: null as SystemStatus | null,
  profileVersion: 0,
});

export function bumpProfile() {
  app.profileVersion += 1;
}
