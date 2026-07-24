from src.ui.app import TranslatorApp
from src.ui.splash import SplashWindow, models_missing


def main():
    missing = models_missing()
    if missing:
        splash = SplashWindow(missing)
        splash.run()

    app = TranslatorApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            app.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    main()
