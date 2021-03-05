def xywh_to_ltrb(xywh_box):
    x, y, w, h = xywh_box
    return (x, y, x + w, y + h)
