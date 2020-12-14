import yaml
import logging

class BotConfig:
    port = 8081
    logfile = None  # 'bot.log'
    debug = True
    apikey = 'put_real_apikey_here'

    register_endpoint = 'https://api.telegram.org/bot{apikey}/setWebhook'
    msg_endpoint = 'https://api.telegram.org/bot{apikey}/sendMessage'
    answerCallbackQuery_endpoint = 'https://api.telegram.org/bot{apikey}/answerCallbackQuery'
    editMessageText_endpoint = 'https://api.telegram.org/bot{apikey}/editMessageText'

    bot_host = 'https://example.org'
    update_path = '/bot/{secret}/update'

    @staticmethod
    def read(filename):
        with open(filename) as f:
            yml = yaml.safe_load(f)
        for key,val in yml.items():
            if hasattr(BotConfig,key):
                setattr(BotConfig,key,val)
            else:
                logging.warning('Unknown configuration key "{}"'.format(key))
