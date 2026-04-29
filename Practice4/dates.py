import datetime

# 1) Subtract five days from current date
today = datetime.date.today()
five_days_ago = today - datetime.timedelta(days=5)
print("Today:", today)
print("5 days ago:", five_days_ago)


# 2) Print yesterday, today, tomorrow
yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)
print("Yesterday:", yesterday)
print("Today:", today)
print("Tomorrow:", tomorrow)


# 3) Drop microseconds from datetime
now_dt = datetime.datetime.now()
no_microseconds = now_dt.replace(microsecond=0)
print("With Microseconds - ", now_dt)
print("Without Microsecond - ", no_microseconds)


# 4) Calculate two date difference in seconds
dt1 = datetime.datetime(2026, 2, 26, 10, 0, 0)
dt2 = datetime.datetime(2026, 2, 27, 13, 30, 0)
diff_seconds = (dt2 - dt1).total_seconds()
print("Datetime 1:", dt1)
print("Datetime 2:", dt2)
print("Difference in seconds:", diff_seconds)   