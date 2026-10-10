#!/usr/bin/env node
import { access, mkdir } from "node:fs/promises";
import { constants } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const flag = argv[index];
    if (!["--input", "--desktop", "--mobile"].includes(flag)) {
      throw new Error(`Unknown argument: ${flag}`);
    }
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for ${flag}`);
    }
    options[flag.slice(2)] = path.resolve(value);
    index += 1;
  }
  for (const key of ["input", "desktop", "mobile"]) {
    if (!options[key]) throw new Error(`Required option missing: --${key}`);
  }
  return options;
}

async function ensureParent(filePath) {
  await mkdir(path.dirname(filePath), { recursive: true });
}

async function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`${error.message}\nUsage: node tools/render-preview.mjs --input FILE --desktop PNG --mobile PNG`);
    process.exitCode = 2;
    return;
  }

  try {
    await access(options.input, constants.R_OK);
  } catch {
    console.error(`Input HTML is missing or unreadable: ${options.input}`);
    process.exitCode = 1;
    return;
  }

  let chromium;
  try {
    const require = createRequire(import.meta.url);
    ({ chromium } = require("playwright"));
  } catch (error) {
    console.error(`Playwright is unavailable. Run npm install in the source repository.\n${error.message}`);
    process.exitCode = 1;
    return;
  }

  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    await page.goto(pathToFileURL(options.input).href, { waitUntil: "load" });
    await ensureParent(options.desktop);
    await page.screenshot({ path: options.desktop, fullPage: true });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: options.mobile, fullPage: true });
    await page.close();
    console.log(`Rendered desktop ${options.desktop} and mobile ${options.mobile}`);
  } catch (error) {
    console.error(`Preview render failed: ${error.message}`);
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
  }
}

await main();
