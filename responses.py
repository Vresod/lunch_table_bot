import os
import pathlib
from typing import Literal

import discord

DIRECTORY = "./responses"

responses = {
	pathlib.Path(file).stem:f"{DIRECTORY}/{file}"
	for file in os.listdir(DIRECTORY)
}

@discord.app_commands.command(name="response",description="Precompiled responses that can be triggered instantly")
async def _response(interaction: discord.Interaction, chosen_response: Literal[tuple(responses.keys())]): # don't worry about that not-literal literal it's fine
	await interaction.response.send_mesage(f"Sending {chosen_response}")


if __name__ == "__main__":
	print(responses)
