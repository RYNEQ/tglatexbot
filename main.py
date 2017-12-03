from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto, ParseMode, ChatAction
from telegram.ext import InlineQueryHandler, Updater, CommandHandler, MessageHandler, Filters
import logging, hashlib, os, subprocess
from PIL import Image


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token='461006523:AAHETU3yYZTvMtar_rucUuRLsh6lZb36aQY')
dispatcher = updater.dispatcher

cachepath = "/var/www/html/text2png/"
remotepath = 'http://2220.ir/text2png/'


def text2png_inline(bot, update):
    query = update.inline_query.query
    if not query:
        return

    try:
        m = hashlib.md5()
        m.update(query)
        h = m.hexdigest()

        teximage = os.path.join(cachepath, "%s.png" % h)
        if not os.path.isfile(teximage):
            subprocess.check_call(['pnglatex', '-e','displaymath', '-d', '300', '-p', 'amssymb:amsmath',
                                   '-S', '-o', teximage, '-s', '20', '-P', '5', '-f', query])

        with Image.open(teximage) as img:
            width, height = img.size

            results = list()
            results.append(
                InlineQueryResultPhoto(
                    id='1',
                    photo_url='%s%s.png' % (remotepath, h),
                    thumb_url='%s%s.png' % (remotepath, h),
                    photo_width=width,
                    photo_height=height
                )
            )

        results.append(
            InlineQueryResultArticle(
                id='2',
                title="Bot Address",
                input_message_content=InputTextMessageContent('@text2png_bot'),
                #url='http://t.me/text2png_bot',
                description='Just send bot address',
                #thumb_url="http://2220.ir/text2png/avatar.png"
            )
        )

        bot.answer_inline_query(update.inline_query.id, results)
    except (subprocess.CalledProcessError,):
        bot.answer_inline_query(update.inline_query.id, [])


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Hi, this is a Tex to PNG convert bot\n"
                          "It uses 'amssymb:amsmath' package\n"
                          "The Bot caches formulas so only new formulas are compiled\n"
                          "You Can Use it both in inline mode or chat mode!\n"
                          "Try me! Send some Tex\n"
                          "Examples:\n"
                          " -   `E=mc^2` or\n"
                          " -   `\sum_{i=0}^n i=\\frac{n(n+1)}{2}` or\n"
                          " -   `A\\triangleq B`",
                     parse_mode=ParseMode.MARKDOWN)


def text2png(bot, update):
    query = update.message.text
    if not query:
        return

    try:
        m = hashlib.md5()
        m.update(query)
        h = m.hexdigest()

        teximage = os.path.join(cachepath, "%s.png" % h)
        if not os.path.isfile(teximage):
            subprocess.check_call(['pnglatex', '-e','displaymath', '-d', '300', '-p', 'amssymb:amsmath',
                                   '-S', '-o', teximage, '-s', '20', '-P', '5', '-f', query])

        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(teximage), reply_to_message_id=update.message.message_id)
    except (subprocess.CalledProcessError,):
        bot.send_message(chat_id=update.message.chat_id, text="Invalid Tex !")


inline_caps_handler = InlineQueryHandler(text2png_inline)
start_handler = CommandHandler('start', start)
normal_handler = MessageHandler(Filters.text, text2png)
dispatcher.add_handler(inline_caps_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(normal_handler)

updater.start_polling()
