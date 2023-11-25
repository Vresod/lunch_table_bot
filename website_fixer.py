import re

import discord

WEBSITES_TO_FIX = { # should be good to stay as is, could potentially be updated later; on the left is regex strings so escape `.`
	"twitter.com": "fxtwitter.com",
	"x.com": "fixupx.com",
	"instagram.com": "ddinstagram.com",
	"reddit.com": "rxyddit.com",
	"tiktok.com": "tiktxk.com",
	# "clips.twitch.tv": "clips.txitch.tv",
	# "twitch.tv/clips": "txitch.tv/clips"
}

website_fixer_regex = re.compile(
	rf"https?://(?:www.)?({'|'.join(WEBSITES_TO_FIX.keys())})/(\S*)"
	.replace(".","\.") # auto replace "." with "\."
)

def get_and_convert_links(string:str):
	matches = website_fixer_regex.findall(string)
	links = ""
	for match in matches:
		links += f"https://{WEBSITES_TO_FIX[match[0]]}/{match[1]}\n"
	return links

async def handle_website(message:discord.Message):
	await message.channel.send(get_and_convert_links(message.content))

def __main__():
	print(get_and_convert_links("https://www.tiktok.com/t/ZPRvHE311/")) # the actual test case is 20 random tweets off my timeline but I'm not putting that in the code lmao

if __name__ == "__main__":
	__main__()
