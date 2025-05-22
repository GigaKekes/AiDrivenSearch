import os
import logging
import time
import url_parcer
import web_search
import paraphrase
import reranker
import answer_generator

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to the AI Search Bot. Send me a query!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("🔍 Searching the web...")

    try:
        # Paraphrase the query
        paraphrased_queries = paraphrase.paraphrase_query(query)
        # Perform web search
        visited_urls = set()
        parsed_results = []
        url_dict = dict()
        
        
        for q in paraphrased_queries:
            urls = web_search.parallel_search_yandex_google(q, num_results=10)
            for url in urls:
                if url not in visited_urls:
                    try:
                        md = url_parcer.parse_url(url)
                    except Exception as e:
                        continue
                    
                    relevant_from_url = url_parcer.extract_relevant(q, md)
                    parsed_results.append(relevant_from_url)
                    url_dict[relevant_from_url] = url
                    visited_urls.add(url)
        
        await update.message.reply_text("🔍 Extracting top results...")
        top_results = reranker.rerank_documents(query, parsed_results, top_n=5)
        
        await update.message.reply_text("🔍 Generating the answer...")
        final_answer = answer_generator.generate_answer(query, [(url_dict[doc], doc) for doc in top_results])
        
        await update.message.reply_text(f"🤖 Answer:\n{(final_answer)}")
    
    except Exception as e:
        logger.exception("Error handling message: %s", e)
        await update.message.reply_text("❌ Something went wrong. Try again later.")

def main():
    print("Starting bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()