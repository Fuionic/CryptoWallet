# CryptoWallet

A personal cryptocurrency portfolio tracker built with FastAPI, SQLAlchemy, and a browser-based dashboard. Users can register accounts, sign in securely, add crypto transactions, and review portfolio value and holdings in real time.

This project combines a REST API backend with a lightweight frontend interface in [index.html](index.html) to let users manage transactions and monitor portfolio performance without needing a full external dashboard.

## Overview

CryptoWallet allows a user to:

- Create a personal account with username, email, and password
- Sign in using JWT-based authentication
- Record buy or sell transactions for crypto assets
- Search and manage transactions by coin name
- View the portfolio total and transaction-level details
- Fetch live crypto prices from CoinGecko for portfolio evaluation

The application is designed for personal use and stores user-specific transaction data in PostgreSQL.

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT authentication via `python-jose`
- Password hashing via `passlib` and `bcrypt`
- CoinGecko API integration via `httpx`
- Browser UI using plain HTML/CSS/JavaScript

## Project Structure

```text
Crypto_Wallet/
├── Database.py          # PostgreSQL connection, ORM models, schema migrations
├── auth.py              # Sign-up, login, JWT token generation, user lookup
├── main.py              # FastAPI routes for portfolio and transaction operations
├── model.py             # Pydantic request/response models
├── index.html           # Frontend dashboard UI
├── requirement.txt      # Python dependencies
├── README.md            # Project documentation
├── .env                 # Local environment variables (not committed)
└── crypto/              # Local virtual environment folder
```

## Features

### Authentication

- User registration at `/auth/register`
- Token generation at `/auth/token`
- User profile lookup at `/auth/me`
- Protected endpoints require an `Authorization: Bearer <token>` header

### Portfolio Management

- Add a transaction with type (`buy` or `sell`), coin name, price, and quantity
- List all transactions for the current authenticated user
- Search transactions by crypto name
- Update an existing transaction
- Delete a transaction
- Fetch real-time portfolio estimates with live crypto pricing

### Security

- Passwords are hashed with bcrypt before storage
- JWT tokens contain the username and expire after 24 hours
- Each transaction is linked to a specific authenticated user
- Data access is limited to the currently logged-in user

## Database Configuration

This project is configured for PostgreSQL and expects a local database server running on:

- Host: `localhost`
- Port: `5432`
- Database: `Wallet`
- Username: `postgres`

The database connection is defined in [Database.py](Database.py). The file also creates the `Users` and `transaction` tables and runs a migration function to add auth-related columns (`username`, `password`, and `user_id`) when needed.

## Environment Variables

Create a `.env` file in the project root with the following values:

```env
DATABASE_PASSWORD=your_postgres_password
SECRET_KEY=your_secret_key_here
COINGECKO_API_KEY=your_optional_coingecko_key
```

Notes:

- `DATABASE_PASSWORD` is required because the app builds a PostgreSQL connection string from it.
- `SECRET_KEY` is required for JWT signing.
- `COINGECKO_API_KEY` is optional but can be used for CoinGecko requests when required by the API.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Fuionic/CryptoWallet.git
cd Crypto_Wallet
```

2. Create and activate a virtual environment:

```bash
python -m venv crypto
```

On Windows PowerShell:

```powershell
.\crypto\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source crypto/bin/activate
```

3. Install the required Python packages:

```bash
pip install -r requirement.txt
```

4. Confirm PostgreSQL is running and the database exists.

5. Start the API server:

```bash
uvicorn main:app --reload
```

The app will run locally at:

- API: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`

6. Open [index.html](index.html) in a browser to use the UI.

## API Endpoints

### Authentication

#### Register a user

```http
POST /auth/register
```

Request body:

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "securepass123"
}
```

#### Login and receive JWT

```http
POST /auth/token
```

This endpoint expects form data in the standard OAuth2 format:

- `username`
- `password`

Example response:

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

#### Fetch authenticated user details

```http
GET /auth/me
```

Requires bearer authentication.

### Portfolio and Transaction Routes

#### Add a transaction

```http
POST /addtransaction
```

Authorization: required

Request body:

```json
{
  "transaction_type": "buy",
  "crypto_name": "bitcoin",
  "price_per_unit": 52000,
  "quantity": 0.25
}
```

#### Get all user transactions

```http
GET /all
```

Authorization: required

#### Search transactions by coin name

```http
GET /search/{crypto_name}
```

Example:

```http
GET /search/bitcoin
```

#### Update a transaction

```http
PUT /update/{crypto_name}
```

Authorization: required

#### Delete a transaction

```http
DELETE /delete/{id}
```

Authorization: required

#### Fetch live portfolio data

```http
GET /portfolio/live
```

Authorization: required

Returns portfolio totals, estimated current price, and transaction details for the logged-in user.

## Data Models

### User

Stored in the `Users` table and includes:

- `id`
- `username`
- `email`
- `password`

### Transaction

Stored in the `transaction` table and includes:

- `id`
- `transaction_type` (`buy` or `sell`)
- `crypto_name`
- `price_per_unit`
- `quantity`
- `user_id`

## Authentication Flow

1. A user registers an account.
2. The backend hashes the password with bcrypt.
3. The user logs in via `/auth/token`.
4. The server issues a JWT token.
5. Protected API routes use the token to identify the current user.
6. All portfolio queries and updates are filtered by `user_id`.

## Example Usage

### Register a user

```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "securepass123"
  }'
```

### Login to get token

```bash
curl -X POST "http://127.0.0.1:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=securepass123"
```

### Add a transaction

```bash
curl -X POST "http://127.0.0.1:8000/addtransaction" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "buy",
    "crypto_name": "bitcoin",
    "price_per_unit": 52000,
    "quantity": 0.25
  }'
```

### View portfolio

```bash
curl "http://127.0.0.1:8000/portfolio/live" \
  -H "Authorization: Bearer <token>"
```

## Notes and Caveats

- The app expects PostgreSQL to be available locally.
- The database connection is set with a hardcoded PostgreSQL configuration in [Database.py](Database.py), so if your local setup differs, update the connection values accordingly.
- The project uses a demo CoinGecko pricing endpoint and may require an API key depending on service restrictions.
- JWT tokens expire after 24 hours, so clients will need to log in again after expiration.
- The UI file is static and intended for local development and testing.

## Future Enhancements

Possible improvements for this project include:

- Portfolio analytics such as P/L by asset and overall gains/losses
- Coin search and chart history
- Dark/light theme improvements
- Multi-currency support
- Better error handling and validation feedback
- Deployment to a production-ready hosting environment

## License

This project is currently provided as a local development project without a formal license file. If you plan to distribute or deploy it publicly, add an appropriate open-source license before doing so.

## Contributing

Pull requests and improvements are welcome. For significant changes, it is a good idea to discuss the feature or bugfix first by opening an issue or discussing the changes in the repository.
