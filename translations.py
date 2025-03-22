"""
This file contains translations for all messages in the bot.
Languages supported: English (en), Arabic (ar), French (fr)
"""

TRANSLATIONS = {
    # English translations
    "en": {
        # General
        "bot_name": "Troy Trading Bot",
        "welcome_message": "Hi there! Welcome to Solana Trading Bot!",
        "welcome_back": "Welcome back! Choose Your Option!",
        "choose_language": "Please choose your preferred language:",
        "language_set": "Language set to English!",

        
        # Menus
        "main_menu": "Main Menu",
        "wallet_menu": "Wallet",
        "swap_menu": "Buy & Sell",
        "copy_trade_menu": "Copy Trade",
        "transaction_menu": "Transaction",
        "positions_menu": "Positions",
        "alerts_menu": "Price Alerts",
        "settings_menu": "Settings",
        "help_menu": "Help",
        
        # Wallet options
        "wallet_address": "Wallet Address",
        "private_key": "Private Key",
        "set_wallet": "Set Wallet",
        "show_wallets": "Show Wallets",
        "reset_wallet": "Reset Wallet",
        "wallet_set_success": "Your wallet has been set successfully!",
        "current_balance": "Current Balance",
        "enter_private_key": "Please enter your private key",
        "invalid_private_key": "Invalid Private Key",
        "wallet_reset_success": "You have reset your wallet data!",
        "no_wallet_set": "You have not set your wallet yet!",
        
        # Swap options
        "buy": "Buy",
        "sell": "Sell",
        "set_slippage": "Set Slippage",
        "enter_slippage": "Please enter your slippage tolerance? Enter a number \nFor Example 5%, Please Enter 5",
        "slippage_changed": "Slippage had changed",
        "slippage_invalid": "Please enter a valid number",
        "to": "to",
        "enter_token_address": "Please Enter The Contract Address of the Token You Want to Buy",
        
        # Token information
        "token_info": "Token Info",
        "symbol": "Symbol",
        "name": "Name",
        "price_usd": "Price in USD",
        "price_sol": "Price in SOL",
        "pool_info": "Pool Info",
        "24h_volume": "24H Volume",
        "token_open_date": "Token Open Date",
        "links": "Links",
        
        # Transaction
        "transaction_starting": "Starting Transaction",
        "transaction_sent": "Transaction sent",
        "transaction_success": "Transaction SUCCESS!",
        "transaction_failed": "Transaction failed",
        "check_status_failed": "Check Transaction Status FAILED! Please Retry.",
        "view_explorer": "View on Solana Explorer",
        "balance_now": "Your balance is now",
        "price": "Price",
        "no_transactions": "You don't have any transactions yet.",
        
        # Positions
        "positions_info": "Track your positions and profits across tokens",
        "no_positions": "You don't have any open positions yet.",
        "open_position": "Open Position",
        "close_position": "Close Position",
        "add_to_position": "Add to Position",
        "pnl": "Profit/Loss",
        "entry_price": "Entry Price",
        "current_value": "Current Value",
        "position_size": "Position Size",
        "holding_since": "Holding Since",
        "total_invested": "Total Invested",
        "total_profit": "Total Profit",
        "profit_percentage": "Profit %",
        "my_coins": "My Coins",
        "no_coins": "You don't have any coins yet.",
        "view_all_positions": "View All Positions",
        "view_coin_positions": "View Positions for",
        "active_coin": "Active",
        "enter_amount": "Enter amount to invest (in SOL):",
        "confirm_open_position": "Confirm opening position for {} with {} SOL?",
        "position_opened": "Position opened successfully!",
        "position_closed": "Position closed successfully!",
        "position_added": "Added to position successfully!",
        
        # Copy Trade
        "view_follow_wallet": "View Follow Wallet",
        "add_follow_wallet": "Add Follow Wallet",
        "remove_follow_wallet": "Remove Follow Wallet",
        
        # Alerts
        "alerts_info": "Create alerts to be notified when token prices reach your targets.\nYou can set alerts for price increases or decreases.",
        "enter_token_alert": "Please enter the token address you want to set an alert for:",
        "enter_target_price": "Please enter your target price in USD:",
        "invalid_token": "Invalid token address. Please try again with a valid Solana token address.",
        "alert_when": "When do you want to be alerted?",
        "alert_above": "Alert when ABOVE this price",
        "alert_below": "Alert when BELOW this price",
        "alert_set": "Alert set!",
        "alert_failed": "Failed to set alert. Please try again.",
        "alert_removed": "Alert removed successfully!",
        "alert_reset": "Alert reset successfully! It will trigger again when conditions are met.",
        "no_alerts": "You don't have any price alerts set up.",
        "price_alert": "PRICE ALERT!",
        "current_price": "Current price",
        "target_price": "Target price",
        "created": "Created",
        "btn_view_alerts": "View My Alerts",
        "btn_add_alert": "Add New Alert",
        
        # Settings
        "language_settings": "Language Settings",
        "change_language": "Change Language",
        "language_options": "Choose your preferred language:",
        
        # Button labels
        "btn_back": "Back",
        "btn_cancel": "Cancel",
        "btn_confirm": "Confirm",
        "btn_go_back": "Go Back",
        "btn_remove": "Remove",
        "btn_reset": "Reset",
        
        # Transaction Menu
        "view_last_transaction": "View Last Transaction",
        "view_last_10_transaction": "View Last 10 Transactions",
        "transaction_history": "Full Transaction History",
    },
    
    # Arabic translations
    "ar": {
        # General
        "bot_name": "روبوت تداول تروي",
        "welcome_message": "مرحبًا! مرحبًا بك في روبوت تداول سولانا!",
        "welcome_back": "مرحبًا بعودتك! اختر خيارك!",
        "choose_language": "يرجى اختيار اللغة المفضلة لديك:",
        "language_set": "تم ضبط اللغة إلى العربية!",
        
        # Menus
        "main_menu": "القائمة الرئيسية",
        "wallet_menu": "المحفظة",
        "swap_menu": "الشراء والبيع",
        "copy_trade_menu": " نسخ التداول",
        "transaction_menu": " المعاملات",
        "positions_menu": "المراكز",
        "alerts_menu": " تنبيهات الأسعار",
        "settings_menu": " الإعدادات",
        "help_menu": " المساعدة",
        
        # Wallet options
        "wallet_address": "عنوان المحفظة",
        "private_key": "المفتاح الخاص",
        "set_wallet": "إعداد المحفظة",
        "show_wallets": "إظهار المحافظ",
        "reset_wallet": "إعادة ضبط المحفظة",
        "wallet_set_success": "تم إعداد محفظتك بنجاح!",
        "current_balance": "الرصيد الحالي",
        "enter_private_key": "الرجاء إدخال المفتاح الخاص بك",
        "invalid_private_key": "المفتاح الخاص غير صالح",
        "wallet_reset_success": "لقد أعدت ضبط بيانات محفظتك!",
        "no_wallet_set": "لم تقم بإعداد محفظتك بعد!",
        
        # Swap options
        "buy": "شراء",
        "sell": "بيع",
        "set_slippage": "ضبط الانزلاق",
        "enter_slippage": "الرجاء إدخال تفاوت الانزلاق الخاص بك؟ أدخل رقمًا \nعلى سبيل المثال 5٪، الرجاء إدخال 5",
        "slippage_changed": "تم تغيير الانزلاق",
        "slippage_invalid": "الرجاء إدخال رقم صحيح",
        "to": "إلى",
        "enter_token_address": "الرجاء إدخال عنوان العقد للرمز الذي تريد شراءه",
        
        # Token information
        "token_info": "معلومات الرمز",
        "symbol": "الرمز",
        "name": "الاسم",
        "price_usd": "السعر بالدولار الأمريكي",
        "price_sol": "السعر بالسولانا",
        "pool_info": "معلومات المجموعة",
        "24h_volume": "حجم التداول خلال 24 ساعة",
        "token_open_date": "تاريخ فتح الرمز",
        "links": "الروابط",
        
        # Transaction
        "transaction_starting": "بدء المعاملة",
        "transaction_sent": "تم إرسال المعاملة",
        "transaction_success": "نجاح المعاملة!",
        "transaction_failed": "فشلت المعاملة",
        "check_status_failed": "فشل التحقق من حالة المعاملة! يرجى إعادة المحاولة.",
        "view_explorer": "عرض في مستكشف سولانا",
        "balance_now": "رصيدك الآن",
        "price": "السعر",
        "no_transactions": "ليس لديك أي معاملات حتى الآن.",
        
        # Positions
        "positions_info": "تتبع مراكزك وأرباحك عبر الرموز",
        "no_positions": "ليس لديك أي مراكز مفتوحة حتى الآن.",
        "open_position": "فتح مركز",
        "close_position": "إغلاق المركز",
        "add_to_position": "إضافة إلى المركز",
        "pnl": "الربح/الخسارة",
        "entry_price": "سعر الدخول",
        "current_value": "القيمة الحالية",
        "position_size": "حجم المركز",
        "holding_since": "محتفظ به منذ",
        "total_invested": "إجمالي الاستثمار",
        "total_profit": "إجمالي الربح",
        "profit_percentage": "نسبة الربح %",
        "my_coins": "عملاتي",
        "no_coins": "ليس لديك أي عملات حتى الآن.",
        "view_all_positions": "عرض جميع المراكز",
        "view_coin_positions": "عرض مراكز لـ",
        "active_coin": "نشط",
        "enter_amount": "أدخل المبلغ المراد استثماره (بالسولانا):",
        "confirm_open_position": "تأكيد فتح مركز لـ {} بـ {} سولانا؟",
        "position_opened": "تم فتح المركز بنجاح!",
        "position_closed": "تم إغلاق المركز بنجاح!",
        "position_added": "تمت الإضافة إلى المركز بنجاح!",
        
        # Copy Trade
        "view_follow_wallet": "عرض محفظة المتابعة",
        "add_follow_wallet": "إضافة محفظة متابعة",
        "remove_follow_wallet": "إزالة محفظة المتابعة",
        
        # Alerts
        "alerts_info": "إنشاء تنبيهات ليتم إخطارك عندما تصل أسعار الرموز إلى أهدافك.\nيمكنك ضبط تنبيهات للزيادات أو الانخفاضات في الأسعار.",
        "enter_token_alert": "الرجاء إدخال عنوان الرمز الذي تريد إعداد تنبيه له:",
        "enter_target_price": "الرجاء إدخال سعرك المستهدف بالدولار الأمريكي:",
        "invalid_token": "عنوان الرمز غير صالح. يرجى المحاولة مرة أخرى باستخدام عنوان رمز سولانا صالح.",
        "alert_when": "متى تريد أن يتم تنبيهك؟",
        "alert_above": "تنبيه عندما يكون فوق هذا السعر",
        "alert_below": "تنبيه عندما يكون أقل من هذا السعر",
        "alert_set": "تم ضبط التنبيه!",
        "alert_failed": "فشل في ضبط التنبيه. حاول مرة اخرى.",
        "alert_removed": "تمت إزالة التنبيه بنجاح!",
        "alert_reset": "تمت إعادة ضبط التنبيه بنجاح! سيتم تشغيله مرة أخرى عند استيفاء الشروط.",
        "no_alerts": "ليس لديك أي تنبيهات أسعار.",
        "price_alert": "تنبيه الأسعار!",
        "current_price": "السعر الحالي",
        "target_price": "السعر المستهدف",
        "created": "تم إنشاؤه",
        "btn_view_alerts": "عرض تنبيهاتي",
        "btn_add_alert": "إضافة تنبيه جديد",
        
        # Settings
        "language_settings": "إعدادات اللغة",
        "change_language": "تغيير اللغة",
        "language_options": "اختر لغتك المفضلة:",
        
        # Button labels
        "btn_back": "رجوع",
        "btn_cancel": "إلغاء",
        "btn_confirm": "تأكيد",
        "btn_go_back": "عد",
        "btn_remove": "إزالة",
        "btn_reset": "إعادة ضبط",
        
        # Transaction Menu
        "view_last_transaction": "عرض آخر معاملة",
        "view_last_10_transaction": "عرض آخر 10 معاملات",
        "transaction_history": "سجل المعاملات الكامل",
    },
    
    # French translations
    "fr": {
        # General
        "bot_name": "Bot de Trading Solana",
        "welcome_message": "Bonjour! Bienvenue sur le Bot de Trading Solana!",
        "welcome_back": "Bon retour! Choisissez votre option!",
        "choose_language": "Veuillez choisir votre langue préférée:",
        "language_set": "Langue définie sur Français!",
        
        # Menus
        "main_menu": "Menu Principal",
        "wallet_menu": "Portefeuille",
        "swap_menu": "Achat & Vente",
        "copy_trade_menu": "Copie de Trade",
        "transaction_menu": "Transaction",
        "positions_menu": "Positions",
        "alerts_menu": "Alertes de Prix",
        "settings_menu": "Paramètres",
        "help_menu": "Aide",
        
        # Wallet options
        "wallet_address": "Adresse du Portefeuille",
        "private_key": "Clé Privée",
        "set_wallet": "Configurer Portefeuille",
        "show_wallets": "Afficher Portefeuilles",
        "reset_wallet": "Réinitialiser Portefeuille",
        "wallet_set_success": "Votre portefeuille a été configuré avec succès!",
        "current_balance": "Solde Actuel",
        "enter_private_key": "Veuillez entrer votre clé privée",
        "invalid_private_key": "Clé Privée Invalide",
        "wallet_reset_success": "Vous avez réinitialisé les données de votre portefeuille!",
        "no_wallet_set": "Vous n'avez pas encore configuré votre portefeuille!",
        
        # Swap options
        "buy": "Acheter",
        "sell": "Vendre",
        "set_slippage": "Définir le Slippage",
        "enter_slippage": "Veuillez entrer votre tolérance de slippage? Entrez un nombre \nPar exemple 5%, veuillez entrer 5",
        "slippage_changed": "Slippage modifié",
        "slippage_invalid": "Veuillez entrer un nombre valide",
        "to": "à",
        "enter_token_address": "Veuillez entrer l'adresse du contrat du jeton que vous souhaitez acheter",
        
        # Token information
        "token_info": "Informations du Jeton",
        "symbol": "Symbole",
        "name": "Nom",
        "price_usd": "Prix en USD",
        "price_sol": "Prix en SOL",
        "pool_info": "Informations de Pool",
        "24h_volume": "Volume 24H",
        "token_open_date": "Date d'ouverture du Jeton",
        "links": "Liens",
        
        # Transaction
        "transaction_starting": "Démarrage de la transaction",
        "transaction_sent": "Transaction envoyée",
        "transaction_success": "Transaction RÉUSSIE!",
        "transaction_failed": "Transaction échouée",
        "check_status_failed": "Échec de la vérification du statut de la transaction! Veuillez réessayer.",
        "view_explorer": "Voir sur Solana Explorer",
        "balance_now": "Votre solde est maintenant",
        "price": "Prix",
        "no_transactions": "Vous n'avez pas encore de transactions.",
        
        # Positions
        "positions_info": "Suivez vos positions et profits sur différents jetons",
        "no_positions": "Vous n'avez pas encore de positions ouvertes.",
        "open_position": "Ouvrir Position",
        "close_position": "Fermer Position",
        "add_to_position": "Ajouter à la Position",
        "pnl": "Profit/Perte",
        "entry_price": "Prix d'Entrée",
        "current_value": "Valeur Actuelle",
        "position_size": "Taille de Position",
        "holding_since": "Détention Depuis",
        "total_invested": "Total Investi",
        "total_profit": "Profit Total",
        "profit_percentage": "Profit %",
        "my_coins": "Mes Jetons",
        "no_coins": "Vous n'avez pas encore de jetons.",
        "view_all_positions": "Voir Toutes les Positions",
        "view_coin_positions": "Voir Positions pour",
        "active_coin": "Actif",
        "enter_amount": "Entrez le montant à investir (en SOL) :",
        "confirm_open_position": "Confirmer l'ouverture d'une position pour {} avec {} SOL ?",
        "position_opened": "Position ouverte avec succès !",
        "position_closed": "Position fermée avec succès !",
        "position_added": "Ajouté à la position avec succès !",
        
        # Copy Trade
        "view_follow_wallet": "Voir Portefeuille Suivi",
        "add_follow_wallet": "Ajouter Portefeuille Suivi",
        "remove_follow_wallet": "Supprimer Portefeuille Suivi",
        
        # Alerts
        "alerts_info": "Créez des alertes pour être notifié lorsque les prix des jetons atteignent vos cibles.\nVous pouvez définir des alertes pour les hausses ou les baisses de prix.",
        "enter_token_alert": "Veuillez entrer l'adresse du jeton pour lequel vous souhaitez définir une alerte:",
        "enter_target_price": "Veuillez entrer votre prix cible en USD:",
        "invalid_token": "Adresse de jeton invalide. Veuillez réessayer avec une adresse de jeton Solana valide.",
        "alert_when": "Quand voulez-vous être alerté?",
        "alert_above": "Alerter quand SUPÉRIEUR à ce prix",
        "alert_below": "Alerter quand INFÉRIEUR à ce prix",
        "alert_set": "Alerte définie!",
        "alert_failed": "Échec de la définition de l'alerte. Veuillez réessayer.",
        "alert_removed": "Alerte supprimée avec succès!",
        "alert_reset": "Alerte réinitialisée avec succès! Elle se déclenchera à nouveau lorsque les conditions seront remplies.",
        "no_alerts": "Vous n'avez pas configuré d'alertes de prix.",
        "price_alert": "ALERTE DE PRIX!",
        "current_price": "Prix actuel",
        "target_price": "Prix cible",
        "created": "Créé le",
        "btn_view_alerts": "Voir Mes Alertes",
        "btn_add_alert": "Ajouter Nouvelle Alerte",
        
        # Settings
        "language_settings": "Paramètres de Langue",
        "change_language": "Changer de Langue",
        "language_options": "Choisissez votre langue préférée:",
        
        # Button labels
        "btn_back": "Retour",
        "btn_cancel": "Annuler",
        "btn_confirm": "Confirmer",
        "btn_go_back": "Retour",
        "btn_remove": "Supprimer",
        "btn_reset": "Réinitialiser",
        
        # Transaction Menu
        "view_last_transaction": "Voir Dernière Transaction",
        "view_last_10_transaction": "Voir 10 Dernières Transactions",
        "transaction_history": "Historique Complet des Transactions",
    }
}

# Function to get translation
def get_text(lang_code, key):
    """
    Get the translation for the given key in the specified language
    
    :param lang_code: Language code ('en', 'ar', or 'fr')
    :param key: Translation key
    :return: Translated text or the key itself if translation is not found
    """
    if lang_code not in TRANSLATIONS:
        lang_code = 'en'  # Default to English if language is not supported
        
    return TRANSLATIONS[lang_code].get(key, key)

# Language names in their native languages
LANGUAGE_NAMES = {
    "en": "English 🇬🇧",
    "ar": "العربية 🇸🇦",
    "fr": "Français 🇫🇷"
}

# Get language name
def get_language_name(lang_code):
    """Get the native name of the language"""
    return LANGUAGE_NAMES.get(lang_code, lang_code) 