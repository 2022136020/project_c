const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1400,900']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });

  const port = process.argv[2] || '7777';
  console.log(`접속 포트: ${port}`);

  await page.goto(`http://localhost:${port}`, { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 3000));

  // 스크린샷으로 현재 상태 확인
  await page.screenshot({ path: 'C:\\project_c\\portfolio-tracker\\presentation\\debug_login.png' });
  console.log('로그인 화면 스크린샷 저장');

  // 데모 계정으로 로그인 버튼 클릭 (1400×900 기준 y≈608)
  try {
    await page.mouse.click(686, 608);
    console.log('데모 계정 로그인 버튼 클릭');
  } catch(e) {
    console.log('클릭 실패:', e.message);
  }

  await new Promise(r => setTimeout(r, 5000));

  await page.screenshot({ path: 'C:\\project_c\\portfolio-tracker\\presentation\\debug_after_login.png' });
  console.log('로그인 후 스크린샷 저장');

  // 차트 탭 클릭 (1400×900 기준 x≈1225, y≈860)
  await page.mouse.click(1225, 860);
  console.log('차트 탭 클릭 (1225, 860)');
  await new Promise(r => setTimeout(r, 3000));

  await page.screenshot({ path: 'C:\\project_c\\portfolio-tracker\\presentation\\debug_chart_tab.png' });
  console.log('차트 탭 클릭 후 스크린샷 저장');

  // 최종 스크린샷
  const outPath = 'C:\\project_c\\portfolio-tracker\\presentation\\chart_screenshot.png';
  await page.screenshot({ path: outPath, fullPage: false });
  console.log('최종 스크린샷 저장:', outPath);

  await browser.close();
})();
