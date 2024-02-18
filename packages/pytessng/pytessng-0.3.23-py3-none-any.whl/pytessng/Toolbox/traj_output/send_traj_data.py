import os
import time
import json
from datetime import datetime
from queue import Queue
from threading import Thread
from .kafka_producer import KafkaMessageProducer
from ...Tessng.MyMenu import Logger


class SendData:
    def __init__(self, traj_json_config:str=None, traj_kafka_config:dict=None):
        self.json_save_path = None
        self.kafka_producer = None

        self.set_config(traj_json_config, traj_kafka_config)

        self.send_data_queue = Queue()
        self.send_data_flag = True
        self.send_data_process = Thread(target=self.send_data)
        self.send_data_process.start()

    def set_config(self, traj_json_config:str, traj_kafka_config:dict):
        # Json
        if traj_json_config:
            # 获取文件夹名称
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            folder_path = os.path.join(traj_json_config, f"轨迹数据_{current_time}")
            # 创建文件夹
            os.makedirs(folder_path, exist_ok=True)
            self.json_save_path = os.path.join(folder_path, "{}.json")

        # Kakfa
        if traj_kafka_config:
            ip = traj_kafka_config["ip"]
            port = traj_kafka_config["port"]
            topic = traj_kafka_config["topic"]
            self.kafka_producer = KafkaMessageProducer(f"{ip}:{port}", topic)

    def put_data(self, traj_data:dict):
        self.send_data_queue.put(traj_data)

    def send_data(self):
        Logger.logger_network.info("The trajectory data sending thread has started.")

        while True:
            time.sleep(0.01)
            if self.send_data_queue.empty():
                if self.send_data_flag:
                    continue
                else:
                    Logger.logger_network.info("The trajectory data sending thread has been closed.")
                    break

            try:
                traj_data = self.send_data_queue.get_nowait()
            except:
                continue

            # 当前仿真计算批次
            batchNum = traj_data["batchNum"]

            t1 = time.time()
            # 需要保存为json
            if self.json_save_path:
                # 当前仿真计算批次
                file_path = self.json_save_path.format(batchNum)
                # 将JSON数据写入文件
                with open(file_path, 'w', encoding="utf-8") as file:
                    json.dump(traj_data, file, indent=4, ensure_ascii=False)

            t2 = time.time()
            # 需要上传至kafka
            if self.kafka_producer:
                traj_data_json = json.dumps(traj_data)
                self.send_data_flag = self.kafka_producer.send_message(traj_data_json)
                if not self.send_data_flag:
                    Logger.logger_network.info("Due to Kafka data sending failure, the trajectory data sending thread is closed.")
                    break

            t3 = time.time()
            json_time = round((t2 - t1) * 1000, 1)
            kafka_time = round((t3 - t2) * 1000, 1)
            print(f"仿真批次：{batchNum}，导出时间：{json_time}ms，上传时间：{kafka_time}ms，队列大小：{self.send_data_queue.qsize()}")

    def close(self):
        # 发送数据线程关闭
        self.send_data_flag = False

        # 清空队列
        while not self.send_data_queue.empty():
            time.sleep(0.01)
        Logger.logger_network.info("The trajectory data queue has been cleared.")

        # Kafka
        # if self.kafka_producer is not None:
        #     self.kafka_producer.close()
        #     Logger.logger_network.info("Kafka has been closed.")



