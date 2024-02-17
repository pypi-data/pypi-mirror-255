#!/usr/bin/env python
import os
import re
import json
from math import floor
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

from .openai_singleton import OpenAIClientSingleton
from .initialize import INIT_BOT_CONFIG, init_structure, init_bot_config, init_bot_prompt, init_bot_commands
from .conversation import Conversation
from .tokenGPT import TokenGPT
from .message_handlers import handle_greetings, handle_common_queries, handle_url_ask
from .utils import read_yaml, read_text, exact_word_match, log_error


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class TelegramBot:
    # Show all the commands available by the bot using the TelegramCommands.txt file
    async def tele_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply = ''
        with open(init_bot_commands('commands.txt'), "r", encoding="utf-8") as file:
            for line in file:
                reply += line
        await update.message.reply_text(reply)

    # Start command only runs by the 'bot_owner' specified in configuration file 
    async def tele_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uname = update.message.from_user.username
        if uname == self.telegram['owner']:
            greeting_text = f"Oh, hello {update.message.from_user.first_name}! Let me get to work!"
            await update.message.reply_text(greeting_text)
            self.started = True
            self.GPTOnline = True
        else:
            await update.message.reply_text("Sorry, but I'm off the clock at the moment.")

    # Stop command formally closes out the polling loop
    async def tele_stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uname = update.message.from_user.username
        if uname == self.telegram['owner']:
            self.GPTOnline = False
            await update.message.reply_text("Sure thing boss, cutting out!")
        else:
            await update.message.reply_text("Sorry, I can't do that for you.")

    # Let bot know to call the user by a different name other than the Telegram user name
    # noinspection RegExpRedundantEscape,PyArgumentList
    async def tele_nick_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Must follow the format of "/nick <nickname>" using regular expression
        result = re.search(r'^\/nick[ \n]+([ \S]+)', update.message.text)
        if result is not None:
            prompt = f"Please refer to me by my nickname, {result.group(1).strip()}, rather than my user name."
            await update.message.reply_text(await self.tele_handle_response(text=prompt, update=update))
        else:
            await update.message.reply_text("Please provide a valid nickname after the command like \"/nick B0b #2\".")

    # Remove the whole conversation including past session logs for peace of mind
    async def tele_forget_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uname = update.message.from_user.username
        if uname in self.conversations:
            self.conversations[uname].clear_interaction()
            del self.conversations[uname]  # Delete object as well
            await update.message.reply_text("My memories of all our conversations are wiped!")
        else:
            await update.message.reply_text(
                "My apologies, but I don't recall any conversations with you, or you"
                " already asked me to forget about you. Either way, nice to meet you!"
            )

    # Responses
    async def tele_handle_response(self, text: str, update: Update) -> str:
        # Before we handle messages, ensure a user has /started us
        # Starting ensures we get some kind of user account details for logging
        not_started_reply = "I'd love to chat, but please wait as I haven't started up yet!"
        if not self.started:
            return not_started_reply

        # For a new session, track if the user has conversed with the Telegram bot before
        # Username is consistent across restarts and different conversation instances
        uname = update.message.from_user.username
        if uname not in self.conversations:
            self.conversations[uname] = Conversation(
                uname,
                self.telegram['username'],
                self.chatgpt['prompt'],
                self.chatgpt['chat_model']
            )
            # If there are past conversations via logs, load by 50% threshold of tokens
            self.conversations[uname].get_past_interaction(
                floor(self.chatgpt['prune_threshold'] / 2)
            )

        # Add the user's message to our conversation
        self.conversations[uname].add_user_message(text)

        # Check if the user is asking about a [URL]
        url_match = re.search(r'\[http(s)?://\S+]', text)

        # Form the assistant's message based on low level easy stuff or send to GPT
        # OpenAI relies on the maximum amount of tokens a ChatGPT model can support
        reply = not_started_reply
        if handle_greetings(text):
            reply = handle_greetings(text)
        elif handle_common_queries(text):
            reply = handle_common_queries(text)
        elif url_match:
            # URL content is passed into another model to summarize (GPT-4 preferred)
            await update.message.reply_text("Sure, give me a moment to look at that URL...")
            reply = await handle_url_ask(text, self.chatgpt['url_model'])
        elif self.GPTOnline:
            # This is essentially the transition point between quick Telegram replies and GPT
            reply = self.gpt_completion(uname).choices[0].message.content

        # Calculate the total token count of our conversation messages via tiktoken
        token_count = self.conversations[uname].get_message_token_count()

        # If the user is getting closer to the bot's token threshold, warn the first time
        if token_count > self.chatgpt['prune_back_to'] and uname not in self.token_warning:
            reply += ("\n\n"
                      "By the way, our conversation will soon reach my token limit, so I may"
                      " start forgetting some of our older exchanges. Would you like me to"
                      " summarize our conversation so far to keep the main points alive?"
                      )
            self.token_warning[uname] = True

        # Add assistant's message to the user's conversation
        self.conversations[uname].add_assistant_message(reply)

        # Truncate older messages if the conversation is above the bot's token threshold
        if token_count > self.chatgpt['prune_threshold']:
            self.conversations[uname].prune_conversation(self.chatgpt['prune_back_to'])

        return reply

    # Handles the Telegram side of the message, discerning between Private and Group conversation
    async def tele_handle_message(self, update: Update, context=ContextTypes.DEFAULT_TYPE):
        message_type: str = update.message.chat.type  # PM or Group Chat
        message_text: str = update.message.text
        message_print = f"User {update.message.from_user.username} in {message_type} chat ID {update.message.chat.id}"

        # If it's a group text, only reply if the bot is named
        # The real magic of how the bot behaves is in tele_handle_response()
        if message_type == 'supergroup' or message_type == 'group':
            if exact_word_match(self.telegram['username'], message_text):
                print(message_print)
                new_text: str = message_text.replace(self.telegram['username'], '').strip()
                response: str = await self.tele_handle_response(text=new_text, update=update)
            elif (
                    exact_word_match(self.telegram['nickname'], message_text) or
                    exact_word_match(self.telegram['initials'], message_text)
            ):
                print(message_print)
                response: str = await self.tele_handle_response(text=message_text, update=update)
            else:
                return
        elif message_type == 'private':
            print(message_print)
            response: str = await self.tele_handle_response(text=message_text, update=update)
        else:
            return
        await update.message.reply_text(response)

    # Handle errors caused on the Telegram side
    async def tele_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.from_user.username is None:
            # If the user doesn't have a Telegram username, we can't really do anything
            await update.message.reply_text('Add a username to your Telegram account so that I can talk to you!')
        else:
            log_error(context.error, 'Telegram', self.ErrorLog)
            await update.message.reply_text("Sorry, I ran into an error! Please contact my creator.")

    # Read the GPT Conversation so far
    @staticmethod
    def gpt_read_interactions(file_path: str):
        with open(file_path, 'r') as interaction_log:
            lines = interaction_log.readlines()
        formatted_messages = [json.loads(line) for line in lines]
        return formatted_messages

    # Get the OpenAI Chat Completion response based on bot configuration
    def gpt_completion(self, uname: str):
        try:
            client = OpenAIClientSingleton.get_instance()
            response = client.chat.completions.create(
                model       = self.chatgpt['chat_model'],
                messages    = self.conversations[uname].messages,
                temperature = self.chatgpt['temperature'],
                top_p       = self.chatgpt['top_p']
            )
            return response

        except openai.AuthenticationError as e:
            # Handle authentication error
            log_error(e, error_type='OpenAI-Authentication', error_filename=self.ErrorLog)
        except openai.BadRequestError as e:
            # Handle invalid request error
            if re.search(r'maximum context.+reduce the length', e.message):
                # Remove older messages and try again since the model's maximum token limit reached
                print(f"Response to {uname} reached maximum context length, pruning conversation")
                self.conversations[uname].prune_conversation(self.chatgpt['prune_back_to'])
                return self.gpt_completion(uname)
            else:
                # Another error is actually invalid to investigate
                log_error(e, error_type='OpenAI-BadRequest', error_filename=self.ErrorLog)
        except openai.APIConnectionError as e:
            # Handle API connection error
            log_error(e, error_type='OpenAI-APIConnection', error_filename=self.ErrorLog)
        except Exception as e:
            # Catch any other unexpected exceptions
            log_error(e, error_type='Other', error_filename=self.ErrorLog)

    # The main polling "loop" the user interacts with via Telegram
    def start_polling(self):
        print(f"TeLLMgramBot {self.telegram['username']} polling...")
        self.telegram['app'].run_polling(poll_interval=self.telegram['pollinterval'])
        print(f"TeLLMgramBot {self.telegram['username']} polling ended.")

    # Initialization
    def __init__(self,
                 bot_username   = INIT_BOT_CONFIG['bot_username'],
                 bot_owner      = INIT_BOT_CONFIG['bot_owner'],
                 bot_name       = INIT_BOT_CONFIG['bot_name'],
                 bot_nickname   = INIT_BOT_CONFIG['bot_nickname'],
                 bot_initials   = INIT_BOT_CONFIG['bot_initials'],
                 chat_model     = INIT_BOT_CONFIG['chat_model'],
                 url_model      = INIT_BOT_CONFIG['url_model'],
                 token_limit    = INIT_BOT_CONFIG['token_limit'],
                 persona_temp   = INIT_BOT_CONFIG['persona_temp'],
                 persona_prompt = INIT_BOT_CONFIG['persona_prompt']
                 ):
        # First provide the main structure if not already there
        init_structure()

        # Set up our variables
        self.ErrorLog = os.path.join(os.environ['TELLMGRAMBOT_APP_PATH'], 'errorlogs', 'error.log')
        self.started = False
        self.GPTOnline = False
        self.token_warning = {}  # Determines whether user has reached token limit by OpenAI model
        self.conversations = {}  # Provides Conversation class per user based on bot response

        # Get Telegram Spun Up
        # noinspection PyDictCreation
        self.telegram = {
            'owner'        : bot_owner,
            'username'     : bot_username,
            'nickname'     : bot_nickname,
            'initials'     : bot_initials,
            'pollinterval' : 3
        }
        self.telegram['app'] = Application.builder().token(os.environ['TELLMGRAMBOT_TELEGRAM_API_KEY']).build()

        # Add our handlers for Commands, Messages, and Errors
        self.telegram['app'].add_handler(CommandHandler('help', self.tele_commands))
        self.telegram['app'].add_handler(CommandHandler('start', self.tele_start_command))
        self.telegram['app'].add_handler(CommandHandler('stop', self.tele_stop_command))
        self.telegram['app'].add_handler(CommandHandler('nick', self.tele_nick_command))
        self.telegram['app'].add_handler(CommandHandler('forget', self.tele_forget_command))
        self.telegram['app'].add_handler(MessageHandler(filters.TEXT, self.tele_handle_message))
        self.telegram['app'].add_error_handler(self.tele_error)

        # Get our LLM spun up with defaults if not defined by user input
        # Tokens as integers measure the length of conversation messages
        self.chatgpt = {
            'name'        : bot_name,
            'prompt'      : persona_prompt,
            'chat_model'  : chat_model,
            'url_model'   : url_model,
            'token_limit' : token_limit or TokenGPT(chat_model).max_tokens(),
            'temperature' : persona_temp or 1.0,
            'top_p'       : 0.9
        }
        # Set a rounded-down integer to prune a lengthy conversation by 500 tokens
        # Note if the upper limit is below 500, the lower limit is set to 0
        self.chatgpt['prune_threshold'] = floor(0.95 * self.chatgpt['token_limit'])
        self.chatgpt['prune_back_to'] = max(0, self.chatgpt['prune_threshold'] - 500)

    # Sets TeLLMgramBot object based on its YAML configuration and prompt files
    # noinspection PyMethodParameters
    def set(config_file='config.yaml', prompt_file='test_personality.prmpt'):
        # First provide the main structure if not already there
        init_structure()

        # Ensure both bot configuration and prompt files are defined and readable
        config = read_yaml(init_bot_config(config_file))
        prompt = read_text(init_bot_prompt(prompt_file))

        # Check any configuration values missing and apply default values:
        for parameter, value in INIT_BOT_CONFIG.items():
            if parameter == 'persona_prompt':
                # Apply initial prompt if not defined
                if not prompt:
                    prompt = value
                    print(f"File '{prompt_file}' is empty, set default prompt '{prompt}'")
            elif parameter not in config:
                # Apply initial configuration parameter with default if not defined
                config[parameter] = value
                if value:
                    print(f"Configuration '{parameter}' not defined, set to '{value}'")

        # Apply parameters to bot:
        return TelegramBot(
            bot_username   = config['bot_username'],
            bot_owner      = config['bot_owner'],
            bot_name       = config['bot_name'],
            bot_nickname   = config['bot_nickname'],
            bot_initials   = config['bot_initials'],
            chat_model     = config['chat_model'],
            url_model      = config['url_model'],
            token_limit    = config['token_limit'],
            persona_temp   = config['persona_temp'],
            persona_prompt = prompt
        )
