import asyncio
from datetime import datetime
import logging
import math
import sys
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from solders.pubkey import Pubkey # type: ignore

import sys

sys.path.append('..')

from swap import Swap
from config import *
from bot_handlers_aiogram import register_position_handlers
from menus import *
from db_handler_aio import *
from tokenInfo import TokenInfo
from translations import get_text

TOKEN = TELEGRAM_BOT_TOKEN
class Form(StatesGroup):
    start_menu = State()
    wallet_menu = State()
    show_wallets = State()
    copy_trade_menu = State()
    transaction_menu = State()
    help_menu = State()
    swap_menu = State()
    set_wallet = State()
    waiting_for_private_key = State()
    set_slippage = State()
    buy_token = State()
    start_transaction = State()
    transaction_history = State()
    first_time_language_selection = State()
    settings_menu = State()
    positions_menu = State()
    waiting_for_position_amount = State()
    waiting_for_position_confirmation = State()


form_router = Router()
ALL_USERS_DATA = get_all_users()
#Start Menu Handler
@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    userId = message.from_user.id
    userData = await get_user(user_id=userId)
    
    # Store user ID in state data
    await state.update_data(userId=userId)
    
    if userData:
        # Existing user - load their data
        ALL_USERS_DATA[userId] = userData
        lang = userData.get("language", "en")
        await state.update_data(userData=userData)
        await state.update_data(lang=lang)
        
        # Create language-specific keyboard and formatted message
        keyboard = make_main_menu_keyboard(lang)
        menu_text = format_menu_message("main_menu", get_text(lang, "welcome_back"), lang)
        
        await message.answer(menu_text, reply_markup=keyboard)
        await state.set_state(Form.start_menu)
    else:
        # New user - ask for language preference first
        # Create user with default values
        await insert_user(
            user_id=userId, 
            wallet_address="", 
            private_key="", 
            trades="{}", 
            slippage=10, 
            monitor_wallet="{}", 
            language="en"  # Default language
        )
        ALL_USERS_DATA[userId] = await get_user(user_id=userId)
        await state.update_data(userData=ALL_USERS_DATA[userId])
        await state.update_data(lang="en")  # Default to English initially
        
        # Ask user to select language
        message_text = f"{get_text('en', 'bot_name')}\n\n📌 {get_text('en', 'language_settings')}\n{'─' * 30}\n\n" + \
                       "Please choose your language / اختر لغتك / Choisissez votre langue:"
        language_keyboard = make_language_selection_keyboard()
        await message.answer(message_text, reply_markup=language_keyboard)
        await state.set_state(Form.first_time_language_selection)

#set_slippage Handler
@form_router.message(Form.set_slippage)
async def process_slippage_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    userData = data.get("userData")
    lang = data.get("lang", "en")
    
    if message.text and message.text.isdigit():
        slippage = float(message.text)
        if slippage < 0 or slippage > 100:
            await message.answer(get_text(lang, "slippage_invalid"), reply_markup=go_back_btn(lang))
        else:
            await update_user(user_id=userId, slippage=slippage)
            userData = await get_user(user_id=userId)
            await state.update_data(userData=userData)
            
            await message.answer(
                f"{get_text(lang, 'slippage_changed')} {get_text(lang, 'to')} {slippage}%", 
                reply_markup=make_swap_menu_keyboard(lang)
            )
            await state.set_state(Form.swap_menu)
    else:
        await message.answer(get_text(lang, "slippage_invalid"), reply_markup=go_back_btn(lang))

# Function to show slippage input prompt
async def set_slippage(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    await message.edit_text(get_text(lang, "enter_slippage"), reply_markup=go_back_btn(lang))
    await state.set_state(Form.set_slippage)


#Private Key Handler
@form_router.message(Form.waiting_for_private_key)
async def process_private_key(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    lang = data.get("lang", "en")
    await state.update_data(private_key=message.text)
    private_key = message.text
    # Save the private key to the database

    wallet = Wallet(RPC_URL, private_key)
    wallet_address = wallet.wallet.pubkey().__str__()

    if wallet_address:
        await update_user(user_id=userId, wallet_address=wallet_address, private_key=private_key, trades="{}", slippage=10)
        userData = await get_user(user_id=userId)
        await state.update_data(userData=userData)
        accBalance = await wallet.get_token_balance(wallet_address)
        await message.answer(
            f"{get_text(lang, 'wallet_set_success')}\n"
            f"{get_text(lang, 'current_balance')}: {accBalance['balance']['float']} SOL", 
            reply_markup=make_wallet_menu_keyboard(lang)
        )
    else:
        await message.answer(get_text(lang, "invalid_private_key"), reply_markup=go_back_btn(lang))
        await state.set_state(Form.wallet_menu)
    await state.set_state(Form.wallet_menu)


async def show_wallet_data(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userData = data.get("userData")
    lang = data.get("lang", "en")
    
    if userData.get("wallet_address") == "":
        await message.edit_text(get_text(lang, "no_wallet_set"), reply_markup=go_back_btn(lang))
        await state.set_state(Form.wallet_menu)
    else:
        wallet = Wallet(RPC_URL, userData['private_key'])
        balance = await wallet.get_token_balance(userData['wallet_address'])
        
        # Format wallet data with HTML tags for better presentation
        wallet_address = f"<b>💼 {get_text(lang, 'wallet_address')}:</b>\n<code>{userData['wallet_address']}</code>"
        private_key = f"\n\n<b>🔑 {get_text(lang, 'private_key')}:</b>\n<code>{userData['private_key']}</code>"
        balance_text = f"\n\n<b>💰 {get_text(lang, 'current_balance')}:</b>\n<code>{balance['balance']['float']} SOL</code>"
        
        # Create formatted wallet information
        formatted_wallet_data = f"{wallet_address}{private_key}{balance_text}"
        
        # Use the menu formatting function to create a consistent display
        menu_text = format_menu_message("wallet_menu", formatted_wallet_data, lang)
        
        await message.edit_text(menu_text, reply_markup=go_back_btn(lang), parse_mode=ParseMode.HTML)

async def set_wallet(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userData = data.get("userData")
    lang = data.get("lang", "en")
    
    if userData.get("wallet_address"):
        await message.edit_text(
            f"{get_text(lang, 'wallet_set_success')}\n"
            f"Wallet Address: {userData['wallet_address']}", 
            reply_markup=go_back_btn(lang)
        )
    else:
        await message.edit_text(get_text(lang, "enter_private_key"), reply_markup=go_back_btn(lang))
        await state.set_state(Form.waiting_for_private_key)


async def reset_wallet(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    userData = data.get("userData")
    lang = data.get("lang", "en")
    
    if userData.get("wallet_address"):
        await update_user(user_id=userId, wallet_address="", private_key="", trades="{}", slippage=10)
        # Format reset wallet message with translations
        reset_message = f"{get_text(lang, 'wallet_reset')}\n\n"
        reset_message += f"{get_text(lang, 'wallet_address')}: {userData['wallet_address']}\n"
        reset_message += f"{get_text(lang, 'private_key')}: {userData['private_key']}"
        await message.answer(reset_message)
        userData = await get_user(user_id=userId)
        await state.update_data(userData=userData)
    else:
        await message.edit_text(get_text(lang, "no_wallet_set"), reply_markup=go_back_btn(lang))
    await state.clear()
    await state.set_state(Form.wallet_menu)


@form_router.message(Form.swap_menu)
async def buy_token(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userData = data.get("userData")
    lang = data.get("lang", "en")
    token_address = message.text
    swapClient = Swap(RPC_URL, userData.get("private_key"))
    account_token_info = await swapClient.get_wallet_token_balance(token_address)
    token_info = await TokenInfo.get_token_info(token_address)
    print(token_info, "token_info")
    await state.update_data(token_info=token_info)
    await state.update_data(token_address=token_address)
    await state.update_data(account_token_info=account_token_info)

    # Format token information with HTML
    token_balance = f"<b>{get_text(lang, 'current_balance')}:</b> <code>{account_token_info['balance']['float']} {token_info['symbol']}</code>"
    
    # Token information section
    token_info_section = (
        f"<b>💵 {get_text(lang, 'token_info')}:</b>\n"
        f"├─ <b>{get_text(lang, 'symbol')}:</b> <code>{token_info['symbol']}</code>\n"
        f"├─ <b>{get_text(lang, 'name')}:</b> <code>{token_info['name']}</code>\n"
        f"├─ <b>{get_text(lang, 'price_usd')}:</b> <code>${token_info['price_in_usd']}</code>\n"
        f"└─ <b>{get_text(lang, 'price_sol')}:</b> <code>{token_info['price_in_sol']} SOL</code>\n"
    )
    
    # Pool information section
    pool_info_section = (
        f"<b>🔍 {get_text(lang, 'pool_info')}:</b>\n"
        f"└─ <b>{get_text(lang, '24h_volume')}:</b> <code>{TokenInfo.convert_volume_to_string(token_info['daily_volume'])}</code>\n"
    )
    
    # Date information
    date_section = (
        f"<b>📅 {get_text(lang, 'token_info')}:</b>\n"
        f"└─ <b>{get_text(lang, 'token_open_date')}:</b> <code>{token_info['created_at']}</code>\n"
    )
    
    # Links section
    links_section = (
        f"<b>🔗 {get_text(lang, 'links')}:</b>\n"
        f"<a href='https://gmgn.ai/sol/token/{token_address}'>GMGN</a> | "
        f"<a href='https://dexscreener.com/solana/{token_address}'>DexScreener</a> | "
        f"<a href='https://birdeye.so/token/{token_address}?chain=solana'>Birdeye</a> | "
        f"<a href='https://www.dextools.io/app/cn/ether/pair-explorer/{token_address}'>Dextools</a>"
    )
    
    # Combine all sections
    formatted_content = f"{token_balance}\n\n{token_info_section}\n{pool_info_section}\n{date_section}\n{links_section}"
    
    # Create formatted message
    swap_text = format_menu_message("swap_menu", formatted_content, lang)
    
    # Use language-specific keyboard
    keyboard = make_swap_menu_keyboard(lang)
    
    await message.answer(swap_text, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    await state.set_state(Form.buy_token)


async def start_transaction(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    userData = await get_user(user_id=userId)
    token_address = data.get("token_address")
    swapData = data.get("swapData")
    lang = data.get("lang", "en")
    
    if userData.get("private_key") is None or token_address is None:
        await message.answer("Please set your wallet first", reply_markup=make_wallet_menu_keyboard(lang))
    else:
        await message.edit_text(f"Starting Transaction for {swapData.get('amount')} {data.get('token_info')['symbol']} {swapData.get('action')}ing.......\nPlease Wait....")
        swapClient = Swap(RPC_URL, userData.get("private_key"))
        token_address = data.get("token_address")
        token_info = data.get("token_info")
        
        # Store pending transaction in database
        await add_transaction(
            user_id=userId,
            transaction_hash="pending", # Will update this once we have the actual transaction hash
            token_address=token_address,
            token_symbol=token_info["symbol"],
            amount=float(swapData.get("amount")),
            transaction_type=swapData.get("action"),
            status="pending",
            price_usd=token_info.get("price_in_usd"),
            price_sol=token_info.get("price_in_sol")
        )
        
        if swapData.get("action") == "buy":
            print("Buying")
            amount = float(swapData.get("amount"))
            slippage = userData.get("slippage")
            tansactionStatus, transactionId = await swapClient.swap_token(
                input_mint="So11111111111111111111111111111111111111112",
                output_mint=token_address,
                amount=amount,
                slippage_bps=slippage
            )
        elif swapData.get("action") == "sell":
            print("Selling")
            product = (float(swapData.get("amount")) * data.get("account_token_info")["balance"]["float"]) #rounding down to near 2 decimal places
            slippage = userData.get("slippage")
            rounded_down_product = math.floor(product * 100) / 100.0
            tansactionStatus, transactionId = await swapClient.swap_token(
                input_mint=token_address,
                output_mint="So11111111111111111111111111111111111111112",
                amount=float(rounded_down_product),
                slippage_bps=slippage
            )
        else:
            await message.answer("Invalid Action")
            await state.set_state(Form.start_menu)
            return

        # Update the transaction in the database with the actual hash
        if tansactionStatus:
            # Update transaction with the actual hash
            await update_transaction_status("pending", "processing")
            
            # Add transaction with real hash
            await add_transaction(
                user_id=userId,
                transaction_hash=transactionId,
                token_address=token_address,
                token_symbol=token_info["symbol"],
                amount=float(swapData.get("amount")),
                transaction_type=swapData.get("action"),
                status="processing",
                price_usd=token_info.get("price_in_usd"),
                price_sol=token_info.get("price_in_sol")
            )
            
            main_menu = make_main_menu_keyboard(lang)
            await message.answer(f"TX ID:{transactionId}\nTransaction sent: [View on Solana Explorer](https://explorer.solana.com/tx/{transactionId})\n--------------\nNow Checking for Transaction Status", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=main_menu)
            swap_status, swap_msg = await swapClient.swap_status(transactionId)
            
            # Update final transaction status
            final_status = "success" if swap_status else "failed"
            await update_transaction_status(transactionId, final_status)
            
            if swap_status:
                await message.answer(f"Transaction SUCCESS! | [View on Solana Explorer](https://explorer.solana.com/tx/{transactionId})", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                
                # Track balance changes after successful transaction
                if swapData.get("action") == "buy":
                    balance_info = await swapClient.track_balance_changes(token_address)
                    await message.answer(f"Your {token_info['symbol']} balance is now {balance_info[0]} tokens")
                else:
                    balance_info = await swapClient.track_balance_changes(swapClient.wallet.pubkey().__str__())
                    await message.answer(f"Your SOL balance is now {balance_info[0]} SOL")
            else:
                await message.answer(f"Check Transaction Status FAILED! Please Retry. {swap_msg}", reply_markup=main_menu)
        else:
            # Mark transaction as failed
            await update_transaction_status("pending", "failed")
            await message.answer(f"Transaction failed: {transactionId}", reply_markup=main_menu)

    await state.set_state(Form.start_menu)

async def buy_handler(message_or_callback, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    userData = await get_user(user_id=userId)
    lang = data.get("lang", "en")
    
    if userData.get("private_key") == "":
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.message.edit_text(get_text(lang, "no_wallet_set"), reply_markup=go_back_btn(lang))
        else:
            await message_or_callback.edit_text(get_text(lang, "no_wallet_set"), reply_markup=go_back_btn(lang))
    else:
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.message.edit_text(get_text(lang, "enter_token_address"))
        else:
            await message_or_callback.edit_text(get_text(lang, "enter_token_address"))
        await state.set_state(Form.swap_menu)


async def wallet_menu(message_or_callback, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    # Create language-specific keyboard
    keyboard = make_wallet_menu_keyboard(lang)
    
    # Use formatted menu message
    menu_text = format_menu_message("wallet_menu", "", lang)
    
    # Handle both Message and CallbackQuery objects
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await message_or_callback.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    
    await state.set_state(Form.wallet_menu)


async def main_menu(message_or_callback, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    # Create language-specific keyboard
    keyboard = make_main_menu_keyboard(lang)
    
    # Use formatted menu message
    menu_text = format_menu_message("main_menu", get_text(lang, "welcome_message"), lang)
    
    # Handle both Message and CallbackQuery objects
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await message_or_callback.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    
    await state.set_state(Form.start_menu)

async def swap_menu(message_or_callback, state: FSMContext) -> None:
    await buy_handler(message_or_callback, state)

async def copy_trade_menu(message_or_callback, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    # Create language-specific keyboard
    keyboard = make_copy_trade_menu(lang)
    
    # Use formatted menu message
    menu_text = format_menu_message("copy_trade_menu", "", lang)
    
    # Handle both Message and CallbackQuery objects
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await message_or_callback.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    
    await state.set_state(Form.copy_trade_menu)

async def transaction_menu(message_or_callback, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    # Create language-specific keyboard
    keyboard = make_transaction_menu(lang)
    
    # Use formatted menu message
    menu_text = format_menu_message("transaction_menu", "", lang)
    
    # Handle both Message and CallbackQuery objects
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await message_or_callback.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    
    await state.set_state(Form.transaction_menu)

async def help_menu(message_or_callback, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    # Create language-specific keyboard
    keyboard = make_help_menu(lang)
    
    # Use formatted menu message
    menu_text = format_menu_message("help_menu", "", lang)
    
    # Handle both Message and CallbackQuery objects
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await message_or_callback.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    
    await state.set_state(Form.help_menu)

async def settings_menu_handler(message_or_callback, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    # Create language-specific keyboard
    keyboard = make_settings_menu_keyboard(lang)
    
    # Use formatted menu message
    menu_text = format_menu_message("settings_menu", "", lang)
    
    # Handle both Message and CallbackQuery objects
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await message_or_callback.edit_text(menu_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    
    await state.set_state(Form.settings_menu)

@form_router.callback_query(F.data)
async def handle_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
    button_message = callback_query.data
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    
    if button_message == "swap_menu":
        await swap_menu(callback_query, state)
    elif button_message == "wallet_menu":
        await wallet_menu(callback_query, state)
    elif button_message == "copy_trade_menu":
        await copy_trade_menu(callback_query, state)
    elif button_message == "transaction_menu":
        await transaction_menu(callback_query, state)
    elif button_message == "help_menu":
        await help_menu(callback_query, state)
    elif button_message == "main_menu":
        await main_menu(callback_query, state)
    elif button_message == "settings_menu":
        await settings_menu_handler(callback_query, state)
    elif button_message == "positions_menu":
        await positions_menu_callback(callback_query, state)
    else:
        await callback_query.message.edit_text(f"Unknown callback data: {button_message}")
    
    await callback_query.answer()

@form_router.message(Form.transaction_history)
async def transaction_history_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    lang = data.get("lang", "en")
    
    transactions = await get_user_transactions(userId, limit=10)
    
    if not transactions:
        # Use formatted message for empty transaction history
        empty_msg = format_menu_message(
            "transaction_menu", 
            f"<i>{get_text(lang, 'no_transactions')}</i>", 
            lang
        )
        await message.answer(empty_msg, reply_markup=go_back_btn(lang), parse_mode=ParseMode.HTML)
        return
    
    # Format transaction history with HTML
    transaction_list = ""
    
    for i, tx in enumerate(transactions):
        status_emoji = "✅" if tx["status"] == "success" else "❌" if tx["status"] == "failed" else "⏳"
        tx_type_emoji = "💰" if tx["transaction_type"] == "buy" else "💸"
        
        # Format individual transaction with HTML
        transaction_list += f"<b>{i+1}. {tx_type_emoji} {tx['transaction_type'].upper()}</b> "
        transaction_list += f"<code>{tx['amount']} {tx['token_symbol']}</code> {status_emoji}\n"
        transaction_list += f"   <i>📅 {tx['timestamp']}</i>\n"
        
        if tx["price_usd"]:
            transaction_list += f"   <b>💵 {get_text(lang, 'price')}:</b> <code>${tx['price_usd']:.6f}</code>\n"
        
        # Use HTML link format instead of markdown for consistency
        transaction_list += f"   <b>🔍 <a href='https://explorer.solana.com/tx/{tx['transaction_hash']}'>{get_text(lang, 'view_explorer')}</a></b>\n\n"
    
    # Create formatted message
    history_text = format_menu_message("transaction_menu", transaction_list, lang)
    
    # Use language-specific keyboard
    keyboard = make_transaction_menu(lang)
    
    await message.answer(history_text, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    await state.set_state(Form.transaction_menu)

async def positions_menu_callback(query: CallbackQuery, state: FSMContext) -> None:
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    
    # Format the positions menu message with title and description
    menu_text = format_menu_message("positions_menu", get_text(lang, 'positions_info'), lang)
    
    # Create keyboard for positions menu
    keyboard = make_positions_menu(lang)
    
    await query.message.edit_text(menu_text, reply_markup=keyboard, parse_mode='HTML')
    await state.set_state(Form.positions_menu)
    await query.answer()

# Add positions menu handler
@form_router.callback_query(F.data == "positions_menu")
async def positions_menu_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    
    # Format the positions menu with title and description
    menu_text = format_menu_message("positions_menu", get_text(lang, 'positions_info'), lang)
    
    # Create the positions menu keyboard
    keyboard = make_positions_menu(lang)
    
    await callback_query.message.edit_text(menu_text, reply_markup=keyboard, parse_mode='HTML')
    await state.set_state(Form.positions_menu)
    await callback_query.answer()

# Update the main menu to include a positions button
@form_router.callback_query(F.data == "main_menu")
async def main_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Return to the main menu"""
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    # Create the main menu keyboard
    keyboard = make_main_menu_keyboard(lang)
    
    # Format the main menu message
    menu_text = format_menu_message("main_menu", get_text(lang, "welcome_back"), lang)
    
    await callback_query.message.edit_text(menu_text, reply_markup=keyboard, parse_mode='HTML')
    await state.set_state(Form.start_menu)
    await callback_query.answer()

async def main():
    # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting bot...")
    
    # Create database tables if they don't exist
    await create_db_and_table()
    logger.info("Database initialized")
    
    # Initialize bot and dispatcher
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)
    
    # Log available languages
    logger.info(f"Available languages: English (en), Arabic (ar), French (fr)")
    
    # Clear webhook to ensure we don't get any errors
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Bot is now running!")
    
    # Register position handlers from bot_handlers_aiogram
    # Import here to avoid circular imports
    register_position_handlers(dp)
    
    # Start polling for updates
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())