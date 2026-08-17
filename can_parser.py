import re
from binascii import unhexlify
import cantools

def parse_can_log_line(line: str):
    pattern = re.compile(r"\(\s*([\d\.]+)\)\s+\w+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)")
    match = pattern.search(line.strip())
    if not match:
        return None
    timestamp = float(match.group(1))
    can_id_hex = match.group(2)
    data_hex = match.group(3)
    can_id = int(can_id_hex,16)
    data_bytes = []
    for i in range(0, len(data_hex), 2):
        byte_str = data_hex[i:i+2]
        data_bytes.append(int(byte_str, 16))

    return {
        "timestamp": timestamp,
        "can_id_hex": can_id_hex,
        "can_id": can_id,
        "data_hex": data_hex,
        "data_bytes": data_bytes
    }


def parse_log_file(file_path: str):
    result_list = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            item = parse_can_log_line(line)
            if item:
                result_list.append(item)
    return result_list


def print_report(frames, db=None):
    print(f"{'Time(s)':<12} {'CAN-ID':<8} {'Data(Hex)':<24} {'Signals'}")
    print("-"*90)
    for fr in frames:
        time_s = f"{fr['timestamp']:.6f}"
        cid_hex = fr["can_id_hex"]
        d_hex = fr["data_hex"]
        sig_text = ""
        if db is not None:
            try:
                raw_data = unhexlify(d_hex)
                sig_dict = db.decode_message(fr["can_id"], raw_data)
                sig_text = str(sig_dict)
            except Exception:
                sig_text = "NoDbcMatch"
        print(f"{time_s:<12} {cid_hex:<8} {d_hex:<24} {sig_text}")


if __name__ == "__main__":
    log_file = "can_log.txt"
    dbc_file = "test.dbc"
    db = None
    try:
        db = cantools.database.load_file(dbc_file)
        print(f"✅加载DBC成功，报文数量:{len(db.messages)}\n")
    except FileNotFoundError:
        print("⚠️未找到DBC文件，仅打印原始报文，不解析信号\n")

    try:
        frames = parse_log_file(log_file)
        print_report(frames, db)
        print(f"\n总共解析到 {len(frames)} 条CAN报文")
    except FileNotFoundError:
        print(f"未找到文件 {log_file}")
        print("请在当前目录新建 can_log.txt，填入CAN日志内容")