import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from quiz_data import DATA


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for grade in range(1, 13):
        keyboard.append([
            InlineKeyboardButton(
                f"Grade {grade}",
                callback_data=f"grade_{grade}"
            )
        ])

    await update.message.reply_text(
        "🎓 Welcome to HayAI Quiz!\n\nChoose your grade:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def send_question(query, context):
    questions = context.user_data["questions"]
    current = context.user_data["current"]

    question, answers, correct = questions[current]

    keyboard = []

    for i, answer in enumerate(answers):
        keyboard.append([
            InlineKeyboardButton(
                answer,
                callback_data=f"answer_{i}"
            )
        ])

    await query.edit_message_text(
        f"Question {current + 1}/10\n\n{question}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_result(query, context):
    score = context.user_data["score"]

    keyboard = [[
        InlineKeyboardButton("🔄 Play again", callback_data="restart")
    ]]

    await query.edit_message_text(
        f"🏆 Quiz finished!\n\nYour score: {score}/10",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("grade_"):
        grade = int(data.split("_")[1])

        if grade not in DATA:
            await query.edit_message_text("Questions not found.")
            return

        context.user_data["grade"] = grade
        context.user_data["questions"] = DATA[grade]
        context.user_data["current"] = 0
        context.user_data["score"] = 0

        await send_question(query, context)

    elif data.startswith("answer_"):
        questions = context.user_data.get("questions")

        if not questions:
            await query.edit_message_text("Please send /start first.")
            return

        current = context.user_data["current"]
        selected = int(data.split("_")[1])

        question, answers, correct = questions[current]

        if selected == correct:
            context.user_data["score"] += 1
            result = "✅ Correct answer!"
        else:
            result = f"❌ Wrong answer!\nCorrect answer: {answers[correct]}"

        keyboard = [[
            InlineKeyboardButton("➡️ Next question", callback_data="next")
        ]]

        await query.edit_message_text(
            f"{result}\n\nScore: {context.user_data['score']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "next":
        context.user_data["current"] += 1

        if context.user_data["current"] < len(context.user_data["questions"]):
            await send_question(query, context)
        else:
            await show_result(query, context)

    elif data == "restart":
        await start_again(query, context)


async def start_again(query, context):
    keyboard = []

    for grade in range(1, 13):
        keyboard.append([
            InlineKeyboardButton(
                f"Grade {grade}",
                callback_data=f"grade_{grade}"
            )
        ])

    await query.edit_message_text(
        "🎓 Choose your grade:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    token = "9221811093:AAHRR_xnTlNBGztLRJZ1X3DL17sBrQ1m5Cc"  # Replace with your bot token or use os.environ.get("BOT_TOKEN") to fetch from environment

    if not token:
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 HayAI Quiz Bot is running!")

    app.run_polling()


if __name__ == "__main__":
    main()
