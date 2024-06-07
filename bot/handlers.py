import logging
import os
import sys
from os.path import join, abspath
sys.path.append(abspath('..'))

import numpy as np
import pandas as pd

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from keyboards import event_kb, backup_kb

from modelling import utils
from modelling.utils import get_dataset, get_target

DATA_PATH = join(os.getcwd(), '..', 'data', 'events')
import joblib
model = joblib.load(join(abspath(".."), "modelling", "model.pkl"))


async def start(message: Message, state: FSMContext):
    await state.finish()
    reply = "Выберите один из доступных турниров для предсказания:"
    await message.answer(reply, reply_markup=event_kb)


async def choose_player(call: CallbackQuery, state: FSMContext):
    reply = "Введите id игрока, для которого нужно получить предсказание:"
    await call.message.edit_text(reply, reply_markup=backup_kb)
    await state.set_state("get_player")
    await state.update_data(event=call.data)


async def inference_player(message: Message, state: FSMContext):
    reply = "Запускаем модель..."
    await message.answer(reply)

    async with state.proxy() as data:
        try:
            player = int(message.text)
        except Exception as ex:
            reply = "Неверный id игрока!"
            await state.finish()
            await message.answer(reply, reply_markup=backup_kb)
            return

        event = data["event"]
        event_dirs = [join(DATA_PATH, event)]
        teams, players = get_dataset(event_dirs)
        teams = teams.dropna()
        players = players.dropna()
        logging.warning("PARSING COMPLETED!")

        if player not in set(players.player_id.values):
            reply = "Неверный id игрока!"
            await state.finish()
            await message.answer(reply, reply_markup=backup_kb)
            return

        date_cols = ["start_time", "end_time", "start_at", "ends_at"]
        team_drop_cols = ["event_fil", "ranking_fil",
                          "is_lan", "is_qual", "prize_pool", "duration", "event_id"]
        team_drop_cols += [f"player_id_{i + 1}" for i in range(5)]

        players = players[players.player_id == player]
        df = players.drop(date_cols, axis=1).merge(teams.drop(team_drop_cols + date_cols, axis=1),
                                                   on="team_id").drop_duplicates()
        df["target"] = get_target(df.expected_pts_target, df.wr_target)
        player_name = players.player_name.values[0]
        target_col = ["target"]
        drop_cols = ["event_id", "player_id", "team_id", "team_name", "player_name",  # meta
                     "duration", "maps_played", "kpr",  # correlated
                     "wr_target", "expected_pts_target",  # unknown values
                     "event_fil"] + target_col

        bin_cols = ["has_roster_change", "is_lan", "is_qual", "is_awp"]

        df[bin_cols] = df[bin_cols].astype(np.float64)
        df[target_col] = df[target_col].astype(np.float64)
        X_test = df.drop(drop_cols, axis=1)
        preds = model.predict(X_test)

        reply = f"{player_name} ({player}) получит {round(preds.max(), 3)} птс!"
        await message.answer(reply, reply_markup=backup_kb)
        await state.finish()
        return


async def go_back(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await start(call.message, state)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_callback_query_handler(choose_player, lambda call: call.data in ["6976", "7148", "7437", "7440", "7553", "7755"], state="*")
    dp.register_callback_query_handler(go_back, lambda call: call.data == "backup", state="*")
    dp.register_message_handler(inference_player, state="get_player")
