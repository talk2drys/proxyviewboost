import asyncio
import os
import attr
from arsenic import get_session, keys, browsers, services
import logging
from typing import Tuple


class VirtualHuman:
    _url: str

    def __init__(self, youtube_url: str):
        self._url = youtube_url

    async def _skip_ad(element):
        await element.click()

    async def check_for_ad(self, session):
        script = "video_player = document.getElementsByClassName('html5-video-player')[0]; return video_player.classList.contains('ad-showing');"

        # Wait for the video player element to load
        await session.wait_for_element(5, 'video')

        # Check if the "ad-showing" class is present in the classList of movie_player
        is_ad_showing = await session.execute_script(script=script)
        return is_ad_showing

    async def get_current_timestamp(self, session) -> Tuple[int, int]:
        # Find the ytp-progress-bar element
        progress_bar = await session.wait_for_element(5, '.ytp-progress-bar')

        # Extract the desired attributes
        total_play_time = await progress_bar.get_attribute('aria-valuemax')
        current_play_time = await progress_bar.get_attribute('aria-valuenow')
        return current_play_time, total_play_time

    async def run(self, proxy: str):
        service = services.Chromedriver(log_file=os.devnull)
        args = [f"--proxy-server={proxy}"]
        kwargs = {'goog:chromeOptions': dict(args=args)}
        browser = browsers.Chrome(**kwargs)
        async with get_session(service, browser) as session:
            await asyncio.sleep(1)  # wait for video to load

            try:
                await session.get(self._url, timeout=10)
            except asyncio.TimeoutError as err:
                logging.error("Failed loading page")
                session.close()
                return

            while True:
                video_player = await session.wait_for_element(5, "#movie_player")
                video_player.click()
                await asyncio.sleep(0.5)
                # check if the video is playing
                playing = await session.execute_script(
                    "return document.getElementById('movie_player').getPlayerState() == 1")
                if not playing:
                    await video_player.send_keys(keys=keys.SPACE)

                is_ad_playing = await self.check_for_ad(session)
                if is_ad_playing:
                    await asyncio.sleep(5)
                    skip_ad_button = await session.wait_for_element(5, '.ytp-ad-skip-button')
                    await VirtualHuman._skip_ad(skip_ad_button)

                (current_playtime, total_playtime) = await self.get_current_timestamp(session)
                if current_playtime == total_playtime:
                    return
