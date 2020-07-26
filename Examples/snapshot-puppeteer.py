import os
import requests
import asyncio
from pyppeteer import launch
from pyppeteer.page import Page

AGENT_URL = 'http://localhost:5338'
VERSION = 'v0.1.2'

percyIsRunning = True


# Fetches the JS that serializes the DOM
def getAgentJS():
    global percyIsRunning

    try:
        agentJS = requests.get(AGENT_URL + '/percy-agent.js')
        return agentJS.text
    except requests.exceptions.RequestException as e:
        if isDebug():
            print(e)
        if percyIsRunning == True:
            percyIsRunning = False
        print('[percy] failed to fetch percy-agent.js, disabling Percy')
        return percyIsRunning

def envInfo(capabilities=None):
    # return 'python-selenium: ' + webdriver.__version__ + '; ' + capabilities.get(
    #    'browserName') + ': ' + capabilities.get('browserVersion')
    return 'python-selenium: 1.0.0'

def isDebug():
    return os.environ.get('LOG_LEVEL') == 'debug'

async def percySnapshot(page : Page, name, **kwargs):
    global percyIsRunning

    # Exit if we have failed to connect to the percy-agent server
    if percyIsRunning == False:
        return

    agentJS = getAgentJS()

    # Exit if we fail to grab the JS that serializes the DOM
    if agentJS == False:
        return

    await page.addScriptTag({'url': AGENT_URL + '/percy-agent.js'})
    domSnapshot = await page.evaluate('var agent = new PercyAgent({ handleAgentCommunication: false }); agent.snapshot("name");')
    postData = {
        'name': name,
        'url': page.url,
        'widths': kwargs.get('widths') or [],
        'percyCSS': kwargs.get('percyCSS') or '',
        'minHeight': kwargs.get('minHeight') or '',
        'enableJavaScript': kwargs.get('enableJavaScript') or False,
        'domSnapshot': domSnapshot,
        'clientInfo': 'percy-selenium-python/',
        'environmentInfo': envInfo()
    }
    postSnapshot(postData)

def postSnapshot(postData):
    try:
        requests.post(AGENT_URL + '/percy/snapshot', json=postData)
    except requests.exceptions.RequestException as e:
        if isDebug():
            print(e)

        print('[percy] failed to POST snapshot to percy-agent:' + postData.get('name'))
        return

async def main():
    browser = await launch({'headless': False})
    page = await browser.newPage()
    await page.goto('https://example.com')
    await page.screenshot({'path': 'example.png'})

    dimensions = await page.evaluate('''() => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }''')

    await percySnapshot(page, 'hello world')
    await browser.close()


# Run:
# set PERCY_TOKEN=1d730f6004b423ea15045342e12d73683788f4e5c1ef1d1628d26f149ed34953
# npx percy exec -- python .\snapshot-puppeteer.py
asyncio.get_event_loop().run_until_complete(main())
