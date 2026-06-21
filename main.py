import sys
import customtkinter as ctk
from gui.app import BoardingHouseApp

ctk.set_appearance_mode("Light")

if __name__ == "__main__":
    no_session = "--no-session" in sys.argv
    app = BoardingHouseApp(no_session=no_session)
    app.mainloop()
