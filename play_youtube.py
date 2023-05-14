import asyncio
import os
import attr
from arsenic import get_session, keys, browsers, services
import structlog
from typing import Tuple
import structlog

from logger import set_logger
from app_config import YOUTUBE_LINK, PERCENTAGE_TO_WATCH, CHROME_DRIVER

logger = set_logger()


class VirtualHuman:
    _url: str

    def __init__(self, youtube_url: str, proxy: str):
        self._url = youtube_url
        self.proxy = proxy

    async def _skip_ad(element):
        await element.click()

    async def check_for_ad(self, session):
        script = "video_player = document.getElementsByClassName('html5-video-player')[0]; return video_player.classList.contains('ad-showing');"

        # Wait for the video player element to load
        await session.wait_for_element(30, 'video')

        # Check if the "ad-showing" class is present in the classList of movie_player
        is_ad_showing = await session.execute_script(script=script)
        return is_ad_showing

    async def get_current_timestamp(self, session) -> Tuple[float, float]:
        script = "element = document.querySelectorAll('video.html5-main-video')[0];" \
                 "return [element.currentTime, element.duration];"
        playtime = await session.execute_script(script=script)
        return playtime[0], playtime[1]

    async def run(self):
        video_element = "const currentElement = document.getElementsByClassName('.current-element'); " \
                        "const descendantElements = currentElement.querySelectorAll('video.');"

        add_playing_script = """
        Object.defineProperty(HTMLMediaElement.prototype, 'playing', {
            get: function(){
                return !!(this.currentTime > 0 && !this.paused && !this.ended && this.readyState > 2);
            }
        });
        """

        service = services.Chromedriver(binary=CHROME_DRIVER)
        args = [f"--proxy-server={self.proxy}"]
        kwargs = {'goog:chromeOptions': dict(args=args)}
        browser = browsers.Chrome(**kwargs)
        try:
            async with get_session(service, browser) as session:
                await asyncio.sleep(1)  # wait for video to load
                try:
                    await session.get(YOUTUBE_LINK, timeout=60)
                    await session.execute_script(add_playing_script)
                except asyncio.TimeoutError as err:
                    logger.error("Failed loading page")
                    await session.close()
                    return

                pl = await self.get_current_timestamp(session)
                if pl[1] < 60:
                    allowed_play_time = pl[1]
                else:
                    allowed_play_time = float(PERCENTAGE_TO_WATCH) * pl[1]

                while True:
                    video_player = await session.wait_for_element(60, "#movie_player")
                    # await video_player.click()
                    await asyncio.sleep(0.5)
                    # check if the video is playing
                    playing = await session.execute_script(
                        "return element = document.querySelectorAll('video.html5-main-video')[0].playing;")
                    if not playing:
                        await video_player.send_keys(keys=keys.SPACE)

                    is_ad_playing = await self.check_for_ad(session)
                    if is_ad_playing:
                        await asyncio.sleep(5)
                        if await self.check_for_ad(session):
                            skip_ad_button = await session.wait_for_element(30, '.ytp-ad-skip-button')
                            await VirtualHuman._skip_ad(skip_ad_button)

                    (current_playtime, total_playtime) = await self.get_current_timestamp(session)
                    logger.info(f"current_playtime={current_playtime} total_playtime={total_playtime}")
                    if current_playtime >= allowed_play_time or current_playtime > pl[1] - 10:
                        return
        except Exception:
            logger.error("exception occurred")
