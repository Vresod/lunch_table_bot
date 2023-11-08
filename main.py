import logging
import discord
from discord import app_commands
from discord.ext import tasks
import sys

import audit_logs
from message_totals import update_message_totals, send_message_totals, handle_totals_update, count_author
from real_msg import handle_real
import responses

MY_GUILD                  = discord.Object(id=1043170926725955696)  # replace with your guild id
REAL_ID                   = 1044246059284701324                     # replace with channel id of real channel
MESSAGE_TOTALS_CHANNEL_ID = 1053539851292647584                     # replace with channel id of message totals channel
STARBOARD_CHANNEL         = 1043262188606996620                     # replace with channel id of starboard channel
PIN_EMOJIS                = {"💀",}                                 # replace with emojis that should set off the starboard code

class MyClient(discord.Client):
	def __init__(self):
		intents = discord.Intents.default()
		intents.message_content = True
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


client = MyClient()
discord.utils.setup_logging(level=logging.DEBUG)
debugging = hasattr(sys, 'gettrace') and sys.gettrace() is not None
last_message:discord.Message = None
# audit_guild:discord.Guild = None
# audit_channel:discord.TextChannel = None

# this function should be somewhere else but I'll worry about that later (it will never get moved)
async def pin_message(message: discord.Message, starboard: discord.TextChannel):
	embed = discord.Embed(
		title=f"#{message.channel}",
		description=message.content,
		url=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}"
	)
	embed.set_author(name=message.author.display_name, icon_url=str(message.author.avatar))
	# embed.set_footer(text=f"[Jump]({message.jump_url})")
	embed.add_field(name="Original Message:", value=f"[Jump]({message.jump_url})")
	if len(message.attachments) > 0:
		embed.set_image(url=message.attachments[0].url)
	await starboard.send(embed=embed, content="", allowed_mentions=discord.AllowedMentions.none())

@client.event
async def on_ready():
	logging.info(f'Logged in as {client.user} (ID: {client.user.id}, INVITE: "https://discord.com/outh2/authorize?client_id={client.user.id}&permissions=128&scope=bot%20applications.commands")')
	# global audit_guild, audit_channel
	# audit_guild = client.get_guild(1043170926725955696)
	# audit_channel = client.get_channel(1043713945015439402)
	try:
		open("latest_log.txt","x")
		open("latest_log.txt","w").write("0")
	except FileExistsError: pass
	#await audit_logs.check_for_new_logs.start()
	guild = client.get_guild(MY_GUILD.id)
	totals_channel = client.get_channel(MESSAGE_TOTALS_CHANNEL_ID)
	logging.info("Begininning message count")
	if not debugging: #omegalul
		await update_message_totals(client,guild,totals_channel)
	logging.info("Message count complete, updating count in discord...")
	await send_message_totals.start(client,totals_channel)
	logging.info("Count updated")

@client.event
async def on_message(message:discord.Message):
	# TODO: finish #real feature
	if message.guild.id != MY_GUILD.id: # technically does nothing in the actual bot but good to have regardless
		return
	if count_author(message.author):
		await handle_totals_update(message)
	if message.content.startswith(f"<#{REAL_ID}>"):
		await handle_real(message,client.get_channel(REAL_ID))
	global last_message
	message_matches = last_message is not None and last_message.content == message.content and last_message.channel == message.channel
	if message_matches and message.author != client.user and message.content: await message.channel.send(message.content)
	last_message = message

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
	if payload.emoji.name not in PIN_EMOJIS:
		return
	message: discord.Message = await (client.get_channel(payload.channel_id).get_partial_message(payload.message_id)).fetch()
	starboard: discord.TextChannel = client.get_channel(STARBOARD_CHANNEL)
	for reaction in message.reactions:
		if reaction.count > 1:
			return
	await pin_message(message, starboard)

# @client.tree.command()
# async def hello(interaction: discord.Interaction):
# 	"""Says hello!"""
# 	await interaction.response.send_message(f'Hi, {interaction.user.mention}')
#
@client.tree.command()
async def echo(interaction: discord.Interaction, content:str):
	"""Possess PDB!"""
	await interaction.channel.send(content)
	await interaction.response.send_message(f'Echoed',ephemeral=True)

send_message_totals = tasks.loop(minutes=5)(send_message_totals)

def main():
	with open("tokenfile","r") as tokenfile: token = tokenfile.read()
	client.tree.add_command(responses._response)
	client.run(token)


if __name__ == "__main__":
	main()
