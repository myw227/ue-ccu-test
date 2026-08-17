import serial
import serial.tools.list_ports
import threading
import time

class SerialDebugTool:
    def __init__(self):
        self.ser = None
        self.receive_running = False

    def list_com_ports(self):
        """列出本机所有串口"""
        ports = serial.tools.list_ports.comports()
        if not ports:
            print("未检测到串口设备")
            return []
        print("\n可用串口列表：")
        for idx, port in enumerate(ports):
            print(f"[{idx}] {port.device} - {port.description}")
        return ports

    def open_port(self, port_name, baudrate=115200):
        """打开串口"""
        try:
            self.ser = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                timeout=0.1
            )
            if self.ser.is_open:
                print(f"\n串口 {port_name} 打开成功，波特率:{baudrate}")
                self.receive_running = True
                # 启动接收子线程
                recv_thread = threading.Thread(target=self.receive_loop, daemon=True)
                recv_thread.start()
                return True
        except Exception as e:
            print(f"打开串口失败：{e}")
        return False

    def receive_loop(self):
        """循环接收串口数据"""
        with open("serial_log.txt", "a", encoding="utf-8") as log_file:
            while self.receive_running and self.ser and self.ser.is_open:
                data = self.ser.read_all()
                if data:
                    recv_text = data.decode("utf-8", errors="replace")
                    print(f"[RX] {recv_text}", end="")
                    log_file.write(recv_text)
                    log_file.flush()
                time.sleep(0.05)

    def send_data(self, send_str):
        """发送字符串"""
        if not (self.ser and self.ser.is_open):
            print("串口未打开")
            return
        send_bytes = (send_str + "\r\n").encode("utf-8")
        self.ser.write(send_bytes)
        print(f"[TX] {send_str}")

    def close_port(self):
        """关闭串口"""
        self.receive_running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("\n串口已关闭")


def main():
    tool = SerialDebugTool()
    ports = tool.list_com_ports()
    if not ports:
        return

    select_idx = int(input("\n请选择串口序号："))
    port_selected = ports[select_idx].device
    baud = int(input("输入波特率(默认115200):") or 115200)

    if not tool.open_port(port_selected, baud):
        return

    print("\n=====串口工具已启动=====")
    print("输入要发送的内容，直接回车发送；输入exit退出程序")
    while True:
        cmd = input()
        if cmd.strip().lower() == "exit":
            tool.close_port()
            break
        tool.send_data(cmd)


if __name__ == "__main__":
    main()