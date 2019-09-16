# Ticker3

This application powers the ticker at the top of the [r/ethfinance](https://reddit.com/r/ethfinance) subreddit. There are 3 components:

1. data_generator - Fetches CX ([CoinMarketCap](https://coinmarketcap.com)) & FX ([OpenExchangeRates](https://openexchangerates.org)) rates and renders ticker HTML.
2. image_generator - Takes the relevant screenshots using [zenika/alpine-chrome](https://github.com/Zenika/alpine-chrome) and [Puppeteer](https://pptr.dev)
3. reddit_uploader - Uploads the relavant screenshots to Reddit.

## Setup

You need to configure a few settings first:

### data_generator

```sh
cp settings/data_generator.example data_generator.secret
vi data_generator.secret
```

Make sure to set `oer` and `cmc`.

### image_generator

```sh
cp settings/image_generator.example image_generator.secret
vi image_generator.secret
```

Make sure to set `url` if you aren't using the default docker-compose.yml

### reddit_uploader

```sh
cp settings/reddit_uploader.example reddit_uploader.secret
vi reddit_uploader.secret
```

Make sure to set `praw_username`, `praw_password`, `praw_client_id`, `praw_client_secret` and `subreddit`.

## Run

You can use docker-compose to run all of the containers:

```sh
docker-compose up --build -d
docker-compose logs --follow
```

To stop the containers run the following command:

```sh
docker-compose down
```
