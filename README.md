# CryptoWallet

A personal crypto portfolio tracker with account-based sign-up and login.

## Run locally

1. Configure `.env` with `DATABASE_PASSWORD` and `SECRET_KEY`. Set
   `COINGECKO_API_KEY` if you have a CoinGecko demo API key.
2. Install dependencies with `pip install -r requirement.txt`.
3. Start the API from the project directory with `uvicorn main:app --reload`.
4. Open `index.html` in a browser and create an account or log in.

The API issues JWT bearer tokens that expire after 24 hours. Portfolio and
transaction endpoints require a valid token and only return or modify the
authenticated user's transactions. Existing transactions from before account
ownership was added remain unassigned and are not shown in user wallets.
