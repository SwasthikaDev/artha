import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // SPA mode: the app is fully client-side and talks to the FastAPI
    // backend on localhost:8000 (proxied under /api in dev).
    adapter: adapter({
      fallback: "index.html",
    }),
  },
};

export default config;
