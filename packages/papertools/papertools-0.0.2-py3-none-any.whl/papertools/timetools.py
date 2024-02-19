class TimeTools:
    def __init__(self):
        """A class which offers a few time related functions."""
        super().__init__()

    def humanize(self, seconds: int = 0, short: bool = None):
        time = seconds
        seconds_to_minute = 60
        seconds_to_hour = 60 * seconds_to_minute
        seconds_to_day = 24 * seconds_to_hour
        seconds_to_week = 7 * seconds_to_day
        seconds_to_month = 30 * seconds_to_day
        seconds_to_year = 12 * seconds_to_month

        years = time // seconds_to_year
        time %= seconds_to_year

        months = time // seconds_to_month
        time %= seconds_to_month

        weeks = time // seconds_to_week
        time %= seconds_to_week

        days = time // seconds_to_day
        time %= seconds_to_day

        hours = time // seconds_to_hour
        time %= seconds_to_hour

        minutes = time // seconds_to_minute
        time %= seconds_to_minute

        seconds = time

        if not short:
            if years > 0:
                return f"{years} {'year' if years == 1 else 'years'}, {months} {'month' if months == 1 else 'months'}, {weeks} {'week' if weeks == 1 else 'weeks'}, {days} {'day' if days == 1 else 'days'}, {hours} {'hour' if hours == 1 else 'hours'}, {minutes} {'minute' if minutes == 1 else 'minutes'} and {seconds} {'second' if seconds == 1 else 'seconds'}"
            if months > 0:
                return f"{months} {'month' if months == 1 else 'months'}, {weeks} {'week' if weeks == 1 else 'weeks'}, {days} {'day' if days == 1 else 'days'}, {hours} {'hour' if hours == 1 else 'hours'}, {minutes} {'minute' if minutes == 1 else 'minutes'} and {seconds} {'second' if seconds == 1 else 'seconds'}"
            if weeks > 0:
                return f"{weeks} {'week' if weeks == 1 else 'weeks'}, {days} {'day' if days == 1 else 'days'}, {hours} {'hour' if hours == 1 else 'hours'}, {minutes} {'minute' if minutes == 1 else 'minutes'} and {seconds} {'second' if seconds == 1 else 'seconds'}"
            if days > 0:
                return f"{days} {'day' if days == 1 else 'days'}, {hours} {'hour' if hours == 1 else 'hours'}, {minutes} {'minute' if minutes == 1 else 'minutes'} and {seconds} {'second' if seconds == 1 else 'seconds'}"
            if hours > 0:
                return f"{hours} {'hour' if hours == 1 else 'hours'}, {minutes} {'minute' if minutes == 1 else 'minutes'} and {seconds} {'second' if seconds == 1 else 'seconds'}"
            elif minutes > 0:
                return f"{minutes} {'minute' if minutes == 1 else 'minutes'} and {seconds} {'second' if seconds == 1 else 'seconds'}"
            else:
                return f"{seconds} {'second' if seconds == 1 else 'seconds'}"
        else:
            if years > 0:
                return f"{years}y {months}m {weeks}w {days}d {hours}h {minutes}m {seconds}s"
            if months > 0:
                return f"{months}m {weeks}w {days}d {hours}h {minutes}m {seconds}s"
            if weeks > 0:
                return f"{weeks}w {days}d {hours}h {minutes}m {seconds}s"
            if days > 0:
                return f"{days}d {hours}h {minutes}m {seconds}s"
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return "%ds" % seconds
