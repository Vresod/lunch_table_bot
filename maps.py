import discord

content_filter_map = {
	discord.ContentFilter.disabled: "Content filter disabled",
	discord.ContentFilter.no_role:  "Content filter for roleless members",
	discord.ContentFilter.all_members: "Content filter for everyone"
}

word_map = {
	discord.AuditLogActionCategory.create: "created",
	discord.AuditLogActionCategory.delete: "deleted",
	discord.AuditLogActionCategory.update: "updated",
	None: "modified"
}

verification_level_map = {
	discord.VerificationLevel.none: "No verification",
	discord.VerificationLevel.low: "Low verfification; verified email required",
	discord.VerificationLevel.medium: "Medium verfification; verified email + more than 5 minute old account required",
	discord.VerificationLevel.high: "High verfification; verified email + more than 5 minute old account + 10 minutes in the server required",
	discord.VerificationLevel.highest: "Highest verfification; verified phone required",
}

kick_ban_verb_map = {
	discord.AuditLogAction.ban: "banned",
	discord.AuditLogAction.kick: "kicked",
	discord.AuditLogAction.unban: "unbanned",
}

class getter_shortcuts:
	# I am basically using this as a DotDict. if your IDE gives you errors about this just ignore them it's fine, nobody is doing `g_s.str()` anyway
	"""
	lookup table for shortcuts
	"""
	def str(x): return x
	def str_able(x): return str(x)
	def asset(x): return x.url if hasattr(x,"url") else str(x.id) # anything worth its salt should have an id attribute
	def mentionable(x): return x.mention if hasattr(x,"mention") else str(x.id) # ^

	user = mentionable
	member = mentionable
	channel = mentionable
	role = mentionable
	int = str_able
	float = str_able


g_s = getter_shortcuts
