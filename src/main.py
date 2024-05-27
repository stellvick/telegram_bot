from classes.bot_handler import BotHandler
from utils.config_utils import ConfigUtils
from classes.db import Db

cu = ConfigUtils()
cu.load_config()
db = Db()
db.start()
bot = BotHandler(db)
bot.run()

