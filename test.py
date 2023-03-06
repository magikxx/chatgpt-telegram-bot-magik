import openai
import telegram
import os

# Tworzenie połączenia z API OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

# Tworzenie klienta Telegram API
bot = telegram.Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])

# Funkcja odczytuje odpowiedź z pliku
def get_response_from_file(context):
    with open("responses.txt", "r") as file:
        for line in file:
            if line.startswith(context):
                return line[len(context)+1:].strip()
    return None

# Funkcja zapisuje nową odpowiedź do pliku
def save_response_to_file(context, response):
    with open("responses.txt", "a") as file:
        file.write(f"{context}: {response}\n")

# Funkcja wysyła pytanie do API OpenAI i zwraca odpowiedź
def get_response_from_openai(question, context):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"{context}\nQ: {question}\nA:",
            temperature=0.5,
            max_tokens=1024,
            n=1,
            stop=None,
            timeout=20,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(e)
        return "Przepraszam, wystąpił błąd podczas przetwarzania twojego zapytania."

# Funkcja obsługuje przychodzące wiadomości od użytkowników
def handle_message(update, context):
    try:
        message = update.message.text
        chat_id = update.effective_chat.id
        response = get_response_from_file(message)

        if response is not None:
            bot.send_message(chat_id=chat_id, text=response)
        else:
            response = get_response_from_openai(message, context)
            save_response_to_file(message, response)
            bot.send_message(chat_id=chat_id, text=response)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=chat_id, text="Przepraszam, wystąpił błąd podczas przetwarzania twojego zapytania.")

# Uruchomienie bota Telegram
updater = telegram.Updater(token=os.environ["TELEGRAM_BOT_TOKEN"], use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(telegram.MessageHandler(telegram.Filters.text & ~telegram.Filters.command, handle_message))
updater.start_polling()