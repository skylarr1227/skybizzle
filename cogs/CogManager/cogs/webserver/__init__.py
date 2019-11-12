from .webserver import WebServer
from redbot.core import data_manager

def setup(bot):
    data_manager.load_bundled_data(WebServer(bot), __file__)
    bot.add_cog(WebServer(bot))