import re

def parse_can_log_line(line: str):
    """
    解析单行CAN日志，适配类似格式示例：
    (1234.567890) can0 123#1122334455667788
    """
    pattern = re.compile(r"\(\s*([\d\.]+)\)\s+\w+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)")
    match = pattern.search(line.strip())
    if not match:
        return None
    timestamp = float(match.group(1))
    can_id = match.group(2)
    data_hex = match.group(3)

    data_bytes = []
    for i in range(0, len(data_hex), 2):
        byte_str = data_hex[i:i+2]
        data_bytes.append(int(byte_str, 16))

    return {
        "timestamp": timestamp,
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


def print_report(frames):
    print(f"{'Time(s)':<12} {'CAN-ID':<8} {'Data(Hex)':<24} {'Data Bytes'}")
    print("-"*70)
    for fr in frames:
        time_s = f"{fr['timestamp']:.6f}"
        cid = fr["can_id"]
        d_hex = fr["data_hex"]
        d_bytes_str = " ".join(f"{b:02X}" for b in fr["data_bytes"])
        print(f"{time_s:<12} {cid:<8} {d_hex:<24} {d_bytes_str}")


if __name__ == "__main__":
    log_file = "can_log.txt"
    try:
        frames = parse_log_file(log_file)
        print_report(frames)
        print(f"\n总共解析到 {len(frames)} 条CAN报文")
    except FileNotFoundError:
        print(f"未找到文件 {log_file}")
        print("请在当前目录新建 can_log.txt，填入CAN日志内容")