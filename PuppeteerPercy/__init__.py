import asyncio
import requests
from pyppeteer.page import Page
from robot.api.deco import keyword, not_keyword

__version__ = '0.1.0'


class SnapshotPuppeteerLibrary:

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__
    ROBOT_LISTENER_API_VERSION = 3
    AGENT_URL = 'http://localhost:5338'

    loop = asyncio.get_event_loop()
    percyIsRunning = True

    @keyword
    def percy_snapshot(self, page: Page, name, **kwargs):
        self.loop.run_until_complete(self.percy_snapshot_async(page, name))

    @not_keyword
    async def percy_snapshot_async(self, page: Page, name, **kwargs):
        global percyIsRunning

        # Exit if we have failed to connect to the percy-agent server
        if percyIsRunning == False:
            return

        agent_js = self.get_agent_js()
        # Exit if we fail to grab the JS that serializes the DOM
        if agent_js == False:
            return

        await page.addScriptTag({'url': self.AGENT_URL + '/percy-agent.js'})
        domSnapshot = await page.evaluate(
            'var agent = new PercyAgent({ handleAgentCommunication: false }); agent.snapshot("name");')
        postData = {
            'name': name,
            'url': page.url,
            'widths': kwargs.get('widths') or [],
            'percyCSS': kwargs.get('percyCSS') or '',
            'minHeight': kwargs.get('minHeight') or '',
            'enableJavaScript': kwargs.get('enableJavaScript') or False,
            'domSnapshot': domSnapshot,
            'clientInfo': 'percy-selenium-python/',
            'environmentInfo': self.env_info()
        }
        self.post_snapshot(postData)

    @keyword
    def post_snapshot(self, postData):
        try:
            requests.post(self.AGENT_URL + '/percy/snapshot', json=postData)
        except requests.exceptions.RequestException as e:
            print('[percy] failed to POST snapshot to percy-agent:' + postData.get('name'))
            return

    @not_keyword
    def env_info(self, capabilities=None):
        # return 'python-selenium: ' + webdriver.__version__ + '; ' + capabilities.get(
        #    'browserName') + ': ' + capabilities.get('browserVersion')
        return 'python-selenium: 1.0.0'

    @not_keyword
    def get_agent_js(self):
        global percyIsRunning
        try:
            agentJS = requests.get(self.AGENT_URL + '/percy-agent.js')
            return agentJS.text
        except requests.exceptions.RequestException as e:
            if percyIsRunning == True:
                percyIsRunning = False
            print('[percy] failed to fetch percy-agent.js, disabling Percy')
            return percyIsRunning
