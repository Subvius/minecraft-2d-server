import datetime
import logging

import telegram.ext
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, \
    CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup

from bot.lib.functions.commands import strfdelta_round
from lib.functions.images import make_image_for_general, make_image_for_leaderboard
from lib.functions.constants import Constants
import lib.functions.api as api
from lib.functions.settings import *

clearcache()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='bot.log'
)

logger = logging.getLogger(__name__)
reply_markup = [
    ["/help", "/general"],
    ["/rep", "/leaderboard"],
    ["/skin", "/cloak"],
    ["/announcement"],
]

settings_markup = [
    [InlineKeyboardButton("Clear Cache", callback_data='stgsclearcache')],
]

cloaks = ['8bitcogs', '8biteclipse', '8bitufo', '8bittheia', '8bitstar', '8bitlunar', '8bitsunset', '8biticeberg',
          '8bitsword', '8bitcherryblossom', '8bitblackhole', '8bitstreets', '8bitskull', '8bitblossom']

markup = ReplyKeyboardMarkup(reply_markup, one_time_keyboard=False)
constants = Constants()
application: Application = None
bot: Bot = None


async def echo(update: Update, context):
    await help_command(update, context)


async def general(update: Update, context):
    user = update.effective_user
    await update.message.reply_text("Alright. Send me username", reply_markup=markup)
    return 1


async def general_send_stats(update: Update, context):
    user = update.effective_user
    ign = update.message.text.strip()
    message = await update.message.reply_text(f"Searching stats for {ign}...")
    res = api.get_data(constants.api_url + f"player/?player={update.message.text}", json_res=True)
    if res.get("success", False):
        path = make_image_for_general(ign, res.get("player"))

        await message.delete()
        with open(path, "rb") as f:
            await update.message.reply_photo(f, caption=f"General stats of {ign}")
        return ConversationHandler.END

    else:
        await application.bot.edit_message_text(
            "Player is not found! Make sure you have entered the correct username.", message_id=message.message_id,
            chat_id=update.message.chat_id)
    return 1


async def start(update: Update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Hey, {user.mention_html()}! ",
        reply_markup=markup
    )


async def rep(update: Update, context):
    await update.message.reply_text("No problem. Just provide username.")
    return 1


async def rep_send(update: Update, _):
    ign = update.message.text.strip()
    message = await update.message.reply_text(f"Searching stats for {ign}...")
    res = api.get_data(constants.api_url + f"player/?player={update.message.text}", json_res=True)
    if res.get("success", False):
        reputation = res.get("player").get("reputation", {})
        rep_text = str()

        sorted_rep = {"magician": 0, "killer": 0, "robber": 0, "smuggler": 0, "spice": 0}
        for key in list(sorted_rep.keys()):
            sorted_rep.update({
                key: reputation.get(key, 0)
            })

        for el in sorted_rep.items():
            rep_text += f"{el[0].capitalize()} - **{el[1]}**\n"
        await bot.edit_message_text(
            f"Here's the {ign}'s reputation.\n\n{rep_text}", parse_mode="markdown", message_id=message.message_id,
            chat_id=update.message.chat_id)
        return ConversationHandler.END

    else:
        await application.bot.edit_message_text(
            "Player is not found! Make sure you have entered the correct username.", message_id=message.message_id,
            chat_id=update.message.chat_id)
    return 1


async def button(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    if query.data == "no":
        await query.message.delete()
        await query.message.reply_text("Alright. Canceled operation!")
    elif query.data.count("lb"):
        keyboard = [
            [InlineKeyboardButton("Reputation", callback_data='lbreputation'),
             InlineKeyboardButton("Play Time", callback_data='lbplaytime')],
        ]
        replymarkup = InlineKeyboardMarkup(keyboard)
        lb_type = "reputation" if query.data == "lbreputation" else "play_time"
        res = api.get_data(constants.api_url + f"leaderboard/?type={lb_type}", json_res=True)
        if res.get("success", False):
            path = make_image_for_leaderboard(res.get("data"), lb_type)

            await query.message.delete()

            with open(path, "rb") as f:
                await query.message.reply_photo(f, caption=f"", reply_markup=replymarkup)
        else:
            await application.bot.edit_message_text(
                "Something went wrong. Please try again later.", message_id=query.message.message_id,
                chat_id=update.message.chat_id)
    elif query.data.startswith("stgs"):
        replymarkup = InlineKeyboardMarkup(settings_markup)
        operation = query.data[4:]
        if operation == "clearcache":
            clearcache()
            await query.message.reply_text("Successfully cleared the cache! 🧹")
    elif query.data.startswith("anncmt"):
        operation = query.data[6:]
        print(f"{operation=}")

        await query.message.delete()

        if operation == "delete":
            res = api.post_data(constants.api_url + "announcement/", params={"delete": True}, data={})
            if res.get("success"):
                await query.message.reply_text("Announcement was successfully deleted.")
            else:
                await query.message.reply_text("Something went wrong.")


async def leaderboard(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Reputation", callback_data='lbreputation'),
         InlineKeyboardButton("Play Time", callback_data='lbplaytime')],
    ]
    replymarkup = InlineKeyboardMarkup(keyboard)
    message = await update.message.reply_text("Loading data...", reply_markup=replymarkup)
    res = api.get_data(constants.api_url + "leaderboard", json_res=True)
    if res.get("success", False):
        path = make_image_for_leaderboard(res.get("data"), "reputation")

        await message.delete()
        with open(path, "rb") as f:
            await update.message.reply_photo(f, caption=f"", reply_markup=replymarkup)
    else:
        await application.bot.edit_message_text(
            "Something went wrong. Please try again later.", message_id=message.message_id,
            chat_id=update.message.chat_id)


async def stop(update: Update, context):
    await update.message.reply_text("All active commands have been canceled!")
    return ConversationHandler.END


async def cloak(update: Update, context):
    text = "\n".join(cloaks)
    await update.message.reply_text(
        f"Sure. Just pick cloak name from below.\n\n{text}\n\nYou can buy any of those cloak on our website!")
    return 1


async def cloak_send(update: Update, context):
    cloak_name = update.message.text.strip()
    message = await update.message.reply_text(f"Searching for {cloak_name}.")
    formatted_cloaks = [el.lower() for el in cloaks]
    if cloak_name.lower() in formatted_cloaks:
        index = formatted_cloaks.index(cloak_name.lower())
        await message.delete()

        with open(f"lib/assets/cloaks_preview/{cloaks[index]}.png", "rb") as f:
            await update.message.reply_photo(
                f,
            )
        return ConversationHandler.END

    else:
        await bot.edit_message_text(
            "Incorrect cloak name", message_id=message.message_id,
            chat_id=update.message.chat_id)
    return 1


async def help_command(update: Update, context):
    await update.message.reply_text("""**Minecraft 2D Help**
**General**
You can check your stats by running /general command\n
**Reputation**
To view the reputation, you just need to use the /rep command\n
**Leaderboards**
We offer several leaderboards through the /leaderboard command. You can see leaderboards based on total time, reputation and much more!\n
**Minecraft**
You can view general Minecraft information such as skins, cloaks through /skin and /cloak respectively. """,
                                    reply_markup=markup, parse_mode="markdown")


async def skin(update: Update, context):
    await update.message.reply_text("OK. Just send me IGN of skin owner.")
    return 1


async def settings(update: Update, context):
    if update.message.from_user.id in [509737198]:
        replymarkup = InlineKeyboardMarkup(settings_markup)
        await update.message.reply_text("Hey Admin.\nHere's my settings.", reply_markup=replymarkup)

    else:
        await help_command(update, context)


async def announcement(update: Update, context):
    if update.message.from_user.id in [509737198]:
        reply_keyboard = [
            ["View announcement", "Create announcement"],
            ["Delete announcement"],
        ]
        _markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Hey Admin.\nPick an option from keyboard below.", reply_markup=_markup)

    else:
        await help_command(update, context)


async def delete_announcement(update: Update, context):
    if update.message.from_user.id in [509737198]:
        dl_anncmt = [
            [InlineKeyboardButton("Yes", callback_data='anncmtdelete')],
            [InlineKeyboardButton("No", callback_data="no"), ],
        ]
        replymarkup = InlineKeyboardMarkup(dl_anncmt, )

        await update.message.reply_text("Are you sure?", reply_markup=replymarkup)
    else:
        await help_command(update, context)


async def view_announcement(update: Update, context):
    if update.message.from_user.id in [509737198]:
        res = api.get_data(constants.api_url + "announcement/", json_res=True).get("data", {})

        announce = res.get("announcement", None)
        if announce is not None:
            end, text = announce.get("end"), announce.get("text")

            end_date = datetime.datetime.fromtimestamp(end)
            reply_text = f"Here's current announcement:\n\n**{text} " \
                         f"{strfdelta_round(end_date - datetime.datetime.now(), 'second')}**"
        else:
            reply_text = "No announcement's found"

        await update.message.reply_text(reply_text, reply_markup=markup, parse_mode="markdown")
    else:
        await help_command(update, context)


async def create_announcement(update: Update, context):
    if update.message.from_user.id in [509737198]:
        await update.message.reply_text("OK. Provide text to announce", reply_markup=None)
        return 1

    else:
        await help_command(update, context)


async def provide_date(update: Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["announce_text"] = text
    await update.message.reply_text("Great! Now specify the end date of the announcement in format: YYYY-MM-DD HH:MM")
    return 2


async def announcement_done(update: Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    date_string = update.message.text
    user_data = context.user_data
    announce_text = user_data.get("announce_text")
    try:
        date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M")
    except:
        await update.message.reply_text("Date does not match format YYYY-MM-DD HH:MM")
        return 2

    if "announce_text" in user_data:
        del user_data["announce_text"]

    res = api.post_data(constants.api_url + "announcement",
                        data={"text": announce_text.strip(), "end": date.timestamp()},
                        params={"create": True})

    if res.get("success", False):
        await update.message.reply_text("✅ Successfully created a new announcement!")
    else:
        await update.message.reply_text("Something went wrong. Try again later.")

    return ConversationHandler.END


async def skin_send(update: Update, context):
    ign = update.message.text.strip()
    message = await update.message.reply_text(f"Searching for {ign}'s skin...")

    uuid: str = api.get_data(f"https://minecraft-api.com/api/uuid/{ign.strip().replace(' ', '').lower()}",
                             json_res=False).content.decode(encoding="utf-8")

    if uuid is not None and not uuid.lower().count("player"):
        await message.delete()

        await update.message.reply_photo(
            f"https://skins.mcstats.com/body/front/{uuid}",
            caption=f"{ign}'s skin.",

        )
        return ConversationHandler.END
    else:
        await bot.edit_message_text(
            "User does not exist.", message_id=message.message_id,
            chat_id=update.message.chat_id)

    return 1


def main():
    global application, bot
    application = Application.builder().token(input("Enter bot token:\n")).build()
    bot = application.bot

    text_handler = MessageHandler(filters.TEXT, echo)
    view_announcement_handler = MessageHandler(filters.Regex("^View announcement$"), view_announcement)
    delete_announcement_handler = MessageHandler(filters.Regex("^Delete announcement$"), delete_announcement)
    general_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('general', general)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, general_send_stats)],
        },

        fallbacks=[CommandHandler('stop', stop)]
    )
    reputation_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('rep', rep)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, rep_send)],
        },

        fallbacks=[CommandHandler('stop', stop)]
    )
    skin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('skin', skin)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, skin_send)],
        },

        fallbacks=[CommandHandler('stop', stop)]
    )
    cloak_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('cloak', cloak)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, cloak_send)],
        },

        fallbacks=[CommandHandler('stop', stop)]
    )
    announcement_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Create announcement$"), create_announcement)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, provide_date)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, announcement_done)],
        },

        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(view_announcement_handler)
    application.add_handler(delete_announcement_handler)
    application.add_handler(announcement_handler)
    application.add_handler(cloak_conv_handler)
    application.add_handler(skin_conv_handler)
    application.add_handler(reputation_conv_handler)
    application.add_handler(general_conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("announcement", announcement))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(text_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
