import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== НАСТРОЙКИ (ВСТАВЬ СВОИ ДАННЫЕ) ====================
API_TOKEN = '8842026112:AAEhbotiq9DOnL4Fqw3O2e6owmCKxNJBR0k'
ADMIN_ID = 579054851  # Твой ID из @userinfobot (число без кавычек)
CHANNEL_URL = 'https://t.me/+VaBFc7W3Mh1kNTRi'  # Вставьте ссылку на ваш Telegram-канал
# ========================================================================

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Состояния формы
class Form(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_username = State()
    waiting_for_question = State()

# 1. Главное меню
def get_main_menu():
    buttons = [
        [InlineKeyboardButton(text="📅 Записаться на консультацию", callback_data="type_consult")],
        [InlineKeyboardButton(text="❓ Задать вопрос", callback_data="type_question")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 2. Кнопка отмены для каждого шага
def get_cancel_keyboard():
    buttons = [
        [InlineKeyboardButton(text="❌ Отмена / В главное меню", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 3. Финальные кнопки (Ссылка на канал + В меню)
def get_final_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📢 Наш Telegram-канал", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Ответ на /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Здравствуйте! Рад видеть вас.\n\nВыберите, что вас интересует:",
        reply_markup=get_main_menu()
    )

# Обработка отмены и возврата в меню
@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "Вы вернулись в главное меню. Чем я могу вам помочь?",
        reply_markup=get_main_menu()
    )
    await callback.answer()

# Старт ветки "Записаться"
@dp.callback_query(F.data == "type_consult")
async def process_consult(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(form_type="Консультация")
    await state.set_state(Form.waiting_for_name)
    await callback.message.answer(
        "Хорошо! Давайте запишемся ✨\n\nКак к вам обращаться (ваше имя)?",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

# Старт ветки "Задать вопрос"
@dp.callback_query(F.data == "type_question")
async def process_question(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(form_type="Вопрос")
    await state.set_state(Form.waiting_for_name)
    await callback.message.answer(
        "С удовольствием отвечу на ваш вопрос! ✨\n\nКак к вам обращаться (ваше имя)?",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

# 1. Получаем имя
@dp.message(Form.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await state.set_state(Form.waiting_for_phone)
    await message.answer(
        "Очень приятно! Введите ваш номер телефона, чтобы мы могли связаться с вами:",
        reply_markup=get_cancel_keyboard()
    )

# 2. Получаем телефон
@dp.message(Form.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(user_phone=message.text)
    await state.set_state(Form.waiting_for_username)
    await message.answer(
        "Отлично! Напишите ваш *ник в Telegram* (например, @username):\n\n"
        "_(Если у вас нет ника, просто отправьте слово «нет»)_",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )

# 3. Получаем юзернейм
@dp.message(Form.waiting_for_username)
async def process_username(message: types.Message, state: FSMContext):
    await state.update_data(user_tg_username=message.text)
    user_data = await state.get_data()

    # Если "Консультация" — отправляем заявку сразу
    if user_data['form_type'] == "Консультация":
        user_name = user_data['user_name']
        phone = user_data['user_phone']
        tg_username = user_data['user_tg_username']
        sender_profile = f"@{message.from_user.username}" if message.from_user.username else "Не указан в настройках TG"

        # Уведомление тебе
        await bot.send_message(
            ADMIN_ID, 
            f"🔔 *НОВАЯ ЗАЯВКА НА КОНСУЛЬТАЦИЮ!*\n\n"
            f"👤 *Имя:* {user_name}\n"
            f"📞 *Телефон:* {phone}\n"
            f"💬 *Указанный юзернейм:* {tg_username}\n"
            f"🔗 *Профиль в TG:* {sender_profile}",
            parse_mode="Markdown"
        )
        
        await state.clear()
        
        final_text = (
            "✨ *Спасибо! Ваша заявка успешно принята.*\n\n"
            "Я свяжусь с вами в ближайшее время для уточнения деталей!\n\n"
            "🌿 *Пока вы ждёте*, приглашаю вас в мой Telegram-канал. "
            "Там я делюсь секретами ухода за собой, полезными советами и новостями студии! 👇"
        )
        await message.answer(final_text, reply_markup=get_final_keyboard(), parse_mode="Markdown")

    # Если "Вопрос" — просим ввести текст вопроса
    else:
        await state.set_state(Form.waiting_for_question)
        await message.answer(
            "Спасибо! Теперь напишите сам вопрос:",
            reply_markup=get_cancel_keyboard()
        )

# 4. Получаем текст вопроса (для ветки "Вопрос") и отправляем
@dp.message(Form.waiting_for_question)
async def process_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_name = data['user_name']
    phone = data['user_phone']
    tg_username = data['user_tg_username']
    question = message.text
    sender_profile = f"@{message.from_user.username}" if message.from_user.username else "Не указан"
    
    # Уведомление тебе
    await bot.send_message(
        ADMIN_ID, 
        f"🔔 *НОВЫЙ ВОПРОС С САЙТА!*\n\n"
        f"👤 *Имя:* {user_name}\n"
        f"📞 *Телефон:* {phone}\n"
        f"💬 *Указанный юзернейм:* {tg_username}\n"
        f"🔗 *Профиль в TG:* {sender_profile}\n"
        f"❓ *Вопрос:* {question}",
        parse_mode="Markdown"
    )
    
    await state.clear()
    
    final_text = (
        "✅ *Ваш вопрос успешно отправлен!*\n\n"
        "Я отвечу вам совсем скоро.\n\n"
        "🌿 *А пока ожидаете*, загляните в мой Telegram-канал — "
        "там много интересного и полезного о красоте и здоровье! 👇"
    )
    await message.answer(final_text, reply_markup=get_final_keyboard(), parse_mode="Markdown")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())