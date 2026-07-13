<script lang="ts">
  // Thin Chart.js wrapper: instantiated in an $effect, destroyed on teardown.
  // Recreates the chart whenever the config changes (e.g. investor switch).
  import { Chart, type ChartConfiguration } from "chart.js/auto";

  let {
    config,
    height = 260,
  }: { config: ChartConfiguration; height?: number } = $props();

  let canvas: HTMLCanvasElement;

  $effect(() => {
    const chart = new Chart(canvas, config);
    return () => chart.destroy();
  });
</script>

<div style="position: relative; height: {height}px; width: 100%;">
  <canvas bind:this={canvas}></canvas>
</div>
