import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import g4f  # Ensure this is the correct module for your GPT provider.

# Включите логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
API_TOKEN = 'your_token_here'  # Замените на ваш токен
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения истории разговоров
conversation_history = {}

# Функция для обрезки истории разговора
def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history

# Обработчик для команды /clear
@dp.message(Command(commands=["clear"]))  # Исправлено на "clear"
async def process_clear_command(message: types.Message):
    user_id = message.from_user.id
    conversation_history[user_id] = []  # Очищаем историю
    await message.reply("История диалога очищена.")

# Обработчик для каждого нового сообщения
@dp.message()
async def process_message(message: types.Message):
    user_id = message.from_user.id
    user_input = message.text

    # Если пользователя еще нет в истории, создаем запись
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Добавляем сообщение пользователя в историю
    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id]

    try:
        # Обработка с использованием g4f для генерации ответа
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=chat_history,
            provider=g4f.Ai4Chat,
        )
        chat_gpt_response = response
    except Exception as e:
        logging.error(f"Ошибка при запросе к GPT: {e}")
        chat_gpt_response = "Извините, произошла ошибка."

    # Добавляем ответ бота в историю
    conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})
    await message.answer(chat_gpt_response)

# Запуск бота
async def main():
    # Запуск обработки сообщений
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
