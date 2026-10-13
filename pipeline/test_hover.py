# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\prita\Downloads\files\india-elections\india-elections\pipeline"

async def test_hover():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1440, 'height': 1080})

        # 1. Test hover on Lok Sabha Map (#map)
        print("1. Testing hover on Lok Sabha map (#map)...")
        await page.goto("http://localhost:8000/#map", wait_until="networkidle")
        await page.wait_for_selector("#mp path[data-i]", timeout=15000)
        await page.wait_for_timeout(600)

        pt_info = await page.evaluate("""() => {
            const p = document.querySelector('#mp path[data-i]');
            if (!p) return null;
            const r = p.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2, name: p.getAttribute('aria-label') };
        }""")
        print("LS Path coordinate:", pt_info)
        if pt_info:
            await page.mouse.move(pt_info["x"], pt_info["y"])
            await page.wait_for_timeout(400)
            tip_info = await page.evaluate("""() => {
                const tip = document.getElementById('global-election-tooltip');
                if (!tip) return { exists: false };
                const r = tip.getBoundingClientRect();
                return { exists: true, display: tip.style.display, left: tip.style.left, top: tip.style.top, text: tip.innerText, rect: { x: r.left, y: r.top, width: r.width, height: r.height } };
            }""")
            print("LS Tooltip State:", tip_info)

        # 2. Test hover on Haryana Assembly Seat Grid (#assembly/hr)
        print("\n2. Testing hover on Haryana seat tiles (#assembly/hr)...")
        await page.goto("http://localhost:8000/#assembly/hr", wait_until="networkidle")
        await page.wait_for_selector(".seat-tile[data-no='1']", timeout=15000)
        
        # Scroll the seat map into view
        await page.evaluate("""() => {
            const el = document.getElementById('state-seat-map-section');
            if (el) el.scrollIntoView({ block: 'start' });
        }""")
        await page.wait_for_timeout(600)

        tile_info = await page.evaluate("""() => {
            const t = document.querySelector('.seat-tile[data-no="1"]');
            if (!t) return null;
            const r = t.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        }""")
        print("Seat tile coordinate on screen:", tile_info)
        if tile_info and 0 <= tile_info["y"] <= 1080:
            await page.mouse.move(tile_info["x"], tile_info["y"])
            await page.wait_for_timeout(400)
            tip_info = await page.evaluate("""() => {
                const tip = document.getElementById('global-election-tooltip');
                if (!tip) return { exists: false };
                const r = tip.getBoundingClientRect();
                return { exists: true, display: tip.style.display, left: tip.style.left, top: tip.style.top, text: tip.innerText, rect: { x: r.left, y: r.top, width: r.width, height: r.height } };
            }""")
            print("Assembly Seat Tooltip State:", tip_info)

        # 3. Test hover on Maharashtra Map (#mhmap)
        print("\n3. Testing hover on Maharashtra map (#mhmap)...")
        await page.goto("http://localhost:8000/#mhmap", wait_until="networkidle")
        await page.wait_for_selector("#mp path[data-n]", timeout=15000)
        await page.wait_for_timeout(600)

        mh_info = await page.evaluate("""() => {
            const p = document.querySelector('#mp path[data-n]');
            if (!p) return null;
            const r = p.getBoundingClientRect();
            return { x: r.left + r.width / 2, y: r.top + r.height / 2, name: p.getAttribute('aria-label') };
        }""")
        print("MH Path coordinate:", mh_info)
        if mh_info:
            await page.mouse.move(mh_info["x"], mh_info["y"])
            await page.wait_for_timeout(400)
            tip_info = await page.evaluate("""() => {
                const tip = document.getElementById('global-election-tooltip');
                if (!tip) return { exists: false };
                const r = tip.getBoundingClientRect();
                return { exists: true, display: tip.style.display, left: tip.style.left, top: tip.style.top, text: tip.innerText, rect: { x: r.left, y: r.top, width: r.width, height: r.height } };
            }""")
            print("MH Tooltip State:", tip_info)

        await browser.close()
        print("\nAll hover checks executed successfully!")

asyncio.run(test_hover())
