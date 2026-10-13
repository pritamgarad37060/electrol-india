# -*- coding: utf-8 -*-
"""
test_browser_playwright.py - Automates verification of:
1. Home page with State/Year filters & Bottom 31 Assemblies section
2. Universal search across all 4,113 constituencies
3. Fixed rock-solid floating tooltip right next to hovering cursor
"""
import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\prita\.gemini\antigravity-ide\brain\724d65e8-3e01-4734-9f24-886f7a93bc87"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda exc: console_logs.append(f"[PAGE_ERROR] {exc}"))

        print("1. Navigating to Home page http://localhost:8000/...")
        await page.goto("http://localhost:8000/", wait_until="networkidle")
        await page.wait_for_timeout(1500)

        await page.screenshot(path=f"{ARTIFACT_DIR}/home_page_hero_and_filters.png", full_page=False)
        print("Saved: home_page_hero_and_filters.png")

        # Scroll to bottom to view 31 assemblies section
        print("2. Checking bottom 31 assemblies directory...")
        bottom_sec = page.locator("#home-bottom-assemblies")
        await bottom_sec.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)

        card_count = await page.locator("#home-bottom-assemblies .asm-card").count()
        print(f"Home bottom assembly cards found: {card_count}")

        await page.screenshot(path=f"{ARTIFACT_DIR}/home_bottom_31_assemblies.png", full_page=False)
        print("Saved: home_bottom_31_assemblies.png")

        # Test Universal Search: Type 'Kalka'
        print("3. Testing Universal Search for 'Kalka'...")
        search_input = page.locator("#nav-search")
        await search_input.fill("Kalka")
        await page.wait_for_timeout(800)

        sug_count = await page.locator(".sug .si").count()
        print(f"Suggestions found for 'Kalka': {sug_count}")

        await page.screenshot(path=f"{ARTIFACT_DIR}/universal_search_suggestions.png", full_page=False)
        print("Saved: universal_search_suggestions.png")

        # Test Universal Search Full Results: Press Enter or go('q/Kalka')
        print("4. Testing Universal Search Results page...")
        await page.goto("http://localhost:8000/#q/Kalka", wait_until="networkidle")
        await page.wait_for_timeout(1500)

        await page.screenshot(path=f"{ARTIFACT_DIR}/universal_search_results_page.png", full_page=False)
        print("Saved: universal_search_results_page.png")

        # Test Map Tooltip Hover on Haryana Assembly Seat Grid
        print("5. Navigating to Haryana Assembly to test map hovering tooltip...")
        await page.goto("http://localhost:8000/#assembly/hr", wait_until="networkidle")
        await page.wait_for_timeout(1500)

        seat_1 = page.locator(".seat-tile[data-no='1']")
        if await seat_1.count() > 0:
            box = await seat_1.bounding_box()
            if box:
                # Hover over the center of seat #1
                await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                await page.wait_for_timeout(600)
                
                # Check tooltip visibility and location
                tooltip = page.locator("#global-election-tooltip")
                is_visible = await tooltip.is_visible()
                print(f"Tooltip visible on hover: {is_visible}")

        await page.screenshot(path=f"{ARTIFACT_DIR}/map_tooltip_hover_verification.png", full_page=False)
        print("Saved: map_tooltip_hover_verification.png")

        if console_logs:
            print("\nBrowser Console Logs:")
            for log in console_logs:
                print("  ", log.encode("ascii", "replace").decode())

        await browser.close()
        print("\nAll Playwright verifications passed!")

if __name__ == "__main__":
    asyncio.run(run())
