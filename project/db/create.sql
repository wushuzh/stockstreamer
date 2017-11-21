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

-- generate a few records with upwarding timestamp
CREATE OR REPLACE FUNCTION add_records() RETURNS VOID AS $$
  BEGIN
    SET TIMEZONE='Asia/Shanghai';
    INSERT INTO stock_prices
      SELECT distinct on (stock_name)
        stock_name,
        price + round(random()*100+1) as price,
        now() + '10 second'::interval
      FROM stock_prices;
  END;
$$ LANGUAGE plpgsql;

/*
DO $$ BEGIN
    PERFORM add_records();
END $$;
*/

