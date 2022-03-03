import requests
import numpy
import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from data import config

def last_day_of_month(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)

@dp.message_handler(state=None)
async def accumulate_activity(message: types.Message):
    workload_until_now = 0
    accumulated = dict()
    output = list()
    output.append("Часики сгенерированы.\n")
    for message_line in message.md_text.split("\n"):
        if "jira.wargaming.net" in message_line:
            message_line = message_line.replace("https://", "")
            task_id = message_line.split("]")[1].split("(")[1].split(")")[0]
            hours_spend = message_line.split("]")[1].split("(")[1].split(")")[1].strip(" — ").replace("\\","")
            if accumulated.get(task_id) is None:
                accumulated[task_id] = 0
            accumulated[task_id] = accumulated[task_id] + float(hours_spend)
    requests.post(f'https://api.telegram.org/bot{config.BOT_TOKEN}/deleteMessage', data={"chat_id": config.ADMINS[0], "message_id": message.message_id})
    for key, value in accumulated.items():
        workload_until_now += value
        output.append(f"{key} — {value}")
    hours_until_now = 8 * int(numpy.busday_count(datetime.date.today().replace(day=1), datetime.date.today())) + 8
    hours_until_end_of_month = 8 * int(numpy.busday_count(datetime.date.today().replace(day=1), last_day_of_month(datetime.date.today()))) + 8
    output.append(f"\n<b>Количество часов на текущий день</b>: {workload_until_now:g} из {hours_until_now}.")
    output.append(f"<b>Количество часов на конец месяца</b>: {workload_until_now:g} из {hours_until_end_of_month}.")
    await message.answer("\n".join(output))