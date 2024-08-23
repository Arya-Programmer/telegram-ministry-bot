import re
import json
import os
import random
from datetime import datetime, timedelta, time
import pytz
import logging
import requests
from telegram import Update, Poll, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Load questions
with open('questions.json', 'r') as file:
    questions = json.load(file)

# Get the current question number
with open("current_question.txt", "r") as current_ques_file:
    question_num = int(current_ques_file.read())

# Initialize the bot
bot_token = os.getenv("telegram_ministry_bot")
channel_id = '@ministryquestionstest'  # The channel ID for posting the polls

# Load textbooks data from JSON
def load_textbooks():
    with open('textbooks.json', 'r') as file:
        return json.load(file)

textbooks = load_textbooks()

# Constants for stages
CHOOSING_TEXTBOOK = 'CHOOSING_TEXTBOOK'
CHOOSING_CHAPTER = 'CHOOSING_CHAPTER'

CHAPTER, TEXTBOOK = range(2)

async def update_question_num_file():
    with open("current_question.txt", "w") as current_ques_file:
        current_ques_file.write(str(question_num))


def is_image_link(link):
    # A simple function to check if a link is an image link
    return re.match(r'(http(s?):)([/|.|\w|\s|-])', str(link))

async def post_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id, random_question=False):
    if random_question:
        # Select a random question for direct user interaction
        question_data = random.choice(questions)
    else:
        # Use the next question in sequence for scheduled postings
        global question_num
        question_data = questions[question_num]
        question_num += 1  # Increment for the next scheduled post

    correct_option_id = ord(question_data['Ans'].upper()) - 65  # Convert from letter to index (A=0, B=1, ...)

    choices = [question_data[f'Choice {letter}'] for letter in ['A', 'B', 'C', 'D']]
    if is_image_link(choices[0]):  # If the first choice is an image link
            # Send the image with the question as the caption
            await context.bot.send_photo(chat_id=channel_id, photo=choices[0], caption=f"For question {question_data["Ind"]}")
            choices = ['A', 'B', 'C', 'D']  # Reset options for the quiz

    try:
        await context.bot.send_poll(
            chat_id=chat_id,
            question=f"{question_data['Ind']}. {question_data['Question']}",
            options=choices,
            type=Poll.QUIZ,
            correct_option_id=correct_option_id,
            is_anonymous=True,
            explanation=f"This question is from: Ch{question_data["Chapter"]} Sec{question_data['Section']}",
            explanation_parse_mode="Markdown"
        )
        logger.info(f"Successfully posted question number {question_data['Ind']}")
        question_num += 1
        return "Worked"

    except Exception as e:
        logger.error(f"Failed to post question number {question_data['Ind']}: {e}")
        return "Error"

async def get_ministry_question(context: ContextTypes.DEFAULT_TYPE):
    ksa_time = pytz.timezone('Asia/Riyadh')
    now = datetime.now(ksa_time)
    if time(9, 0) <= now.time() <= time(23, 0):  # Check if the current time is between 9 AM and 11 PM KSA
        if await post_quiz(None, context, channel_id, random_question=False) == "Worked":
            await update_question_num_file()

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This responds directly to the user with a random quiz
    await post_quiz(update, context, update.effective_chat.id, random_question=True)


async def send_quiz_random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This responds directly to the user with a random quiz
    if update.effective_user.username == "arya_kurdo":
        await post_quiz(update, context, channel_id, random_question=True)

async def send_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This responds directly to the user with a random quiz
    if update.effective_user.username == "arya_kurdo":
        await post_quiz(update, context, channel_id, random_question=False)

async def scheduler(context: ContextTypes.DEFAULT_TYPE):
    ksa_timezone = pytz.timezone('Asia/Riyadh')
    now = datetime.now(ksa_timezone)

    # Calculate the next odd hour
    if now.hour % 2 == 0:
        next_odd_hour = now.hour + 1
    else:
        next_odd_hour = now.hour + 2

    # Adjust for hour overflow and set within operational hours
    if next_odd_hour >= 23:
        first_run_time = datetime.now(ksa_timezone).replace(day=now.day+1, hour=9, minute=0, second=0, microsecond=0)
    elif next_odd_hour < 9:
        first_run_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    else:
        first_run_time = now.replace(hour=next_odd_hour, minute=0, second=0, microsecond=0)

    # Calculate the delay until the first run in seconds
    delay_until_first_run = (first_run_time - now).total_seconds()
    
    # Ensure we're not setting a negative delay which can happen around midnight transition
    if delay_until_first_run < 0:
        first_run_time += timedelta(days=1)
        delay_until_first_run = (first_run_time - now).total_seconds()

    # Start the job to run every 2 hours starting from the next odd hour
    print(context)
    print(context.job_queue)
    context.job_queue.run_repeating(get_ministry_question, interval=7200, first=delay_until_first_run)


async def start_sending_quizzes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the scheduler."""
    await update.message.reply_text("Hey creator! The quizzes are being posted.")
    if update.effective_user.username == "arya_kurdo":
        await scheduler(context)

async def answers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Post the Answers of the Quizzes"""
    textbook_names = [[KeyboardButton(textbook["textbook"])] for textbook in textbooks]
    reply_keyboard = ReplyKeyboardMarkup(textbook_names, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Choose which textbook do you need answers to:",
        reply_markup=reply_keyboard
    )
    return TEXTBOOK

async def choose_textbook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the textbook choice and asks for the chapter selection."""
    selected_textbook = update.message.text
    context.user_data["selected_textbook"] = selected_textbook
    logger.info("Choosing textbook")
    logger.info(context.user_data)
    logger.info(selected_textbook)
    
    textbook = next((tb for tb in textbooks if tb["textbook"] == selected_textbook), None)
    if textbook:
        chapter_names = [[chapter] for chapter in textbook["choices"]]
        reply_keyboard = ReplyKeyboardMarkup(chapter_names, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            f'You have selected {selected_textbook}. Now choose a chapter:', reply_markup=reply_keyboard
        )
        logger.info("We got here")
        return CHAPTER

    else:
        await update.message.reply_text("Textbook not found. Please choose again.")
        return TEXTBOOK

async def choose_chapter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the image corresponding to the selected chapter."""
    logger.info("Choose_Chapter was run")
    logger.info(context.user_data)
    selected_chapter = update.message.text

    textbook = next((tb for tb in textbooks if tb["textbook"] == context.user_data.get('selected_textbook', None)), None)

    if textbook:
        chapter_info = next((ch for ch in textbook["images"] if ch["chapter"] == selected_chapter), None)
        if chapter_info:
            logger.info(chapter_info["image"])
            # await update.message.reply_photo(photo=chapter_info["image"])
            response = requests.head(chapter_info["image"])
            if response.status_code == 200:
                await update.message.reply_photo(photo=chapter_info["image"], reply_markup=ReplyKeyboardRemove())
                return ConversationHandler.END
            else:
                await update.message.reply_text("Image not accessible. Please try another chapter.")
                return CHAPTER
        else:
            await update.message.reply_text("Chapter not found. Please choose again.")
            return CHAPTER
    else:
        await update.message.reply_text("Textbook not found.", reply_markup=ReplyKeyboardRemove())
        return TEXTBOOK

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    logger.info(context._chat_id)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def count_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Retrieve username from the update object
    username = update.effective_user.username
    name = update.effective_user.first_name
    id = update.effective_user.id
    if id:
        # Open the file in append mode and write the username
        with open("usernames.txt", "a") as file:
            file.write(f"{username}, {name}, {id}, {datetime.now()}" + "\n")
        file.close()

    # Send a greeting or start message to the user
    await update.message.reply_text("Welcome to the Quiz Bot! Type /quiz to quiz yourself.\n"
                                    "Or you can type /answers to get the Textbook answers to different textbooks")

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(bot_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", count_user))
    application.add_handler(CommandHandler("start_send", start_sending_quizzes))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("send_quiz", send_quiz_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("answers", answers_command)],
        states = {
            TEXTBOOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_textbook)],
            CHAPTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_chapter)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
