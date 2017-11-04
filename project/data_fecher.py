import abc


class StockFetcher(metaclass=abc.ADBMeta):
    """
    Base class for fetching stock info
    """
    def __init__(self, stocks):
        self.stocks = stocks

    @abc.abstractmethod
    def fetchPrice(self, stock):
        """
        return current price of stock
        """
        return NotImplemented

    @abc.abstractmethod
    def fetchStockHighLow(self, stock):
        """
        returns the high/low values of stock
        """
        return NotImplemented

    @abc.abstractmethod
    def fetchImageURL(self, stock):
        """
        returns a URL pointing to the logo corresponding to stock
        """
        return NotImplemented

