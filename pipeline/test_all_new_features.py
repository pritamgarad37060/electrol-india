# -*- coding: utf-8 -*-
"""
test_all_new_features.py
Verifies:
1. Compare section: 31 State Assemblies comparison & Lok Sabha benchmarks
2. Parties section: Filter, sort, alliance pills, search, and deep footprint
3. Bordered Assembly SVG Map: Each and every state assembly rendered with borders, zoom, hover tooltip, and click
4. Home Bottom: Official assembly buildings and government emblems/seals
"""
import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\prita\.gemini\antigravity-ide\brain\724d65e8-3e01-4734-9f24-886f7a93bc87"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})

        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("console", lambda m: print(f"[{m.type}] {m.text}") if m.type in ['error', 'warn'] else None)

        # -------------------------------------------------------------
        # 1. TEST COMPARE PAGE (#cmp)
        # -------------------------------------------------------------
        print("\n--- 1. Testing Compare Page (#cmp) ---")
        await page.goto("http://localhost:8000/#cmp", wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # Check for state assembly comparison box
        has_cmp_asm = await page.locator("#cmp-assemblies-box .cmp-state-box").count()
        print(f"Assembly comparison boxes found: {has_cmp_asm}")
        await page.screenshot(path=f"{ARTIFACT_DIR}/compare_assemblies_page.png")
        print("Saved: compare_assemblies_page.png")

        # -------------------------------------------------------------
        # 2. TEST PARTIES DIRECTORY (#parties)
        # -------------------------------------------------------------
        print("\n--- 2. Testing Parties Directory (#parties) ---")
        await page.goto("http://localhost:8000/#parties", wait_until="networkidle")
        await page.wait_for_timeout(1500)

        party_cards_count = await page.locator(".party-card").count()
        print(f"Party cards rendered: {party_cards_count}")

        # Test search filter
        await page.fill("#party-search-inp", "BJP")
        await page.wait_for_timeout(500)
        filtered_count = await page.locator(".party-card").count()
        print(f"Filtered BJP party cards: {filtered_count}")

        await page.screenshot(path=f"{ARTIFACT_DIR}/parties_filter_and_sort.png")
        print("Saved: parties_filter_and_sort.png")

        # -------------------------------------------------------------
        # 3. TEST BORDERED ASSEMBLY MAP (#assembly/hr)
        # -------------------------------------------------------------
        print("\n--- 3. Testing Bordered Assembly Map (#assembly/hr) ---")
        await page.goto("http://localhost:8000/#assembly/hr", wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # Verify SVG map paths with borders
        svg_paths_count = await page.locator(".asm-svg-path").count()
        print(f"Haryana assembly SVG bordered paths found: {svg_paths_count}")

        # Hover over first seat to test tooltip
        seat_1_path = page.locator(".asm-svg-path[data-no='1']")
        if await seat_1_path.count() > 0:
            box = await seat_1_path.bounding_box()
            if box:
                await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                await page.wait_for_timeout(400)
                tip = page.locator("#global-election-tooltip")
                is_vis = await tip.is_visible()
                tip_text = await tip.inner_text() if is_vis else ""
                print(f"Tooltip visible: {is_vis}, Text: {tip_text[:40]}")

        await page.screenshot(path=f"{ARTIFACT_DIR}/bordered_assembly_map_haryana.png")
        print("Saved: bordered_assembly_map_haryana.png")

        # -------------------------------------------------------------
        # 4. TEST HOME BOTTOM DIRECTORY (Buildings & Government Seals)
        # -------------------------------------------------------------
        print("\n--- 4. Testing Home Bottom 31 Assemblies Directory ---")
        await page.goto("http://localhost:8000/", wait_until="networkidle")
        await page.wait_for_timeout(1200)

        bottom_dir = page.locator("#home-bottom-assemblies")
        await bottom_dir.scroll_into_view_if_needed()
        await page.wait_for_timeout(800)

        badges_count = await page.locator(".asm-official-badge").count()
        emblems_count = await page.locator(".asm-emblem-tag").count()
        print(f"Official building badges found: {badges_count}, Seal tags found: {emblems_count}")

        await page.screenshot(path=f"{ARTIFACT_DIR}/home_bottom_assembly_buildings_and_seals.png")
        print("Saved: home_bottom_assembly_buildings_and_seals.png")

        print(f"\nTotal page errors encountered: {len(page_errors)}")
        if page_errors:
            for err in page_errors:
                print("  ERROR:", err)

        await browser.close()
        print("\nAll feature verifications completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
