# Telegram Quiz Bot

This Telegram bot is designed to administer quizzes and manage educational content through Telegram. It supports scheduling quizzes, providing answers from a set of textbooks, and interactive engagement with users via custom commands.

## Features

- **Quiz Scheduling**: Automatically post quizzes to a specific channel at scheduled times.
- **Interactive Quizzes**: Users can interact directly with the bot to receive random quizzes.
- **Educational Content Management**: Users can request answers by selecting textbooks and chapters through an interactive menu.
- **Robust Logging**: Detailed logging to help track the bot's operations and user interactions.

## Prerequisites

Before you start using this bot, you need to set up a few things:

- Python 3.8 or newer.
- A Telegram Bot Token. Follow [these instructions](https://core.telegram.org/bots#3-how-do-i-create-a-bot) to create a bot and get your token.
- Install necessary Python packages:

```bash
pip install python-telegram-bot pytz requests
```

## Configuration

1. **Bot Token**: Set your bot token as an environment variable:

```bash
export telegram_ministry_bot='<YourBotToken>'
```
You can request a bot token from the grandfather bot in telegram.

2. **Questions and Textbooks**: Ensure your `questions.json` and `textbooks.json` files are set up in the same directory as your bot script, following the predefined format.

## Running the Bot

To run the bot, simply execute the Python script:

```bash
cd ./src
python main.py
```

## Commands

- `/start_send` - Initializes the quiz scheduling and posts quizzes to the designated channel.
- `/quiz` - Sends a random quiz question to the user.
- `/send_quiz` - Sends a random quiz question to the channel.
- `/answers` - Starts a conversation to let the user choose a textbook and a chapter to get answers.
- `/cancel` - Cancels any ongoing operation and resets the conversation.

## Deployment

For production environments, it's recommended to deploy the bot on a server with persistent running capabilities. [Heroku](https://www.heroku.com/) or [AWS EC2](https://aws.amazon.com/ec2/) can be suitable options.
I myself am using [pythonanywhere.com](https://www.pythonanywhere.com/) the $5 package which is more than enough for my usecase.

## Contribution

Contributions to the bot are welcome. Please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the [GNU LICENSE](https://www.gnu.org/licenses/gpl-3.0.en.html#license-text) file for details.

## Contact

For any queries or further assistance, please contact [aryakurdo@gmail.com](mailto:aryakurdo@gmail.com).

```

### Explanation of Sections

- **Features**: Describes what the bot does and its key functionalities.
- **Prerequisites**: Lists what needs to be set up or installed before using the bot.
- **Configuration**: Instructions on how to set up the bot’s environment variables and files.
- **Running the Bot**: How to start the bot script.
- **Commands**: Describes the commands that the bot responds to.
- **Deployment**: Suggestions for deployment methods.
- **Contribution**: Encourages and guides contributions.
- **License**: Specifies the licensing of the project.
- **Contact**: Provides a way to contact you for users who need help or have questions.