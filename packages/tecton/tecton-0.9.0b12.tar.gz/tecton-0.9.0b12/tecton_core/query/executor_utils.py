import math
import sys
import threading
import time
import typing


def detect_interactive_shell():
    try:
        import IPython
    except ImportError:
        return False

    return IPython.get_ipython() is not None


def display_timer(str_template: str, output: typing.IO = sys.stdout) -> typing.Callable[[], None]:
    start = time.time()
    finished = threading.Event()

    def fn():
        while True:
            if finished.is_set():
                return
            total_seconds = math.floor(time.time() - start)
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            output.write("\r")
            output.write(str_template.format(clock=f"{minutes:02d}:{seconds:02d}"))
            output.flush()
            # If the current internal duration is e.g. 9.3, we should wait for 0.7s to wake up again. We're reading
            # the system clock again because flushing stdout can take some time
            next_tick = 1.0 - ((time.time() - start) % 1)
            time.sleep(next_tick)

    def cancel():
        output.write("\n")
        output.flush()

        finished.set()

    t = threading.Thread(target=fn)
    t.start()
    return cancel
