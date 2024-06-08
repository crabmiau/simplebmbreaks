import subprocess as sp
import time as t
from discord_webhook import DiscordWebhook as dwh
import random as r
from datetime import datetime as dt, timedelta as td
from threading import Thread

exe = "" # Path to your Binmaster executable (string)
wh_url = "" # Discord Webhook URL (string)


active_time = 30 # Base time for active running (int, minutes)
break_time = 20 # Base time for breaks (int, minutes)
active_randomization = 12 # Randomization for active running time (int, minutes)
break_randomization = 12 # Randomization for break time (int, minutes)
warning_time = 5 # Time to warn before the end of break (int, minutes)



base_run_dur = active_time * 60
base_sleep_dur = break_time * 60
run_var = active_randomization * 60
sleep_var = break_randomization * 60
soontime = warning_time * 60

def randomdur(base, var):
    return base + r.randint(-var, var)

def webhook(msg):
    wh = dwh(url=wh_url, content=msg)
    wh.execute()

def formatdur(dur):
    mins = dur // 60
    secs = dur % 60
    return f"{mins} minutes and {secs} seconds"

def formatend(dur):
    endtime = dt.now() + td(seconds=dur)
    return endtime.strftime("%H:%M")

def read_output(proc):
    while True:
        try:
            output = proc.stdout.readline()
            if output == '' and proc.poll() is not None:
                break
            if output:
                print(output.strip())
        except UnicodeDecodeError:
            print("line unicode decode error, line skipped")
            continue

while True:
    rundur = randomdur(base_run_dur, run_var)
    sleepdur = randomdur(base_sleep_dur, sleep_var)
    run_end_time = formatend(rundur)
    start_msg = f"starting binmaster until {run_end_time} ({formatdur(rundur)})..."
    print(start_msg)
    webhook(start_msg)
    proc = sp.Popen([exe], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
    output_thread = Thread(target=read_output, args=(proc,))
    output_thread.start()
    t.sleep(rundur)
    stop_msg = f"stopping binmaster"
    print(stop_msg)
    webhook(stop_msg)
    proc.stdin.write("pause\n")
    proc.stdin.flush()
    proc.stdin.write("test\n")
    proc.stdin.flush()
    t.sleep(3)
    proc.terminate()
    output_thread.join()
    sleep_end_time = formatend(sleepdur)
    sleep_msg = f"taking a break until {sleep_end_time} ({formatdur(sleepdur)})..."
    print(sleep_msg)
    webhook(sleep_msg)
    t.sleep(sleepdur - soontime)
    soonmsg = f"continuing in {warning_time} minutes..."
    print(soonmsg)
    webhook(soonmsg)
    t.sleep(soontime)
