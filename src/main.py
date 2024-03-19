import pandas as pd
from telegram import Poll, Bot
import asyncio
import aioschedule as schedule
import re
import os

# load json file
with open('questions.json', 'r') as file: # This file has is in .gitignore because of confdentiality
    questions = json.load(file)

# Initialize the bot with your token
bot_token = os.getenv("telegram_minsitry_bot")
bot = Bot(token=bot_token)

channel_id = '@ministryquestions'  # The channel ID where you want to post the polls

async def is_image_link(link):
    # A simple function to check if a link is an image link
    # This is basic validation; consider enhancing it based on your actual image URLs
    return re.match(r'(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png|jpeg)', str(link))


async def post_quiz(question, choices, correct_choice):
    correct_option_id = ord(correct_choice.upper()) - 65  # Convert from letter to index (A=0, B=1, ...)

    if is_image_link(choices[0]):  # If the first choice is an image link
        # Send the image with the question as the caption
        await bot.send_photo(chat_id=channel_id, photo=choices[0], caption="")
        choices = ['A', 'B', 'C', 'D']  # Default options for the quiz

    await bot.send_poll(
        chat_id=channel_id,
        question=question,
        options=choices,
        type=Poll.QUIZ,
        correct_option_id=correct_option_id,
        is_anonymous=True,
        allows_multiple_answers=False,
    )

async def get_ministry_questions():
    for question_data in questions:
        question = question_data['Question']
        choices = [question_data[f'Choice {letter}'] for letter in ['A', 'B', 'C', 'D']]
        correct_choice_letter = question_data['Ans']
        await post_quiz(question, choices, correct_choice_letter)

async def scheduler():
    # Schedule 'get_ministry_questions' to run every hour from 9 AM to 11 PM
    for hour in range(9, 23):  # 9 AM to 11 PM
        schedule.every().day.at(f"{hour:02d}:00").do(get_ministry_questions)

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)  # Check every second for scheduled tasks

async def main():
    await scheduler()


# Run the main function in the asyncio event loop
asyncio.run(main())
