from src.ui.app import TranslatorApp


def main():
    app = TranslatorApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        app.destroy()


if __name__ == "__main__":
    main()
