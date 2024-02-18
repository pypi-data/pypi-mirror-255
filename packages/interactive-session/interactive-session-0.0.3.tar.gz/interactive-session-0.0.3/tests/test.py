import interactive_session as m
assert m.add(1, 2) == 3
assert m.subtract(1, 2) == -1

session = m.InteractiveSession("bash", "exit")
print(session.execute("echo hello"))
session.close()
