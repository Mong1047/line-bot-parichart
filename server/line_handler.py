"""LINE Messaging API handler."""

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from config import settings
from ollama_client import ask_ollama
from sheet_rag import sheet_rag

# LINE SDK setup
configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    """Handle incoming text messages from LINE."""
    user_message = event.message.text

    # Search for relevant products
    product_context = sheet_rag.build_product_context()
    search_results = sheet_rag.search_products(user_message)

    # Combine context: full product list + search results
    full_context = product_context
    if search_results:
        full_context += "\n\n" + search_results

    # Get AI response (run synchronously in the event loop)
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're in an async context, create a new task
        import threading

        result_container = []

        def run_async():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            result = new_loop.run_until_complete(
                ask_ollama(user_message, full_context)
            )
            result_container.append(result)
            new_loop.close()

        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join()
        reply_text = result_container[0] if result_container else "ขออภัยครับ/คะ เกิดข้อผิดพลาด"
    else:
        reply_text = asyncio.run(ask_ollama(user_message, full_context))

    # Reply via LINE
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )