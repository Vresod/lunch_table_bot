import discord
from discord import app_commands
from discord.ext import tasks

MY_GUILD = discord.Object(id=1043170926725955696) # replace with your guild id

class MyClient(discord.Client):
	def __init__(self, *, intents: discord.Intents):
		super().__init__(intents=intents)
		# A CommandTree is a special type that holds all the application command
		# state required to make it work. This is a separate class because it
		# allows all the extra state to be opt-in.
		# Whenever you want to work with application commands, your tree is used
		# to store and work with them.
		# Note: When using commands.Bot instead of discord.Client, the bot will
		# maintain its own tree instead.
		self.tree = app_commands.CommandTree(self)

	# In this basic example, we just synchronize the app commands to one guild.
	# Instead of specifying a guild to every command, we copy over our global commands instead.
	# By doing so, we don't have to wait up to an hour until they are shown to the end-user.
	async def setup_hook(self):
		# This copies the global commands over to your guild.
		self.tree.copy_global_to(guild=MY_GUILD)
		await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)
# audit_guild:discord.Guild = None
# audit_channel:discord.TextChannel = None

@client.event
async def on_ready():
	print(f'Logged in as {client.user} (ID: {client.user.id}, INVITE: "https://discord.com/outh2/authorize?client_id={client.user.id}&permissions=128&scope=bot%20applications.commands")')
	# global audit_guild, audit_channel
	# audit_guild = client.get_guild(1043170926725955696)
	# audit_channel = client.get_channel(1043713945015439402)
	try:
		open("latest_log.txt","x")
		open("latest_log.txt","w").write("0")
	except FileExistsError: pass
	# await check_for_new_logs()
	await update_message_totals.start()

@client.tree.command()
async def hello(interaction: discord.Interaction):
	"""Says hello!"""
	await interaction.response.send_message(f'Hi, {interaction.user.mention}')

@tasks.loop(minutes=5)
async def update_message_totals():
	message_total_channel = client.get_channel(1053539851292647584)
	guild = client.get_guild(MY_GUILD.id)
	members = guild.members


# @tasks.loop(seconds=30)
# async def check_for_new_logs():
# 	global audit_guild, audit_channel
# 	with open("latest_log.txt","r") as logfile: latest_log_id = int(logfile.read())
# 	embed = discord.Embed()
# 	entries = []
# 	async for entry in audit_guild.audit_logs(after=discord.Object(id=latest_log_id),oldest_first=True):
# 		new_latest_log_id = entry.id
# 		print(entry)
# 		entries.append(entry)
# 	# with open("latest_log.txt","w") as logfile: logfile.write(str(latest_log_id))
# 	print("a")

client.run("Nzc3NzAzMDYwMzU2ODU3ODk3.GRqcYo.zJAF8TbtftAAEewHwFwsR7VOF1KFIHynXg1fME")