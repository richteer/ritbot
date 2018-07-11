import discord
from ritutils import channelbind

# This might not be needed?
config = {}

@channelbind(["bot"])
async def _active(client, msg, args):
	if discord.utils.get(msg.server.roles, name="Guild Member") in msg.author.roles:
		role = discord.utils.get(msg.server.roles, name="Raider")
	else:
		role = discord.utils.get(msg.server.roles, name="Non-Member Raider")

	if role in msg.author.roles:
		await client.remove_roles(msg.author, role)
		await client.send_message(msg.channel, "Role removed!")
	else:
		await client.add_roles(msg.author, role)
		await client.send_message(msg.channel, "Role set!")
