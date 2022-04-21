from aiogram import Bot, Dispatcher, executor, types
from databaseconnection import DatabaseConnection
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink
import logging
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import pandas as pd
from datetime import datetime
API_TOKEN = "2118754299:AAGXA1hm91ApMsBCpKiw--GHnGCAdpZ6n3c"

# logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

list_of_regions: list[str] = []
list_of_cities: list[str] = []
list_of_districts: list[str] = []
price_low: int
price_top: int
region: str
city: str
district = ""
rooms: int
apartments: list = []
headers = ["id", "title", "price", "currency", "floor", "rooms", "district", "city", "region", "date", "created",
           "url", "description", "images"]
df_apartments: pd.DataFrame
count = 0


async def in_regions(message: types.Message):
    if message.text in list_of_regions:
        return True
    else:
        return False


async def in_districts(message: types.Message):
    if message.text in list_of_districts:
        return True
    else:
        return False


async def in_cities(message: types.Message):
    if message.text in list_of_cities:
        return True
    else:
        return False


def make_room_keyboard(available_rooms):
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    button_list = [InlineKeyboardButton(text="1 комната", callback_data="1"),
                   InlineKeyboardButton(text="2 комнаты", callback_data="2"),
                   InlineKeyboardButton(text="3 комнаты", callback_data="3"),
                   InlineKeyboardButton(text="4 комнаты", callback_data="4"),
                   InlineKeyboardButton(text="5 и больше комнат", callback_data="5")]
    match len(available_rooms):
        case 1:
            markup.row(button_list[available_rooms[0] - 1])
        case 2:
            markup.row(button_list[available_rooms[0] - 1], button_list[available_rooms[1] - 1])
        case 3:
            markup.row(button_list[available_rooms[0] - 1], button_list[available_rooms[1] - 1])
            markup.row(button_list[available_rooms[2] - 1])
        case 4:
            markup.row(button_list[available_rooms[0] - 1], button_list[available_rooms[1] - 1])
            markup.row(button_list[available_rooms[2] - 1], button_list[available_rooms[3] - 1])
        case 5:
            markup.row(button_list[available_rooms[0] - 1], button_list[available_rooms[1] - 1])
            markup.row(button_list[available_rooms[2] - 1], button_list[available_rooms[3] - 1])
            markup.row(button_list[available_rooms[4] - 1])

    # markup.row(InlineKeyboardButton(text="1 комната", callback_data="1"),
    #            InlineKeyboardButton(text="2 комнаты", callback_data="2")
    #            )
    # markup.row(InlineKeyboardButton(text="3 комнаты", callback_data="3"),
    #            InlineKeyboardButton(text="4 комнаты", callback_data="4")
    #            )
    # markup.row(InlineKeyboardButton(text="5 и больше комнат", callback_data="5"))
    return markup


def make_reply_keyboard(list_of_buttons):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*list_of_buttons)
    return markup


@dp.message_handler(commands="start")
async def start(message: types.Message):
    global list_of_regions
    list_of_regions = DatabaseConnection().get_regions()
    await message.answer("Выберите, пожалуйста, регион из списка ниже",
                         reply_markup=make_reply_keyboard(list_of_regions))

@dp.message_handler(Text(equals="Следующие"))
async def get_next(message: types.Message):
    global count, apartments
    check = count
    max = count + 10
    for index, apartment in enumerate(apartments):
        if index < count:
            continue
        if count != check and count == max and len(apartments) > count:
            await message.answer(f"{hbold('Посмотреть следующие объявления')}",
                         reply_markup=make_reply_keyboard(["Следующие"]))
            break
        card = f"{hlink(apartment[1], apartment[11])}\n" \
               f"{hbold('Цена: ')} {apartment[2]} {apartment[3]}\n"
        await bot.send_photo(chat_id=message.chat.id, photo=apartment[13][0])
        await message.answer(card)
        count += 1

@dp.message_handler(in_regions)
async def get_cities(message: types.Message):
    global list_of_cities, region
    region = message.text
    list_of_cities = DatabaseConnection().get_cities(region)
    await message.answer(f"Вы выбрали {message.text}. Уточните город из списка",
                         reply_markup=make_reply_keyboard(list_of_cities))


@dp.message_handler(in_cities)
async def get_district(message: types.Message):
    global list_of_districts, city
    city = message.text
    list_of_districts = DatabaseConnection().get_districts(region, city)
    if list_of_districts[0] is not None:
        await message.answer(f"Вы выбрали {message.text}",
                             reply_markup=make_reply_keyboard(list_of_districts))
    else:
        available_rooms = DatabaseConnection().get_rooms(region, city, district)
        await message.answer(f"Выберите количество комнат", reply_markup=make_room_keyboard(available_rooms))


@dp.message_handler(in_districts)
async def get_rooms(message: types.Message):
    global district
    district = message.text
    available_rooms = DatabaseConnection().get_rooms(region, city, district)
    await message.answer(f"Выберите количество комнат", reply_markup=make_room_keyboard(available_rooms))


@dp.callback_query_handler()
async def reply_smth(call: types.CallbackQuery):
    global rooms
    rooms = int(call.data)
    price_min, price_max = DatabaseConnection().get_price(rooms, region, city, district)
    await call.message.answer(f"По вашим критериям цены находятся в диапазоне {price_min}-{price_max}. "
                              f"Укажите диапазон искомой цены, используя дефис.")


@dp.message_handler(regexp=r"[0-9]+\-[0-9]+")
async def get_price(message: types.Message):
    global price_low, price_top, apartments, df_apartments, count
    price_low = message.text.split('-')[0]
    price_top = message.text.split('-')[1]
    print(f"{region}, {city}, {district}, {price_low}, {price_top}, {rooms}")
    apartments = DatabaseConnection().get_list(region=region, city=city, district=district, price_low=price_low,
                                               price_top=price_top, rooms=rooms)
    # headers = ["id", "title", "price", "currency", "floor", "rooms", "district", "city", "region", "date", "created",
    #                "url", "description", "images"]
    #
    # df_apartments = pd.DataFrame(data=apartments, columns=headers)
    # print(df_apartments.head(10))
    for index, apartment in enumerate(apartments):
        if count > 0 and count % 10 == 0 and len(apartments) > count:
            await message.answer(f"{hbold('Посмотреть следующие объявления')}",
                         reply_markup=make_reply_keyboard(["Следующие"]))
            break
        try:
            card = f"{hlink(apartment[1], apartment[11])}\n" \
                   f"{hbold('Цена: ')} {apartment[2]} {apartment[3]}\n" \
                   f"{hbold('Опубликовано: ') } {apartment[9].strftime('%d.%m.%Y')}"
            await bot.send_photo(chat_id=message.chat.id, photo=apartment[13][0])
            await message.answer(card)
            count += 1
        except:
            print("smth happened")

    print(len(apartments))



def main():
    executor.start_polling(dp)


if __name__ == "__main__":
    main()
