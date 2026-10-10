#!/usr/bin/env node
import { access, mkdir, writeFile } from "node:fs/promises";
import { constants } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const flag = argv[index];
    if (!["--input", "--desktop", "--mobile", "--qa-json"].includes(flag)) {
      throw new Error(`Unknown argument: ${flag}`);
    }
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for ${flag}`);
    }
    const key = flag === "--qa-json" ? "qaJson" : flag.slice(2);
    options[key] = path.resolve(value);
    index += 1;
  }
  for (const key of ["input", "desktop", "mobile"]) {
    if (!options[key]) throw new Error(`Required option missing: --${key}`);
  }
  return options;
}

async function renderViewport(browser, inputPath, screenshotPath, viewport) {
  const page = await browser.newPage({ viewport });
  const consoleErrors = [];
  const pageErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => pageErrors.push(error.stack || error.message));

  try {
    await page.goto(pathToFileURL(inputPath).href, { waitUntil: "load" });
    const metrics = await page.evaluate(() => {
      const documentElement = document.documentElement;
      const scrollWidth = Math.max(documentElement.scrollWidth, document.body?.scrollWidth || 0);
      const clientWidth = documentElement.clientWidth || window.innerWidth;
      return { scrollWidth, clientWidth, horizontalOverflow: scrollWidth > clientWidth };
    });
    await ensureParent(screenshotPath);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    return {
      viewport,
      ...metrics,
      consoleErrors,
      pageErrors,
      screenshot: screenshotPath,
    };
  } finally {
    await page.close();
  }
}

async function ensureParent(filePath) {
  await mkdir(path.dirname(filePath), { recursive: true });
}

async function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`${error.message}\nUsage: node tools/render-preview.mjs --input FILE --desktop PNG --mobile PNG [--qa-json PATH]`);
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
    const desktop = await renderViewport(browser, options.input, options.desktop, { width: 1440, height: 1000 });
    const mobile = await renderViewport(browser, options.input, options.mobile, { width: 390, height: 844 });
    if (options.qaJson) {
      await ensureParent(options.qaJson);
      await writeFile(options.qaJson, `${JSON.stringify({ desktop, mobile }, null, 2)}\n`, "utf8");
    }
    const receiptText = options.qaJson ? `; QA receipt ${options.qaJson}` : "";
    console.log(`Rendered desktop ${options.desktop} and mobile ${options.mobile}${receiptText}`);
  } catch (error) {
    console.error(`Preview render failed: ${error.message}`);
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
  }
}

await main();
