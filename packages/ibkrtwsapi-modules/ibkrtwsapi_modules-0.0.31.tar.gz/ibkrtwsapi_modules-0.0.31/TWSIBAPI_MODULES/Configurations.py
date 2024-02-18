from datetime import datetime
from TWSIBAPI_MODULES.exceptions_handler import InvalidPeriod, EndDateFormatError


class Configurations:
    """
    Base class for storing trading algorithm configuration settings. It is meant to be inherited by Config classes.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 0):
        """
        :param host: TWS or ib_gateway connection host
        :param port: TWS or ib_gateway connection port
        :param client_id: TWS or ib_gateway client id
        """
        self.CONN_VARS = [host, port, client_id]

    @staticmethod
    def check_periods(duration: str) -> None:
        """
        Checks if the duration period is valid, valid periods are 'S', 'D', 'W', 'M', 'Y'

        :param duration: duration string to check
        :return: Returns None if the duration period is valid

        :raise InvalidPeriod: Raised if the duration period is not valid
        """
        valid_periods = ['S', 'D', 'W', 'M', 'Y']
        if duration.split(" ")[1] not in valid_periods:
            raise InvalidPeriod(valid_periods)

    @staticmethod
    def check_end_date_format(date: str) -> None:
        """
        Checks if the end_date format is valid, valid format is "%Y%m%d %H:%M:%S" "(YYYYMMDD HH:MM:SS)"

        :param date: Date string to check
        :return: Returns None if the date format is valid

        :raise EndDateFormatError: Raised if the end_date format is not valid
        """
        if date == "":
            return
        try:
            datetime.strptime(date, "%Y%m%d %H:%M:%S")
        except ValueError:
            raise EndDateFormatError(date)
