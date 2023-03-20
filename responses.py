import os
import pathlib
from typing import Literal
import json

import discord

DIRECTORY = "./responses"

responses = {
	pathlib.Path(file).stem: discord.File(fp=f"{DIRECTORY}/{file}")
	for file in os.listdir(DIRECTORY)
}

del responses['text_and_embeds']

with open(f"{DIRECTORY}/text_and_embeds.json","r") as taefile: tae = json.load(taefile)
for key, response in tae.items():
	if isinstance(response,str):
		responses[key] = response
	elif isinstance(response,dict):
		response:dict
		embed = discord.Embed( title=response['title'], description=response['description'], )
		embed.set_footer(text=response.get('footer'))
		embed.set_author(name=response.get('author'))
		if fields := response.get('fields'):
			for field in fields:
				embed.add_field(
					name=field['name'],
					value=field['value'],
					inline=field.get('inline',True)
				)
		responses[key] = embed

@discord.app_commands.command(name="response",description="Precompiled responses that can be triggered instantly")
@discord.app_commands.rename(chosen_response="response_to_post")
async def _response(interaction: discord.Interaction, chosen_response: Literal[tuple(responses.keys())]): # don't worry about that not-literal literal it's fine
	if isinstance(response := responses[chosen_response],discord.File):
		await interaction.response.send_message(file=response)
	elif isinstance(response,str):
		await interaction.response.send_message(content=response)
	elif isinstance(response,discord.Embed):
		await interaction.response.send_message(embed=response)
	else:
		raise ValueError("given response is not one of [discord.File, str, discord.Embed]")

if __name__ == "__main__":
	print(responses)
