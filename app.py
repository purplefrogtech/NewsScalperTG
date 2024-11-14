import time
import feedparser
from telegram.ext import ApplicationBuilder, CallbackContext
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup
import logging
import asyncio

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7164667892:AAFNZIaXzWrscAySnECUpreTeyNW4sUDfJ8'
# Telegram group chat ID
TELEGRAM_CHAT_ID = -1002287692349

# RSS feed URLs
RSS_FEEDS = [
    # Finans, ekonomi ve iş dünyası
    'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
    'http://feeds.reuters.com/reuters/businessNews',
    'https://www.ft.com/?format=rss',
    'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',
    'https://www.wsj.com/xml/rss/3_7014.xml',
    'https://www.forbes.com/business/feed/',
    'https://www.theguardian.com/business/rss',
    'https://www.marketwatch.com/rss/',
    'https://www.dunya.com/rss',
    
    # Kripto ve blockchain
    'https://cointelegraph.com/rss',
    'https://www.coindesk.com/arc/outboundfeeds/rss/',
    'https://bitcoinmagazine.com/.rss/full/',
    'https://cryptoslate.com/feed/',
    'https://cryptopotato.com/feed/',
    
    # Girişimcilik ve teknoloji
    'https://www.entrepreneur.com/latest.rss',
    'https://techcrunch.com/feed/',
    'https://www.fastcompany.com/rss',
]


# Dictionary to store the latest entry for each feed
last_entries = {feed_url: None for feed_url in RSS_FEEDS}

# Translator object
translator = GoogleTranslator(source='en', target='tr')

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def escape_markdown(text):
    escape_chars = r'\*_`\['
    return ''.join(['\\' + char if char in escape_chars else char for char in text])

def truncate_text(text, length=200):
    if len(text) > length:
        return text[:length] + '...'
    return text

async def fetch_and_send_news(context: CallbackContext) -> None:
    bot = context.bot
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        latest_entry = feed.entries[0] if feed.entries else None
        
        if latest_entry:
            if last_entries[feed_url] and last_entries[feed_url].link == latest_entry.link:
                continue

            last_entries[feed_url] = latest_entry
            title = latest_entry.title
            summary = latest_entry.get('summary', '') 
            link = latest_entry.link
            image = latest_entry.get('media_thumbnail', [{}])[0].get('url', '')
            
            summary = clean_html(summary) if summary else ''
            
            try:
                translated_title = translator.translate(title)
                translated_summary = translator.translate(summary)
            except Exception as e:
                logger.error(f"Translation error: {e}")
                continue

            translated_title = escape_markdown(translated_title)
            translated_summary = escape_markdown(translated_summary)
            translated_summary = truncate_text(translated_summary)

            if not translated_summary:
                translated_summary = translated_title

            if image:
                message = f"*{translated_title}*\n\n{translated_summary}\n\n[Daha fazla]({link})\n\n*Premium Trader*"
                try:
                    await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image, caption=message, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Telegram sending error with image: {e}")
            else:
                message = f"*{translated_title}*\n\n{translated_summary}\n\n[Daha fazla]({link})\n\n*Premium Trader*"
                try:
                    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown', disable_web_page_preview=True)
                except Exception as e:
                    logger.error(f"Telegram sending error: {e}")

            await asyncio.sleep(1)

async def initial_fetch_and_send_news(application):
    bot = application.bot
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        latest_entry = feed.entries[0] if feed.entries else None

        if latest_entry:
            last_entries[feed_url] = latest_entry
            title = latest_entry.title
            summary = latest_entry.get('summary', '') 
            link = latest_entry.link
            image = latest_entry.get('media_thumbnail', [{}])[0].get('url', '')

            summary = clean_html(summary) if summary else ''
            
            try:
                translated_title = translator.translate(title)
                translated_summary = translator.translate(summary)
            except Exception as e:
                logger.error(f"Translation error: {e}")
                continue

            translated_title = escape_markdown(translated_title)
            translated_summary = escape_markdown(translated_summary)
            translated_summary = truncate_text(translated_summary)

            if not translated_summary:
                translated_summary = translated_title

            if image:
                message = f"*{translated_title}*\n\n{translated_summary}\n\n[Daha fazla]({link})\n\n*Premium Trader*"
                try:
                    await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image, caption=message, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Telegram sending error with image: {e}")
            else:
                message = f"*{translated_title}*\n\n{translated_summary}\n\n[Daha fazla]({link})\n\n*Premium Trader*"
                try:
                    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown', disable_web_page_preview=True)
                except Exception as e:
                    logger.error(f"Telegram sending error: {e}")

            await asyncio.sleep(1)

async def post_init(application):
    await initial_fetch_and_send_news(application)
    application.job_queue.run_repeating(fetch_and_send_news, interval=300, first=10)

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    application.run_polling()

if __name__ == '__main__':
    main()
