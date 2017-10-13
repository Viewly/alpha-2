from toolz import keyfilter


# toolz
# -----
def keep(d, whitelist):
    return keyfilter(lambda k: k in whitelist, d)


def omit(d, blacklist):
    return keyfilter(lambda k: k not in blacklist, d)
