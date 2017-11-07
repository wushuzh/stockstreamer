CREATE DATABASE stocks;
\connect stocks;
-- stock_price: contains records of stock prices with timestamps
CREATE TABLE stock_prices (
    stock_name varchar(6),
    price decimal,
    time timestamp);

-- stock_image_urls: contains a URL where the company log for each stock may be found
CREATE TABLE stock_image_urls (
    stock_name varchar(6),
    image_url varchar(1024));

-- stock_highlow: conntains the 52-week high and low values for the stock
CREATE TABLE stock_highlow(
    stock_name varchar(6),
    high_val52wk decimal,
    low_val52wk decimal);
