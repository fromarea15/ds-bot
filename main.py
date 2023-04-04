import discord
import random
import datetime
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

mentions_count = {}
last_used = {}

greetings = ["Пивет черт, {user}!",
             "Здравствуй, {user}! Надеюсь, ты хорошо проведешь время здесь!",
             "{user} иди нахуй, я догоню",
             "Рад что ты танкист {user}!",
             "Как сам, как мать {user}?",
             "{user} здрасьте, стартуем?",
             "{user} может пробитие хочешь??",
             "Вечер в хату {user}"]


@bot.event
async def on_member_join(member):
    # Выбираем случайное приветствие из списка
    greeting = random.choice(greetings)
    # Отправляем приветствие и тегаем пользователя
    await member.guild.system_channel.send(greeting.format(user=member.mention))


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command()
async def rand(ctx):
    server_id = ctx.guild.id

    if server_id in last_used:
        elapsed_time = datetime.datetime.now() - last_used[server_id]
        if elapsed_time.total_seconds() < 6 * 60 * 60:
            remaining_time = datetime.timedelta(seconds=int(6 * 60 * 60 - elapsed_time.total_seconds()))
            await ctx.send(f"Слышь, жди ешё {remaining_time}.")
            return

    online_members = [member for member in ctx.guild.members if
                      (member.status != discord.Status.offline and not member.bot) or member.voice]

    if len(online_members) > 0:
        random_member = random.choice(online_members)
        if server_id not in mentions_count:
            mentions_count[server_id] = {}
        if random_member.name in mentions_count[server_id]:
            mentions_count[server_id][random_member.name] += 1
        else:
            mentions_count[server_id][random_member.name] = 1

        await ctx.send(f'Пробитие для : {random_member.mention}')
        last_used[server_id] = datetime.datetime.now()
    else:
        await ctx.send('Нет доступных участников для выбора')


def get_mention_stats(guild_id):
    if guild_id in mentions_count:
        mention_stats = sorted(mentions_count[guild_id].items(), key=lambda x: x[1], reverse=True)
    else:
        mention_stats = []
    return mention_stats


@bot.command()
async def stats(ctx):
    guild_id = ctx.guild.id
    mention_stats = get_mention_stats(guild_id)

    if mention_stats:
        top_mentions = mention_stats[:3]
        stats_message = "Топ-3 пробитых :\n"
        for i, (user, count) in enumerate(top_mentions):
            stats_message += f"{i + 1}. {user}: {count}\n"
        await ctx.send(stats_message)
    else:
        await ctx.send(f'Тут нет пробитых')


@bot.command()
async def statALL(ctx):
    guild_id = ctx.guild.id
    mention_stats = get_mention_stats(guild_id)

    if mention_stats:
        stats_message = "Все пробитые :\n"
        for i, (user, count) in enumerate(mention_stats):
            stats_message += f"{i + 1}. {user}: {count}\n"
        await ctx.send(stats_message)
    else:
        await ctx.send(f'Тут нет пробитых')


def reload():
    pass


def upload():
    pass


bot.run('MTA5MTg1MjM3MDI2NDIwMzM2NA.GTt_W3.Sqci461j48vJH0XRVzlBSWmtdDY_iQwwJLXBjY')
