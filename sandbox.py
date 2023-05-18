import time
from datetime import datetime

millis = time.time()
date = datetime.fromtimestamp(millis)

print((date.second + (date.microsecond / 1000000)))