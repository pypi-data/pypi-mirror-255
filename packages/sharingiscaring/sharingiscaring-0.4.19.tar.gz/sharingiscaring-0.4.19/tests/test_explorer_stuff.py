import datetime as dt
from datetime import timezone, timedelta


def verbose_timedelta(delta, days_only=False):
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    dstr = "%s day%s" % (delta.days, "s"[delta.days == 1 :])
    hstr = "%s hr%s" % (hours, "s"[hours == 1 :])
    mstr = "%s min%s" % (minutes, "s"[minutes == 1 :])
    sstr = "%s sec%s" % (seconds, ""[seconds == 1 :])
    total_minutes = delta.days * 24 * 60 + hours * 60 + minutes
    if total_minutes < 30:
        dhms = [dstr, hstr, mstr, sstr] if total_minutes < 30 else [dstr, hstr, mstr]
    elif total_minutes < 720:
        dhms = [dstr, hstr, mstr] if total_minutes < 720 else [dstr, hstr]
    else:
        dhms = [dstr, hstr] if total_minutes < 1440 else [dstr]

    dhms = [dstr] if days_only else dhms

    for x in range(len(dhms)):
        if not dhms[x].startswith("0"):
            dhms = dhms[x:]
            break
    dhms.reverse()
    for x in range(len(dhms)):
        if not dhms[x].startswith("0"):
            dhms = dhms[x:]
            break
    dhms.reverse()
    return " ".join(dhms)


def test_time():
    now = dt.datetime.now().astimezone(tz=timezone.utc)
    plus_1 = now + timedelta(seconds=1)
    minus_1 = now - timedelta(seconds=1)
    print(verbose_timedelta(now - now))
    print(verbose_timedelta(minus_1 - now))
