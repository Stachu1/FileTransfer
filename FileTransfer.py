import time as t, socket, sys, datetime, os, math, asyncio
from colorama import Fore, init
init()



class File:
    def __init__(self, path):
        self.name = path.split('/')[-1]
        if self.name == path:
            self.path = os.path.join(os.getcwd(), self.name)
        else:
            self.path = path
        self.size = os.path.getsize(self.path)


class Network:
    def __init__(self, role="server", file=None, server_ip=None, max_packet_size=2048):
        self.hostname = socket.gethostname()
        self.local_ip = self.get_local_ip()
        self.port = 7881
        self.max_packet_size = max_packet_size
        self.timeout = 5
        if role == "client":
            user_input = input(f"\n{Fore.BLUE}Enter reciver's IP or press ENTER to perform network scan: ")
            if len(user_input.split(".")) == 4:
                self.server_ip = user_input
            else:
                print(f"\n{Fore.MAGENTA}Sacnning...{Fore.RESET}")
                devices_online = self.scan_network()
                devide_index = int(input("Choose device from list: ")) - 1
                self.server_ip = devices_online[devide_index][1]
                self.server_hostname = devices_online[devide_index][0]
                
            self.file = File(input("Enter path to the file: "))
            self.client()
                
            
        elif role == "server":
            self.server()
    
    def server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.local_ip, self.port))
            print(f"\n{Fore.GREEN}Hostname: {Fore.RESET}{self.hostname}\n{Fore.BLUE}IP: {Fore.RESET}{self.local_ip}\n{Fore.YELLOW}Port: {Fore.RESET}{self.port}\n")
            print(f"{Fore.MAGENTA}Waiting for files...\n{Fore.RESET}")
            while True:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(self.max_packet_size).decode().split(":")
                    if data[0] == "ping":
                        conn.send(f"{self.hostname}:{self.max_packet_size}".encode())
                        continue
                        
                    file_name = data[0]
                    sender_name = data[1]
                    file_size = int(data[2])
                    file_size_c = convert_size(file_size)
                    print(f"{Fore.MAGENTA}Incoming file:\n   {Fore.GREEN}Filename: {Fore.RESET}{file_name}\n   {Fore.YELLOW}File size: {Fore.RESET}{file_size_c}\n   {Fore.GREEN}Sender's name: {Fore.RESET}{sender_name}\n   {Fore.BLUE}Sender's IP: {Fore.RESET}{addr[0]}\n\n{Fore.RESET}")
                    answer = input("Do You want to download it?(y/n): ")
                    while answer != "y" and answer != "n":
                        answer = input("\nDo You want to download it?(y/n): ")
                    if answer == "y":
                        conn.send("y".encode())
                        print(f"{Fore.YELLOW}\nDownloading...\n")
                        self.recive_file(conn, file_name, file_size)
                        print(f"{Fore.GREEN}\nDownloaded{Fore.RESET}\n\n")
                        print(f"{Fore.MAGENTA}Waiting for files...\n{Fore.RESET}")
                    elif answer == "n":
                        conn.send("n".encode())
                        print("\n\n")
                        print(f"{Fore.MAGENTA}Waiting for files...\n{Fore.RESET}")
                        
    
    def recive_file(self, conn, file_name, file_size):
        time_start = t.time()
        progress = 0
        with open("_" + file_name, "wb") as f:
            while True:
                data = conn.recv(self.max_packet_size)
                progress += len(data)
                if not data:
                    break
                else:
                    f.write(data)
                    printProgressBar(progress, file_size, time_start)
            
            
    def client(self):
        print(f"[{Fore.GREEN}File: {Fore.RESET}{self.file.name} {Fore.YELLOW}Size: {Fore.RESET}{self.file.size}] --> [{Fore.GREEN}Hostname: {Fore.RESET}{self.server_hostname} {Fore.BLUE}IP: {Fore.RESET}{self.server_ip}]")
        with socket.socket() as s:
            try:
                s.connect((self.server_ip, self.port))
            except socket.error as e:
                return False, e
            msg = f"{self.file.name}:{self.hostname}:{self.file.size}"
            s.send(msg.encode())
            r = s.recv(self.max_packet_size).decode()
            if r == "y":
                print(f"{Fore.GREEN}File accepted{Fore.RESET}")
                print(f"\n{Fore.MAGENTA}Sending...")
                self.send_file(s)
                print(f"{Fore.GREEN}Sent")
            else:
                print(f"{Fore.RED}File rejected{Fore.RESET}")
                
    
    def send_file(self, s):
        chunks = self.file.size // self.max_packet_size
        left_bytes = self.file.size - chunks * self.max_packet_size
        with open(self.file.path, "rb") as f:
            for _ in range(chunks):
                chunk = f.read(self.max_packet_size)
                s.send(chunk)
            byte = f.read(left_bytes)
            s.send(byte)
    
    
      
    def scan_network(self, p=True):
        time_start = t.time()
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(self.get_devices())
        print(f"{Fore.GREEN}\nDone\n\n{Fore.CYAN}Available devices:\n")
        active = []
        for r in results:
            if r != False:
                active.append(r)
        for index, r in enumerate(active):
            if r != False:
                print(f"{Fore.YELLOW}[{index+1}]\n{Fore.GREEN}Hostname: {Fore.RESET}{r[0]}\n{Fore.BLUE}IP: {Fore.RESET}{r[1]}{Fore.RESET}\n")
        return active
        
        
    async def get_devices(self):
        ip_mask = self.local_ip.split(".")
        ip_mask = f"{ip_mask[0]}.{ip_mask[1]}.{ip_mask[2]}." 
        results = await asyncio.gather(*(self.ping(ip_mask+str(i), self.port) for i in range(256)))
        return results
    
    
    async def ping(self, ip, port):
        try:
            r, w = await asyncio.wait_for(asyncio.open_connection(ip, port), self.timeout)
        except Exception as e:
            return False
        w.write("ping".encode())
        r = await r.read(self.max_packet_size)
        r = r.decode().split(":")
        user = [r[0], ip, r[1]]
        return user
    
    
    
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        local_ip_address = s.getsockname()[0]
        s.close()
        return local_ip_address



def time_stamp():
    return datetime.datetime.now().strftime(f"{Fore.LIGHTBLACK_EX}[%Y-%m-%d %H:%M:%S]{Fore.RESET}")


def printProgressBar (progress, total, time_start):
    percent = 100 * (progress / total)
    bar = "█" * int(percent) + "-" * (100 - int(percent))
    time_total = t.time() - time_start
    if time_total >= 60:
        time_total = f"{int(time_total // 60)}m {(time_total % 60):.2f}s"
    else:
        time_total = f"{time_total:.2f}s"

    if percent == 0:
        time_left = "--"
    else:
        time_left = (t.time() - time_start) / (percent / 100) - (t.time() - time_start)
        if time_left >= 60:
            time_left = f"{int(time_left // 60)}m {(time_left % 60):.2f}s"
        else:
            time_left = f"{time_left:.2f}s"
    print(f"{bar} {percent:.2f}%   t: {time_total}   eta: " + time_left, end="     \r")
    if progress == total: 
        print(f"{Fore.GREEN}{bar} {percent:.2f}%   t: {time_total}   eta: --      {Fore.RESET}")


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1000)))
    p = math.pow(1000, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"
        
        



if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg == "-r":
        network = Network(role="server")
    elif arg == "-s":
        network = Network(role="client")
else:
    network = Network(role="client")