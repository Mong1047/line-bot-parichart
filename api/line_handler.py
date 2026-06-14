"""LINE Messaging API handler for Vercel."""

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from config import settings
from gemini_client import ask_gemini
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

    # Get AI response from Gemini (synchronous)
    reply_text = ask_gemini(user_message, full_context)

    # Reply via LINE
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )