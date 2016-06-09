from macropy.core.macros import *
from kafka import KafkaProducer, KafkaConsumer, TopicPartition


macros = Macros()

host = 'localhost'
port = 9092
partition = 0


@macros.expr
def insure_host_port(hostname, port_num):
    if hostname not in locals():
        hostname = host
    if port_num not in locals():
        port_num = port
    return hostname, port_num


def publish(topics, message, hostname=None, port_num=None):
    hostname, port_num = insure_host_port(hostname, port_num)
    server = hostname+':'+str(port_num)
    publisher = KafkaProducer(bootstrap_servers=server)
    for topic in topics:
        publisher.send(topic, message.encode('utf-8'))


def poll(topic, offset=0, hostname=None, port_num=None, max_timeout=100):
    hostname, port_num = insure_host_port(hostname, port_num)
    server = hostname+':'+str(port_num)
    topic_partition = TopicPartition(topic, partition)

    consumer = KafkaConsumer(bootstrap_servers=server, group_id=None)
    consumer.assign([topic_partition])
    consumer.seek(topic_partition, offset)
    msgs = consumer.poll(max_timeout).values()
    consumer.close()
    if len(msgs) > 0:
        return msgs[0]
    else:
        return {}
