import hashlib
import ecdsa
import base58
import requests
import random
import time

# 钉钉机器人Webhook配置
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=e40d2c94bb41f0b403d44fecb3e68f33af4c6dbff053e4aaaa09c2adaa43d219"

# 更新后的目标地址
TARGET_ADDRESSES = [
    "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
    "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
    "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
]

def private_key_to_bch_address(private_key_hex):
    """将十六进制私钥转换为比特币现金（BCH）P2PKH地址"""
    try:
        # 将十六进制私钥转换为字节
        private_key_bytes = bytes.fromhex(private_key_hex)
        
        # 使用ecdsa库生成签名密钥
        sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        
        # 获取验证密钥（公钥）
        vk = sk.get_verifying_key()
        
        # 获取压缩的公钥
        if vk.pubkey.point.y() % 2 == 0:
            public_key = b'\x02' + vk.to_string()[:32]  # 偶数Y坐标，前缀0x02
        else:
            public_key = b'\x03' + vk.to_string()[:32]  # 奇数Y坐标，前缀0x03
        
        # 计算SHA-256哈希
        sha256_hash = hashlib.sha256(public_key).digest()
        
        # 计算RIPEMD-160哈希
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        ripemd160_hash = ripemd160.digest()
        
        # 添加比特币现金主网版本字节00
        network_byte = b'\x00'  # 比特币现金的版本字节仍然是0x00
        network_payload = network_byte + ripemd160_hash
        
        # 计算校验和（双重SHA-256）
        checksum = hashlib.sha256(hashlib.sha256(network_payload).digest()).digest()[:4]
        
        # 组合最终字节
        address_bytes = network_payload + checksum
        
        # Base58编码
        bch_address = base58.b58encode(address_bytes).decode('utf-8')
        
        return bch_address
    
    except Exception as e:
        print(f"地址生成错误: {e}")
        return None

def send_dingtalk_notification(message):
    """发送钉钉通知"""
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    try:
        response = requests.post(DINGTALK_WEBHOOK, json=data, headers=headers)
        if response.status_code == 200:
            print("钉钉通知发送成功")
        else:
            print(f"钉钉通知发送失败: {response.text}")
    except Exception as e:
        print(f"发送钉钉通知时出错: {e}")

def main():
    # 新的私钥范围（由你提供的起始和结束地址计算）
    start_hex = "0000000000000000000000000000000000000000000000400000000000000000"
    end_hex = "0000000000000000000000000000000000000000000003ffffffffffffffffff"
    
    start_int = int(start_hex, 16)
    end_int = int(end_hex, 16)
    
    print("BCH地址生成器已启动")
    print(f"搜索范围: {start_hex} 到 {end_hex}")
    print(f"目标地址: {TARGET_ADDRESSES}")
    
    count = 0
    start_time = time.time()
    
    try:
        while True:
            # 生成随机私钥
            private_key_int = random.randint(start_int, end_int)
            private_key_hex = format(private_key_int, '064x')
            
            # 生成BCH地址
            address = private_key_to_bch_address(private_key_hex)
            
            if not address:
                continue
            
            count += 1
            if count % 1000 == 0:
                elapsed = time.time() - start_time
                speed = count / elapsed
                print(f"已尝试 {count} 次 | 速度: {speed:.2f} 地址/秒", end="\r")
            
            # 打印当前私钥和地址（只更新这部分）
            print(f"私钥: {private_key_hex} | 地址: {address}", end="\r")
            
            # 检查是否匹配目标地址
            if address in TARGET_ADDRESSES:
                message = f"🎉 找到匹配地址! 🎉\n地址: {address}\n私钥: {private_key_hex}"
                print(f"\n{message}")
                send_dingtalk_notification(message)
                
                # 保存结果到文件
                with open("88.txt", "a") as f:
                    f.write(f"地址: {address}\n私钥: {private_key_hex}\n\n")
                
    except KeyboardInterrupt:
        print("\n程序已停止")

if __name__ == "__main__":
    main()
