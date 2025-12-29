import subprocess
import psutil
import platform
import os
import pygetwindow as gw
import json

def get_os():
    os_name = platform.system()
    return os_name

USER_APP_KEYWORDS = {
    "chrome",
    "msedge",
    "code",
    "terminal",
    "python",
    "chatgpt",
    "whatsapp",
    "explorer",
}

#just a fallback if get_open_windows_windows() fails; can still give maybe bad data
def get_user_processes_windows():
    processes = []

    for proc in psutil.process_iter(['name','exe']):
        try:
            name = proc.info['name']
            exe = proc.info['exe']
            if not name or not exe:
                continue
            
            name_l = name.lower()
            exe_l = exe.lower()

            if any(k in name_l for k in USER_APP_KEYWORDS):
                processes.append(name)
                continue
            
            if exe_l.startswith(("c:\\users",)):
                processes.append(name)
        
        except (psutil.NoSuchProcess,psutil.AccessDenied):
            continue
    
    return list(set(processes))

# even shows searching tabs on google
def get_open_windows_windows():
    return [w.title for w in gw.getAllWindows() if w.title and w.title.strip()]

#fallback; need to construct main function
def get_user_processes_linux():
    processes = []
    for proc in psutil.process_iter(['name','uids']):
        try:
            if proc.info['uids'].real != os.getuid():
                continue

            name = proc.info['name']
            if name:
                processes.append(name)
            
        except (psutil.NoSuchProcess,psutil.AccessDenied):
            continue
    
    return list(set(processes))

if __name__ == "__main__":
    engine_file = "decision_engine.py"

    os_name = get_os().lower()
    if os_name == "windows":
        processes = get_open_windows_windows()
        if not processes:
            processes = get_user_processes_windows()
    elif os_name == "linux": # needs a main function this is fallback temp only
        processes = get_user_processes_linux()
    else:
        print("ERROR: OS UNDETECTED")

    # print(processes)

    data = {
        "processes" : list(set(processes))
    }

    result = subprocess.run(
        ["python",engine_file],
        input=json.dumps(data),
        capture_output=True,
        text=True
    )
    print(result.stdout)