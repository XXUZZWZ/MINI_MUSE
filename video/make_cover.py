import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
root=Path(__file__).resolve().parent
edge=Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path=str(edge))
  page=await browser.new_page(viewport={'width':720,'height':1280},device_scale_factor=1)
  await page.goto((root/'cover.html').as_uri(),wait_until='load')
  await page.wait_for_function("document.fonts.status==='loaded'")
  await page.screenshot(path=str(root/'封面_MinMuse.png'))
  await browser.close()
asyncio.run(main())
