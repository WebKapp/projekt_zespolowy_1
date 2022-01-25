import os

os.system("ampy --port COM3 rm boot.py")
os.system("ampy --port COM3 put boot.py")
# os.system("ampy --port COM3 run boot.py")
print("Done")



# Message for future me: You've changed timeout=None in line 256 in pyboard.py (was 10).
# This might a issue if something doesn't work.
