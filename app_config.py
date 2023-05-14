import toml


class AppConfig:
    __conf = None

    @staticmethod
    def config():
        if AppConfig.__conf is None:  # Read only once, lazy.
            AppConfig.__conf = toml.load("settings/config.toml")
        return AppConfig.__conf


TIMEOUT_IN_SECS: int = AppConfig.config()['timeout']
NUMBER_OF_PARALLEL: int = AppConfig.config()['number_of_parallel']
YOUTUBE_LINK: str = AppConfig.config()['youtube_video']
PERCENTAGE_TO_WATCH: float = AppConfig.config()['percentage_to_watch']

