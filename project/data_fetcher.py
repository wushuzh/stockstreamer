import abc
from urllib.request import urlopen
import json
import time
import datetime
from retrying import retry
from threading import Thread
from functools import partial


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

    def fetchAllPrices(self):
        stock_data = {}
        stock_data['timestamp'] = datetime.datetime.now()
        prices = {}
        threads = []
        for stock in self.stocks:
            t = Thread(target=partial(self.fetchPriceInto, stock, prices))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        stock_data['prices'] = prices
        return stock_data

    def fetchPriceInto(self, stock, results=None):
        results[stock] = self.fetchPrice(stock)

    def fetchPrice(self, stock):
        # get the price of a single stock
        price_url = "{}{}{}".format(IEXStockFetcher.url_prefix,
                                    stock,
                                    IEXStockFetcher.url_suffix_price)
        delay = 1
        for i in range(1, 6):
            try:
                resp = urlopen(price_url)
                price = float(resp.readlines()[0])
                return price
            except:
                print("failed to get price, retrying {0} secs".format(delay))
                time.sleep(delay)
                delay *= i
        raise ConnectionError

    def fetchAllImages(self):
        urls = {}
        threads = []
        for stock in self.stocks:
            t = Thread(target=partial(self.fetchImageInto, stock, urls))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        return urls

    def fetchImageInto(self, stock, results=None):
        results[stock] = self.fetchImageURL(stock)

    def fetchImageURL(self, stock, retries=1):
        # get the image url of a single stock
        if retries > 5:
            raise ConnectionError
        try:
            resp = urlopen("{}{}{}".format(IEXStockFetcher.url_prefix,
                                           stock,
                                           IEXStockFetcher.url_suffix_img))
            resp = json.loads(resp.readlines()[0].decode('utf8'))
            return resp['url']
        except:
            print("failed to get image, retrying {0} secs".format(retries))
            time.sleep(retries)
            retries += 1
            self.fetchImageURL(stock, retries)

    def fetchAllHighLow(self):
        highlow = {}
        threads = []
        for stock in self.stocks:
            t = Thread(target=partial(self.fetchHighLowInto, stock, highlow))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        return highlow

    def fetchHighLowInto(self, stock, results=None):
        results[stock] = self.fetchStockHighLow(stock)

    @retry(wait_random_min=1000, wait_random_max=2000,
           stop_max_attempt_number=5)
    def fetchStockHighLow(self, stock):
        # get the image url of a single stock
        try:
            resp = urlopen("{}{}{}".format(IEXStockFetcher.url_prefix,
                                           stock,
                                           IEXStockFetcher.url_suffix_highlow))
            resp = json.loads(resp.readlines()[0].decode('utf8'))
            return (resp['week52High'], resp['week52Low'])
        except:
            print("wait 1-2 secs then retries get highlow")
        raise ConnectionError


if __name__ == '__main__':
    f = IEXStockFetcher(['AAPL', 'GOOGL'])
    print(f.fetchAllPrices())
    print(f.fetchAllImages())
    print(f.fetchAllHighLow())
    # print(f.fetchPrice('AAPL'))
    # print(f.fetchImageURL('AAPL'))
    # print(f.fetchStockHighLow('AAPL'))

