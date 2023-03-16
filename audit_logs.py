import typing
import discord

from discord.ext import tasks
from maps import word_map

audit_log_handlers:dict[discord.AuditLogAction,typing.Awaitable[discord.Embed]] = {} # a little confusing but let the IDE figure it out
@tasks.loop(seconds=30)
async def check_for_new_logs(audit_guild:discord.Guild,audit_channel:discord.abc.Messageable,debugging:bool = False):
	with open("latest_log.txt","r") as logfile: latest_log_id = int(logfile.read())
	async for entry in audit_guild.audit_logs(after=discord.Object(id=latest_log_id),oldest_first=True):
		new_latest_log_id = entry.id
		await create_embed_for_entry(entry)
		# if debugging: break
	# with open("latest_log.txt","w") as logfile: logfile.write(str(latest_log_id))

async def create_embed_for_entry(audit_log_entry:discord.AuditLogEntry):
	try:
		embed = await audit_log_handlers.get(audit_log_entry.action,not_implemented)(audit_log_entry)
	except Exception as e:
		# embed = await call_errored(audit_log_entry,e)
		raise e
	# embed = await (audit_log_handlers[discord.AuditLogAction.guild_update])(audit_log_entry)
	if not embed.title:
		embed.title = f"{audit_log_entry.user} {word_map[audit_log_entry.category]} a {type(audit_log_entry.target).__qualname__.lower()}"
	if not embed.description and not embed.fields:
		embed.description = "No description implemented. Go yell at vresod to fix this if it matters so much to you"
	if not embed.author:
		embed.set_author(name=str(audit_log_entry.user),icon_url=audit_log_entry.user.avatar.url)
	if not embed.footer:
		embed.set_footer(text=f"Audit entry id: {audit_log_entry.id}. Why? {audit_log_entry.reason or 'No reason provided'}")
	return embed
def handle_action(handles:list[discord.AuditLogAction] = None) -> typing.Callable:
	"""
	A decorater that sets a coroutine to run when an audit log entry is being handled
	:param handles: the list of audit log entries to handle
	:return:
	The coroutine should return an embed, which will be used and filled with a basic template if need be.
	"""
	if handles is None: handles = [] # lists are mutable, even when created at function creation

	def decorator(coro:typing.Callable) -> typing.Callable:
		if not handles:
			if coro.__name__.endswith("_all"):
				action = coro.__name__.replace("_all","")
				handles.append(discord.AuditLogAction[f"{action}_create"])
				handles.append(discord.AuditLogAction[f"{action}_update"])
				handles.append(discord.AuditLogAction[f"{action}_delete"])
			else:
				handles.append(discord.AuditLogAction[coro.__name__])
		for i in handles:
			audit_log_handlers[i] = coro
		return coro
	return decorator

async def not_implemented(entry:discord.AuditLogEntry):
	return discord.Embed(description="This action has not been implemented yet. Go yell at vresod to implement this if it means so much to you")

async def call_errored(entry:discord.AuditLogEntry,exception:Exception):
	return discord.Embed(description=f"""This action *is* implemented, but it errored, so something might've went wrong? God knows! Go yell at vresod to fix it
Details: ```
Type: {entry.action}
Before: {entry.before}
After: {entry.after}
Extra: {entry.extra}
Reason: {entry.reason}
Exception: {type(exception).__qualname__}: {exception}""")