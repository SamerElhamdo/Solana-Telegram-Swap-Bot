import sys
import logging
import json
import datetime
import os

from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from tokenInfo import TokenInfo
from translations import get_text
import db_handler_aio
from db_handler_aio import get_user_positions, get_user_coins, update_position, get_user, add_position
import wallet
import menus
from menus import (
    make_positions_menu, make_coin_list_keyboard, make_coin_position_keyboard,
    format_menu_message, format_alert_message, go_back_btn,
    make_settings_menu_keyboard, make_language_selection_keyboard, make_main_menu_keyboard
)

# Create a router for this module
form_router = Router()

# Define Form class here to match the states in main.py
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
    waiting_for_token_address = State()
    transaction_history = State()
    first_time_language_selection = State()
    settings_menu = State()
    language_settings = State()
    positions_menu = State()
    waiting_for_position_amount = State()
    waiting_for_position_confirmation = State()

#show_wallets Handler
@form_router.message(Form.show_wallets)
async def show_wallets(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "en")
    keyboard = go_back_btn(lang)
    menu_text = format_menu_message("wallet_menu", get_text(lang, "here_is_your_wallet_data"), lang)
    await message.edit_text(menu_text, reply_markup=keyboard)

@form_router.message(Form.settings_menu)
async def settings_menu_handler(message: types.Message, state: FSMContext) -> None:
    """Handle the settings menu"""
    data = await state.get_data()
    lang = data.get("lang", "en")
    keyboard = make_settings_menu_keyboard(lang)
    
    menu_text = format_menu_message("settings_menu", "", lang)
    
    await message.edit_text(menu_text, reply_markup=keyboard)

@form_router.message(Form.language_settings)
async def language_settings_handler(message: types.Message, state: FSMContext) -> None:
    """Handle the language settings menu"""
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    menu_text = format_menu_message(
        "language_settings", 
        get_text(lang, "language_options"),
        lang
    )
    
    language_keyboard = make_language_selection_keyboard(lang)
    await message.edit_text(menu_text, reply_markup=language_keyboard, parse_mode=ParseMode.HTML)

@form_router.message(Form.first_time_language_selection)
async def first_time_language_selection_handler(message: types.Message, state: FSMContext) -> None:
    """Handle the first time language selection"""
    # This uses all languages to display the message
    message_text = "Please choose your language / اختر لغتك / Choisissez votre langue:"
    
    language_keyboard = make_language_selection_keyboard()
    await message.answer(message_text, reply_markup=language_keyboard)

@form_router.callback_query(lambda c: c.data.startswith("lang_"))
async def handle_language_selection(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle language selection callback"""
    lang_code = callback_query.data.split("_")[1]
    data = await state.get_data()
    userId = data.get("userId")
    
    # Save the language preference
    await update_user(user_id=userId, language=lang_code)
    
    # Update state data
    await state.update_data(lang=lang_code)
    
    # First-time setup or changing language from settings?
    current_state = await state.get_state()
    if current_state == "Form:first_time_language_selection":
        # First time setup - move to main menu
        keyboard = make_main_menu_keyboard(lang_code)
        menu_text = format_menu_message(
            "main_menu", 
            f"{get_text(lang_code, 'language_set')}\n\n{get_text(lang_code, 'welcome_message')}", 
            lang_code
        )
        await callback_query.message.edit_text(menu_text, reply_markup=keyboard)
        await state.set_state(Form.start_menu)
    else:
        # Changed language from settings
        keyboard = make_settings_menu_keyboard(lang_code)
        menu_text = format_menu_message(
            "settings_menu", 
            get_text(lang_code, "language_set"), 
            lang_code
        )
        await callback_query.message.edit_text(menu_text, reply_markup=keyboard)
        await state.set_state(Form.settings_menu)

@form_router.callback_query(lambda c: c.data == "language_settings")
async def handle_language_settings(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle language settings callback"""
    data = await state.get_data()
    lang = data.get("lang", "en")
    
    menu_text = format_menu_message(
        "language_settings", 
        get_text(lang, "language_options"),
        lang
    )
    
    language_keyboard = make_language_selection_keyboard(lang)
    await callback_query.message.edit_text(menu_text, reply_markup=language_keyboard, parse_mode=ParseMode.HTML)
    await state.set_state(Form.language_settings)

@form_router.callback_query(lambda c: c.data == "settings_menu")
async def handle_settings_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Handle settings menu callback"""
    data = await state.get_data()
    lang = data.get("lang", "en")
    keyboard = make_settings_menu_keyboard(lang)
    
    menu_text = format_menu_message("settings_menu", "", lang)
    
    await callback_query.message.edit_text(menu_text, reply_markup=keyboard)
    await state.set_state(Form.settings_menu)

async def positions_menu_handler(message_or_query, state: FSMContext):
    """Handler for positions menu button click"""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')  # Changed from 'language' to 'lang' to match other handlers
    
    # Format the positions menu message
    message_text = f"<b>{get_text(lang, 'positions_menu')}</b>\n\n"
    message_text += get_text(lang, 'positions_info')
    
    # Create keyboard for positions menu
    keyboard = make_positions_menu(lang)
    
    # Handle both Message and CallbackQuery
    if isinstance(message_or_query, CallbackQuery):
        await message_or_query.message.edit_text(message_text, reply_markup=keyboard, parse_mode='HTML')
        await state.set_state(Form.positions_menu)
        await message_or_query.answer()
    else:  # Message object
        await message_or_query.edit_text(message_text, reply_markup=keyboard, parse_mode='HTML')
        await state.set_state(Form.positions_menu)

async def view_all_positions_handler(query: CallbackQuery, state: FSMContext):
    """Handler for viewing all positions"""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    user_id = query.from_user.id
    
    # Get all user positions
    positions = await get_user_positions(user_id)
    
    if not positions:
        message_text = f"<b>{get_text(lang, 'positions_menu')}</b>\n\n"
        message_text += get_text(lang, 'no_positions')
        keyboard = make_positions_menu(lang)
        await query.message.edit_text(message_text, reply_markup=keyboard, parse_mode='HTML')
        await query.answer()
        return
    
    # Calculate current values and PnL for each position
    total_invested = 0
    total_current_value = 0
    
    message_text = f"<b>{get_text(lang, 'positions_menu')} - {get_text(lang, 'view_all_positions')}</b>\n\n"
    
    for position in positions:
        token_symbol = position['token_symbol']
        token_address = position['token_address']
        entry_price = position['entry_price']
        amount_sol = position['amount_sol']
        amount_token = position['amount_token']
        open_date = position['open_date']
        
        # Get current price
        try:
            token_info = await get_token_info(token_address)
            current_price = token_info['price_usd'] if token_info and 'price_usd' in token_info else 0
        except Exception as e:
            logger.error(f"Error getting token price: {e}")
            current_price = 0
        
        # Calculate PnL
        current_value = amount_token * current_price
        invested_value = amount_sol * (await get_sol_price())
        profit_loss = current_value - invested_value
        profit_percentage = (profit_loss / invested_value) * 100 if invested_value > 0 else 0
        
        total_invested += invested_value
        total_current_value += current_value
        
        # Add position details
        message_text += f"<b>{token_symbol}</b>\n"
        message_text += f"• {get_text(lang, 'entry_price')}: ${entry_price:.4f}\n"
        message_text += f"• {get_text(lang, 'current_value')}: ${current_value:.2f}\n"
        message_text += f"• {get_text(lang, 'position_size')}: {amount_token:.2f} {token_symbol}\n"
        message_text += f"• {get_text(lang, 'holding_since')}: {open_date}\n"
        
        # Add PnL details
        if profit_loss >= 0:
            message_text += f"• {get_text(lang, 'pnl')}: <b>+${profit_loss:.2f} (+{profit_percentage:.2f}%)</b>\n"
        else:
            message_text += f"• {get_text(lang, 'pnl')}: <b>${profit_loss:.2f} ({profit_percentage:.2f}%)</b>\n"
            
        message_text += "\n"
    
    # Add summary
    total_profit = total_current_value - total_invested
    total_profit_percentage = (total_profit / total_invested) * 100 if total_invested > 0 else 0
    
    message_text += f"<b>{get_text(lang, 'total_invested')}</b>: ${total_invested:.2f}\n"
    
    if total_profit >= 0:
        message_text += f"<b>{get_text(lang, 'total_profit')}</b>: +${total_profit:.2f} (+{total_profit_percentage:.2f}%)\n"
    else:
        message_text += f"<b>{get_text(lang, 'total_profit')}</b>: ${total_profit:.2f} ({total_profit_percentage:.2f}%)\n"
    
    # Create keyboard to go back
    back_button = InlineKeyboardMarkup()
    back_button.add(InlineKeyboardButton(get_text(lang, 'btn_go_back'), callback_data='positions_menu'))
    
    await query.message.edit_text(message_text, reply_markup=back_button, parse_mode='HTML')
    await query.answer()

async def my_coins_handler(query: CallbackQuery, state: FSMContext):
    """Handler for viewing user's coins"""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    user_id = query.from_user.id
    
    # Get unique coins the user has positions in
    coins = await get_user_coins(user_id)
    
    # Create keyboard with user's coins
    keyboard = make_coin_list_keyboard(coins, lang=lang)
    
    message_text = f"<b>{get_text(lang, 'positions_menu')} - {get_text(lang, 'my_coins')}</b>\n\n"
    if not coins:
        message_text += get_text(lang, 'no_coins')
    else:
        message_text += f"{get_text(lang, 'my_coins')}:"
    
    await query.message.edit_text(message_text, reply_markup=keyboard, parse_mode='HTML')
    await query.answer()

async def select_coin_handler(query: CallbackQuery, state: FSMContext):
    """Handler for selecting a coin from the list"""
    callback_data = query.data
    token_address = callback_data.replace('select_coin_', '')
    
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    user_id = query.from_user.id
    
    # Store the selected coin in state
    await state.update_data(selected_coin=token_address)
    
    # Get positions for this token
    positions = await get_user_positions(user_id, token_address=token_address)
    
    if not positions:
        # No positions for this token - show options to open position
        token_info = await get_token_info(token_address)
        token_symbol = token_info.get('symbol', 'Unknown')
        token_name = token_info.get('name', 'Unknown Token')
        current_price = token_info.get('price_usd', 0)
        
        message_text = f"<b>{token_symbol} ({token_name})</b>\n\n"
        message_text += f"{get_text(lang, 'current_price')}: ${current_price:.4f}\n\n"
        message_text += f"{get_text(lang, 'no_positions')}"
        
        # Create keyboard for coin actions
        keyboard = make_coin_position_keyboard(token_address, has_position=False, lang=lang)
        
        await query.message.edit_text(message_text, reply_markup=keyboard, parse_mode='HTML')
        await query.answer()
        return
    
    # Calculate total position value and PnL
    token_info = await get_token_info(token_address)
    token_symbol = token_info.get('symbol', positions[0]['token_symbol'])
    token_name = token_info.get('name', positions[0]['token_name'])
    current_price = token_info.get('price_usd', 0)
    
    total_token_amount = sum(position['amount_token'] for position in positions)
    total_sol_invested = sum(position['amount_sol'] for position in positions)
    sol_price = await get_sol_price()
    total_invested_usd = total_sol_invested * sol_price
    current_value = total_token_amount * current_price
    profit_loss = current_value - total_invested_usd
    profit_percentage = (profit_loss / total_invested_usd) * 100 if total_invested_usd > 0 else 0
    
    # Create message with position details
    message_text = f"<b>{token_symbol} ({token_name})</b>\n\n"
    message_text += f"{get_text(lang, 'current_price')}: ${current_price:.4f}\n"
    message_text += f"{get_text(lang, 'position_size')}: {total_token_amount:.2f} {token_symbol}\n"
    message_text += f"{get_text(lang, 'total_invested')}: ${total_invested_usd:.2f}\n"
    
    if profit_loss >= 0:
        message_text += f"{get_text(lang, 'pnl')}: <b>+${profit_loss:.2f} (+{profit_percentage:.2f}%)</b>\n\n"
    else:
        message_text += f"{get_text(lang, 'pnl')}: <b>${profit_loss:.2f} ({profit_percentage:.2f}%)</b>\n\n"
    
    # Add details for each position
    message_text += f"<b>{get_text(lang, 'view_coin_positions')}:</b>\n"
    for position in positions:
        entry_price = position['entry_price']
        amount_token = position['amount_token']
        open_date = position['open_date']
        amount_sol = position['amount_sol']
        
        position_value = amount_token * current_price
        position_invested = amount_sol * sol_price
        position_pnl = position_value - position_invested
        position_pnl_percentage = (position_pnl / position_invested) * 100 if position_invested > 0 else 0
        
        message_text += f"• {amount_token:.2f} {token_symbol}\n"
        message_text += f"  {get_text(lang, 'entry_price')}: ${entry_price:.4f}\n"
        message_text += f"  {get_text(lang, 'holding_since')}: {open_date}\n"
        
        if position_pnl >= 0:
            message_text += f"  {get_text(lang, 'pnl')}: +${position_pnl:.2f} (+{position_pnl_percentage:.2f}%)\n"
        else:
            message_text += f"  {get_text(lang, 'pnl')}: ${position_pnl:.2f} ({position_pnl_percentage:.2f}%)\n"
        
        message_text += "\n"
    
    # Create keyboard for coin actions
    keyboard = make_coin_position_keyboard(token_address, has_position=True, lang=lang)
    
    await query.message.edit_text(message_text, reply_markup=keyboard, parse_mode='HTML')
    await query.answer()

async def open_position_handler(query: CallbackQuery, state: FSMContext):
    """Handler for opening a new position"""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    
    callback_data = query.data
    # Check if this is from the positions menu or coin specific
    if callback_data == 'open_position':
        # From positions menu - ask for token address
        message_text = f"<b>{get_text(lang, 'open_position')}</b>\n\n"
        message_text += get_text(lang, 'enter_token_address')
        
        # Create keyboard to cancel
        cancel_button = InlineKeyboardMarkup()
        cancel_button.add(InlineKeyboardButton(get_text(lang, 'btn_cancel'), callback_data='positions_menu'))
        
        await query.message.edit_text(message_text, reply_markup=cancel_button, parse_mode='HTML')
        await state.set_state(Form.waiting_for_token_input)
        # Store context that we're waiting for a token for position
        await state.update_data(input_context='open_position')
    else:
        # From coin specific menu - token address is in the callback
        token_address = callback_data.replace('open_position_', '')
        await state.update_data(position_token=token_address)
        
        # Get token info
        token_info = await get_token_info(token_address)
        token_symbol = token_info.get('symbol', 'Unknown')
        current_price = token_info.get('price_usd', 0)
        
        message_text = f"<b>{get_text(lang, 'open_position')}</b>\n\n"
        message_text += f"{get_text(lang, 'token_info')}: {token_symbol} (${current_price:.4f})\n\n"
        message_text += get_text(lang, 'enter_amount')
        
        # Create keyboard to cancel
        cancel_button = InlineKeyboardMarkup()
        cancel_button.add(InlineKeyboardButton(get_text(lang, 'btn_cancel'), callback_data='my_coins'))
        
        await query.message.edit_text(message_text, reply_markup=cancel_button, parse_mode='HTML')
        await state.set_state(Form.waiting_for_position_amount)
    
    await query.answer()

async def add_to_position_handler(query: CallbackQuery, state: FSMContext):
    """Handler for adding to an existing position"""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    
    callback_data = query.data
    token_address = callback_data.replace('add_position_', '')
    await state.update_data(position_token=token_address)
    
    # Get token info
    token_info = await get_token_info(token_address)
    token_symbol = token_info.get('symbol', 'Unknown')
    current_price = token_info.get('price_usd', 0)
    
    message_text = f"<b>{get_text(lang, 'add_to_position')}</b>\n\n"
    message_text += f"{get_text(lang, 'token_info')}: {token_symbol} (${current_price:.4f})\n\n"
    message_text += get_text(lang, 'enter_amount')
    
    # Create keyboard to cancel
    cancel_button = InlineKeyboardMarkup()
    cancel_button.add(InlineKeyboardButton(get_text(lang, 'btn_cancel'), callback_data=f'select_coin_{token_address}'))
    
    await query.message.edit_text(message_text, reply_markup=cancel_button, parse_mode='HTML')
    await state.set_state(Form.waiting_for_position_amount)
    await state.update_data(is_add_to_position=True)
    
    await query.answer()

async def close_position_handler(query: CallbackQuery, state: FSMContext):
    """Handler for closing a position"""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    user_id = query.from_user.id
    
    callback_data = query.data
    token_address = callback_data.replace('close_position_', '')
    
    # Get positions for this token
    positions = await get_user_positions(user_id, token_address=token_address)
    
    if not positions:
        await query.answer(get_text(lang, 'no_positions'), show_alert=True)
        return
    
    # Get token info
    token_info = await get_token_info(token_address)
    token_symbol = token_info.get('symbol', positions[0]['token_symbol'])
    current_price = token_info.get('price_usd', 0)
    
    # Close all positions for this token
    for position in positions:
        await update_position(position['id'], is_active=0)
    
    # Calculate the final PnL
    total_token_amount = sum(position['amount_token'] for position in positions)
    total_sol_invested = sum(position['amount_sol'] for position in positions)
    sol_price = await get_sol_price()
    total_invested_usd = total_sol_invested * sol_price
    current_value = total_token_amount * current_price
    profit_loss = current_value - total_invested_usd
    profit_percentage = (profit_loss / total_invested_usd) * 100 if total_invested_usd > 0 else 0
    
    # Display closing summary
    if profit_loss >= 0:
        pnl_text = f"+${profit_loss:.2f} (+{profit_percentage:.2f}%)"
    else:
        pnl_text = f"${profit_loss:.2f} ({profit_percentage:.2f}%)"
    
    message_text = f"<b>{get_text(lang, 'close_position')}</b>\n\n"
    message_text += f"{get_text(lang, 'position_closed')}\n\n"
    message_text += f"{get_text(lang, 'token_info')}: {token_symbol}\n"
    message_text += f"{get_text(lang, 'position_size')}: {total_token_amount:.2f} {token_symbol}\n"
    message_text += f"{get_text(lang, 'pnl')}: {pnl_text}\n\n"
    
    # Create button to return to positions menu
    back_button = InlineKeyboardMarkup()
    back_button.add(InlineKeyboardButton(get_text(lang, 'btn_go_back'), callback_data='positions_menu'))
    
    await query.message.edit_text(message_text, reply_markup=back_button, parse_mode='HTML')
    await query.answer()

async def position_amount_handler(message: types.Message, state: FSMContext):
    """Handler for receiving position amount"""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    token_address = user_data.get('position_token')
    is_add = user_data.get('is_add_to_position', False)
    
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        await message.reply(get_text(lang, 'slippage_invalid'))
        return
    
    # Check if user has enough SOL
    user_id = message.from_user.id
    user = await get_user(user_id)
    
    if not user or not user.get('wallet_address'):
        await message.reply(get_text(lang, 'no_wallet_set'))
        return
    
    wallet_address = user['wallet_address']
    private_key = user['private_key']
    
    # Check balance
    sol_balance = await wallet.get_balance(wallet_address)
    if sol_balance < amount:
        await message.reply(get_text(lang, 'insufficient_balance'))
        return
    
    # Get token info
    token_info = await get_token_info(token_address)
    token_symbol = token_info.get('symbol', 'Unknown')
    token_name = token_info.get('name', 'Unknown Token')
    current_price = token_info.get('price_usd', 0)
    
    # Store info for confirmation
    await state.update_data(position_amount=amount)
    
    # Ask for confirmation
    action = get_text(lang, 'add_to_position') if is_add else get_text(lang, 'open_position')
    confirm_text = get_text(lang, 'confirm_open_position').format(token_symbol, amount)
    
    message_text = f"<b>{action}</b>\n\n"
    message_text += f"{confirm_text}\n\n"
    message_text += f"{get_text(lang, 'token_info')}: {token_symbol} (${current_price:.4f})\n"
    
    # Create confirmation keyboard
    confirm_keyboard = InlineKeyboardMarkup(row_width=2)
    confirm_btn = InlineKeyboardButton(get_text(lang, 'btn_confirm'), callback_data='confirm_position')
    cancel_btn = InlineKeyboardButton(get_text(lang, 'btn_cancel'), callback_data='positions_menu')
    confirm_keyboard.add(confirm_btn, cancel_btn)
    
    await message.reply(message_text, reply_markup=confirm_keyboard, parse_mode='HTML')
    await state.set_state(Form.waiting_for_position_confirmation)

async def confirm_position_handler(query: CallbackQuery, state: FSMContext):
    """Handler for confirming position opening/adding"""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'en')
    user_id = query.from_user.id
    token_address = user_data.get('position_token')
    amount_sol = user_data.get('position_amount')
    is_add = user_data.get('is_add_to_position', False)
    
    user = await get_user(user_id)
    wallet_address = user['wallet_address']
    private_key = user['private_key']
    
    # Get token info
    token_info = await get_token_info(token_address)
    token_symbol = token_info.get('symbol', 'Unknown')
    token_name = token_info.get('name', 'Unknown Token')
    current_price = token_info.get('price_usd', 0)
    
    # This is a simulation - in a real app, you would actually execute the trade here
    # For this demo, we're just recording the position
    
    # Calculate tokens received (simulated)
    sol_price = await get_sol_price()
    usd_value = amount_sol * sol_price
    tokens_received = usd_value / current_price
    
    if is_add:
        # Adding to existing position - find most recent active position
        positions = await get_user_positions(user_id, token_address=token_address)
        if positions:
            # Update the most recent position
            position_id = positions[0]['id']
            await update_position(
                position_id, 
                amount_sol=amount_sol,
                amount_token=tokens_received
            )
            success_message = get_text(lang, 'position_added')
        else:
            # No existing position found, create new
            await add_position(
                user_id,
                token_address,
                token_symbol,
                token_name,
                current_price,
                amount_sol,
                tokens_received
            )
            success_message = get_text(lang, 'position_opened')
    else:
        # Creating new position
        await add_position(
            user_id,
            token_address,
            token_symbol,
            token_name,
            current_price,
            amount_sol,
            tokens_received
        )
        success_message = get_text(lang, 'position_opened')
    
    # Display success message
    message_text = f"<b>{success_message}</b>\n\n"
    message_text += f"{get_text(lang, 'token_info')}: {token_symbol} (${current_price:.4f})\n"
    message_text += f"{get_text(lang, 'position_size')}: {tokens_received:.2f} {token_symbol}\n"
    message_text += f"{get_text(lang, 'entry_price')}: ${current_price:.4f}\n"
    
    # Create button to return to positions menu
    back_button = InlineKeyboardMarkup()
    back_button.add(InlineKeyboardButton(get_text(lang, 'btn_go_back'), callback_data='positions_menu'))
    
    await query.message.edit_text(message_text, reply_markup=back_button, parse_mode='HTML')
    await query.answer()

def register_position_handlers(dp: Dispatcher):
    """Register all position related handlers"""
    # Use the correct method for aiogram 3.x
    positions_router = Router(name='positions')
    
    # Add position menu handlers
    positions_router.callback_query.register(positions_menu_handler, F.data == "positions_menu")
    
    # Add handlers that require specific Form states
    positions_router.callback_query.register(view_all_positions_handler, F.data == "view_all_positions")
    positions_router.callback_query.register(my_coins_handler, F.data == "my_coins")
    positions_router.callback_query.register(open_position_handler, F.data == "open_position")
    
    # Coin selection handlers with pattern matching
    positions_router.callback_query.register(
        select_coin_handler, 
        lambda c: c.data and c.data.startswith('select_coin_')
    )
    
    # Position action handlers with pattern matching
    positions_router.callback_query.register(
        open_position_handler, 
        lambda c: c.data and c.data.startswith('open_position_')
    )
    positions_router.callback_query.register(
        add_to_position_handler, 
        lambda c: c.data and c.data.startswith('add_position_')
    )
    positions_router.callback_query.register(
        close_position_handler, 
        lambda c: c.data and c.data.startswith('close_position_')
    )
    
    # Position amount handlers
    positions_router.message.register(
        position_amount_handler, 
        Form.waiting_for_position_amount
    )
    
    # Position confirmation handlers
    positions_router.callback_query.register(
        confirm_position_handler, 
        F.data == "confirm_position"
    )
    
    # Include the router in the dispatcher
    dp.include_router(positions_router)

# Helper functions to simplify token operations
async def get_token_info(token_address):
    return await TokenInfo.get_token_info(token_address)

async def get_sol_price():
    # Get SOL price from the token info
    sol_address = "So11111111111111111111111111111111111111112"  # SOL token address
    sol_info = await get_token_info(sol_address)
    return sol_info.get('price_usd', 0) if sol_info else 0