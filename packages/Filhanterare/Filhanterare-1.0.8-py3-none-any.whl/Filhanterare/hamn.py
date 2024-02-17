import sys, socket, os

def is_windows() -> bool:
    return sys.platform == 'win32'

def is_mac() -> bool:
    return sys.platform == 'darwin'

def is_port_taken(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock.connect_ex(('localhost', port)) == 0

def bring_to_front(app_name: str):
    try:
        if is_windows():
            import win32com.client, win32con, win32gui

            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            HWND = win32gui.FindWindowEx(0, 0, 0, app_name)
            win32gui.ShowWindow(HWND, win32con.SW_RESTORE)
            win32gui.SetWindowPos(HWND, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(HWND, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(HWND, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)

        elif is_mac():
            os.system(f"osascript -e 'tell application \"{app_name}\" to activate'")

        else:
            print('Not implemented for this platform.')

        hard_exit()

    except Exception as e:
        print(e)
        hard_exit()

def hard_exit():
    sys.exit(0)

def main(app_name: str, port: int):
    if is_port_taken(port):
        bring_to_front(app_name)

