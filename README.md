# @soothingbot

🤖 A [Telegram bot](https://core.telegram.org/bots) pretending to be an [NFA](nfa.json).<br>
🙏 Inspired by [@happyautomata](https://twitter.com/happyautomata).<br>
🐍 Built in Python using [aiohttp](https://docs.aiohttp.org/en/stable/).<br>
🔧 Mildly over-engineered, playing around with async message processing and dependency injection.<br>
💬 [Talk to it](https://t.me/soothingbot) on Telegram!

![soothingbot in action](soothingbot.webp)

## Install

    git clone https://github.com/sanderevers/soothingbot
    cd soothingbot
    pip install -e .
     
## Run

Get an API key from Telegram and a web server with public HTTPS access.
Configure nginx for SSL offloading and forward to port 8081.

Edit `.env.yaml`

    apikey: 12345:INSERT_HERE
    bot_host: https://example.org

Run `python -m soothingbot .env.yaml` from the repo root (it has to find `.env.yaml` and `nfa.json`).

## Configure NFA

Soothingbot can read JSON output from [re](https://github.com/katef/libfsm), for example:

    $ re -cb -pl json "🦸|🦸‍♂️|🦸🏿‍♂️"
    {
      "statecount": 18,
      "start": 13,
      "end": [ 3, 14 ],
      "edges": [
        { "src": 0, "dst": 1, "symbol": "\u00ef" },
        { "src": 1, "dst": 2, "symbol": "\u00b8" },
        { "src": 2, "dst": 3, "symbol": "\u008f" },
        { "src": 4, "dst": 0, "symbol": "\u0082" },
        { "src": 5, "dst": 6, "symbol": "\u009f" },
        { "src": 6, "dst": 7, "symbol": "\u008f" },
        { "src": 7, "dst": 8, "symbol": "\u00bf" },
        { "src": 8, "dst": 9, "symbol": "\u00e2" },
        { "src": 9, "dst": 10, "symbol": "\u0080" },
        { "src": 10, "dst": 11, "symbol": "\u008d" },
        { "src": 11, "dst": 12, "symbol": "\u00e2" },
        { "src": 12, "dst": 4, "symbol": "\u0099" },
        { "src": 13, "dst": 17, "symbol": "\u00f0" },
        { "src": 14, "dst": 9, "symbol": "\u00e2" },
        { "src": 14, "dst": 5, "symbol": "\u00f0" },
        { "src": 15, "dst": 14, "symbol": "\u00b8" },
        { "src": 16, "dst": 15, "symbol": "\u00a6" },
        { "src": 17, "dst": 16, "symbol": "\u009f" }
      ]
    }
 
 It will reconstruct Unicode, and then do its best to collapse emoji
 sequences into single emoji. (But you can also put emoji in the JSON directly.)
 You can put this JSON in `nfa.json` or POST it to
 `https://your_host/bot/api_key/nfa`.
  

