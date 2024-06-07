from dataclasses import dataclass
from typing import List
from environs import Env


@dataclass
class TgBot:
    token: str

@dataclass
class Miscellaneous:
    params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
        ),
        misc=Miscellaneous()
    )
