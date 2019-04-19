import socket
import asyncio
import os

save_dir = 'training_data/teat/'
samples_per_batch = 100

class DataSaver(object):
    def __init__(self, hostname, port):
        self._done = False
        self.csv_file = open(os.path.join(save_dir, "data.csv"), 'w+')
        self.current_sample = 0
        asyncio.run(self.main(hostname,port))
        print(f"Connected to {hostname} port {port} !!!")

    async def handle(self,reader,writer):
        while self.current_sample < samples_per_batch:
            data = await reader.read(1000)
            if not data:
                continue
            path = os.path.join(save_dir, f"img{self.current_sample}.jpg")
            data[0].save(path, 'JPEG', quality=90)
            self.csv_file.write(f'{data[1]:f},{data[2]:f},{data[3]:f},{data[4]:f},{path}\n')
            print(f'{data[1]},{data[2]},{data[3]},{data[4]},{path}')
            self.current_sample += 1
        self.socket.close()
        print("SpeedOutputListener thread exiting!!!")

    async def main(self,host,port):
        self.server = await asyncio.start_server(handle,host,port)
        await self.server.serve_forever()

    
