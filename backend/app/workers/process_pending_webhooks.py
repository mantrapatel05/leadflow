import asyncio

from app.services.webhook_processor import process_pending_webhooks


async def main():
    result = await process_pending_webhooks(batch_size=20)
    print("Webhook processing completed")
    print(f"Attempted: {result['attempted']}")
    print(f"Processed: {result['processed']}")
    print(f"Unsuccessful: {result['unsuccessful']}")


if __name__ == "__main__":
    asyncio.run(main())