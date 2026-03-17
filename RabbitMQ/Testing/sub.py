import aio_pika
import asyncio
import json

# def proccess_message(ch, method, properties, body):
#     try:
#         msg = json.loads(body)
#         print(msg["foo"])
#         ch.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
#     except Exception as e:
#         print(e)
#         ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


# def sub():
#     conn = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
#     channel = conn.channel()

#     channel.queue_declare(queue='test')
#     channel.basic_consume(
#         queue='test',
#         on_message_callback=proccess_message
    # )
    # channel.start_consuming()

async def sub():
    async with await aio_pika.connect_robust("amqp://guest:guest@localhost/") as conn:
        async with conn.channel() as channel:
            queue = await channel.declare_queue("test_async")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process() as msg:
                        try:
                            msg_data = json.loads(msg.body)
                            print(f"Consumed: {msg_data}")

                        except ConnectionError as e:
                            print(f"Errored because a connection:: {e}")
                            await msg.nack(requeue=True)
                            
                        except ValueError as e:
                            print(f"Worng value format:: {e}")


if __name__ == '__main__':
    asyncio.run(sub())