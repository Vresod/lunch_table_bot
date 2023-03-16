import typing
from collections import namedtuple
import discord

from audit_logs import handle_action
from maps import content_filter_map, verification_level_map, g_s, word_map, kick_ban_verb_map

formattable_text = "Old {thing}: {old}\nNew {thing}: {new}\n"
formattable_text_only_old = "Old {thing}: {old}\n"
formattable_text_only_new = "New {thing}: {new}\n"

def formatted_text(*, thing: str, changes: discord.AuditLogChanges, getter: typing.Callable[[discord.AuditLogDiff], str]) -> str:
	"""
	:param thing: the type of thing to format for
	:param changes: the changes to format for
	:param getter: a function that gets the wanted parameter from the AuditLogDiff
	:return str:
	"""
	old = list(changes.before)
	new = list(changes.after)
	final = ""
	for before,after in zip(old,new):
		if before[1]:
			final += formattable_text_only_old.format(thing=thing,old=getter(before[1]))
		if after[1]:
			print(thing,getter,after)
			final += formattable_text_only_new.format(thing=thing,new=getter(after[1]))
	return final


format_string = namedtuple('format_string', ['thing', 'getter'])

# TODO: handle all of these goddamn actions:
# overwrite_create
# overwrite_update
# overwrite_delete
# member_prune
# member_update
# member_move
# member_disconnect
# role_create
# role_update
# role_delete
# invite_create
# invite_update
# invite_delete
# webhook_create
# webhook_update
# webhook_delete
# message_delete
# message_bulk_delete
# message_pin
# message_unpin
# integration_create
# integration_update
# integration_delete
# stage_instance_create
# stage_instance_update
# stage_instance_delete
# scheduled_event_create
# scheduled_event_update
# scheduled_event_delete
# thread_create
# thread_update
# thread_delete
# app_command_permission_update
# automod_rule_create
# automod_rule_update
# automod_rule_delete
# automod_block_message
# automod_flag_message
# automod_timeout_member

# DONE:
# guild_update
# member_role_update
# channel_create
# channel_update*
# channel_delete
# emoji_create
# emoji_update
# emoji_delete
# kick
# ban
# unban
# bot_add
# sticker_create
# sticker_update
# sticker_delete

guild_updates_map = {
	'icon': format_string(thing="icon url", getter=g_s.asset),
	'name': format_string(thing="name", getter=g_s.str),
	'afk_channel': format_string(thing="AFK channel", getter=g_s.channel),
	'system_channel': format_string(thing="system channel", getter=g_s.channel),
	'afk_timeout': format_string(thing="AFK timeout", getter=g_s.int),
	'default_notifications': format_string(thing="notification level", getter=lambda x: "All messages" if x == discord.NotificationLevel.all_messages else "Only mentions"),
	'explicit_content_filter': format_string(thing="explicit content filter", getter=lambda x: content_filter_map[x]),
	'mfa_level': format_string(thing="MFA requirement", getter=lambda x: "Disabled" if x == discord.MFALevel.disabled else "Enabled"),
	'owner': format_string(thing="owner", getter=g_s.member),
	'splash': format_string(thing="invite splash URL", getter=g_s.asset),
	'discovery_splash': format_string(thing="discovery splash URL", getter=g_s.asset),
	'banner': format_string(thing="banner URL", getter=g_s.asset),
	'vanity_url_code': format_string(thing="vanity URL code", getter=g_s.str),
	'description': format_string(thing="description", getter=g_s.str),
	'preferred_locale': format_string(thing="preferred locale", getter=g_s.str_able),
	'prune_delete_days': format_string(thing="days between prunes", getter=g_s.int),
	'public_updates_channel': format_string(thing="public updates channel", getter=g_s.channel),
	'rules_channel': format_string(thing="rules channel", getter=g_s.channel),
	'verification_level': format_string(thing="verification level", getter=lambda x: verification_level_map[x]),
	'widget_channel': format_string(thing="widget channel", getter=g_s.channel),
	'widget_enabled': format_string(thing="widget status", getter=g_s.str_able),
}

channel_updates_map = {
	'name': format_string(thing="name",getter=g_s.str),
	'type': format_string(thing="channel type", getter=lambda x: str(x).replace("_"," ")),
	'position': format_string(thing="position in the list",getter=g_s.int),
	'overwrites': format_string(thing="permission overwrites",getter=g_s.str), # TODO: WRITE CHANNEL OVERWRITES STRINGIFIER
	'topic': format_string(thing="topic",getter=g_s.str),
	'bitrate': format_string(thing="bitrate",getter=g_s.int),
	'rtc_region': format_string(thing="region", getter=g_s.str),
	'video_quality_mode': format_string(thing="video quality mode", getter=g_s.str_able),
	'default_auto_archive_duration': format_string(thing="thread auto archive duration", getter=g_s.int),
	'user_limit': format_string(thing="user limit",getter=g_s.int)
}

sticker_updates_map = {
	'name': format_string(thing="name",getter=g_s.str),
	'emoji': format_string(thing="emoji", getter=g_s.str),
	'type': format_string(thing="name", getter=lambda x: "standard" if x == discord.StickerType.standard else "server"),
	'format_type': format_string(thing="format", getter=lambda x: x.name),
	'description': format_string(thing="description", getter=g_s.str),
	'available': format_string(thing="available", getter=g_s.str_able),
}

webhook_updates_map = {
	'channel': format_string(thing="channel",getter=g_s.channel),
	'name': format_string(thing="name",getter=g_s.str),
	'avatar': format_string(thing="avatar",getter=g_s.asset),
	'application_id': format_string(thing="application id",getter=g_s.str)
}

@handle_action()
async def guild_update(entry: discord.AuditLogEntry):
	embed = discord.Embed(title=f"{entry.user} modified the server")
	embed.description = ""
	for old, new in zip(entry.before, entry.after):
		formatter = guild_updates_map[old[0]]
		embed.description += formatted_text(thing=formatter.thing, changes=entry.changes, getter=formatter.getter)
	return embed


@handle_action()
async def member_role_update(entry: discord.AuditLogEntry):
	embed = discord.Embed(title=f"{entry.user} updated the roles of {entry.target}")
	embed.description = ""
	for after_role in entry.after.roles:
		if after_role not in entry.before.roles:
			embed.description += f"+ {after_role.mention}\n"
	for before_role in entry.before.roles:
		if before_role not in entry.after.roles:
			embed.description += f"- {before_role.mention}\n"
	return embed

@handle_action()
async def channel_all(entry: discord.AuditLogEntry):
	embed = discord.Embed(title=f"{entry.user} {word_map[entry.category]} the channel {entry.target} ({entry.target.id})")
	embed.description = ""
	if entry.category != discord.AuditLogActionCategory.update:
		embed.description += f"Type: {str(entry.target.type).replace('_',' ')}"
		return embed
	for old, new in zip(entry.before, entry.after):
		formatter = channel_updates_map[old[0]]
		embed.description += formatted_text(thing=formatter.thing, changes=entry.changes, getter=formatter.getter)
	return embed

@handle_action()
async def emoji_all(entry: discord.AuditLogEntry):
	embed = discord.Embed(title=f"{entry.user} {word_map[entry.category]} an emoji called {entry.target.name} ({entry.target.id})",description="\n")
	return embed

@handle_action(handles=[discord.AuditLogAction.kick,discord.AuditLogAction.ban,discord.AuditLogAction.unban])
async def kick_ban_unban(entry: discord.AuditLogEntry):
	verb = kick_ban_verb_map[entry.action]
	embed = discord.Embed(title=f"{entry.user} {verb} {entry.target} ({entry.target.id})", description="\n")
	return embed

@handle_action()
async def bot_add(entry:discord.AuditLogEntry):
	embed = discord.Embed(title=f"{entry.user} added a bot {entry.target} ({entry.target.id})", description="\n")
	return embed

@handle_action()
async def sticker_all(entry:discord.AuditLogEntry):
	embed = discord.Embed(title=f"{entry.user} {word_map[entry.category]} a sticker called {entry.target.name} ({entry.target.id})")
	embed.description = ""
	# if entry.category != discord.AuditLogActionCategory.update:
	# 	embed.description += f"Type: {str(entry.target.type).replace('_',' ')}"
	# 	return embed
	for old, new in zip(entry.before, entry.after):
		formatter = sticker_updates_map[old[0]]
		embed.description += formatted_text(thing=formatter.thing, changes=entry.changes, getter=formatter.getter)
	return embed

# @handle_action()
# async def webhook_all(entry:discord.AuditLogEntry):
# 	embed = discord.Embed(title=f"{entry.user} {word_map[entry.category]} a webhook ({entry.target.id})")
# 	embed.description = ""
# 	# if entry.category != discord.AuditLogActionCategory.update:
# 	# 	embed.description += f"Type: {str(entry.target.type).replace('_',' ')}"
# 	# 	return embed
# 	for old, new in zip(entry.before, entry.after):
# 		formatter = webhook_updates_map[old[0]]
# 		embed.description += formatted_text(thing=formatter.thing, changes=entry.changes, getter=formatter.getter)
# 	return embed
