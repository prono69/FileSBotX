import sys
import io
import traceback
import os
from FileStream.bot import FileStream
from FileStream.config import Telegram
from FileStream.utils.bot_utils import json_parser
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums.parse_mode import ParseMode

# Define constants missing in your snippet
MAX_MESSAGE_LENGTH = 4096

@FileStream.on_message(filters.command("eval") & filters.user(Telegram.OWNER_ID))
async def eval_command(client, message):
    status_message = await message.reply_text("`Processing ...`")
    cmd = message.text.split(" ", maxsplit=1)[1]

    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc, result = None, None, None, None

    try:
        # Run the user-provided code and capture the result of the last expression
        result = await aexec(cmd, client, message)
    except Exception as e:
        exc = traceback.format_exc()
        error_type = e.__class__.__name__
        error_message = str(e)
        evaluation = (
            f"❌ **Error**: `{error_type}`\n"
            f"**Message**: `{error_message}`\n"
            f"**Traceback**:\n<code>{exc}</code>"
        )
    else:
        stdout = redirected_output.getvalue()
        stderr = redirected_error.getvalue()
        formatted_result = json_parser(result, indent=2)
        if stderr:
            evaluation = f"⚠️ **Stderr**:\n<code>{stderr}</code>"
        elif stdout:
            evaluation = f"<code>{stdout}</code>"
        elif result is not None:  # If the last expression returned something
            evaluation = f"<code>{formatted_result}</code>"
        else:
            evaluation = "✅ **Success**"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    final_output = "<b>EVAL</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>OUTPUT</b>:\n"
    final_output += f"{evaluation.strip()} \n"

    if len(final_output) > MAX_MESSAGE_LENGTH:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[: MAX_MESSAGE_LENGTH // 4 - 1],
                disable_notification=True,
                quote=True,
            )
    else:
        await reply_to_.reply_text(final_output, quote=True)
    await status_message.delete()


async def aexec(code, client, message):
    indent = "    "  # 4 spaces for consistent indentation
    
    header = (
        "async def __aexec(client, message):\n"
        f"{indent}import os\n"
        f"{indent}import requests\n"
        f"{indent}from pprint import pformat\n"
        f"{indent}neo = message\n"
        f"{indent}e = message = event = neo\n"
        f"{indent}r = reply = message.reply_to_message\n"
        f"{indent}chat = message.chat.id\n"
        f"{indent}c = client\n"
        f"{indent}to_photo = message.reply_photo\n"
        f"{indent}to_video = message.reply_video\n"
        f"{indent}p = print\n"
        f"{indent}_result = None\n"
    )
    
    lines = code.split("\n")
    try:
        # Try to compile the last line as an expression.
        compile(lines[-1], "<string>", "eval")
        # Indent all lines except the last.
        body = "\n".join(indent + l for l in lines[:-1])
        # Append the last line to capture its return value.
        last_line = "\n" + indent + "_result = " + lines[-1]
    except SyntaxError:
        body = "\n".join(indent + l for l in lines)
        last_line = ""
    
    # Add a final return statement to return the captured result.
    return_line = "\n" + indent + "return _result\n"
    full_code = header + body + last_line + return_line
    
    # Dynamically compile and execute the function definition.
    exec(full_code)
    result = await locals()["__aexec"](client, message)
    return result