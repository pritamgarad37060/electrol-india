import fs from 'node:fs/promises';

let chromiumModule;
try {
  chromiumModule = await import('playwright');
} catch (e) {
  try {
    chromiumModule = await import('file:///C:/Users/prita/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs');
  } catch (err) {
    throw new Error('Playwright not found. Please install playwright or set up environment.');
  }
}

export const { chromium } = chromiumModule;

export async function launchBrowser(options = {}) {
  const defaultOpts = { headless: true, ...options };
  if (!defaultOpts.executablePath) {
    if (process.env.CHROMIUM_PATH || process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH) {
      defaultOpts.executablePath = process.env.CHROMIUM_PATH || process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
    } else if (process.platform === 'win32') {
      const fallbackPath = 'C:/Users/prita/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe';
      const exists = await fs.access(fallbackPath).then(() => true, () => false);
      if (exists) {
        defaultOpts.executablePath = fallbackPath;
      }
    }
  }
  return await chromium.launch(defaultOpts);
}
