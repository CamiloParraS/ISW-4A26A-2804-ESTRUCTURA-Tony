from datetime import datetime


class TimeUtils:
    @staticmethod
    def normalize_time(hours: int, minutes: int, seconds: int) -> tuple[int, int, int]:
        """Trnasforma el tiempo, 60s = 1min, 60min = 1h"""
        minutes += seconds // 60
        seconds %= 60

        hours += minutes // 60
        minutes %= 60

        hours = min(hours, 999)
        return hours, minutes, seconds

    @staticmethod
    def to_seconds(hours: int, minutes: int, seconds: int) -> int:
        """Convierte Horas y Minutos a Segundos"""
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def from_seconds(total_seconds: int) -> tuple[int, int, int]:
        """Convierte Segundos a Horas y Minutos"""
        hours, rem = divmod(total_seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        return hours, minutes, seconds

    @staticmethod
    def format_digital(current_time: datetime) -> str:
        return current_time.strftime("%I:%M:%S %p").lstrip("0")
