from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

event_kb = InlineKeyboardMarkup(row_width=2,
                                inline_keyboard=[
                                    [InlineKeyboardButton(text="Blast Premier 2023", callback_data="6976")],
                                    [InlineKeyboardButton(text="PGL Major Copenhagen 2024", callback_data="7148")],
                                    [InlineKeyboardButton(text="IEM Chengdu 2024", callback_data="7437")],
                                    [InlineKeyboardButton(text="ESL Pro League Season 19", callback_data="7440")],
                                    [InlineKeyboardButton(text="Blast Premier Showdown 2024", callback_data="7553")],
                                    [InlineKeyboardButton(text="BetBoom Dacha Belgrade 2024", callback_data="7755")]
                                ])

backup_kb = InlineKeyboardMarkup(row_width=1,
                                 inline_keyboard=[
                                     [InlineKeyboardButton(text="◄ Назад", callback_data="backup")]
                                 ])
