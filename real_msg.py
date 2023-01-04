import discord

async def handle_real(message:discord.Message,real_channel:discord.abc.Messageable):
	"""
	Deals with messages that are real
	:param message: the message to call real
	:param real_channel: the channel to repost the real message to
	:return:
	"""
	channel = message.channel
	real_msg = hasattr(message.reference,"resolved") and message.reference.resolved
	if not real_msg:
		real_msg = [msg async for msg in channel.history(before=discord.Object(message.id), limit=1)][0]
	# await channel.send(f"real {real_msg.jump_url}")
	embed = generate_pin_embed(real_msg)
	await real_channel.send(embed=embed,content="real")
	await channel.send("real")

def generate_pin_embed(message:discord.Message): # stolen code from Vresod/Starboard
	"""
	Makes an embed for a message
	:param message: the message to generate a pin for
	:return:
	"""
	embed = discord.Embed(
		title=f"#{message.channel}",
		description=message.content,
		url=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}"
	)
	embed.set_author(name=message.author.display_name, icon_url=str(message.author.avatar))
	# embed.set_footer(text=f"[Jump]({message.jump_url})")
	embed.add_field(name="Original Message:", value=f"[Jump]({message.jump_url})")
	if len(message.attachments) > 0: embed.set_image(url=message.attachments[0].url)
	return embed
