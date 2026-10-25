import { createRequire } from "node:module";
import { mkdirSync, writeFileSync, readFileSync, existsSync } from "node:fs";
import { inside, ffmpeg } from "./lib.mjs";

// Browser automation records the real application. No application code is changed.
const require = createRequire(import.meta.url);
const { chromium } = require(
  process.env.PLAYWRIGHT_MODULE ||
    "C:/Users/gael8/AppData/Local/npm-cache/_npx/31e32ef8478fbf80/node_modules/playwright",
);
const base = process.env.APP_URL || "http://127.0.0.1:5174";
const browser = await chromium.launch({
  headless: true,
  executablePath:
    process.env.CHROME_PATH ||
    "C:/Users/gael8/AppData/Local/ms-playwright/chromium-1247/chrome-win64/chrome.exe",
});
mkdirSync(inside("public/recordings"), { recursive: true });
mkdirSync(inside(".cache/capture"), { recursive: true });
const takes = existsSync(inside(".cache/capture/report.json"))
  ? JSON.parse(readFileSync(inside(".cache/capture/report.json"), "utf8"))
  : [];
async function record(id, hash, action) {
  const only = process.argv.find((x) => x.startsWith("--only="))?.slice(7);
  if (only && id !== only) return;
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: {
      dir: inside(".cache/capture"),
      size: { width: 1920, height: 1080 },
    },
  });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(`${base}/#${hash}`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(2000);
  const started = Date.now();
  const cues = {};
  const mark = (name) => {
    cues[name] = (Date.now() - started) / 1000;
  };
  const raw = page.video();
  await action(page, mark);
  await page.screenshot({ path: inside(`.cache/capture/${id}.png`) });
  const body = await page.locator("body").innerText();
  await context.close();
  const rawPath = await raw.path();
  const target = inside(`public/recordings/${id}.mp4`);
  // CFR conversion is source preparation only; Remotion remains the film renderer.
  ffmpeg([
    "-y",
    "-i",
    rawPath,
    "-an",
    "-r",
    "30",
    "-c:v",
    "libx264",
    "-preset",
    "fast",
    "-crf",
    "18",
    "-pix_fmt",
    "yuv420p",
    "-movflags",
    "+faststart",
    target,
  ]);
  const take = {
    id,
    src: `recordings/${id}.mp4`,
    cues,
    errors,
    recordedAt: new Date().toISOString(),
    notes:
      "Real app; CFR 30fps source preparation. Media trims are verified visually after capture.",
    finalText: body.slice(0, 4000),
  };
  takes.push(take);
  writeFileSync(
    inside(".cache/capture/report.json"),
    JSON.stringify(takes, null, 2),
  );
  console.log(JSON.stringify({ id, cues, errors }));
  if (errors.length) throw Error(`${id}: browser errors`);
}
try {
  await record("demo-304", "demo", async (p, mark) => {
    await p
      .getByRole("button", { name: "Show divisions", exact: true })
      .click();
    await p.waitForTimeout(2000);
    mark("play");
    await p
      .getByRole("button", { name: "Play controlled replay", exact: true })
      .click();
    await p.waitForFunction(
      () =>
        document.querySelector('input[aria-label="Controlled replay frame"]')
          ?.value === "239",
      {},
      { timeout: 45000 },
    );
    mark("completed");
    await p.getByRole("button", { name: "View results", exact: true }).click();
    await p.waitForTimeout(8000);
    mark("end");
  });
  await record("gaussian-controls", "model", async (p, mark) => {
    await p.waitForTimeout(2000);
    mark("default");
    const sliders = p.locator("input[type=range]");
    if (await sliders.count()) {
      const slider = p.getByLabel("Gaussian shape", { exact: true });
      await slider.focus();
      await p.keyboard.press("End");
      mark("shape");
      await p.waitForTimeout(4500);
      const reset = p.getByRole("button", { name: /reset/i });
      if (await reset.count()) await reset.first().click();
    }
    await p.waitForTimeout(4500);
    mark("end");
  });
  await record("cuda-tiles", "compute", async (p, mark) => {
    await p.waitForTimeout(2500);
    mark("default");
    const tiles = p.getByRole("button", { name: /tile/i });
    if (await tiles.count()) {
      await tiles.nth(Math.min(5, (await tiles.count()) - 1)).click();
      mark("tile");
    }
    await p.waitForTimeout(6500);
    mark("end");
  });
  await record("abrupt-304", "demo", async (p, mark) => {
    await p
      .locator("summary")
      .filter({ hasText: "Experiment settings" })
      .click();
    await p
      .getByLabel("Controlled scenario", { exact: true })
      .selectOption("abrupt");
    await p
      .locator("summary")
      .filter({ hasText: "Experiment settings" })
      .click();
    await p.waitForTimeout(1000);
    await p
      .getByRole("button", { name: "Reveal run results", exact: true })
      .click();
    mark("results");
    await p.waitForTimeout(7000);
    mark("end");
  });
  await record("featured-result", "demo", async (p, mark) => {
    await p
      .getByRole("button", { name: "Reveal run results", exact: true })
      .click();
    mark("results");
    await p.waitForTimeout(7000);
    mark("end");
  });
} finally {
  await browser.close();
}
