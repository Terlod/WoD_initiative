import discord
from discord.ext import commands
from discord import app_commands
import random
import os

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Хранение данных инициативы для каждого сервера
initiative_data = {}

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")
    # Синхронизация слэш-команд с Discord
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")

# === Слэш-команды через CommandTree ===

@bot.tree.command(name="добавить_персонажа", description="Добавляет персонажа с указанием ловкости+смекалки")
@app_commands.describe(имя="Имя персонажа", ловкость_смекалка="Сумма Ловкости и Смекалки")
async def добавить_персонажа(interaction: discord.Interaction, имя: str, ловкость_смекалка: int):
    guild_id = interaction.guild_id
    if guild_id not in initiative_data:
        initiative_data[guild_id] = []

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
            "initiative": 0
        })

    await interaction.response.send_message(f"✅ Персонаж **{имя}** добавлен/обновлен.")


@bot.tree.command(name="удалить_инициативу", description="Удаляет персонажа из списка")
@app_commands.describe(имя="Имя персонажа")
async def удалить_инициативу(interaction: discord.Interaction, имя: str):
    guild_id = interaction.guild_id
    if guild_id not in initiative_data or len(initiative_data[guild_id]) == 0:
        await interaction.response.send_message("❌ Список инициативы пуст.")
        return

    new_list = [char for char in initiative_data[guild_id] if char["name"] != имя]
    if len(new_list) == len(initiative_data[guild_id]):
        await interaction.response.send_message(f"❌ Персонаж **{имя}** не найден.")
    else:
        initiative_data[guild_id] = new_list
        await interaction.response.send_message(f"✅ Персонаж **{имя}** удален.")


@bot.tree.command(name="показать_инициативу", description="Показывает текущий список инициативы")
async def показать_инициативу(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    if guild_id not in initiative_data or len(initiative_data[guild_id]) == 0:
        await interaction.response.send_message("❌ Список инициативы пуст.")
        return

    response = "**Текущая инициатива (от меньшего к большему):**\n"
    for idx, char in enumerate(initiative_data[guild_id], 1):
        response += f"{idx}. **{char['name']}**: {char['initiative']}\n"
    await interaction.response.send_message(response)


@bot.tree.command(name="обнулить_инициативу", description="Полностью очищает список инициативы")
async def обнулить_инициативу(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    if guild_id in initiative_data:
        del initiative_data[guild_id]
    await interaction.response.send_message("✅ Список инициативы очищен.")


@bot.tree.command(name="бросок_инициативы", description="Перебрасывает инициативу для всех персонажей")
async def бросок_инициативы(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    if guild_id not in initiative_data or len(initiative_data[guild_id]) == 0:
        await interaction.response.send_message("❌ Список инициативы пуст.")
        return

    for char in initiative_data[guild_id]:
        roll = random.randint(1, 10)
        char["initiative"] = char["dex_wits"] + roll

    initiative_data[guild_id].sort(key=lambda x: (x["initiative"], -x["dex_wits"]))

    response = "**Новая инициатива после броска:**\n"
    for char in initiative_data[guild_id]:
        response += f"🎲 **{char['name']}**: {char['initiative']}\n"
    await interaction.response.send_message(response)


# Запуск
TOKEN = os.getenv("API_TOKEN")
if TOKEN is None:
    raise ValueError("Не задана переменная окружения API_TOKEN.")
bot.run(TOKEN)
