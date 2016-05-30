from macropy.core.macros import *
from kafka import KafkaProducer, KafkaConsumer


macros = Macros()

host = 'localhost'
port = 9092


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


def subscribe(interests, hostname=None, port_num=None):
    hostname, port_num = insure_host_port(hostname, port_num)
    server = hostname+':'+str(port_num)
    subscription = KafkaConsumer(interests, bootstrap_servers=server, group_id=None, auto_offset_reset='earliest')
    return subscription
    # store subscriber instance in a dictionary with key as subscriber id
