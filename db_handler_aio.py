import sqlite3
import aiosqlite
import asyncio
import logging
from datetime import datetime

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_errors.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

#create a error decorator
def error_decorator(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            return None
    return wrapper


SCHEMA = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        wallet_address TEXT NOT NULL,
        private_key TEXT NOT NULL,
        trades TEXT NOT NULL,
        slippage INTEGER NOT NULL,
        monitor_wallet TEXT NOT NULL,
        language TEXT DEFAULT 'en'
    );
    
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        user_id TEXT NOT NULL,
        transaction_hash TEXT UNIQUE NOT NULL,
        token_address TEXT NOT NULL,
        token_symbol TEXT NOT NULL,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL,
        status TEXT NOT NULL,
        price_usd REAL,
        price_sol REAL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
'''

@error_decorator
async def create_db_and_table():
    """Creates database and tables if they don't exist."""
    try:
        logging.info("Creating database and tables...")
        async with aiosqlite.connect("users.db") as db:
            # Create users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    wallet_address TEXT,
                    private_key TEXT,
                    follow_wallet TEXT,
                    slippage TEXT DEFAULT '1.5',
                    language TEXT DEFAULT 'en'
                )
            ''')
            
            # Create transactions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    token_a TEXT,
                    token_b TEXT,
                    token_a_symbol TEXT,
                    token_b_symbol TEXT,
                    amount_a REAL,
                    amount_b REAL,
                    price REAL,
                    tx_hash TEXT,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            ''')
            
            # Create positions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    token_address TEXT,
                    token_symbol TEXT,
                    token_name TEXT,
                    entry_price REAL,
                    amount_sol REAL,
                    amount_token REAL,
                    open_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            ''')
            
            await db.commit()
        logging.info("Database and tables created successfully!")
    except Exception as e:
        logging.error(f"Error creating database and tables: {e}")
        raise

@error_decorator
async def insert_user(user_id, wallet_address, private_key, trades, slippage, monitor_wallet, language='en'):
    async with aiosqlite.connect('users.db') as db:
        await db.execute('''
            INSERT INTO users (user_id, wallet_address, private_key, trades, slippage, monitor_wallet, language)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, wallet_address, private_key, trades, slippage, monitor_wallet, language))
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect('users.db') as db:
        # Change the row factory to dictionary
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM users WHERE user_id = ?
        ''', (user_id,))
        row = await cursor.fetchone()
        await cursor.close()
        
        if row is not None:
            return dict(row)
        else:
            return None
        
@error_decorator
async def update_user(user_id, wallet_address=None, private_key=None, trades=None, slippage=None, monitor_wallet=None, language=None):
    async with aiosqlite.connect('users.db') as db:
        # Dictionary to hold the fields to update
        updates = {}
        if wallet_address is not None:
            updates['wallet_address'] = wallet_address
        if private_key is not None:
            updates['private_key'] = private_key
        if trades is not None:
            updates['trades'] = trades
        if slippage is not None:
            updates['slippage'] = slippage
        if monitor_wallet is not None:
            updates['monitor_wallet'] = monitor_wallet
        if language is not None:
            updates['language'] = language

        # Construct the SQL query dynamically
        if updates:
            update_clause = ', '.join(f"{key} = ?" for key in updates)
            sql_query = f"UPDATE users SET {update_clause} WHERE user_id = ?"
            values = list(updates.values()) + [user_id]

            await db.execute(sql_query, values)
            await db.commit()
        else:
            print("No updates specified.")

@error_decorator
async def get_all_users():
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute('''
            SELECT * FROM users
        ''')
        #return as a dictionary with user_id as key
        return {user['user_id']: user for user in await cursor.fetchall()}



def get_all_users():
    dbConnection = sqlite3.connect('users.db')
    cursor = dbConnection.cursor()
    cursor.execute('''
        SELECT * FROM users
    ''')
    #return as a dictionary with user_id as key
    #
    ALLUser ={}
    for user in cursor.fetchall():
        data = {
            'id': user[0],
            'user_id': user[1],
            'wallet_address': user[2],
            'private_key': user[3],
            'trades': user[4],
            'slippage': user[5],
            'monitor_wallet': user[6]
        }
        ALLUser[user[1]] = data
    dbConnection.close()
    return ALLUser

@error_decorator
async def add_transaction(user_id, transaction_hash, token_address, token_symbol, amount, 
                          transaction_type, status, price_usd=None, price_sol=None):
    """
    Add a transaction to the database
    :param user_id: Telegram user ID
    :param transaction_hash: Solana transaction hash
    :param token_address: Token contract address
    :param token_symbol: Token symbol
    :param amount: Amount of tokens
    :param transaction_type: 'buy' or 'sell'
    :param status: 'pending', 'success', 'failed'
    :param price_usd: Optional price in USD
    :param price_sol: Optional price in SOL
    :return: Success status
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    async with aiosqlite.connect('users.db') as db:
        await db.execute('''
            INSERT INTO transactions 
            (user_id, transaction_hash, token_address, token_symbol, amount, 
             transaction_type, status, price_usd, price_sol, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, transaction_hash, token_address, token_symbol, amount, 
              transaction_type, status, price_usd, price_sol, timestamp))
        await db.commit()
    
    logger.info(f"Added transaction: {transaction_hash} for user {user_id}")
    return True

@error_decorator
async def update_transaction_status(transaction_hash, status):
    """
    Update the status of a transaction
    :param transaction_hash: Solana transaction hash
    :param status: 'pending', 'success', 'failed'
    :return: Success status
    """
    async with aiosqlite.connect('users.db') as db:
        await db.execute('''
            UPDATE transactions
            SET status = ?
            WHERE transaction_hash = ?
        ''', (status, transaction_hash))
        await db.commit()
    
    logger.info(f"Updated transaction status: {transaction_hash} to {status}")
    return True

@error_decorator
async def get_user_transactions(user_id, limit=10):
    """
    Get transactions for a user
    :param user_id: Telegram user ID
    :param limit: Maximum number of transactions to return (most recent first)
    :return: List of transaction dictionaries
    """
    async with aiosqlite.connect('users.db') as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM transactions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = await cursor.fetchall()
        transactions = [dict(row) for row in rows]
        await cursor.close()
    
    return transactions

@error_decorator
async def get_transaction(transaction_hash):
    """
    Get a specific transaction by hash
    :param transaction_hash: Solana transaction hash
    :return: Transaction dictionary or None
    """
    async with aiosqlite.connect('users.db') as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM transactions
            WHERE transaction_hash = ?
        ''', (transaction_hash,))
        
        row = await cursor.fetchone()
        await cursor.close()
        
        if row is not None:
            return dict(row)
        else:
            return None

@error_decorator
async def add_position(telegram_id, token_address, token_symbol, token_name, entry_price, amount_sol, amount_token):
    """
    Add a new position to the database
    
    :param telegram_id: Telegram ID of the user
    :param token_address: Token address
    :param token_symbol: Token symbol
    :param token_name: Token name
    :param entry_price: Entry price in USD
    :param amount_sol: Amount of SOL invested
    :param amount_token: Amount of tokens received
    :return: ID of the new position
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute('''
                INSERT INTO positions (
                    telegram_id, token_address, token_symbol, token_name, 
                    entry_price, amount_sol, amount_token
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (telegram_id, token_address, token_symbol, token_name, entry_price, amount_sol, amount_token))
            
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logging.error(f"Error adding position: {e}")
        raise

@error_decorator
async def update_position(position_id, amount_sol=None, amount_token=None, is_active=None):
    """
    Update an existing position
    
    :param position_id: ID of the position to update
    :param amount_sol: New SOL amount (for adding to position)
    :param amount_token: New token amount (for adding to position)
    :param is_active: Set to 0 to close the position
    :return: True if successful
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            update_fields = []
            params = []
            
            if amount_sol is not None:
                update_fields.append("amount_sol = amount_sol + ?")
                params.append(amount_sol)
                
            if amount_token is not None:
                update_fields.append("amount_token = amount_token + ?")
                params.append(amount_token)
                
            if is_active is not None:
                update_fields.append("is_active = ?")
                params.append(is_active)
                
            # Always update last_updated timestamp
            update_fields.append("last_updated = CURRENT_TIMESTAMP")
            
            if not update_fields:
                return False
                
            query = f"UPDATE positions SET {', '.join(update_fields)} WHERE id = ?"
            params.append(position_id)
            
            await db.execute(query, params)
            await db.commit()
            return True
    except Exception as e:
        logging.error(f"Error updating position: {e}")
        raise

@error_decorator
async def get_user_positions(telegram_id, active_only=True, token_address=None):
    """
    Get user positions
    
    :param telegram_id: Telegram ID of the user
    :param active_only: If True, only return active positions
    :param token_address: If provided, only return positions for this token
    :return: List of positions
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            db.row_factory = aiosqlite.Row
            
            query = "SELECT * FROM positions WHERE telegram_id = ?"
            params = [telegram_id]
            
            if active_only:
                query += " AND is_active = 1"
                
            if token_address:
                query += " AND token_address = ?"
                params.append(token_address)
                
            query += " ORDER BY open_date DESC"
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            positions = []
            for row in rows:
                position = dict(row)
                positions.append(position)
                
            return positions
    except Exception as e:
        logging.error(f"Error getting user positions: {e}")
        raise

@error_decorator
async def get_user_coins(telegram_id, active_only=True):
    """
    Get unique coins/tokens that the user has positions in
    
    :param telegram_id: Telegram ID of the user
    :param active_only: If True, only return coins with active positions
    :return: List of coins with their details
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            db.row_factory = aiosqlite.Row
            
            query = """
                SELECT DISTINCT token_address, token_symbol, token_name 
                FROM positions 
                WHERE telegram_id = ?
            """
            params = [telegram_id]
            
            if active_only:
                query += " AND is_active = 1"
                
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            coins = []
            for row in rows:
                coin = dict(row)
                coins.append(coin)
                
            return coins
    except Exception as e:
        logging.error(f"Error getting user coins: {e}")
        raise

@error_decorator
async def get_position(position_id):
    """
    Get a specific position by ID
    
    :param position_id: ID of the position
    :return: Position details or None if not found
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
            row = await cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    except Exception as e:
        logging.error(f"Error getting position: {e}")
        raise

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.run(create_db_and_table())


