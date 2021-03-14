def xywh_to_ltrb(xywh_box):
    x, y, w, h = xywh_box
    return (x, y, x + w, y + h)


# https://stackoverflow.com/questions/5531249/how-to-convert-time-format-into-milliseconds-and-back-in-python
def conv_ms_to_timestamp(ms: int) -> str:
    hours, milliseconds = divmod(ms, 3600000)
    minutes, milliseconds = divmod(ms, 60000)
    seconds = float(milliseconds) / 1000
    return "%02i:%02i:%06.3f" % (hours, minutes, seconds)
