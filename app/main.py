import os
import sched
import sys
import time
import yaml

from discord_webhook import DiscordWebhook
from formater import create_menu_embed
from datetime import datetime

def load_config():
    with open('./config.yml', 'r') as file:
        return yaml.safe_load(file)

def create_webhook(config):
    for webhook_config in config['webhooks']:
        webhook = DiscordWebhook(url=webhook_config["url"])
        webhook.add_embed({"title": "Webhook created"})
        webhook.execute()
    print("Webhooks created successfully")
    sys.exit(0)

def main(s, config):
    s.enter(600, 1, main, (s, config))

    for webhook_config in config['webhooks']:
        webhook = DiscordWebhook(url=webhook_config["url"], id=webhook_config['message_id'])
        for canteen in webhook_config['canteens']:
            if datetime.now().time() > datetime.strptime(canteen["time"], "%H:%M").time():
                embed = create_menu_embed(canteen['canteen_id'], canteen['name'], time_offset=.5, weekday=True, time=canteen['meal'])
            else:
                embed = create_menu_embed(canteen['canteen_id'], canteen['name'], time_offset=0, weekday=True, time=canteen['meal'])
            webhook.add_embed(embed)
        webhook.edit()

if __name__ == "__main__":
    config = load_config()
    if config["create"]:
        create_webhook(config)
    s = sched.scheduler(time.time, time.sleep)
    s.enter(10, 1, main, (s, config))
    s.run()