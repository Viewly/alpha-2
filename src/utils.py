from toolz import keyfilter

CHARSET = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')


def gen_uid():
    import uuid
    return str(uuid.uuid4()).replace('-', '')[::2]


def gen_video_id(length=12):
    from random import sample
    return ''.join(sample(CHARSET, length))


# toolz
# -----
def keep(d, whitelist):
    return keyfilter(lambda k: k in whitelist, d)


def omit(d, blacklist):
    return keyfilter(lambda k: k not in blacklist, d)
