import { redirect } from "@sveltejs/kit";

// Unknown routes fall back to the dashboard (React app: <Navigate to="/" replace />).
export function load() {
  redirect(307, "/");
}
