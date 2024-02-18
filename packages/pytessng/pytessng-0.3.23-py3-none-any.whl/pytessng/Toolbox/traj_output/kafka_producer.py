from kafka import KafkaProducer


# kafka 消息生产者
class KafkaMessageProducer:
    def __init__(self, bootstrap_servers:str, topic:str):
        self.producer = KafkaProducer(
            bootstrap_servers = bootstrap_servers,
            api_version = (0, 10),
            max_request_size = 20 * 1024 * 1024,
            acks = 0,  # 不等待确认
            max_in_flight_requests_per_connection=100,  # 控制最大同时未确认的请求
        )
        self.topic = topic

    # 发数据
    def send_message(self, message:str):
        try:
            self.producer.send(self.topic, message.encode('utf-8'))
            print(f"Kafka 消息发送成功.")
            return True
        except Exception as e:
            print(f"Kafka 发送消息时发生错误：{e}")
            return False

    # 关闭
    def close(self):
        self.producer.close()
