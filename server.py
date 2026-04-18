import discord
from discord.ext import commands
import random
import os  # Добавляем импорт модуля os для работы с переменными окружения

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Хранение данных инициативы для каждого сервера
initiative_data = {}


@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")


@bot.slash_command(name="добавить_персонажа", description="Добавляет персонажа с указанием ловкости+смекалки")
async def добавить_персонажа(
        ctx: discord.ApplicationContext,
        имя: str,
        ловкость_смекалка: int
):
    guild_id = ctx.guild.id
    if guild_id not in initiative_data:
        initiative_data[guild_id] = []

    # Обновляем существующую запись или добавляем новую
    updated = False
    for char in initiative_data[guild_id]:
        if char["name"] == имя:
            char["dex_wits"] = ловкость_смекалка
            updated = True
            break
    if not updated:
        initiative_data[guild_id].append({
            "name": имя,
            "dex_wits": ловкость_смекалка,
            "initiative": 0  # Инициатива пока не определена
        })

    await ctx.respond(f"✅ Персонаж **{имя}** добавлен/обновлен.")


@bot.slash_command(name="удалить_инициативу", description="Удаляет персонажа из списка")
async def удалить_инициативу(ctx: discord.ApplicationContext, имя: str):
    guild_id = ctx.guild.id
    if guild_id not in initiative_data or len(initiative_data[guild_id]) == 0:
        await ctx.respond("❌ Список инициативы пуст.")
        return

    new_list = [char for char in initiative_data[guild_id] if char["name"] != имя]
    if len(new_list) == len(initiative_data[guild_id]):
        await ctx.respond(f"❌ Персонаж **{имя}** не найден.")
    else:
        initiative_data[guild_id] = new_list
        await ctx.respond(f"✅ Персонаж **{имя}** удален.")


@bot.slash_command(name="показать_инициативу", description="Показывает текущий список инициативы")
async def показать_инициативу(ctx: discord.ApplicationContext):
    guild_id = ctx.guild.id
    if guild_id not in initiative_data or len(initiative_data[guild_id]) == 0:
        await ctx.respond("❌ Список инициативы пуст.")
        return

    # Формируем сообщение с порядком от меньшего к большему
    response = "**Текущая инициатива (от меньшего к большему):**\n"
    for idx, char in enumerate(initiative_data[guild_id], 1):
        response += (
            f"{idx}. **{char['name']}**: {char['initiative']}\n "
        )
    await ctx.respond(response)


@bot.slash_command(name="обнулить_инициативу", description="Полностью очищает список инициативы")
async def обнулить_инициативу(ctx: discord.ApplicationContext):
    guild_id = ctx.guild.id
    if guild_id in initiative_data:
        del initiative_data[guild_id]
    await ctx.respond("✅ Список инициативы очищен.")


@bot.slash_command(name="бросок_инициативы", description="Перебрасывает инициативу для всех персонажей")
async def бросок_инициативы(ctx: discord.ApplicationContext):
    guild_id = ctx.guild.id
    if guild_id not in initiative_data or len(initiative_data[guild_id]) == 0:
        await ctx.respond("❌ Список инициативы пуст.")
        return

    # Перебрасываем инициативу для каждого персонажа
    for char in initiative_data[guild_id]:
        roll = random.randint(1, 10)
        char["initiative"] = char["dex_wits"] + roll

    # Сортируем по новым значениям
    initiative_data[guild_id].sort(key=lambda x: (x["initiative"], -x["dex_wits"]))

    # Формируем ответ
    response = "**Новая инициатива после броска:**\n"
    for char in initiative_data[guild_id]:
        response += (
            f"🎲 **{char['name']}**: {char['initiative']} \n"
        )
    await ctx.respond(response)


# Получаем токен из переменной окружения
TOKEN = os.getenv("API_TOKEN")
if TOKEN is None:
    raise ValueError("Не задана переменная окружения API_TOKEN. Бот не может запуститься.")

bot.run(TOKEN)
