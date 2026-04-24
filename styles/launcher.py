import os
import signal
import subprocess
import sys
import time
import webbrowser


DEFAULT_PORT = 8501


def start_streamlit(ui_relpath="styles/UI.py", port=DEFAULT_PORT, open_browser=True):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ui_path = os.path.join(base_dir, ui_relpath)

    if not os.path.exists(ui_path):
        print(f"[launcher] Streamlit UI file not found at: {ui_path}")
        return None

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        ui_path,
        "--server.port",
        str(port),
    ]

    try:
        creationflags = 0
        preexec_fn = None
        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            preexec_fn = os.setsid

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=base_dir,
            preexec_fn=preexec_fn,
            creationflags=creationflags,
            text=True,
        )
    except FileNotFoundError:
        print(
            "[launcher] Could not start Streamlit: 'streamlit' is not installed in this Python environment."
        )
        print("[launcher] Install it with: pip install streamlit")
        return None
    except Exception as exc:
        print(f"[launcher] Failed to start Streamlit subprocess: {exc}")
        return None

    if open_browser:
        url = f"http://localhost:{port}"

        def try_open():
            time.sleep(1.0)
            webbrowser.open(url)

        import threading

        threading.Thread(target=try_open, daemon=True).start()

    print(
        f"[launcher] Streamlit started (pid={proc.pid}) serving {ui_path} on port {port}"
    )
    return proc


def stop_streamlit(proc):
    if proc is None:
        return

    print(f"[launcher] Stopping Streamlit (pid={proc.pid})...")
    try:
        if os.name == "nt":
            proc.send_signal(signal.CTRL_BREAK_EVENT)
            proc.wait(timeout=3)
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

    try:
        stdout, stderr = proc.communicate(timeout=1)
    except Exception:
        stdout, stderr = ("", "")

    if stdout:
        print("[launcher][streamlit stdout]:")
        print(stdout)
    if stderr:
        print("[launcher][streamlit stderr]:")
        print(stderr)

    print("[launcher] Streamlit stopped.")


def run_ui():
    proc = start_streamlit(ui_relpath=os.path.join("styles", "UI.py"))

    try:
        print("[launcher] UI started. Press Ctrl+C to exit and stop Streamlit.")
        while True:
            if proc is not None:
                poll = proc.poll()
                if poll is not None:
                    print(f"[launcher] Streamlit process exited with code {poll}.")
                    break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[launcher] KeyboardInterrupt received. Shutting down...")
    finally:
        stop_streamlit(proc)
        print("[launcher] Exiting.")
