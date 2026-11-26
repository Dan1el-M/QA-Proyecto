const {defineConfig}=require('@playwright/test');
const path=require('node:path');
const run=process.env.QA_RUN_DIR || path.resolve(__dirname,'../reports/browser');
module.exports=defineConfig({testDir:__dirname,testMatch:'mundial.spec.cjs',workers:1,fullyParallel:false,retries:0,
  timeout:45000,expect:{timeout:7000},outputDir:path.join(run,'playwright'),
  reporter:[['list'],['html',{outputFolder:path.join(run,'playwright-html'),open:'never'}],['json',{outputFile:path.join(run,'playwright.json')}]],
  use:{baseURL:'http://127.0.0.1:3100',browserName:'chromium',headless:true,viewport:{width:1440,height:1000},
       screenshot:'only-on-failure',trace:'retain-on-failure',video:'retain-on-failure'},
  webServer:{command:'ruby qa/scripts/server.rb',cwd:path.resolve(__dirname,'../..'),url:'http://127.0.0.1:3100/up',
             reuseExistingServer:!process.env.CI,timeout:60000}
});
