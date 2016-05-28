from kafka import KafkaProducer, KafkaConsumer


def publish(topics, message, host='localhost', port=9092):
    server = host+':'+str(port)
    publisher = KafkaProducer(bootstrap_servers=server)
    for topic in topics:
        publisher.send(topic, message.encode('utf-8'))


def subscribe(topic, host='localhost', port=9092):
    server = host+':'+str(port)
    subscriber = KafkaConsumer(bootstrap_servers=server, group_id=None, auto_offset_reset='earliest')
    # store subscriber instance in a dictionary with key as subscriber id
