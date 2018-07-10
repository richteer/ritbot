def channelbind(channels):
	def decorator(func):
		async def wrapper(client, msg, args):
			if msg.channel.name not in channels:
				print("REJECTING CHANNEL: " + msg.channel.name)
				return
			return await func(client, msg, args)
		return wrapper
	return decorator
