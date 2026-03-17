import aio_pika
import asyncio
import json
import sys


# def pub():
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
#     channel = connection.channel()
#     channel.queue_declare(queue='test')

#     msg = {'foo': sys.argv[1]}

#     channel.basic_publish(
#         exchange='',
#         routing_key='test',
#         body=json.dumps(msg)
#     )

#     print('Sent message')
#     connection.close()  

async def pub():
    async with await aio_pika.connect_robust("amqp://guest:guest@localhost/") as conn:
        async with conn.channel() as channel:
            queue = await channel.declare_queue("test_async")

            await channel.default_exchange.publish(
                aio_pika.Message(b'{"Hello": "World async"}'),
                routing_key=queue.name
            )



if __name__ == '__main__':
    asyncio.run(pub())