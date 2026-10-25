import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";
import { root, inside } from "./lib.mjs";
const sources = [];
function read(file) {
  const bytes = readFileSync(path.resolve(root, "..", file));
  sources.push({
    path: file,
    sha256: createHash("sha256").update(bytes).digest("hex"),
  });
  return JSON.parse(bytes);
}
const manifest = read("apps/web/public/demo/controlled/budget32/manifest.json");
const evidence = read("apps/web/public/demo/controlled/budget32/evidence.json");
const run = manifest.experiments.find((x) => x.key === "304-precursor");
const score = evidence.experiments.find((x) => x.key === run.key);
if (
  run.methods.event_focus.acquired_indices.length !== 32 ||
  run.methods.fixed_0.acquired_indices.length !== 40 ||
  score.metrics.event_focus.covered_events !== 4 ||
  score.metrics.fixed_0.covered_events !== 1
)
  throw Error("Featured evidence changed; review the edit.");
const audit = read("runs/cuda-latency-audit/matrix/latency.json");
const caseIndex=audit.cases.findIndex(c=>c.label==='synthetic-G10000-B1');
const measured=audit.cases[caseIndex];
if(!measured||measured.batch!==1||JSON.stringify(measured.shape)!=='[64,64]'||JSON.stringify(measured.gaussian_counts)!=='[10000]'||measured.cpu_warm.n!==15||measured.worker_warm_full.n!==15)throw Error('Benchmark conditions changed; review the scope.');
const cpu={value:measured.cpu_warm.median_ms,path:`cases.${caseIndex}.cpu_warm.median_ms`};
const gpu={value:measured.worker_warm_full.median_ms,path:`cases.${caseIndex}.worker_warm_full.median_ms`};
if (Math.abs(cpu.value-2913.97979995)>0.01||Math.abs(gpu.value-230.11979996)>0.01)
  throw Error("Audited medians unavailable; do not invent a benchmark.");
const abrupt = evidence.experiments.find((x) => x.key === "304-abrupt");
const output = {
  sources,
  featured: {
    key: run.key,
    frames: 240,
    adaptiveImages: 32,
    fixedImages: 40,
    adaptiveCovered: 4,
    fixedCovered: 1,
    events: 4,
    eventFrames: [...score.events].sort((a, b) => a - b),
    toleranceFrames: 1,
    selection: "Selected after evaluation",
    exposureReduction: 1 - 32 / 40,
  },
  benchmark: {
    cpuMs: cpu.value,
    gpuMs: gpu.value,
    ratio: cpu.value / gpu.value,
    cpuPath: cpu.path,
    gpuPath: gpu.path,
    components: 10000,
    width: 64,
    height: 64,
    scope: "Warmed persistent full rendering call; startup excluded",
  },
  abrupt: {
    key: abrupt.key,
    adaptiveCovered: abrupt.metrics.event_focus.covered_events,
    fixedCovered: abrupt.metrics.fixed_0.covered_events,
    events: 4,
  },
};
mkdirSync(inside("src/film"), { recursive: true });
writeFileSync(
  inside("src/film/evidence.json"),
  JSON.stringify(output, null, 2) + "\n",
);
console.log(
  "Verified featured outcome, adverse outcome and measured renderer medians; evidence snapshot written.",
);
