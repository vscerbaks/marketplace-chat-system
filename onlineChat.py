from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

class MessageListenerError(Exception):
    pass

class OnlineChat:
    def __init__(self):
        self.chatUrl = ""
        self.browserSession = None
        self.browserContext = None
        self.pageFrame = None
        self.chatFrame = None

    async def initializeBrowser(self):
        try:
            if self.browserSession:
                await self.browserSession.close()

            print('Starting the browser...')
            playwright = await async_playwright().start()
            
            webkitEngine = playwright.webkit
            deviceProfile = playwright.devices['Galaxy S9+ landscape']

            self.browserSession = await webkitEngine.launch(headless=True)
            self.browserContext = await self.browserSession.new_context(**deviceProfile)
            self.pageFrame = await self.browserContext.new_page()
            
            await self.pageFrame.goto(self.chatUrl)
            
            await (await self.pageFrame.query_selector('div#doyoo_panel')).click()
            self.chatFrame = self.pageFrame.frames[1]
            await self.chatFrame.wait_for_selector('div.inMsg')

            return True
        
        except Exception:

            print('Could not launch the browser!')
            return False

    async def getChatLink(self):
        return self.chatFrame.url

    async def getMessages(self):
        receivedMessagesCount = 0

        print('Starting message listener...')
        while True:
            try:
                pageHtmlContent = await self.chatFrame.content()
                
                if 'the chat is ended!' in pageHtmlContent:
                    yield False

                soup = BeautifulSoup(pageHtmlContent, "html.parser")
                
                currentMessages = [msg for msg in soup.select('div.inMsg')]
                currentMessages = [msg.select('div.msg')[0].text for msg in list(dict.fromkeys(currentMessages))]

                if receivedMessagesCount < len(currentMessages):
                    print(f'New message received! {currentMessages[-1]}')

                    receivedMessagesCount += 1
                    yield currentMessages[-1]

            except Exception:
                print('Message listener has been interupted!')
                raise MessageListenerError

    async def sendMessage(self,messageText):
        try:
            print(f'Sending {messageText}...')

            inputField = await self.chatFrame.query_selector('#inputer')
            await inputField.click()
            await self.pageFrame.keyboard.type(messageText)
            await self.pageFrame.keyboard.press('Enter')

            return True

        except Exception:
            print(f"Couldn't send message {messageText}")
            return False