#!/usr/bin/env python3
"""BruceClaw Bridge v10 - Walkie-Talkie proxy
Sits between UI and Mimo. Injects tool knowledge into every message."""
import socketserver, http.server, json, subprocess, os, time, threading, re, urllib.request
from pathlib import Path
from datetime import datetime

PORT = 9999
HOME = Path(os.path.expanduser("~"))
MESSAGES_DIR = HOME / "bruceclaw_messages"
MESSAGES_DIR.mkdir(exist_ok=True)
SCRIPT_DIR = Path(__file__).parent

# Load API key
API_KEY = ""
for p in [HOME / ".bruceclaw_config.json", HOME / ".openclaw" / "openclaw.json"]:
    if p.exists():
        try:
            with open(p) as f:
                c = json.load(f)
            API_KEY = c.get("api_key", c.get("providers",{}).get("openai",{}).get("apiKey",""))
            if API_KEY: break
        except: pass

# Knowledge base
KB = {}
try:
    with open(SCRIPT_DIR / "knowledge_base.json") as f:
        KB = json.load(f)
except: pass

# States
answering_machine = {"enabled": False, "messages": [], "conversation_log": []}
conversation_history = []
HISTORY_FILE = HOME / "bruceclaw_history.json"

def load_history():
    global conversation_history
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                conversation_history = json.load(f)
        except: pass

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(conversation_history[-100:], f, indent=2)

def add_history(role, content):
    conversation_history.append({"role": role, "content": content, "time": datetime.now().strftime("%H:%M")})
    save_history()

def speak(text):
    cleaned = re.sub(r'[#*/\\@<>{}|~`]', '', text)
    cleaned = re.sub(r'[\U00010000-\U0010ffff]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    try: subprocess.run(["termux-tts-speak", cleaned], timeout=15)
    except: pass

# ======== TOOL EXECUTION ========
def run_tool(tool_str):
    """Execute a tool command"""
    print(f"TOOL: {tool_str}")
    try:
        parts = tool_str.split(":", 2)
        tool = parts[0].strip()
        args = parts[1].strip() if len(parts) > 1 else ""

        if tool == "answering_machine":
            answering_machine["enabled"] = args == "on"
            return f"Answering machine {'enabled' if args == 'on' else 'disabled'}"

        elif tool == "stop_voice":
            try: subprocess.run(["pkill", "-f", "termux-tts-speak"], timeout=3)
            except: pass
            try: subprocess.run(["pkill", "-f", "say"], timeout=3)
            except: pass
            return "Voice readout killed"

        elif tool == "send_sms":
            number, text = args.split(",", 1) if "," in args else (args, "Hello")
            subprocess.run(["termux-sms-send", "-n", number.strip(), text.strip()], timeout=10)
            return f"SMS sent to {number.strip()}: {text.strip()}"

        elif tool == "make_call":
            subprocess.run(["am", "start", "-a", "android.intent.action.DIAL", "-d", f"tel:{args}"], timeout=5)
            return f"Calling {args}..."

        elif tool == "battery":
            r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=3)
            d = json.loads(r.stdout)
            return f"Battery: {d.get('percentage','?')}% at {d.get('voltage',0)/1000:.1f}V"

        elif tool == "camera":
            path = str(HOME / f"photo_{int(time.time())}.jpg")
            subprocess.run(["termux-camera-photo", path], timeout=15)
            return f"Photo saved: {path}" if os.path.exists(path) else "Camera failed"

        elif tool == "location":
            r = subprocess.run(["termux-location", "-p", "gps"], capture_output=True, text=True, timeout=10)
            d = json.loads(r.stdout)
            return f"Location: {d.get('latitude','?')}, {d.get('longitude','?')}"

        elif tool == "contacts":
            r = subprocess.run(["termux-contact-list"], capture_output=True, text=True, timeout=5)
            contacts = json.loads(r.stdout)
            return f"{len(contacts)} contacts"

        elif tool == "call_log":
            r = subprocess.run(["termux-call-log", "-l", "5"], capture_output=True, text=True, timeout=5)
            calls = json.loads(r.stdout)
            return f"{len(calls)} recent calls"

        elif tool == "storage":
            r = subprocess.run(["df", "-h", "/data"], capture_output=True, text=True, timeout=3)
            lines = r.stdout.strip().split("\n")
            return lines[1] if len(lines) > 1 else "N/A"

        elif tool == "tts":
            speak(args)
            return f"Speaking: {args}"

        elif tool == "notify":
            subprocess.run(["termux-notification", "-t", "BruceClaw", "-c", args], timeout=3)
            return "Notification sent"

        elif tool == "shell":
            r = subprocess.run(args, shell=True, capture_output=True, text=True, timeout=30)
            return (r.stdout or r.stderr or "Done")[:200]

        elif tool == "open_app":
            apps = {"whatsapp":"com.whatsapp","chrome":"com.android.chrome","settings":"com.android.settings"}
            pkg = apps.get(args.lower(), args)
            subprocess.run(["monkey","-p",pkg,"-c","android.intent.category.LAUNCHER","1"], capture_output=True, timeout=5)
            return f"Opening {args}..."

        elif tool == "wifi":
            if args == "on":
                subprocess.run(["termux-wifi-enable","on"], timeout=3); return "WiFi on"
            elif args == "off":
                subprocess.run(["termux-wifi-enable","off"], timeout=3); return "WiFi off"
            r = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True, timeout=3)
            d = json.loads(r.stdout)
            return f"WiFi: {d.get('ssid','?')}"

        elif tool == "bluetooth":
            if args == "on":
                subprocess.run(["termux-bt-enable","on"], timeout=3); return "Bluetooth on"
            elif args == "off":
                subprocess.run(["termux-bt-enable","off"], timeout=3); return "Bluetooth off"
            r = subprocess.run(["termux-bt-scan"], capture_output=True, text=True, timeout=15)
            devs = json.loads(r.stdout)
            return f"Found {len(devs)} devices"

        elif tool == "screenshot":
            path = str(HOME / f"screen_{int(time.time())}.png")
            subprocess.run(["termux-screenshot", path], timeout=5)
            return f"Screenshot: {path}" if os.path.exists(path) else "Failed"

        elif tool == "learn":
            if "learned_facts" not in KB: KB["learned_facts"] = []
            KB["learned_facts"].append({"fact": args, "added": datetime.now().strftime("%Y-%m-%d %H:%M")})
            with open(SCRIPT_DIR / "knowledge_base.json", "w") as f:
                json.dump(KB, f, indent=2)
            return f"Learned: {args}"

        elif tool == "volume":
            if args == "mute": subprocess.run(["termux-volume","music","0"], timeout=3); return "Muted"
            elif args == "up": subprocess.run(["termux-volume","music","15"], timeout=3); return "Volume up"
            else: subprocess.run(["termux-volume","music","7"], timeout=3); return "Volume set"

        elif tool == "brightness":
            if args == "max": subprocess.run(["termux-brightness","255"], timeout=3); return "Max brightness"
            elif args == "min": subprocess.run(["termux-brightness","10"], timeout=3); return "Dim"
            else: subprocess.run(["termux-brightness","128"], timeout=3); return "50%"

        elif tool == "vibrate":
            ms = "2000" if "long" in args else "500"
            subprocess.run(["termux-vibrate","-d",ms], timeout=5)
            return f"Vibrating {ms}ms"

        else:
            return f"Unknown tool: {tool}"
    except Exception as e:
        return f"Error: {e}"

# System prompt for Mimo
SYSTEM_PROMPT = f"""You are BruceClaw, Bruce's AI mobile assistant. You control this phone.

CRITICAL RESPONSE RULES:
1. ALWAYS GIVE SHORT, CONCISE REPLIES (1-2 sentences max).
2. Zero fluff, direct, concise, no emojis.
3. GO VERBOSE ONLY IF THE USER EXPLICITLY ASKS FOR A DETAILED OR VERBOSE EXPLANATION.

WHEN USER ASKS TO DO SOMETHING ON THE PHONE, REPLY WITH EXACTLY THIS FORMAT:
TOOL:tool_name:arguments

AVAILABLE TOOLS:
TOOL:answering_machine:on - enable call answering
TOOL:answering_machine:off - disable call answering
TOOL:stop_voice - kill TTS voice readout immediately
TOOL:send_sms:number,message - send SMS
TOOL:make_call:number - dial a number
TOOL:battery - check battery
TOOL:camera - take photo
TOOL:location - get GPS
TOOL:contacts - list contacts
TOOL:call_log - recent calls
TOOL:storage - check storage
TOOL:tts:text - speak text
TOOL:notify:message - notification
TOOL:shell:command - run command
TOOL:open_app:name - open app
TOOL:wifi:on/off - wifi control
TOOL:bluetooth:on/off - bluetooth control
TOOL:screenshot - take screenshot
TOOL:learn:fact - remember something
TOOL:volume:up/down/mute - volume
TOOL:brightness:max/min - brightness
TOOL:vibrate:long/short - vibrate
"""

def call_mimo(messages):
    """Call LLM via fast multi-provider chain (API key first for 1s response)"""
    formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    # 1. Gemini API Key (starts with AIza or AQ.) - Immediate 1s response
    if API_KEY and (API_KEY.startswith("AIza") or API_KEY.startswith("AQ.")):
        try:
            contents = []
            for m in messages:
                role = "user" if m.get("role") in ["user", "system"] else "model"
                contents.append({"role": role, "parts": [{"text": str(m.get("content",""))}]})
            
            payload = json.dumps({
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": contents,
                "generationConfig": {"maxOutputTokens": 500, "temperature": 0.7}
            }).encode()
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={API_KEY}"
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                res = data["candidates"][0]["content"]["parts"][0]["text"]
                if res and res.strip():
                    return res
        except Exception as e:
            print(f"Gemini API error: {e}")

    # 2. OpenRouter API Key (starts with sk-or-)
    if API_KEY and API_KEY.startswith("sk-or-"):
        try:
            payload = json.dumps({
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": formatted_messages,
                "max_tokens": 500,
                "temperature": 0.7
            }).encode()
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                res = data["choices"][0]["message"]["content"]
                if res and res.strip():
                    return res
        except Exception as e:
            print(f"OpenRouter error: {e}")

    # 3. Local OmniRoute / PC LAN IP (fast 1.5s timeout)
    for host in ["127.0.0.1", "192.168.1.53"]:
        try:
            payload = json.dumps({
                "model": "auto/best-free",
                "messages": formatted_messages,
                "max_tokens": 500
            }).encode()
            req = urllib.request.Request(
                f"http://{host}:20128/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read())
                res = data["choices"][0]["message"]["content"]
                if res and res.strip():
                    return res
        except Exception:
            pass

    return "Error: Could not reach LLM. Please check your API key in ~/.bruceclaw_config.json"

class FastServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == "/kill_voice" or self.path == "/stop_voice":
                try: subprocess.run(["pkill", "-f", "termux-tts-speak"], timeout=3)
                except: pass
                try: subprocess.run(["pkill", "-f", "say"], timeout=3)
                except: pass
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write(json.dumps({"status":"ok","message":"Voice killed"}).encode())
                return
            # Serve chat UI at /chat
            if self.path == "/chat" or self.path == "/chat.html":
                chat_path = SCRIPT_DIR / "chat.html"
                if chat_path.exists():
                    with open(chat_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type","text/html")
                    self.send_header("Access-Control-Allow-Origin","*")
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_response(404)
                    self.end_headers()
                return
            
            tools_path = SCRIPT_DIR / "tools.json"
            tools = json.load(open(tools_path)) if tools_path.exists() else []
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Access-Control-Allow-Origin","*")
            self.end_headers()
            self.wfile.write(json.dumps({"status":"ok","tools":tools}).encode())
        except: pass

    def do_POST(self):
        result = ""
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length",0))))
            
            # Key Injection Endpoint
            if self.path == "/key" or "key" in body:
                new_key = body.get("key", "").strip()
                if new_key:
                    global API_KEY
                    API_KEY = new_key
                    # Save to ~/.bruceclaw_config.json
                    config_file = HOME / ".bruceclaw_config.json"
                    with open(config_file, "w") as f:
                        json.dump({"api_key": new_key}, f, indent=2)
                    
                    # Inject into OpenClaw config if present
                    openclaw_file = HOME / ".openclaw" / "openclaw.json"
                    if openclaw_file.exists():
                        try:
                            with open(openclaw_file, "r") as f:
                                oc_data = json.load(f)
                            if "models" in oc_data and "providers" in oc_data["models"]:
                                if new_key.startswith("AIza"):
                                    oc_data["models"]["providers"]["google"] = {
                                        "apiKey": new_key,
                                        "baseUrl": "https://generativelanguage.googleapis.com/v1beta"
                                    }
                                elif new_key.startswith("sk-or-"):
                                    oc_data["models"]["providers"]["openrouter"] = {
                                        "apiKey": new_key,
                                        "baseUrl": "https://openrouter.ai/api/v1"
                                    }
                            with open(openclaw_file, "w") as f:
                                json.dump(oc_data, f, indent=2)
                        except Exception:
                            pass

                    self.send_response(200)
                    self.send_header("Content-Type","application/json")
                    self.send_header("Access-Control-Allow-Origin","*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status":"ok","message":"API Key injected into BruceClaw & OpenClaw!"}).encode())
                    return

            msg = body.get("message","").strip()
            add_history("user", msg)
            print(f"USER: {msg}")

            # Send to Mimo with tool knowledge
            messages = [{"role": "user", "content": msg}]
            mimo_response = call_mimo(messages)
            print(f"MIMO: {mimo_response[:100]}")

            # Check if Mimo wants a tool
            if "TOOL:" in mimo_response:
                import re
                tool_match = re.search(r'TOOL:([^:\n]+):?([^\n]*)', mimo_response)
                if tool_match:
                    tool_name = tool_match.group(1).strip()
                    tool_args = tool_match.group(2).strip()
                    tool_result = run_tool(f"{tool_name}:{tool_args}")
                    print(f"TOOL RESULT: {tool_result}")
                    # Feed result back to Mimo
                    messages.append({"role": "assistant", "content": mimo_response})
                    messages.append({"role": "user", "content": f"Tool result: {tool_result}"})
                    final = call_mimo(messages)
                    result = final
                else:
                    result = mimo_response
            else:
                result = mimo_response

            add_history("assistant", result)
            print(f"REPLY: {result[:80]}")
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Access-Control-Allow-Origin","*")
            self.end_headers()
            self.wfile.write(json.dumps({"reply":result}).encode())
        except Exception as e:
            print(f"ERR: {e}")
            try:
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.send_header("Access-Control-Allow-Origin","*")
                self.end_headers()
                self.wfile.write(json.dumps({"reply":f"Error: {e}"}).encode())
            except: pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","POST,GET,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()

    def log_message(self,*a): pass

load_history()
try:
    subprocess.run(["termux-wake-lock"], timeout=3)
except Exception:
    pass
print(f"BruceClaw Bridge v10 at http://localhost:{PORT}")
FastServer(("0.0.0.0",PORT),H).serve_forever()
