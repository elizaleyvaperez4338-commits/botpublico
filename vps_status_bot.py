import os
import time
import platform
import psutil
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("8278705583:AAFOwQffTb-7vsa7g79HLj9sh_iZufZvaKE")

def bytes_to_gb(b: int) -> float:
    return b / (1024 ** 3)

def fmt_uptime(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))

def get_status_text() -> str:
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=True)

    # RAM
    vm = psutil.virtual_memory()
    ram_total = bytes_to_gb(vm.total)
    ram_used = bytes_to_gb(vm.used)
    ram_percent = vm.percent

    # Disco (root)
    du = psutil.disk_usage("/")
    disk_total = bytes_to_gb(du.total)
    disk_used = bytes_to_gb(du.used)
    disk_percent = du.percent

    # Uptime
    boot_ts = psutil.boot_time()
    uptime = time.time() - boot_ts

    # Load average (Linux)
    load_str = "N/A"
    try:
        la1, la5, la15 = os.getloadavg()
        load_str = f"{la1:.2f}, {la5:.2f}, {la15:.2f}"
    except Exception:
        pass

    hostname = platform.node()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = (
        f"🖥️ *VPS Status*\n"
        f"🕒 *Hora:* `{now}`\n"
        f"🏷️ *Host:* `{hostname}`\n\n"
        f"⚙️ *CPU:* `{cpu_percent:.1f}%` (cores: `{cpu_count}`)\n"
        f"📈 *Load (1/5/15):* `{load_str}`\n\n"
        f"🧠 *RAM:* `{ram_used:.2f} / {ram_total:.2f} GB` (`{ram_percent:.1f}%`)\n"
        f"💾 *Disco (/):* `{disk_used:.2f} / {disk_total:.2f} GB` (`{disk_percent:.1f}%`)\n\n"
        f"⏱️ *Uptime:* `{fmt_uptime(uptime)}`\n"
    )
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Listo ✅\nUsa /status para ver recursos del VPS.",
        parse_mode="Markdown",
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(get_status_text(), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error leyendo estado: {e}")

def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("Falta BOT_TOKEN. Ej: export BOT_TOKEN='123:ABC'")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))

    print("Bot corriendo... Ctrl+C para salir")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

