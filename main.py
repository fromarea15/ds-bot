import discord
import random
import datetime
import mysql.connector
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

    # Получение всех пользователей с чатид, присутствующих онлайн
    online_members = [member for member in ctx.guild.members if
                      (member.status != discord.Status.offline and not member.bot) or member.voice]

    # Получение информации о пользователях из базы данных
    cnx = mysql.connector.connect(user='root', password='lCEoii1qpNCeIhzVUz6e',
                                  host='containers-us-west-42.railway.app', port='7287',
                                  database='railway')
    cursor = cnx.cursor()
    query = "SELECT name, count FROM users WHERE chatid = %s"
    cursor.execute(query, (server_id,))
    rows = cursor.fetchall()
    # Создание словаря с информацией о пользователе и его количестве упоминаний
    mentions_count = {name: count for name, count in rows}
    cursor.close()
    cnx.close()

    if server_id in last_used:
        elapsed_time = datetime.datetime.now() - last_used[server_id]
        time = 60 * 60 / 2
        if elapsed_time.total_seconds() < time:
            remaining_time = datetime.timedelta(seconds=int(time - elapsed_time.total_seconds()))
            await ctx.send(f"Слышь, жди ешё {remaining_time}.")
            return

    if len(online_members) > 0:
        random_member = random.choice(online_members)

        # Обновление информации о пользователе в базе данных
        cnx = mysql.connector.connect(user='root', password='lCEoii1qpNCeIhzVUz6e',
                                      host='containers-us-west-42.railway.app', port='7287',
                                      database='railway')
        cursor = cnx.cursor()
        if random_member.name in mentions_count:
            mentions_count[random_member.name] += 1
            query = "UPDATE users SET count = %s WHERE chatid = %s AND name = %s"
            cursor.execute(query, (mentions_count[random_member.name], server_id, random_member.name))
        else:
            mentions_count[random_member.name] = 1
            query = "INSERT INTO users (name, chatid, count) VALUES (%s, %s, %s)"
            cursor.execute(query, (random_member.name, server_id, 1))

        await ctx.send(f'Пробитие для : {random_member.mention}')
        last_used[server_id] = datetime.datetime.now()
        cnx.commit()
        cursor.close()
        cnx.close()
    else:
        await ctx.send('Нет доступных участников для выбора')


# функция для обновления информации о пользователе в базе данных
def update_user_count(name, chatid):
    cnx = mysql.connector.connect(user='root', password='lCEoii1qpNCeIhzVUz6e',
                                  host='containers-us-west-42.railway.app', port='7287',
                                  database='railway')
    cursor = cnx.cursor()
    query = "SELECT count FROM users WHERE name = %s AND chatid = %s"
    cursor.execute(query, (name, chatid))
    result = cursor.fetchone()

    if result:
        count = result[0] + 1
        query = "UPDATE users SET count = %s WHERE name = %s AND chatid = %s"
        cursor.execute(query, (count, name, chatid))
    else:
        count = 1
        query = "INSERT INTO users (name, chatid, count) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, chatid, count))

    cnx.commit()
    cursor.close()
    cnx.close()


# функция для получения топ-3 пробитых пользователей
def get_mention_stats(guild_id):
    cnx = mysql.connector.connect(user='root', password='lCEoii1qpNCeIhzVUz6e',
                                  host='containers-us-west-42.railway.app', port='7287',
                                  database='railway')
    cursor = cnx.cursor()
    query = "SELECT name, count FROM users WHERE chatid = %s ORDER BY count DESC"
    cursor.execute(query, (guild_id,))
    result = cursor.fetchall()

    mention_stats = [(row[0], row[1]) for row in result]
    cursor.close()
    cnx.close()

    return mention_stats


# команда для вывода топ-3 пробитых пользователей
@bot.command()
async def stats(ctx):
    guild_id = ctx.guild.id
    mention_stats = get_mention_stats(guild_id)

    if mention_stats:
        stats_message = "Топ пробитых:\n"
        count = 0
        prev_count = None
        for user, num in mention_stats:
            count += 1
            if num != prev_count:
                place = count
            stats_message += f"{place}. {user}: {num}\n"
            prev_count = num
        await ctx.send(stats_message)
    else:
        await ctx.send('Тут нет пробитых')


def reload():
    pass


def upload():
    pass


bot.run('MTA5MTg1MjM3MDI2NDIwMzM2NA.GTt_W3.Sqci461j48vJH0XRVzlBSWmtdDY_iQwwJLXBjY')
