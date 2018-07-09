possible_roles = [
	"chronomancer"
]


def getroles(user):
	u = users.get(str(user))
	if not u:
		return

	ls = u.get("roles", [])

	ret = ""
	for r in ls:
		ret += " :{}:".format(r)

	return ret


async def _roles(msg, arg):
	u = users.get(str(msg.author))
	if not u:
		u = {}
		users[str(msg.author)] = u

	s = set(u.get("roles", []))

	for a in arg:
		if a.lower() in possible_roles:
			s.add(a.lower().capitalize())
	u["roles"] = list(s)
	users[str(msg.author)] = u

	with open("users.json", "w") as f:
		f.write(json.dumps(users, indent=4))
