# AioPika broker for taskiq

This lirary provides you with aio-pika broker for taskiq.

Usage:
```python
from taskiq_aio_pika import AioPikaBroker

broker = AioPikaBroker()

@broker.task
async def test() -> None:
    print("nothing")

```

## Configuration

Here's the suggested configuration making use of RabbitMQ's more modern quorum queue type.

```python
from taskiq_aio_pika import AioPikaBroker

broker = AioPikaBroker(
    queue_type=QueueType.QUORUM,
    declare_queues_kwargs={"durable": True},
)
```

Some configuration parameters to keep in mind:
* `qos` - [prefetch count](https://www.rabbitmq.com/docs/consumer-prefetch#overview), that is, the maximum number of messages that can be processed simultaneously by one worker, which makes it a measure of concurrency.
* `queue_type` - either ["classic"](https://www.rabbitmq.com/docs/classic-queues#overview) or ["quorum"](https://www.rabbitmq.com/docs/quorum-queues#overview).
* `declare_queues_args` - a `dict` of arguments that will be passed to aiopika's `AbstractChannel.declare_queue` method, which includes:
** [`x-delivery-limit`](https://www.rabbitmq.com/docs/quorum-queues#poison-message-handling) (for quorum queues) - for messages that keep getting redelivered to the consumer (e.g. due to consumer application instance crashes) this sets the maximum number of proccessing attempts after which the message will be discarded (dead-lettered); defaults to 20.

Other parameters of `AioPikaBroker`:
* `url` - URL of RabbitMQ. If `None`, "amqp://guest:guest@localhost:5672" is used.
* `result_backend` - Custom result backend.
* `task_id_generator` - Custom task ID generator.
* `exchange_name` - Name of the exchange that is used to send messages.
* `exchange_type` - type of the exchange. Used only if `declare_exchange` is True.
* `queue_name` - queue that is used to receive incoming messages.
* `routing_key` - used to bind the queue to the exchange.
* `declare_exchange` - whether you want to declare a new exchange if it doesn't exist.
* `max_priority` - maximum priority for messages.
* `delay_queue_name` - custom delay queue name.
    This queue is used to deliver messages with delays.
* `dead_letter_queue_name` - custom dead letter queue name.
    This queue is used to receive negatively acknowledged messages from the main queue.
* `declare_queues` - whether you want to declare queues even on the
    client side. May be useful for message persistence.


## Non-obvious things

You can send delayed messages and set priorities to messages using labels.

## Delays

### **Default retries**

To send delayed message, you have to specify
delay label. You can do it with `task` decorator,
or by using kicker.
In this type of delay we are using additional queue with `expiration` parameter and after with time message will be deleted from `delay` queue and sent to the main taskiq queue.
For example:

```python
broker = AioPikaBroker()

@broker.task(delay=3)
async def delayed_task() -> int:
    return 1

async def main():
    await broker.startup()
    # This message will be received by workers
    # After 3 seconds delay.
    await delayed_task.kiq()

    # This message is going to be received after the delay in 4 seconds.
    # Since we overriden the `delay` label using kicker.
    await delayed_task.kicker().with_labels(delay=4).kiq()

    # This message is going to be send immediately. Since we deleted the label.
    await delayed_task.kicker().with_labels(delay=None).kiq()

    # Of course the delay is managed by rabbitmq, so you don't
    # have to wait delay period before message is going to be sent.
```

### **Retries with `rabbitmq-delayed-message-exchange` plugin**

To send delayed message you can install `rabbitmq-delayed-message-exchange`
plugin https://github.com/rabbitmq/rabbitmq-delayed-message-exchange.

And you need to configure you broker.
There is `delayed_message_exchange_plugin` `AioPikaBroker` parameter and it must be `True` to turn on delayed message functionality.

The delay plugin can handle tasks with different delay times well, and the delay based on dead letter queue is suitable for tasks with the same delay time.
For example:

```python
broker = AioPikaBroker(
    delayed_message_exchange_plugin=True,
)

@broker.task(delay=3)
async def delayed_task() -> int:
    return 1

async def main():
    await broker.startup()
    # This message will be received by workers
    # After 3 seconds delay.
    await delayed_task.kiq()

    # This message is going to be received after the delay in 4 seconds.
    # Since we overriden the `delay` label using kicker.
    await delayed_task.kicker().with_labels(delay=4).kiq()
```

## Priorities

You can define priorities for messages using `priority` label.
Messages with higher priorities are delivered faster.
But to use priorities you need to define `max_priority` of the main queue, by passing `max_priority` parameter in broker's init.
This parameter sets maximum priority for the queue and
declares it as the prority queue.

Before doing so please read the [documentation](https://www.rabbitmq.com/priority.html#behaviour) about what
downsides you get by using prioritized queues.


```python
broker = AioPikaBroker(max_priority=10)

# We can define default priority for tasks.
@broker.task(priority=2)
async def prio_task() -> int:
    return 1

async def main():
    await broker.startup()
    # This message has priority = 2.
    await prio_task.kiq()

    # This message is going to have priority 4.
    await prio_task.kicker().with_labels(priority=4).kiq()

    # This message is going to have priority 0.
    await prio_task.kicker().with_labels(priority=None).kiq()

```
