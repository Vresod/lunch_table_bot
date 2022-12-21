import logging
import discord

message_totals = {}

async def update_message_totals(client:discord.Client,guild:discord.Guild,message_total_channel:discord.abc.Messageable) -> None:
	"""
	updates the message totals channel
	:param client: the client to use to update the totals
	:param guild: the guild to update the totals of
	:param message_total_channel: the channel to pots the totals into
	:return:
	"""
	await get_message_totals(guild)
	await send_message_totals(client, message_total_channel)


async def send_message_totals(client:discord.Client, message_total_channel:discord.abc.Messageable) -> None:
	"""
	:param client:
	:param message_total_channel:
	:return:
	"""
	if not message_totals:
		return
	try:
		total_msg = [msg async for msg in message_total_channel.history(limit=None) if msg.author == client.user][0]
	except IndexError:
		total_msg = await message_total_channel.send("fart", allowed_mentions=discord.AllowedMentions.none())
	msg_content = "```\n"
	totals_sorted = sort_dict(message_totals)
	users:dict[discord.User] = {user_id:await client.fetch_user(user_id) for user_id in totals_sorted}
	# these are the worst 2 lines in the entire codebase and I wish there was a better way to do it
	longest_name = len(users[max(users,key=lambda x:len(users[x].name))].name)
	longest_id = len(str(users[max(users,key=lambda x:len(str(users[x].id)))].id))
	for entry in totals_sorted.items():
		msg_content += f"{(await client.fetch_user(entry[0])).name.ljust(longest_name)} <{str(entry[0]).ljust(longest_id)}> - {entry[1]}\n"
	msg_content += "```"
	await total_msg.edit(content=msg_content, allowed_mentions=discord.AllowedMentions.none())

def sort_dict(dictionary:dict) -> dict:
	"""
	sorts a dict by value, large to small
	:param dictionary: the dict that is to be sorted
	:return: the sorted dict
	"""
	return {k: dictionary[k] for k in sorted(dictionary, key=lambda x: dictionary[x], reverse=True)}

async def get_message_totals(guild:discord.Guild) -> None:
	"""
	gets the message totals and puts them in the `message_totals` variable
	:param guild: the guild to get the totals of
	:return:
	"""
	channels = get_talkable_channels(guild)
	for index,channel in enumerate(channels):
		logging.debug(f"starting {channel}, id:{channel.id}")
		# if channel.id == 1052616491721310338: continue
		# if index > 1: break # debug statement to improve speed of testing
		async for message in channel.history(limit=None):
			logging.debug(f"message in {channel}, id:{message.id}")
			if not count_author(message.author):
				continue
			if not message_totals.get(message.author.id):
				message_totals[message.author.id] = 0
			message_totals[message.author.id] += 1
	logging.debug(message_totals)

def count_author(author:discord.Member) -> bool:
	"""
	returns if the member should be counted
	:param author:
	:return bool:
	"""
	return not (author.bot and author.discriminator == "0000")

def get_talkable_channels(guild:discord.Guild):
	"""
	gets every channel and thread in a guild that can contain messages
	:param guild: the guild to get the talkable channels of
	:type guild: discord.Guild
	:return: a generator containing all the threads and channels a guild contains
	"""
	# TODO: use `discord.abc.Messageable` somehow
	for channel in guild.channels:
		channel_types = discord.ChannelType
		if channel.type in [channel_types.category, channel_types.stage_voice]:  # oh yes baaaaaaaby guard statements B)
			continue
		if channel.type in [channel_types.forum, channel_types.text]: # get threads of forums and
			for thread in channel.threads:
				yield thread
		if channel.type != channel_types.forum:
			yield channel
