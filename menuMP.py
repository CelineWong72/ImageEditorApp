from tkinter import *
import paintoMP
# color code: light #d9f5f7, dark #333333, subtle white #FFFAFA


class Menu:

    def __init__(self, root):
        self.root = root
        self.root.title("PAINTO verX")
        self.root.config(bg='#333333')
        self.root.geometry("800x600")
        self.root.resizable(0, 0)
        self.root.iconbitmap('moonicon_.ico')
        self.btn_state = False

        self.onImg = PhotoImage(file="darkk_button.png")
        self.offImg = PhotoImage(file="light_button.png")
        self.onBackground = PhotoImage(file="lightX.png")
        self.offBackground = PhotoImage(file="darkkX.png")
        self.startImg = PhotoImage(file="SSTARTO.png")

        self.background = Label(root, image=self.onBackground)
        self.background.pack(fill=BOTH)

        self.btn = Button(root, text="OFF", borderwidth=0, command=self.switch, bg="#CECCBE", activebackground="#CECCBE")
        self.btn.place(relx=0.874, rely=0.849)
        self.btn.config(image=self.offImg)

        self.startbtn = Button(root, borderwidth=0, command=self.start)
        self.startbtn.place(relx=0.45, rely=0.75)
        self.startbtn.config(image=self.startImg)

        self.txt = Label(root, text="Dark Mode:OFF", font="FixedSys 10", bg="#CECCBE", fg="#FFFF00")
        self.txt.place(relx=0.93, rely=0.86, anchor="center")

    def switch(self):
        if self.btn_state:
            self.btn.config(image=self.offImg, bg="#CECCBE", activebackground="#CECCBE")
            self.root.config(bg="#CECCBE")
            self.txt.config(text="Dark Mode: OFF", bg="#CECCBE")
            self.btn_state = False
            self.background.config(image=self.onBackground)
        else:
            self.btn.config(image=self.onImg, bg="#2B2B2B", activebackground="#2B2B2B")
            self.root.config(bg="#2B2B2B")
            self.txt.config(text="Dark Mode: ON", bg="#2B2B2B")
            self.btn_state = True
            self.background.config(image=self.offBackground)

    def start(self):
        self.closeWindow()
        master = paintoMP.Tk()
        paintoMP.Painto(master)

    def closeWindow(self):
        self.root.destroy()


if __name__ == "__main__":
    root = Tk()
    Menu(root)
    root.mainloop()

