import typing

import discord
from discord.ext import tasks

audit_log_handlers:dict[discord.AuditLogAction,list] = {}
@tasks.loop(seconds=30)
async def check_for_new_logs(audit_guild:discord.Guild,audit_channel:discord.abc.Messageable):
	with open("latest_log.txt","r") as logfile: latest_log_id = int(logfile.read())
	embed = discord.Embed()
	entries = []
	async for entry in audit_guild.audit_logs(after=discord.Object(id=latest_log_id),oldest_first=True):
		new_latest_log_id = entry.id
		print(entry)
		entries.append(entry)
	# with open("latest_log.txt","w") as logfile: logfile.write(str(latest_log_id))
	print("a")

def handle_action(handles:list[discord.AuditLogAction] = None) -> typing.Callable:
	"""
	A decorater that sets a function to run when an audit log entry is being handled
	:param handles: the list of audit log entries to handle
	:return:
	"""
	if handles is None: handles = []

	def decorator(func:typing.Callable) -> typing.Callable:
		if not handles: handles.append(discord.AuditLogAction[func.__name__])
		for i in handles:
			if not audit_log_handlers.get(i): audit_log_handlers[i] = []
			audit_log_handlers[i].append(func)
		return func
	return decorator

