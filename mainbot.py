import nextcord
import logging
import requests
import datetime

logger = logging.getLogger('nextcord')
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
client = nextcord.Client(intents=intents)

domen = "https://minecraft2d.pythonanywhere.com"


def make_get_request(url, params):
    res: dict = requests.get(url, params=params
                             ).json()
    return res


@client.slash_command(name="stats", description="Get stats", guild_ids=[905824363788517377])
async def stats_command(interaction: nextcord.Interaction, player: str):
    res = make_get_request(domen + '/player', {'player': player.strip()})
    player_data = res.get('player')
    first_login = datetime.datetime.fromtimestamp(player_data.get('first_login')).strftime("%d/%m/%Y, %H:%M")
    last_login = datetime.datetime.fromtimestamp(player_data.get('last_login')).strftime("%d/%m/%Y, %H:%M")
    reputation_data = player_data.get('reputation')
    stats_data = player_data.get('stats')
    if player_data.get('last_logout') == 0:
        status = 'Online'
    if player_data.get('last_logout') != 0:
        status = 'Offline'
    if not res.get('success'):
        await interaction.send('Такого игрока не существует!\n Но вы можете создать его на нашем официальном сайте!')
        return
    time = stats_data.get('play_time')
    formatted = f"{round(time / 60 / 60, 2)}h" if time / 60 / 60 > 1 else f"{round(time / 60, 2)}m"
    await interaction.send(f"Nickname: {player_data.get('nickname')}\n"
                           f"First Login: {first_login}\n"
                           f"Last Login: {last_login}\n"
                           f"Status: {status}\n"
                           f"Reputation:\n"
                           f"killer: {reputation_data.get('killer')}\n"
                           f"magician: {reputation_data.get('magician')}\n"
                           f"robber: {reputation_data.get('robber')}\n"
                           f"smuggler: {reputation_data.get('smuggler')}\n"
                           f"spice: {reputation_data.get('spice')}\n"
                           f"Stats:\n"
                           f"blocks mined: {stats_data.get('blocks_mined')}\n"
                           f"blocks placed: {stats_data.get('blocks_placed')}\n"
                           f"playtime: {formatted}", ephemeral=True)


@client.slash_command(name='leaderboard', description='Get leaderboard', guild_ids=[905824363788517377])
async def leaderboard_command(interaction: nextcord.Interaction,
                              leaderboard: str = nextcord.SlashOption(name="leaderboard",
                                                                      description="Get leaderboard by"
                                                                                  " reputation or play time",
                                                                      choices=["reputation", "play_time"]),
                              amount: int = nextcord.SlashOption(name="amount", description="number of seats",
                                                                 min_value=1,
                                                                 max_value=10, default=5, required=False),
                              start: int = nextcord.SlashOption(name="start",
                                                                description="from where to start the countdown",
                                                                min_value=1,
                                                                default=1, required=False)):
    res = make_get_request(domen + '/leaderboard', {'type': leaderboard, 'amount': amount, 'start': start})
    text = ''
    if res.get('success'):
        data = res.get('data')
        for index, player in enumerate(data, start=1):
            time = player.get('stats').get('play_time')
            formatted = f"{round(time / 60 / 60, 2)}h" if time / 60 / 60 > 1 else f"{round(time / 60, 2)}m"
            if leaderboard == 'reputation':
                text += f"{index} - {player.get('nickname')} reputation:" \
                        f" {sum(list(player.get('reputation').values()))}\n"
            elif leaderboard == 'play_time':
                text += f"{index} - {player.get('nickname')} play time: {formatted}\n"
    else:
        text = 'Ошибка, перепроверте правильность ввода данных!'
    await interaction.send(text, ephemeral=True)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.slash_command(name="help", description="Get help")
async def help_command(interaction: nextcord.Interaction):
    await interaction.send('Список команд:\n'
                           '/stats команда позволяет увидеть статистику игрока через его никнейм\n'
                           '/leaderboard оманда позволяет увидеть список лидеров по репутации или времени,'
                           ' проведенному в игре(amount позволяет выбрать количество мест от 1 до 10,'
                           ' start позволяет выбрать с какого места начинать)', ephemeral=True)


client.run('MTA5NTcyMzU1NDQyNDc2MjQ2OA.G0hbMM.KaEyBTNJsMZ6v9dKUmvJt0mdZ4qYiYXGlP5BWw')
