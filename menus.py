from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from translations import LANGUAGE_NAMES, get_text

# Bot name for header

def make_main_menu_keyboard(lang="en") -> None:
    print(lang)
    wallet_btn = InlineKeyboardButton(text=get_text(lang, "wallet_menu"), callback_data="wallet_menu")
    swap_btn = InlineKeyboardButton(text=get_text(lang, "swap_menu"), callback_data="swap_menu")
    copy_trade_btn = InlineKeyboardButton(text=get_text(lang, "copy_trade_menu"), callback_data="copy_trade_menu")
    positions_btn = InlineKeyboardButton(text=get_text(lang, "positions_menu"), callback_data="positions_menu")
    settings_btn = InlineKeyboardButton(text=get_text(lang, "settings_menu"), callback_data="settings_menu")
    help_btn = InlineKeyboardButton(text=get_text(lang, "help_menu"), callback_data="help_menu")
    
    # Arrange buttons in a grid (2 buttons per row)
    main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [wallet_btn, swap_btn],
        [copy_trade_btn, positions_btn],
        [settings_btn, help_btn]
    ])
    return main_keyboard

def make_wallet_menu_keyboard(lang="en") -> None:
    set_wallet_btn = InlineKeyboardButton(text=get_text(lang, "set_wallet"), callback_data="set_wallet")
    show_wallet_btn = InlineKeyboardButton(text=get_text(lang, "show_wallets"), callback_data="show_wallet")
    reset_wallet_btn = InlineKeyboardButton(text=get_text(lang, "reset_wallet"), callback_data="reset_wallet")
    main_menu_btn = InlineKeyboardButton(text=get_text(lang, "main_menu"), callback_data="main_menu")
    wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [set_wallet_btn, show_wallet_btn], 
        [reset_wallet_btn],
        [main_menu_btn]
    ])
    return wallet_keyboard

def make_swap_menu_keyboard(lang="en") -> None:
    buy_0_25_btn = InlineKeyboardButton(text=f"{get_text(lang, 'buy')} 0.01 SOL", callback_data="buy_0.01")
    buy_0_5_btn = InlineKeyboardButton(text=f"{get_text(lang, 'buy')} 0.1 SOL", callback_data="buy_0.1")
    buy_1_0_btn = InlineKeyboardButton(text=f"{get_text(lang, 'buy')} 0.5 SOL", callback_data="buy_0.5")
    buy_option_btn = InlineKeyboardButton(text=f"{get_text(lang, 'buy')} _ SOL", callback_data="buy_option")

    sell_0_25_btn = InlineKeyboardButton(text=f"{get_text(lang, 'sell')} 25 %", callback_data="sell_0.25")
    sell_0_5_btn = InlineKeyboardButton(text=f"{get_text(lang, 'sell')} 50 %", callback_data="sell_0.5")
    sell_1_0_btn = InlineKeyboardButton(text=f"{get_text(lang, 'sell')} 100 %", callback_data="sell_1")
    sell_option_btn = InlineKeyboardButton(text=f"{get_text(lang, 'sell')} _ %", callback_data="sell_option")

    set_slippage_btn = InlineKeyboardButton(text=get_text(lang, "set_slippage"), callback_data="set_slippage")
    main_menu_btn = InlineKeyboardButton(text=get_text(lang, "main_menu"), callback_data="main_menu")
    swap_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [buy_0_25_btn, buy_0_5_btn], 
        [buy_1_0_btn, buy_option_btn], 
        [sell_0_25_btn, sell_0_5_btn], 
        [sell_1_0_btn, sell_option_btn],
        [set_slippage_btn],
        [main_menu_btn]
    ])
    return swap_keyboard

def make_copy_trade_menu(lang="en") -> None:
    view_follow_wallet_btn = InlineKeyboardButton(text=get_text(lang, "view_follow_wallet"), callback_data="view_follow_wallet")
    add_follow_wallet_btn = InlineKeyboardButton(text=get_text(lang, "add_follow_wallet"), callback_data="add_follow_wallet")
    remove_follow_wallet_btn = InlineKeyboardButton(text=get_text(lang, "remove_follow_wallet"), callback_data="remove_follow_wallet")
    main_menu_btn = InlineKeyboardButton(text=get_text(lang, "main_menu"), callback_data="main_menu")
    copy_trade_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [view_follow_wallet_btn], 
        [add_follow_wallet_btn], 
        [remove_follow_wallet_btn],
        [main_menu_btn]
    ])
    return copy_trade_keyboard

def make_positions_menu(lang="en") -> None:
    """Create a keyboard for the positions menu"""
    view_all_positions_btn = InlineKeyboardButton(text=get_text(lang, "view_all_positions"), callback_data="view_all_positions")
    my_coins_btn = InlineKeyboardButton(text=get_text(lang, "my_coins"), callback_data="my_coins")
    open_position_btn = InlineKeyboardButton(text=get_text(lang, "open_position"), callback_data="open_position")
    main_menu_btn = InlineKeyboardButton(text=get_text(lang, "main_menu"), callback_data="main_menu")
    
    positions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [view_all_positions_btn],
        [my_coins_btn],
        [open_position_btn],
        [main_menu_btn]
    ])
    return positions_keyboard

def make_coin_list_keyboard(coins, active_coin=None, lang="en") -> None:
    """
    Create a keyboard with buttons for each coin
    
    Parameters:
    - coins: List of coin data dictionaries with at least 'symbol' and 'token_address' keys
    - active_coin: Token address of the currently active coin (if any)
    - lang: Language code
    
    Returns:
    - Inline keyboard with coin buttons
    """
    buttons = []
    
    # No coins message
    if not coins:
        no_coins_btn = InlineKeyboardButton(
            text=get_text(lang, "no_coins"), 
            callback_data="no_action"
        )
        buttons.append([no_coins_btn])
    else:
        # Create a button for each coin, 2 per row
        row = []
        for i, coin in enumerate(coins):
            # If this is the active coin, mark it
            text = f"{coin['symbol']}"
            if active_coin and coin['token_address'] == active_coin:
                text = f"✅ {text}"
            
            btn = InlineKeyboardButton(
                text=text,
                callback_data=f"select_coin_{coin['token_address']}"
            )
            
            row.append(btn)
            
            # Two buttons per row
            if len(row) == 2 or i == len(coins) - 1:
                buttons.append(row)
                row = []
    
    # Add back button
    back_btn = InlineKeyboardButton(
        text=get_text(lang, "btn_go_back"),
        callback_data="positions_menu"
    )
    buttons.append([back_btn])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def make_coin_position_keyboard(token_address, has_position=False, lang="en") -> None:
    """
    Create a keyboard for actions on a specific coin
    
    Parameters:
    - token_address: The token address of the coin
    - has_position: Whether the user already has a position in this coin
    - lang: Language code
    
    Returns:
    - Inline keyboard with coin position actions
    """
    buttons = []
    
    if has_position:
        add_btn = InlineKeyboardButton(
            text=get_text(lang, "add_to_position"),
            callback_data=f"add_position_{token_address}"
        )
        close_btn = InlineKeyboardButton(
            text=get_text(lang, "close_position"),
            callback_data=f"close_position_{token_address}"
        )
        buttons.append([add_btn])
        buttons.append([close_btn])
    else:
        open_btn = InlineKeyboardButton(
            text=get_text(lang, "open_position"),
            callback_data=f"open_position_{token_address}"
        )
        buttons.append([open_btn])
    
    # Add back button
    back_btn = InlineKeyboardButton(
        text=get_text(lang, "btn_go_back"),
        callback_data="my_coins"
    )
    buttons.append([back_btn])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def make_transaction_menu(lang="en") -> None:
    view_last_transaction_btn = InlineKeyboardButton(text=get_text(lang, "view_last_transaction"), callback_data="view_last_transaction")
    view_last_10_transactions_btn = InlineKeyboardButton(text=get_text(lang, "view_last_10_transactions"), callback_data="view_last_10_transactions")
    transaction_history_btn = InlineKeyboardButton(text=get_text(lang, "transaction_history"), callback_data="transaction_history")
    main_menu_btn = InlineKeyboardButton(text=get_text(lang, "main_menu"), callback_data="main_menu")
    transaction_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [view_last_transaction_btn],
        [view_last_10_transactions_btn],
        [transaction_history_btn],
        [main_menu_btn]
    ])
    return transaction_keyboard

def make_help_menu(lang="en") -> None:
    main_menu_btn = InlineKeyboardButton(text=get_text(lang, "main_menu"), callback_data="main_menu")
    help_keyboard = InlineKeyboardMarkup(inline_keyboard=[[main_menu_btn]])
    return help_keyboard

def make_language_selection_keyboard(lang="en") -> None:
    """Create a keyboard for selecting language"""
    # Note: The lang parameter is not used for translations in this specific case,
    # but is included for consistency with other keyboard creation functions
    en_btn = InlineKeyboardButton(text=LANGUAGE_NAMES["en"], callback_data="lang_en")
    ar_btn = InlineKeyboardButton(text=LANGUAGE_NAMES["ar"], callback_data="lang_ar")
    fr_btn = InlineKeyboardButton(text=LANGUAGE_NAMES["fr"], callback_data="lang_fr")
    
    language_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [en_btn],
        [ar_btn],
        [fr_btn]
    ])
    return language_keyboard

def make_settings_menu_keyboard(lang="en") -> None:
    """Create a keyboard for the settings menu"""
    language_btn = InlineKeyboardButton(text=f"🌐 {get_text(lang, 'language_settings')}", callback_data="language_settings")
    main_menu_btn = InlineKeyboardButton(text=f"🏠 {get_text(lang, 'main_menu')}", callback_data="main_menu")
    
    settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [language_btn],
        [main_menu_btn]
    ])
    return settings_keyboard

def go_back_btn(lang="en") -> None:
    go_back_btn = InlineKeyboardButton(text=get_text(lang, "btn_go_back"), callback_data="main_menu")
    go_back_keyboard = InlineKeyboardMarkup(inline_keyboard=[[go_back_btn]])
    return go_back_keyboard

# Format menu messages with consistent style
def format_menu_message(title, content="", lang="en"):
    """Format a menu message with consistent style and translated title"""
    BOT_NAME = get_text(lang, "bot_name")

    # Create a styled header with the bot name
    width = 50
    space_between_name_and_title = " " * ((width - len(BOT_NAME)) // 2)
    header = f"<b>{space_between_name_and_title}{BOT_NAME}{space_between_name_and_title}</b>"
    
    # Format the title with a decorative element
    title_text = f"<b>📌 {get_text(lang, title)}</b>"
    
    # Create a separator with consistent styling
    separator = f"<code>{'─' * 30}</code>"
    
    # Format the content with proper spacing
    formatted_content = content if content else ""
    
    # Build the complete message with proper spacing
    message = f"{header}\n\n{title_text}\n{separator}\n\n{formatted_content}"
    
    return message

# Format alert/notification messages with consistent style
def format_alert_message(title, content="", lang="en", alert_type="info"):
    """
    Format an alert or notification message with consistent style
    
    Parameters:
    - title: The title key for translation
    - content: The message content
    - lang: Language code
    - alert_type: Type of alert (info, success, warning, error)
    
    Returns:
    - Formatted message with HTML tags
    """
    # Define emoji based on alert type
    alert_emoji = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "alert": "🔔"
    }.get(alert_type, "ℹ️")
    
    # Get the bot name using the provided language
    BOT_NAME = get_text(lang, "bot_name")
    
    # Create a styled header with the bot name
    header = f"<b>{BOT_NAME}</b>"
    
    # Format the title with alert emoji
    title_text = f"<b>{alert_emoji} {get_text(lang, title)}</b>"
    
    # Create a separator
    separator = f"<code>{'─' * 30}</code>"
    
    # Format the content with proper spacing
    formatted_content = content if content else ""
    
    # Build the complete message with proper spacing
    message = f"{header}\n\n{title_text}\n{separator}\n\n{formatted_content}"
    
    return message

# Note: Don't use global keyboards because they don't have language context
# Always create keyboards with the appropriate language parameter in the handlers
