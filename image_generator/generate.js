const puppeteer = require('puppeteer');
const url = "http://data_generator/ticker"
const height = 38;
const width = 1920;
async function run () {
    console.log("Starting browser")
    const browser = await puppeteer.launch({
      bindAddress: "0.0.0.0",
      args: [
        "--headless",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--remote-debugging-port=9222",
        "--remote-debugging-address=0.0.0.0"
      ]
    });
    console.log("Opening page")
    const page = await browser.newPage();
    await page.setViewport({width: width, height: 208, deviceScaleFactor: 2});
    let tickerResponse = await page.goto(url, {
      waitUntil: "networkidle2"
    });
    if(tickerResponse.status() === 200){
      console.log("Saving ticker screenshots.");
      await page.screenshot({
        clip: {x:0, y:0, width:width, height:height/2},
        path: "/data/upper-ticker.png",
        omitBackground: true
      });
      await page.screenshot({
        clip: {x:0, y:height/2, width:width, height:height/2},
        path: "/data/lower-ticker.png",
        omitBackground: true
      });
    } else {
      console.log("Error fetching data for ticker screenshots.");
    }
    let bannerResponse = await page.goto(url + "?style=true", {
      waitUntil: "networkidle2"
    });
    if(bannerResponse.status() === 200){
      console.log("Saving banner screenshot.");
      await page.screenshot({
        clip: {x:0, y:0, width:width, height:208},
        path: "/data/banner.png"
      });
    } else {
      console.log("Error fetching data for banner screenshot.");
    }
    await page.close({});
    await browser.close();
    console.log("Waiting 300 seconds.")
}
console.log("Waiting 10 seconds.")
setTimeout(run, 10 * 1000);
setInterval(run, 300*1000);