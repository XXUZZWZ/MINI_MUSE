import asyncio,sys
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parent
EDGE=Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
async def main():
 server=await asyncio.create_subprocess_exec(sys.executable,'-m','http.server','8767','--bind','127.0.0.1',cwd=ROOT,stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.DEVNULL)
 await asyncio.sleep(1)
 try:
  async with async_playwright() as p:
   browser=await p.chromium.launch(headless=True,executable_path=str(EDGE))
   page=await browser.new_page(viewport={'width':1180,'height':1500},accept_downloads=True)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.goto('http://127.0.0.1:8767/editor.html',wait_until='load')
   await page.wait_for_function("document.querySelector('#voice').readyState>=2",timeout=120000)
   await page.wait_for_function("document.querySelectorAll('.cue').length>0",timeout=30000)
   print('READY',await page.locator('#status').inner_text(),flush=True)
   async with page.expect_download(timeout=600000) as dlinfo:
    await page.locator('#record').click()
   download=await dlinfo.value;target=ROOT/'MinMuse_最小邮件Agent.webm';await download.save_as(target)
   print('SAVED',target.stat().st_size,'PAGE_ERRORS',errors,flush=True)
   await browser.close()
 finally:
  server.terminate();await server.wait()
asyncio.run(main())
