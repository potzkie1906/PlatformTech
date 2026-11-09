"""Launch the Operating Systems Simulator or run its console checks."""

import sys


def main():
    if "--test" in sys.argv[1:]:
        from self_test import run_self_test
        return 0 if run_self_test() else 1

    try:
        import customtkinter as ctk
    except ImportError:
        sys.exit("Install the dependency with: python -m pip install -r requirements.txt")

    from app import App
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    App().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())