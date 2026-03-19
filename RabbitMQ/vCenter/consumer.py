import json
import asyncio
import aio_pika
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError
from create_vm import VMCreation, execute_vcenter_provisioning
from logger_config import setup_logger

logger = setup_logger("RabbitWorker")

# Thread pool for blocking Terraform/vSphere operations
executor = ThreadPoolExecutor(max_workers=10)

async def process_message(message: aio_pika.IncomingMessage):
    """Callback for processing RabbitMQ messages concurrently."""
    # Using the context manager ensures the message is acknowledged only if no exception occurs
    # Or we can handle nack manually. Here we use manual ack for more control.
    async with message.process(requeue=False):
        try:
            body = message.body.decode('utf-8')
            raw_data = json.loads(body)
            payload = VMCreation(**raw_data)
            
            logger.info(f"[{payload.transaction_uuid}] Received provisioning request for VM: {payload.vm_name}")
            
            # Offload blocking synchronous provisioning logic to the thread executor
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(executor, execute_vcenter_provisioning, payload)
            
            if "detail" in result or result.get("status") == "failed":
                logger.error(f"[{payload.transaction_uuid}] Provisioning failed for {payload.vm_name}. Details: {result}")
            else:
                logger.info(f"[{payload.transaction_uuid}] Provisioning successful for {payload.vm_name}.")
                
        except json.JSONDecodeError:
            logger.critical("Payload is not valid JSON. Dropping message.")
        except ValidationError as e:
            logger.error(f"Payload failed Pydantic validation. Dropping message. Errors: {e.errors()}")
        except Exception as e:
            logger.critical(f"Unhandled exception in worker task.", exc_info=True)

async def start_worker():
    """Initializes and starts the asynchronous RabbitMQ consumer."""
    # amqp://guest:guest@rabbitmq/ is used because it's running in docker-compose
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    
    async with connection:
        channel = await connection.channel()
        
        # Increase prefetch count to allow multiple messages to be processed in parallel
        await channel.set_qos(prefetch_count=5)
        
        queue = await channel.declare_queue("create_vm")
        
        logger.info(f"Infrastructure Worker (Async) active. Listening to queue: 'create_vm'")
        
        # Start consuming
        await queue.consume(process_message)
        
        # Keep the worker running
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            logger.info("Worker task cancelled.")
        except Exception as e:
            logger.error(f"Worker main loop error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(start_worker())
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully via KeyboardInterrupt.")