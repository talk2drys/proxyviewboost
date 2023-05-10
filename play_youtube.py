from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import asyncio


class VirtualHuman:
    _url: str

    def __init__(self, youtube_url: str):
        self._url = youtube_url

    async def run(self, proxy: str):
        options = webdriver.ChromeOptions()
        options.add_argument('--proxy-server=' + proxy)
        driver = webdriver.Chrome(options=options)

        await asyncio.sleep(1)  # wait for video to load
        try:
            driver.get(self._url)
        except Exception:
            pass

        await asyncio.sleep(30)
        # get vide element
        video = driver.find_element(By.ID, "movie_player")

        # check if the video is playing
        playing = await driver.execute_script(
            "return document.getElementById('movie_player').getPlayerState() == 1")
        if not playing:
            video.send_keys(Keys.SPACE)

        # let video play for 30 second before closing
        await asyncio.sleep(30)
        driver.close()
