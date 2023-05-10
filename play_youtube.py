import asyncio
from arsenic import get_session, keys, browsers, services


class VirtualHuman:
    _url: str

    def __init__(self, youtube_url: str):
        self._url = youtube_url

    async def run(self, proxy: str):
        # options = webdriver.ChromeOptions()
        # options.add_argument('--proxy-server=' + proxy)
        # driver = webdriver.Chrome(options=options)

        service = services.Chromedriver()
        args = [f"--proxy-server={proxy}"]
        kwargs = {'goog:chromeOptions': dict(args=args)}
        browser = browsers.Chrome(**kwargs)
        async with get_session(service, browser) as session:
            await asyncio.sleep(1)  # wait for video to load
            await session.get(self._url, timeout=10)
            await asyncio.sleep(5)
            # get video element
            video_player = await session.wait_for_element(5, "#movie_player")
            video_player.click()
            await asyncio.sleep(0.5)
            # check if the video is playing
            playing = await session.execute_script("return document.getElementById('movie_player').getPlayerState() == 1")
            if not playing:
                await video_player.send_keys(keys=keys.SPACE)
                is_now_playing = await session.execute_script("return document.getElementById('movie_player').getPlayerState() == 1")
                print(f"Video is playing: {is_now_playing}")

            # let video play for 30 second before closing
            await asyncio.sleep(30)