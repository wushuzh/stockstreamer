import abc
from urllib.request import urlopen
import json


class StockFetcher(metaclass=abc.ABCMeta):
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


class IEXStockFetcher(StockFetcher):
    """
    Fetches stock info using iextrading.com API
    """

    url_prefix = "https://api.iextrading.com/1.0/stock/"
    url_suffix_price = "/price"
    url_suffix_img = "/logo"
    url_suffix_highlow = "/quote"

    def __init__(self, stocks):
        super().__init__(stocks)

    def fetchPrice(self, stock):
        # get the price of a single stock
        try:
            resp = urlopen("{}{}{}".format(IEXStockFetcher.url_prefix,
                                           stock,
                                           IEXStockFetcher.url_suffix_price))
            price = float(resp.readlines()[0])
            return price
        except:
            return self.fetchPrice(stock)

    def fetchImageURL(self, stock):
        # get the image url of a single stock
        try:
            resp = urlopen("{}{}{}".format(IEXStockFetcher.url_prefix,
                                           stock,
                                           IEXStockFetcher.url_suffix_img))
            resp = json.loads(resp.readlines()[0].decode('utf8'))
            return resp['url']
        except:
            return self.fetchImageURL(stock)

    def fetchStockHighLow(self, stock):
        # get the image url of a single stock
        try:
            resp = urlopen("{}{}{}".format(IEXStockFetcher.url_prefix,
                                           stock,
                                           IEXStockFetcher.url_suffix_highlow))
            resp = json.loads(resp.readlines()[0].decode('utf8'))
            return (resp['week52High'], resp['week52Low'])
        except:
            return self.fetchStockHighLow(stock)


if __name__ == '__main__':
    f = IEXStockFetcher([])
    print(f.fetchPrice('AAPL'))
    print(f.fetchImageURL('AAPL'))
    print(f.fetchStockHighLow('AAPL'))
