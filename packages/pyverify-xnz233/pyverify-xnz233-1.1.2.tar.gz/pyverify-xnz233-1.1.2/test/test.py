import pyverify
pyverify.gui_verify()
for i in range(1, 10):
    for m in range(1, i + 1):
        print(f"{i} * {m} = {i*m}", end='  ')
    print()
