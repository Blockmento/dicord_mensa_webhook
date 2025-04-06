from datetime import datetime, timedelta
import sys
import random
from discord_webhook import DiscordEmbed

from thueringen import Canteen, Parser

ON_DAY = lambda dt, day: dt + timedelta(days=(int(day) - dt.weekday()) % 7)


ITALIC = lambda text: f"_{text}_" if text != "" else ""
BOLD = lambda text: f"*{text}*" if text != "" else ""
INLINE_CODE = lambda text: f"`{text}`" if text !="" else ""
BLOCK_CODE = lambda text, lang="": f"```{lang}\n{text}\n```" if text != "" else ""


# lambda to check if vegan in meal['category'], meal['name'] or meal['notes']
VEGAN_old = (
    lambda meal: "vegan" in meal["category"].lower()
    or "vegan" in meal[0].lower()
    or "vegan" in ", ".join(set(meal["notes"])).lower()
)

# PRINT_PRICES = lambda d: for val in d :

EMOJI_REPLACE_CROUPS = {
    "student": [":woman_student:", ":man_student:"],
    "employee": [":woman_office_worker:", ":man_office_worker:"],
    "pupils": [":school_satchel:"],
    "other": [":woman:", ":man:"],
}

EMOJI_REPLACE_MEALS = {
    "Vegan": ":broccoli:",
    "Vegetarisch": ":cucumber:",
    "Fleisch": ":meat_on_bone:",
    "Fisch": ":fish:"
}

WEEKDAYS = [
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag",
]

parser = Parser('thueringen', version='2.0')

CANTEENS = {
    69: Canteen('ei-wartenberg', parser, canteen_id=69),
    44: Canteen('ef-nordhaeuser', parser, canteen_id=44),
    47: Canteen('ef-altonaer', parser, canteen_id=47),
    51: Canteen('ef-schlueterstr', parser, canteen_id=51),
    52: Canteen('ef-leipzigerstr', parser, canteen_id=52),
    67: Canteen('ge-freundschaft', parser, canteen_id=67),
    46: Canteen('il-ehrenberg', parser, canteen_id=46),
    53: Canteen('il-cafeteria', parser, canteen_id=53),
    55: Canteen('il-nanoteria', parser, canteen_id=55),
    57: Canteen('il-roentgen', parser, canteen_id=57),
    58: Canteen('je-zeiss', parser, canteen_id=58),
    61: Canteen('je-eah', parser, canteen_id=61),
    41: Canteen('je-ernstabbe', parser, canteen_id=41),
    60: Canteen('je-vegeTable', parser, canteen_id=60),
    63: Canteen('je-rosen', parser, canteen_id=63),
    59: Canteen('je-philosophen', parser, canteen_id=59),
    64: Canteen('je-haupt', parser, canteen_id=64),
    65: Canteen('je-bib', parser, canteen_id=65),
    71: Canteen('nh-mensa', parser, canteen_id=71),
    73: Canteen('sk-mensa', parser, canteen_id=73),
    77: Canteen('we-park', parser, canteen_id=77),
    80: Canteen('we-anna', parser, canteen_id=80),
    81: Canteen('we-coudray', parser, canteen_id=81),
}


def create_price_string(prices):
    res = ""
    delim = ""
    for key, value in prices.items():
        if value is not None:
            res += delim
            res += (
                f"{random.choice(EMOJI_REPLACE_CROUPS[key])} {'{:2.2f}'.format(prices[key] / 100)}€ "
            )
            delim = "| "
    return res


def create_menu_embed(id: int, mensa_name: str, weekday: int = None, time_offset: float = None, time: str = "Mittagessen") -> DiscordEmbed:

    if time_offset and weekday == True:
        date = timedelta(time_offset) + datetime.now()
        if date.weekday() in [5,6]:
            date = ON_DAY(datetime.now(), 0)
    elif weekday:
        date = ON_DAY(datetime.now(), weekday)
    elif time_offset:
        date = timedelta(time_offset) + datetime.now()
    else:
        date = datetime.now()


    canteen = CANTEENS[id]
    if date.date() not in canteen.feed._days.keys():
        canteen.parse_single_date(date)

    try:
        response = canteen.feed._days[date.date()]
        # print(f"{mensa_name}, Speiseplan vom {date.strftime('%d.%m.%Y')}")
        embed = (
            DiscordEmbed(
                title=f"{mensa_name}, {time} vom {WEEKDAYS[date.weekday()]} dem {date.strftime('%d.%m.%Y')}",
                description="",
                colour="00B1AB",
                timestamp=datetime.now().astimezone(),
            )
        )
        for category, meals in response.items():
            for meal in meals:
                if meal[1][0] != time:
                    continue
                # prices = ast.literal_eval(meal['prices'])
                # prices = json.load(meal['prices'])
                prices = meal[2]
                # print(await create_price_string(prices))
                # print(f"prices: {prices['students']}")
                embed.add_embed_field(
                    # name is meal['category'] + emoji if vegan
                    name=f"{meal[0]}",
                    # name=f"{meal['category']} {await create_price_string(prices)} ",
                    value=f"{category} {EMOJI_REPLACE_MEALS[category]}\n{create_price_string(prices)}\n{" ".join([INLINE_CODE(info) for info in meal[1][1:]])}",
                    inline=False,
                )
        return embed
    except:
        # log exception
        print("Exception:", sys.exc_info()[0])

        embed = DiscordEmbed(
            title=f"{mensa_name}, Speiseplan vom {WEEKDAYS[date.weekday()]} dem {date.strftime('%d.%m.%Y')}",
            description="Geschlossen!",
            timestamp=datetime.now().astimezone(),
            color="00B1AB",
        )
        return embed