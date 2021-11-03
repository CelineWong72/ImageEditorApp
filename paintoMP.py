from tkinter import *
from tkinter.ttk import Scale
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageTk
from image_slicer import join
from pixellib.semantic import semantic_segmentation
from pixellib.instance import instance_segmentation
from scipy.spatial.distance import euclidean
from imutils import perspective
from imutils import contours
from skimage import img_as_float
from skimage import io, color, morphology
import matplotlib.pyplot as plt
import PIL.ImageGrab as ImageGrab
import cv2
import numpy as np
import math
import image_slicer
import pygame
import imutils
import pytesseract

pygame.init()
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class Painto:

    def __init__(self, root):
        self.root = root
        self.name = "PAINTO verX"
        self.root.title(self.name)
        self.root.geometry("1200x700+80+0")
        self.root.configure(background='#dbf3fa')
        self.root.resizable(0, 0)
        self.root.iconbitmap('moonicon_.ico')
        self.my_menu = Menu(self.root)
        self.root.config(menu=self.my_menu)
        # imp things
        self.pen_color = "black"
        self.eraser_color = "white"
        self.shown_image = None
        self.filename = ""
        self.original_image = None
        self.processed_image = None
        self.preview_source = None
        self.is_image_selected = False
        self.drawing = False
        self.rotation_image = None
        self.rotated = False
        self.switch_mode = False
        # crop
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.crop_end_x = 0
        self.crop_end_y = 0
        self.rectangle_id = 0
        self.ratio = 0

        self.stack = []

        #menu bar
        self.file_menu = Menu(self.my_menu, tearoff=0)
        self.my_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.newfile)
        self.file_menu.add_command(label="Save", command=self.save_paint)

        self.info_menu = Menu(self.my_menu, tearoff=0)
        self.my_menu.add_cascade(label="Info", menu=self.info_menu)
        self.info_menu.add_command(label="Dimension", command=self.image_detail)

        self.his_menu = Menu(self.my_menu, tearoff=0)
        self.my_menu.add_cascade(label="Histogram", menu=self.his_menu)
        self.his_menu.add_command(label="Original", command=self.h_ori)
        self.his_menu.add_command(label="Filtered", command=self.h_filter)

        self.help_menu = Menu(self.my_menu, tearoff=0)
        self.my_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Edge Detection", command=self.g_edge)
        self.help_menu.add_command(label="Segmentation", command=self.g_segment)
        self.help_menu.add_command(label="Object Detection", command=self.g_objdetect)
        self.help_menu.add_command(label="Thinning", command=self.g_thinning)
        self.help_menu.add_command(label="Measure", command=self.g_measure)

        # adding widget to tkinter

        # DESIGN
        self.leftdes = Label(self.root, bg='#b7e9f7', height=500, width=10)
        self.leftdes.place(x=0, y=0)

        # LEFT TOOL
        self.crop_button = Button(self.root, text="Crop", bd=3, bg='white', command=self.crop_select, width=6, height=2,
                                  relief=RAISED)
        self.crop_button.place(x=10, y=5)

        self.undo_button = Button(self.root, text="Undo", bd=3, bg='white', command=self.undo, width=6, height=2, relief=RAISED)
        self.undo_button.place(x=10, y=55)

        self.shape_button = Button(self.root, text="Shape", bd=3, bg='white', command=self.shape_select, width=6, height=2, relief=RAISED)
        self.shape_button.place(x=10, y=105)

        self.transform_button = Button(self.root, text="Transform", bd=3, bg='white', command=self.transform_select, width=6, height=2,
                                   relief=RAISED)
        self.transform_button.place(x=10, y=155)

        self.filter_button = Button(self.root, text="Filter", bd=3, bg='white', command=self.filter_select,
                                       width=6, height=2, relief=RAISED)
        self.filter_button.place(x=10, y=205)

        self.adjust_button = Button(self.root, text="Adjust", bd=3, bg='white', command=self.adjust_select, width=6, height=2,
                                    relief=RAISED)
        self.adjust_button.place(x=10, y=255)

        self.sam_info = Button(self.root, text="Split\n&\nMerge", bd=3, bg='white', command=self.sam, width=6, height=3,
                                    relief=RAISED)
        self.sam_info.place(x=10, y=305)

        self.ed = Button(self.root, text="Edge\nDetection", bd=4, bg='white', command=self.edge_detect, width=6, height=2, relief=RAISED)
        self.ed.place(x=10, y=370)

        self.img_seg = Button(self.root, text="Segment", bd=4, bg='white', command=self.segmentation, width=6, height=2, relief=RAISED)
        self.img_seg.place(x=10, y=420)

        self.od = Button(self.root, text="Object\nDetection", bd=4, bg='white', command=self.object_detect, width=6,
                         height=2, relief=RAISED)
        self.od.place(x=10, y=470)

        self.thin = Button(self.root, text="Thinning", bd=4, bg='white', command=self.thinning, width=6,
                         height=2, relief=RAISED)
        self.thin.place(x=10, y=520)

        self.measurement = Button(self.root, text="Measure", bd=4, bg='white', command=self.measuretool, width=6,
                              height=2, relief=RAISED)
        self.measurement.place(x=10, y=570)

        self.switch_button = Button(self.root, text="MODE", bd=4, bg='white', command=self.mode, width=6, height=2, relief=RAISED)
        self.switch_button.place(x=10, y=625)

        # DESIGN
        self.rightdes = Label(self.root, bg='#b7e9f7', height=500, width=100)
        self.rightdes.place(x=910, y=0)

        # RIGHT TOOL
        self.color_frame = LabelFrame(self.root, text='Palette', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.color_frame.place(x=930, y=30, width=250, height=180)

        colors = ['#FFFFFF', '#C0C0C0', '#808080', '#000000', '#FF0000', '#FFA500', '#FFFF00', '#008000', '#0000FF',
                  '#800080', '#800000', '#808000', '#00FF00', '#00FFFF', '#008080', '#000080', '#FF00FF', '#DD571C']
        i = j = 0
        for color in colors:
            Button(self.color_frame, bg=color, bd=2, relief=RIDGE, width=4, height=2,
                   command=lambda col=color: self.select_color(col)).grid(row=i, column=j)
            j += 1
            if j == 6:
                i += 1
                j = 0

        self.current_color = Label(self.root, text="CURRENT COLOR", bg=self.pen_color, bd=4, relief=RIDGE, width=35,
                                   height=3)
        self.current_color.place(x=930, y=270)

        self.canvas_button = Button(self.root, text="Canvas", bd=3, bg='white', command=self.canvas_color, width=8,
                                    height=1, relief=RAISED)
        self.canvas_button.place(x=930, y=225)

        self.eraser_button = Button(self.root, text="Eraser", bd=3, bg='white', command=self.eraser, width=8, height=1,
                                    relief=RAISED)
        self.eraser_button.place(x=1020, y=225)

        self.eraser_button = Button(self.root, text="Clear", bd=3, bg='white', command=lambda: self.canvas.delete("all"),
                                    width=8, height=1, relief=RAISED)
        self.eraser_button.place(x=1110, y=225)

        # create scale for pen and eraser size
        self.pen_size_scale_frame = LabelFrame(self.root, text="size", bd=4, bg='white', font=('arial', 15, 'bold'),
                                               relief=RIDGE)
        self.pen_size_scale_frame.place(x=930, y=340, height=70, width=250)

        self.pen_size = Scale(self.pen_size_scale_frame, orient=HORIZONTAL, from_=0, to=50, length=170)
        self.pen_size.set(1)
        self.pen_size.grid(row=0, column=1, padx=15)

        # create canvas
        self.canvas = Canvas(self.root, bg='white', bd=5, relief=GROOVE, height=600, width=800)
        self.canvas.place(relx=0.41, rely=0.5, anchor=CENTER)

        # preview image
        self.canvas2 = Label(self.root, bg='white', bd=5, relief=RIDGE, height=14, width=35)
        self.canvas2.place(relx=0.88, rely=0.78, anchor=CENTER)

        # bind canvas with mouse drag
        self.canvas.bind("<B1-Motion>", self.paint)

    def g_segment(self):
        guide = cv2.imread("G sementation.png")
        cv2.imshow("Image Segmentation", guide)

    def g_edge(self):
        guide = cv2.imread("G edge detect.png")
        cv2.imshow("Edge Detection", guide)

    def g_objdetect(self):
        guide = cv2.imread("G object detect.png")
        cv2.imshow("Object Detection", guide)

    def g_thinning(self):
        guide = cv2.imread("G thinning.png")
        cv2.imshow("Thinning", guide)

    def g_measure(self):
        guide = cv2.imread("G measure.png")
        cv2.imshow("Measure", guide)

    def play(self):
        sound = pygame.mixer.Sound("buttonclick.wav")
        pygame.mixer.Sound.play(sound)
        pygame.mixer.music.stop()

    def paint(self, event):
        x1, y1 = (event.x - 2), (event.y - 2)
        x2, y2 = (event.x + 2), (event.y + 2)

        self.canvas.create_oval(x1, y1, x2, y2, fill=self.pen_color, outline=self.pen_color, width=self.pen_size.get())

    def select_color(self, col):
        self.pen_color = col
        self.current_color.config(bg=col)

    def eraser(self):
        self.play()
        self.pen_color = self.eraser_color

    def canvas_color(self):
        self.play()
        color = colorchooser.askcolor()
        self.canvas.configure(background=color[1])
        self.eraser_color = color[1]

    def save_paint(self):
        try:
            files = [('JPEG', ('*.jpg', '*.jpeg', '*.jpe')), ('PNG', '*.png'), ('BMP', ('*.bmp', '*.jdib')), ('GIF', '*.gif')]
            # self.canvas.update()
            filename = filedialog.asksaveasfilename(filetypes=files, defaultextension=files)
            # print(filename)
            x = self.root.winfo_rootx() + self.canvas.winfo_rootx()
            # print(x, self.canvas.winfo_x())
            y = self.root.winfo_rooty() + self.canvas.winfo_rooty()
            # print(y)
            x1 = x + self.canvas.winfo_width()
            # print(x1)
            y1 = y + self.canvas.winfo_height()
            # print(y1)
            ImageGrab.grab().crop((x, y, x1, y1)).save(filename)
            messagebox.showinfo('paint says ', 'image is saved as ' + str(filename))
        except:
            messagebox.showerror("PAINTO says ", "unable to save image, \nsomething went wrong")

    def newfile(self):
        filename = filedialog.askopenfilename()
        self.image = cv2.imread(filename)

        if self.image is not None:
            self.filename = filename
            self.original_image = self.image.copy()
            self.processed_image = self.image.copy()
            self.preview_source = self.image.copy()
            self.show_image()
            self.is_image_selected = True
            self.preview_image()
            self.stack.append(self.original_image)

    def show_image(self, img=None):
        if img is None:
            image = self.processed_image.copy()
        else:
            image = img

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = image.shape
        ratio = height / width

        new_width = width
        new_height = height

        if height > self.canvas.winfo_height() or width > self.canvas.winfo_width():
            if ratio < 1:
                new_width = self.canvas.winfo_width()
                new_height = int(new_width * ratio)
            else:
                new_height = self.canvas.winfo_height()
                new_width = int(new_height * (width / height))

        self.shown_image = cv2.resize(image, (new_width, new_height))
        self.shown_image = ImageTk.PhotoImage(Image.fromarray(self.shown_image))

        self.ratio = height / new_height

        if not self.rotated:
            self.canvas.config(width=new_width, height=new_height)  # restrict canvas dimension
        self.canvas.create_image(new_width / 2, new_height / 2, anchor=CENTER, image=self.shown_image)

    def preview_image(self):
        image = self.preview_source
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = image.shape
        ratio = height / width

        new_width = width
        new_height = height

        if height > self.canvas2.winfo_height() or width > self.canvas2.winfo_width():
            if ratio < 1:
                new_width = self.canvas2.winfo_width()
                new_height = int(new_width * ratio)
            else:
                new_height = self.canvas2.winfo_height()
                new_width = int(new_height * (width / height))

        self.ori_image = cv2.resize(image, (new_width, new_height))
        self.ori_image = ImageTk.PhotoImage(Image.fromarray(self.ori_image))
        self.ratio = height / new_height
        self.canvas2.config(width=new_width, height=new_height, anchor=CENTER, image=self.ori_image)

    def shape_select(self):
        top = Toplevel()
        top.title('Selection')
        top.geometry('100x100')
        top.resizable(0, 0)
        top.configure(bg='#FFFFFF')
        self.play()
        btn = Button(top, text='Rectangle', width=10, command=self.rec_select)
        btn1 = Button(top, text='Circle', width=10, command=self.circ_select)
        btn.pack(pady=5)
        btn1.pack(pady=5)
        top.mainloop()

    def rec_select(self):
        self.canvas.bind("<ButtonPress>", self.start_rec)
        self.canvas.bind("<B1-Motion>", self.rec)
        self.canvas.bind("<ButtonRelease>", self.end_rec)

    def start_rec(self, event):
        self.drawing = True
        self.rec_start_x = event.x
        self.rec_start_y = event.y

    def rec(self, event):
        if self.drawing:
            self.rec_end_x = event.x
            self.rec_end_y = event.y
            self.rectangle_id = cv2.rectangle(self.original_image, (self.rec_start_x, self.rec_start_y), (self.rec_end_x, self.rec_end_y), (0, 255, 0), -1)
        self.show_image(img=self.rectangle_id)
        self.stack.append(self.rectangle_id)

    def end_rec(self, event):
        self.drawing = False

    def circ_select(self):
        self.canvas.bind("<ButtonPress>", self.start_circ)
        self.canvas.bind("<B1-Motion>", self.circ)
        self.canvas.bind("<ButtonRelease>", self.end_circ)

    def start_circ(self, event):
        self.drawing = True
        self.c_start_x = event.x
        self.c_start_y = event.y

    def circ(self, event):
        if self.drawing:
            self.c_end_x = event.x
            self.c_end_y = event.y
            self.radius = int(math.sqrt((self.c_end_x - self.c_start_x)**2 + (self.c_end_y - self.c_start_y)**2))
            self.circle_id = cv2.circle(self.image, (self.c_start_x, self.c_start_y), self.radius, (255, 0, 0), -1)
        self.show_image(img=self.circle_id)
        self.stack.append(self.circle_id)

    def end_circ(self, event):
        self.drawing = False

    def rotation(self, angle, scale):
        self.center = (self.original_image.shape[1] / 2, self.original_image.shape[0] / 2)
        M = cv2.getRotationMatrix2D(self.center, angle, scale)
        self.rotation_image = cv2.warpAffine(self.original_image, M, (self.original_image.shape[0], self.original_image.shape[1]))
        self.show_image(img=self.rotation_image)
        self.stack.append(self.rotation_image)

    def deg45(self):
        self.rotated = True
        self.rotation(45, 1)

    def deg90(self):
        self.rotated = True
        self.rotation(90, 1)

    def deg180(self):
        self.rotated = True
        self.rotation(180, 1)

    def deg270(self):
        self.rotated = True
        self.rotation(270, 1)

    def deg360(self):
        self.rotated = True
        self.rotation(360, 1)

    def crop_select(self):
        self.play()
        self.canvas.bind("<ButtonPress>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.crop)
        self.canvas.bind("<ButtonRelease>", self.end_crop)

    def start_crop(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y

    def crop(self, event):
        if self.rectangle_id:
            self.canvas.delete(self.rectangle_id)

        self.crop_end_x = event.x
        self.crop_end_y = event.y

        self.rectangle_id = self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y, self.crop_end_x,
                                                         self.crop_end_y, width=1)

    def end_crop(self, event):
        if self.crop_start_x <= self.crop_end_x and self.crop_start_y <= self.crop_end_y:
            start_x = int(self.crop_start_x * self.ratio)
            start_y = int(self.crop_start_y * self.ratio)
            end_x = int(self.crop_end_x * self.ratio)
            end_y = int(self.crop_end_y * self.ratio)
        elif self.crop_start_x > self.crop_end_x and self.crop_start_y <= self.crop_end_y:
            start_x = int(self.crop_end_x * self.ratio)
            start_y = int(self.crop_start_y * self.ratio)
            end_x = int(self.crop_start_x * self.ratio)
            end_y = int(self.crop_end_y * self.ratio)
        elif self.crop_start_x <= self.crop_end_x and self.crop_start_y > self.crop_end_y:
            start_x = int(self.crop_start_x * self.ratio)
            start_y = int(self.crop_end_y * self.ratio)
            end_x = int(self.crop_end_x * self.ratio)
            end_y = int(self.crop_start_y * self.ratio)
        else:
            start_x = int(self.crop_end_x * self.ratio)
            start_y = int(self.crop_end_y * self.ratio)
            end_x = int(self.crop_start_x * self.ratio)
            end_y = int(self.crop_start_y * self.ratio)

        x = slice(start_x, end_x, 1)
        y = slice(start_y, end_y, 1)

        self.processed_image = self.processed_image[y, x]
        self.show_image()
        self.stack.append(self.processed_image)

    def resized_image(self):
        self.width = int(self.original_image.shape[1] * int(self.w.get()) / 100)
        self.height = int(self.original_image.shape[0] * int(self.h.get()) / 100)
        dimension = (self.width, self.height)
        self.resized = cv2.resize(self.original_image, dimension)
        self.show_image(img=self.resized)
        self.stack.append(self.resized)

    def image_detail(self):
        top = Toplevel()
        top.title('Image Dimension')
        top.geometry("200x50+200+100")
        top.resizable(0, 0)
        top.configure(bg='#FFFFFF')
        top.resizable(0, 0)
        width = self.original_image.shape[1]
        height = self.original_image.shape[0]
        lbl1 = Label(top, text=str(width))
        lbl1.place(x=50, y=10)
        lbl2 = Label(top, text="x")
        lbl2.place(x=100, y=10)
        lbl3 = Label(top, text=str(height))
        lbl3.place(x=140, y=10)

    def translate_select(self):
        tx = int(self.x.get())
        ty = int(self.y.get())
        self.translationMatrix = np.float32([[1.0, 0.0, tx], [0.0, 1.0, ty]])
        self.translatedImg = cv2.warpAffine(self.original_image, self.translationMatrix, (self.original_image.shape[1], self.original_image.shape[0]))
        self.show_image(img=self.translatedImg)
        self.stack.append(self.translatedImg)

    def affine_select(self):
        M = cv2.getAffineTransform(np.float32([[50, 50], [200, 50], [50, 200]]),
                                   np.float32([[10, 100], [200, 50], [100, 250]]))
        self.affine_image = cv2.warpAffine(self.original_image, M,
                                           (self.original_image.shape[0], self.original_image.shape[1]))
        self.show_image(img=self.affine_image)
        self.stack.append(self.affine_image)

    def perspective_select(self):
        M = cv2.getPerspectiveTransform(np.float32([[56, 65], [368, 52], [28, 387], [389, 390]]),
                                        np.float32([[0, 0], [self.original_image.shape[0], 0], [0, self.original_image.shape[1]],
                                        [self.original_image.shape[0], self.original_image.shape[1]]]))
        self.perspective_image = cv2.warpPerspective(self.original_image, M, (self.original_image.shape[0], self.original_image.shape[1]))
        self.show_image(img=self.perspective_image)
        self.stack.append(self.perspective_image)

    def cancel_select(self):
        self.show_image(img=self.original_image)
        self.stack.append(self.original_image)

    def transform_select(self):
        top = Toplevel()
        top.title('Selection')
        top.geometry("300x700+1200+0")
        top.resizable(0, 0)
        top.configure(bg='#FFFFFF')
        top.resizable(0, 0)
        self.play()
        scale_frame = LabelFrame(top, text='Scale', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        scale_frame.place(x=15, y=10, width=270, height=160)
        self.w = StringVar()
        self.h = StringVar()
        lbl1 = Label(scale_frame, text="Width")
        lbl1.place(x=10, y=10)
        e1 = Entry(scale_frame, width=20, textvariable=self.w)  # Width
        e1.place(x=100, y=10)
        lbl2 = Label(scale_frame, text="Height")
        lbl2.place(x=10, y=50)
        e2 = Entry(scale_frame, width=20, textvariable=self.h)  # Height
        e2.place(x=100, y=50)
        apply_b = Button(scale_frame, text="Apply", command=self.resized_image)
        apply_b.place(x=150, y=90)
        cancel_b = Button(scale_frame, text="Cancel", command=self.cancel_select)
        cancel_b.place(x=190, y=90)

        trans_frame = LabelFrame(top, text='Translate', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        trans_frame.place(x=15, y=180, width=270, height=160)
        self.x = StringVar()
        self.y = StringVar()
        lbl1 = Label(trans_frame, text="tx")
        lbl1.place(x=10, y=10)
        e1 = Entry(trans_frame, width=20, textvariable=self.x)
        e1.place(x=100, y=10)
        lbl2 = Label(trans_frame, text="ty")
        lbl2.place(x=10, y=50)
        e2 = Entry(trans_frame, width=20, textvariable=self.y)
        e2.place(x=100, y=50)
        apply_b = Button(trans_frame, text="Apply", command=self.translate_select)
        apply_b.place(x=150, y=90)
        cancel_b = Button(trans_frame, text="Cancel", command=self.cancel_select)
        cancel_b.place(x=190, y=90)

        rot_frame = LabelFrame(top, text='Rotate', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        rot_frame.place(x=15, y=350, width=270, height=80)
        btn = Button(rot_frame, text='45', width=5, command=self.deg45)
        btn1 = Button(rot_frame, text='90', width=5, command=self.deg90)
        btn2 = Button(rot_frame, text='180', width=5, command=self.deg180)
        btn3 = Button(rot_frame, text='270', width=5, command=self.deg270)
        btn4 = Button(rot_frame, text='360', width=5, command=self.deg360)
        btn.place(x=10, y=10)
        btn1.place(x=60, y=10)
        btn2.place(x=110, y=10)
        btn3.place(x=160, y=10)
        btn4.place(x=210, y=10)

        aff_frame = LabelFrame(top, text='Affine', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        aff_frame.place(x=15, y=440, width=270, height=80)
        btn3 = Button(aff_frame, text='Affine', width=10, command=self.affine_select)
        btn3.place(x=90, y=10)
        per_frame = LabelFrame(top, text='Perspective', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        per_frame.place(x=15, y=530, width=270, height=80)
        btn4 = Button(per_frame, text='Perspective', width=10, command=self.perspective_select)
        btn4.place(x=90, y=10)

        top.mainloop()

#######################################################
    def filter_select(self):
        self.top = Toplevel()
        self.top.title('Selection')
        self.top.configure(bg='#FFFFFF')
        self.top.geometry("890x290+80+500")
        my_frame = Frame(self.top)
        my_frame.pack(fill=BOTH, expand=1)
        my_canvas = Canvas(my_frame)
        my_canvas.pack(fill=BOTH, expand=1)
        my_scroll = Scrollbar(my_frame, orient=HORIZONTAL, command=my_canvas.xview)
        my_scroll.pack(side=BOTTOM, fill=X)
        my_canvas.configure(xscrollcommand=my_scroll.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
        second_frame = Frame(my_canvas)
        my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

        self.basic_frame = LabelFrame(second_frame, text='Basic', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.basic_frame.pack(side=LEFT, padx=15, pady=10)
        self.lowp_frame = LabelFrame(second_frame, text='Low Pass', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.lowp_frame.pack(side=LEFT, padx=15, pady=10)
        self.highp_frame = LabelFrame(second_frame, text='High Pass', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.highp_frame.pack(side=LEFT, padx=15, pady=10)
        self.ctm_frame = LabelFrame(second_frame, text='Custom', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.ctm_frame.pack(side=LEFT, padx=15, pady=10)

        self.bm_frame = LabelFrame(self.basic_frame, text='Black & White', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.bm_frame.pack(side=LEFT, padx=15, pady=10)
        self.bw_l = Button(self.bm_frame, width=100, height=100, command=self.black_white)
        self.bw_l.pack(side=LEFT, padx=15, pady=10)
        self.con_frame = LabelFrame(self.basic_frame, text='Contour', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.con_frame.pack(side=LEFT, padx=15, pady=10)
        self.con_l = Button(self.con_frame, width=100, height=100, command=self.contour)
        self.con_l.pack(side=LEFT, padx=15, pady=10)
        self.em_frame = LabelFrame(self.basic_frame, text='Emboss', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.em_frame.pack(side=LEFT, padx=15, pady=10)
        self.em_l = Button(self.em_frame, width=100, height=100, command=self.emboss)
        self.em_l.pack(side=LEFT, padx=15, pady=10)
        self.hsv_frame = LabelFrame(self.basic_frame, text='HSV', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.hsv_frame.pack(side=LEFT, padx=15, pady=10)
        self.hsv_l = Button(self.hsv_frame, width=100, height=100, command=self.hsv)
        self.hsv_l.pack(side=LEFT, padx=15, pady=10)
        self.neg_frame = LabelFrame(self.basic_frame, text='Negative', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.neg_frame.pack(side=LEFT, padx=15, pady=10)
        self.neg_l = Button(self.neg_frame, width=100, height=100, command=self.negative)
        self.neg_l.pack(side=LEFT, padx=15, pady=10)
        self.sep_frame = LabelFrame(self.basic_frame, text='Sepia', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.sep_frame.pack(side=LEFT, padx=15, pady=10)
        self.sep_l = Button(self.sep_frame, width=100, height=100, command=self.sepia)
        self.sep_l.pack(side=LEFT, padx=15, pady=10)
        self.shp_frame = LabelFrame(self.basic_frame, text='Sharpening', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.shp_frame.pack(side=LEFT, padx=15, pady=10)
        self.shp_l = Button(self.shp_frame, width=100, height=100, command=self.sharpening)
        self.shp_l.pack(side=LEFT, padx=15, pady=10)
        self.thr_frame = LabelFrame(self.basic_frame, text='Threshold', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.thr_frame.pack(side=LEFT, padx=15, pady=10)
        self.thr_l = Button(self.thr_frame, width=100, height=100, command=self.thresholding)
        self.thr_l.pack(side=LEFT, padx=15, pady=10)
        self.thrinv_frame = LabelFrame(self.basic_frame, text='Threshold Inv', font=('arial', 15), bd=5, relief=RIDGE,bg='white')
        self.thrinv_frame.pack(side=LEFT, padx=15, pady=10)
        self.thrinv_l = Button(self.thrinv_frame, width=100, height=100, command=self.thresholdinginv)
        self.thrinv_l.pack(side=LEFT, padx=15, pady=10)

        self.ave_frame = LabelFrame(self.lowp_frame, text='Average', font=('arial', 15), bd=5, relief=RIDGE,bg='white')
        self.ave_frame.pack(side=LEFT, padx=15, pady=10)
        self.ave_l = Button(self.ave_frame, width=100, height=100, command=self.average)
        self.ave_l.pack(side=LEFT, padx=15, pady=10)
        self.bil_frame = LabelFrame(self.lowp_frame, text='Bilateral', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.bil_frame.pack(side=LEFT, padx=15, pady=10)
        self.bil_l = Button(self.bil_frame, width=100, height=100, command=self.bilateral)
        self.bil_l.pack(side=LEFT, padx=15, pady=10)
        self.blu_frame = LabelFrame(self.lowp_frame, text='Blur', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.blu_frame.pack(side=LEFT, padx=15, pady=10)
        self.blu_l = Button(self.blu_frame, width=100, height=100, command=self.blur)
        self.blu_l.pack(side=LEFT, padx=15, pady=10)
        self.box_frame = LabelFrame(self.lowp_frame, text='Box Blur', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.box_frame.pack(side=LEFT, padx=15, pady=10)
        self.box_l = Button(self.box_frame, width=100, height=100, command=self.box_blur)
        self.box_l.pack(side=LEFT, padx=15, pady=10)
        self.gau_frame = LabelFrame(self.lowp_frame, text='Gaussian Blur', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.gau_frame.pack(side=LEFT, padx=15, pady=10)
        self.gau_l = Button(self.gau_frame, width=100, height=100, command=self.gaussian_blur)
        self.gau_l.pack(side=LEFT, padx=15, pady=10)
        self.med_frame = LabelFrame(self.lowp_frame, text='Median Blur', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.med_frame.pack(side=LEFT, padx=15, pady=10)
        self.med_l = Button(self.med_frame, width=100, height=100, command=self.median_blur)
        self.med_l.pack(side=LEFT, padx=15, pady=10)

        self.lap_frame = LabelFrame(self.highp_frame, text='Laplacian', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.lap_frame.pack(side=LEFT, padx=15, pady=10)
        self.lap_l = Button(self.lap_frame, width=100, height=100, command=self.laplacian)
        self.lap_l.pack(side=LEFT, padx=15, pady=10)
        self.sx_frame = LabelFrame(self.highp_frame, text='Sobel X', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.sx_frame.pack(side=LEFT, padx=15, pady=10)
        self.sx_l = Button(self.sx_frame, width=100, height=100, command=self.sobelx)
        self.sx_l.pack(side=LEFT, padx=15, pady=10)
        self.sy_frame = LabelFrame(self.highp_frame, text='Sobel Y', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.sy_frame.pack(side=LEFT, padx=15, pady=10)
        self.sy_l = Button(self.sy_frame, width=100, height=100, command=self.sobely)
        self.sy_l.pack(side=LEFT, padx=15, pady=10)
        self.sxy_frame = LabelFrame(self.highp_frame, text='Sobel X+Y', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.sxy_frame.pack(side=LEFT, padx=15, pady=10)
        self.sxy_l = Button(self.sxy_frame, width=100, height=100, command=self.sobelxy)
        self.sxy_l.pack(side=LEFT, padx=15, pady=10)

        self.bw_filter()
        self.con_filter()
        self.em_filter()
        self.hsv_filter()
        self.neg_filter()
        self.sep_filter()
        self.shp_filter()
        self.thr_filter()
        self.thrinv_filter()
        self.ave_filter()
        self.bil_filter()
        self.blu_filter()
        self.box_filter()
        self.gau_filter()
        self.med_filter()
        self.lap_filter()
        self.sx_filter()
        self.sy_filter()
        self.sxy_filter()

        self.top.mainloop()

########################################################################
    def bw_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.bwview_image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        self.bw_image = ImageTk.PhotoImage(Image.fromarray(self.bwview_image))
        self.bw_l.config(anchor=CENTER, image=self.bw_image)

    def black_white(self):
        self.filtered_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGRA2GRAY)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def con_filter(self):
        gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        retval, threshold = cv2.threshold(gray_img, 110, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        createdContour = cv2.drawContours(gray_img, contours, -1, (0, 255, 0), 2)
        self.conview_image = createdContour
        self.con_image = ImageTk.PhotoImage(Image.fromarray(self.conview_image))
        self.con_l.config(anchor=CENTER, image=self.con_image)

    def contour(self):
        gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        retval, threshold = cv2.threshold(gray_img, 110, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        createdContour = cv2.drawContours(gray_img, contours, -1, (0, 255, 0), 2)
        self.filtered_image = createdContour
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def em_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        kernel = np.array([[0, -1, -1], [1, 0, -1], [1, 1, 0]])
        self.emview_image = cv2.filter2D(image, -1, kernel)
        self.em_image = ImageTk.PhotoImage(Image.fromarray(self.emview_image))
        self.em_l.config(anchor=CENTER, image=self.em_image)

    def emboss(self):
        kernel = np.array([[0, -1, -1], [1, 0, -1], [1, 1, 0]])
        self.filtered_image = cv2.filter2D(self.original_image, -1, kernel)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def hsv_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.hsvview_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        self.hsv_image = ImageTk.PhotoImage(Image.fromarray(self.hsvview_image))
        self.hsv_l.config(anchor=CENTER, image=self.hsv_image)

    def hsv(self):
        self.filtered_image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2HSV)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def neg_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.negview_image = cv2.bitwise_not(image)
        self.neg_image = ImageTk.PhotoImage(Image.fromarray(self.negview_image))
        self.neg_l.config(anchor=CENTER, image=self.neg_image)

    def negative(self):
        self.filtered_image = cv2.bitwise_not(self.original_image)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def sep_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
        self.sepview_image = cv2.filter2D(image, -1, kernel)
        self.sep_image = ImageTk.PhotoImage(Image.fromarray(self.sepview_image))
        self.sep_l.config(anchor=CENTER, image=self.sep_image)

    def sepia(self):
        kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
        self.filtered_image = cv2.filter2D(self.original_image, -1, kernel)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def shp_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        self.shpview_image = cv2.filter2D(image, -1, kernel)
        self.shp_image = ImageTk.PhotoImage(Image.fromarray(self.shpview_image))
        self.shp_l.config(anchor=CENTER, image=self.shp_image)

    def sharpening(self):
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        self.filtered_image = cv2.filter2D(self.original_image, -1, kernel)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def thr_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        retval, threshold = cv2.threshold(gray_img, 62, 255, cv2.THRESH_BINARY)
        self.thrview_image = threshold
        self.thr_image = ImageTk.PhotoImage(Image.fromarray(self.thrview_image))
        self.thr_l.config(anchor=CENTER, image=self.thr_image)

    def thresholding(self):
        gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        retval, threshold = cv2.threshold(gray_img, 62, 255, cv2.THRESH_BINARY) # 128 max for second column
        self.filtered_image = threshold
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def thrinv_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        retval, threshold = cv2.threshold(gray_img, 62, 255, cv2.THRESH_BINARY_INV)
        self.thrinvview_image = threshold
        self.thrinv_image = ImageTk.PhotoImage(Image.fromarray(self.thrinvview_image))
        self.thrinv_l.config(anchor=CENTER, image=self.thrinv_image)

    def thresholdinginv(self):
        gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        retval, threshold = cv2.threshold(gray_img, 62, 255, cv2.THRESH_BINARY_INV)  # white to black
        self.filtered_image = threshold
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

#################################################################################

    def ave_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.aveview_image = cv2.blur(image, (9, 9))
        self.ave_image = ImageTk.PhotoImage(Image.fromarray(self.aveview_image))
        self.ave_l.config(anchor=CENTER, image=self.ave_image)

    def average(self):
        self.filtered_image = cv2.blur(self.original_image, (9, 9))
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def bil_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.bilview_image = cv2.bilateralFilter(image, 11, 75, 75)
        self.bil_image = ImageTk.PhotoImage(Image.fromarray(self.bilview_image))
        self.bil_l.config(anchor=CENTER, image=self.bil_image)

    def bilateral(self):
        self.filtered_image = cv2.bilateralFilter(self.original_image, 11, 75, 75)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def blu_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.bluview_image = cv2.blur(image, (31, 31))
        self.blu_image = ImageTk.PhotoImage(Image.fromarray(self.bluview_image))
        self.blu_l.config(anchor=CENTER, image=self.blu_image)

    def blur(self):
        self.filtered_image = cv2.blur(self.original_image, (31, 31))
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def box_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.boxview_image = cv2.boxFilter(image, 0, (7, 7))
        self.box_image = ImageTk.PhotoImage(Image.fromarray(self.boxview_image))
        self.box_l.config(anchor=CENTER, image=self.box_image)

    def box_blur(self):
        self.filtered_image = cv2.boxFilter(self.original_image, 0, (7, 7))
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def gau_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.gauview_image = cv2.GaussianBlur(image, (15, 15), 9)
        self.gau_image = ImageTk.PhotoImage(Image.fromarray(self.gauview_image))
        self.gau_l.config(anchor=CENTER, image=self.gau_image)

    def gaussian_blur(self):
        # self.filtered_image = cv2.GaussianBlur(self.original_image, (35, 35), 0)
        self.filtered_image = cv2.GaussianBlur(self.original_image, (15, 15), 9)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def med_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.medview_image = cv2.medianBlur(image, 9)
        self.med_image = ImageTk.PhotoImage(Image.fromarray(self.medview_image))
        self.med_l.config(anchor=CENTER, image=self.med_image)

    def median_blur(self):
        # self.filtered_image = cv2.medianBlur(self.original_image, 41)
        self.filtered_image = cv2.medianBlur(self.original_image, 9)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

####################################################################################

    def lap_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        self.lapview_image = cv2.Laplacian(gray, cv2.CV_8U)
        self.lap_image = ImageTk.PhotoImage(Image.fromarray(self.lapview_image))
        self.lap_l.config(anchor=CENTER, image=self.lap_image)

    def laplacian(self):
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_8U)
        # laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        # laplacian = np.uint8(np.absolute(laplacian))
        self.filtered_image = cv2.cvtColor(laplacian, cv2.COLOR_BGR2RGB)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def sx_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1)
        sobelx = np.uint8(np.absolute(sobelx))
        self.sxview_image = cv2.cvtColor(sobelx, cv2.COLOR_BGR2RGB)
        self.sx_image = ImageTk.PhotoImage(Image.fromarray(self.sxview_image))
        self.sx_l.config(anchor=CENTER, image=self.sx_image)

    def sobelx(self):
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        # sobelx = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=1)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1)
        sobelx = np.uint8(np.absolute(sobelx))
        self.filtered_image = cv2.cvtColor(sobelx, cv2.COLOR_BGR2RGB)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def sy_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1)
        sobely = np.uint8(np.absolute(sobely))
        self.syview_image = cv2.cvtColor(sobely, cv2.COLOR_BGR2RGB)
        self.sy_image = ImageTk.PhotoImage(Image.fromarray(self.syview_image))
        self.sy_l.config(anchor=CENTER, image=self.sy_image)

    def sobely(self):
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        # sobely = cv2.Sobel(gray, cv2.CV_8U, 0, 1, ksize=1)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1)
        sobely = np.uint8(np.absolute(sobely))
        self.filtered_image = cv2.cvtColor(sobely, cv2.COLOR_BGR2RGB)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def sxy_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1)
        sobelx = np.uint8(np.absolute(sobelx))
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1)
        sobely = np.uint8(np.absolute(sobely))
        sobelxy = cv2.bitwise_or(sobelx, sobely)
        self.sxyview_image = cv2.cvtColor(sobelxy, cv2.COLOR_BGR2RGB)
        self.sxy_image = ImageTk.PhotoImage(Image.fromarray(self.sxyview_image))
        self.sxy_l.config(anchor=CENTER, image=self.sxy_image)

    def sobelxy(self):
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1)
        sobelx = np.uint8(np.absolute(sobelx))
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1)
        sobely = np.uint8(np.absolute(sobely))

        sobelCombine = cv2.bitwise_or(sobelx, sobely)
        self.filtered_image = cv2.cvtColor(sobelCombine, cv2.COLOR_BGR2RGB)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

######################################################################################
    def h_ori(self):
        hist = cv2.calcHist(self.original_image, [0], None, [256], [0, 256])
        plt.plot(hist)
        plt.hist(self.original_image.flatten(), 256, [0, 256])
        plt.show()

    def h_filter(self):
        hist = cv2.calcHist(self.filtered_image, [0], None, [256], [0, 256])
        plt.plot(hist)
        plt.hist(self.filtered_image.flatten(), 256, [0, 256])
        plt.show()

    def sam(self):
        top = Toplevel()
        top.title("Split and Merge")
        top.geometry("300x300+1200+0")
        top.configure(bg="#FFFFFF")
        self.play()
        self.num = StringVar()
        self.channel_f = LabelFrame(top, text='Channel', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.channel_f.place(x=15, y=10, width=270, height=90)
        self.image_f = LabelFrame(top, text='Image', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.image_f.place(x=15, y=120, width=270, height=130)
        ch_s = Button(self.channel_f, text="Split", command=self.ch_split, width=9)
        ch_s.place(x=5, y=10)
        ch_m = Button(self.channel_f, text="Merge", command=self.ch_merge, width=9)
        ch_m.place(x=90, y=10)
        ch_save = Button(self.channel_f, text="Save", command=self.ch_save, width=9)
        ch_save.place(x=175, y=10)

        lbl1 = Label(self.image_f, text="Number of Tile")
        lbl1.place(x=5, y=10)
        e1 = Entry(self.image_f, width=20, textvariable=self.num)
        e1.place(x=110, y=10)
        im_s = Button(self.image_f, text="Split", command=self.im_split, width=9)
        im_s.place(x=5, y=50)
        im_m = Button(self.image_f, text="Merge", command=self.im_merge, width=9)
        im_m.place(x=90, y=50)
        im_save = Button(self.image_f, text="Save", command=self.im_save, width=9)
        im_save.place(x=175, y=50)

        top.mainloop()

    def resizeDisplay(self):
        img = self.original_image
        scale_percent = 50  # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        self.resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    def ch_split(self):
        # self.processing_image = cv2.convertScaleAbs(self.original_image)
        self.resizeDisplay()
        self.b, self.g, self.r = cv2.split(self.resized)
        cv2.imshow('Red', self.r)
        cv2.moveWindow('Red', 0, 0)
        cv2.imshow('Green', self.g)
        cv2.moveWindow('Green', 0, 200)
        cv2.imshow('Blue', self.b)
        cv2.moveWindow('Blue', 0, 400)

        color = ('b', 'g', 'r')
        for i, col in enumerate(color):
            histr = cv2.calcHist([self.resized], [i], None, [256], [0, 256])
            plt.plot(histr, color=col)
            plt.xlim([0, 256])
        plt.show()

    def ch_merge(self):
        self.resizeDisplay()
        b, g, r = cv2.split(self.resized)
        self.mimg = cv2.merge((r, g, b))
        cv2.imshow('Merged Image', self.mimg)
        cv2.moveWindow('Merged Image', 400, 400)

    def ch_save(self):
        cv2.imwrite(str(self.filename) + " RED IMG.png", self.r)
        cv2.imwrite(str(self.filename) + " BLUE IMG.png", self.b)
        cv2.imwrite(str(self.filename) + " GREEN IMG.png", self.g)
        cv2.imwrite(str(self.filename) + " Merged IMG.png", self.mimg)

    def adjust_select(self):
        top = Toplevel()
        top.title("Adjust Tool")
        top.geometry("300x250+1200+0")
        top.configure(bg="#FFFFFF")
        top.resizable(0, 0)
        self.play()
        self.r_label = Label(top, text="R")
        self.r_label.place(x=5, y=30)
        self.r_scale = Scale(top, from_=-100, to_=100, length=240, orient=HORIZONTAL)
        self.r_scale.place(x=50, y=30)
        self.g_label = Label(top, text="G")
        self.g_label.place(x=5, y=80)
        self.g_scale = Scale(top, from_=-100, to_=100, length=240, orient=HORIZONTAL)
        self.g_scale.place(x=50, y=80)
        self.b_label = Label(top, text="B")
        self.b_label.place(x=5, y=130)
        self.b_scale = Scale(top, from_=-100, to_=100, length=240, orient=HORIZONTAL)
        self.b_scale.place(x=50, y=130)
        apply_button = Button(top, text="Apply", command=self.apply_sam)
        apply_button.place(x=250, y=200)

    def apply_sam(self):
        self.processing_image = cv2.convertScaleAbs(self.original_image)
        b, g, r = cv2.split(self.processing_image)

        for b_value in b:
            cv2.add(b_value, self.b_scale.get(), b_value)
        for g_value in g:
            cv2.add(g_value, self.g_scale.get(), g_value)
        for r_value in r:
            cv2.add(r_value, self.r_scale.get(), r_value)

        self.processing_image = cv2.merge((b, g, r))
        self.show_image(self.processing_image)

    def im_split(self):
        self.samimg = self.filename
        self.num_tiles = int(self.num.get())
        self.tiles = image_slicer.slice(self.samimg, self.num_tiles)

        for i in range(0, self.num_tiles):
            img = self.tiles[i].image
            final_image = np.uint8(np.absolute(img))
            image = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB)
            cv2.imshow("SPLIT " + str(i), image)

    def im_merge(self):
        image = join(self.tiles)
        # image.save('watch-join.png')
        image.show(image)

    def im_save(self):
        for i in range(0, self.num_tiles):
            img = self.tiles[i].image
            final_image = np.uint8(np.absolute(img))
            image = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(str(self.filename) + str(i) + " SPLIT.png", image)
        image = join(self.tiles)
        image.save(str(self.filename) + "MERGED IMG.png")

###########################################################################################

    def edge_detect(self):
        self.top = Toplevel()
        self.top.title('Selection')
        self.top.configure(bg='#FFFFFF')
        self.top.geometry("890x290+80+500")
        self.play()
        my_frame = Frame(self.top)
        my_frame.pack(fill=BOTH, expand=1)
        my_canvas = Canvas(my_frame)
        my_canvas.pack(fill=BOTH, expand=1)
        my_scroll = Scrollbar(my_frame, orient=HORIZONTAL, command=my_canvas.xview)
        my_scroll.pack(side=BOTTOM, fill=X)
        my_canvas.configure(xscrollcommand=my_scroll.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
        second_frame = Frame(my_canvas)
        my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

        self.canny_frame = LabelFrame(second_frame, text='Canny', font=('arial', 15), bd=5, relief=RIDGE,
                                   bg='white')
        self.canny_frame.pack(side=LEFT, padx=15, pady=10)
        self.canny_l = Button(self.canny_frame, width=100, height=100, command=self.canny_detect)
        self.canny_l.pack(side=LEFT, padx=15, pady=10)
        self.concanny_frame = LabelFrame(second_frame, text='Contour Canny', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.concanny_frame.pack(side=LEFT, padx=15, pady=10)
        self.concanny_l = Button(self.concanny_frame, width=100, height=100, command=self.contourcanny_detect)
        self.concanny_l.pack(side=LEFT, padx=15, pady=10)
        self.px_frame = LabelFrame(second_frame, text='Prewitt X', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.px_frame.pack(side=LEFT, padx=15, pady=10)
        self.px_l = Button(self.px_frame, width=100, height=100, command=self.prewitX)
        self.px_l.pack(side=LEFT, padx=15, pady=10)
        self.py_frame = LabelFrame(second_frame, text='Prewitt Y', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.py_frame.pack(side=LEFT, padx=15, pady=10)
        self.py_l = Button(self.py_frame, width=100, height=100, command=self.prewitY)
        self.py_l.pack(side=LEFT, padx=15, pady=10)
        self.pxy_frame = LabelFrame(second_frame, text='Prewitt X+Y', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.pxy_frame.pack(side=LEFT, padx=15, pady=10)
        self.pxy_l = Button(self.pxy_frame, width=100, height=100, command=self.prewitXY)
        self.pxy_l.pack(side=LEFT, padx=15, pady=10)
        self.sx_frame = LabelFrame(second_frame, text='Sobel X', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.sx_frame.pack(side=LEFT, padx=15, pady=10)
        self.sx_l = Button(self.sx_frame, width=100, height=100, command=self.sobelX)
        self.sx_l.pack(side=LEFT, padx=15, pady=10)
        self.sy_frame = LabelFrame(second_frame, text='Sobel Y', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.sy_frame.pack(side=LEFT, padx=15, pady=10)
        self.sy_l = Button(self.sy_frame, width=100, height=100, command=self.sobelY)
        self.sy_l.pack(side=LEFT, padx=15, pady=10)
        self.sxy_frame = LabelFrame(second_frame, text='Sobel X+Y', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.sxy_frame.pack(side=LEFT, padx=15, pady=10)
        self.sxy_l = Button(self.sxy_frame, width=100, height=100, command=self.sobelXY)
        self.sxy_l.pack(side=LEFT, padx=15, pady=10)
        self.compare_f = LabelFrame(second_frame, text='Comparison', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        self.compare_f.pack(side=LEFT, padx=15, pady=10)

        self.var1 = IntVar()
        self.var2 = IntVar()
        self.var3 = IntVar()

        c1 = Checkbutton(self.compare_f, text="Canny", variable=self.var1, width=5, height=1)
        c1.pack(pady=5)
        c2 = Checkbutton(self.compare_f, text="Sobel", variable=self.var2, width=5, height=1)
        c2.pack(pady=5)
        c3 = Checkbutton(self.compare_f, text="Prewitt", variable=self.var3, width=5, height=1)
        c3.pack(pady=5)

        mybutton = Button(self.compare_f, text="Apply", command=self.compare_show).pack()

        self.canny_filter()
        self.concanny_filter()
        self.px_filter()
        self.py_filter()
        self.pxy_filter()
        self.slx_filter()
        self.sly_filter()
        self.slxy_filter()

        self.top.mainloop()

    def canny_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        self.canny = cv2.Canny(gray, 30, 200)
        self.c_image = ImageTk.PhotoImage(Image.fromarray(self.canny))
        self.canny_l.config(anchor=CENTER, image=self.c_image)

    def canny_detect(self):
        self.gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        self.edgeCanny = cv2.Canny(self.gray_img, 30, 200)
        self.show_image(img=self.edgeCanny)
        self.stack.append(self.edgeCanny)

    def concanny_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        self.canny = cv2.Canny(gray, 30, 200)
        contours, hierarchy = cv2.findContours(self.canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        createdc = cv2.drawContours(gray, contours, -1, (0, 255, 0), 1)
        self.cc_image = ImageTk.PhotoImage(Image.fromarray(createdc))
        self.concanny_l.config(anchor=CENTER, image=self.cc_image)

    def contourcanny_detect(self):
        self.gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        contours, hierarchy = cv2.findContours(self.edgeCanny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        createdContour = cv2.drawContours(self.gray_img, contours, -1, (0, 255, 0), 1)
        self.show_image(img=createdContour)

    def px_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        img_gaussian = cv2.GaussianBlur(gray, (3, 3), 0)
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        self.img_px = cv2.filter2D(img_gaussian, -1, kernelx)
        self.px_image = ImageTk.PhotoImage(Image.fromarray(self.img_px))
        self.px_l.config(anchor=CENTER, image=self.px_image)

    def prewitX(self):
        self.gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        img_gaussian = cv2.GaussianBlur(self.gray_img, (3, 3), 0)
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        self.img_prewittx = cv2.filter2D(img_gaussian, -1, kernelx)
        self.show_image(img=self.img_prewittx)

    def py_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        img_gaussian = cv2.GaussianBlur(gray, (3, 3), 0)
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        self.img_py = cv2.filter2D(img_gaussian, -1, kernely)
        self.py_image = ImageTk.PhotoImage(Image.fromarray(self.img_py))
        self.py_l.config(anchor=CENTER, image=self.py_image)

    def prewitY(self):
        self.gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        img_gaussian = cv2.GaussianBlur(self.gray_img, (3, 3), 0)
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        self.img_prewitty = cv2.filter2D(img_gaussian, -1, kernely)
        self.show_image(img=self.img_prewitty)

    def pxy_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        img_gaussian = cv2.GaussianBlur(gray, (3, 3), 0)
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        img_px = cv2.filter2D(img_gaussian, -1, kernelx)
        img_py = cv2.filter2D(img_gaussian, -1, kernely)
        combinationxy = cv2.bitwise_or(img_px, img_py)
        finalimg = cv2.cvtColor(combinationxy, cv2.COLOR_BGR2RGB)
        self.pxy_image = ImageTk.PhotoImage(Image.fromarray(finalimg))
        self.pxy_l.config(anchor=CENTER, image=self.pxy_image)

    def prewitXY(self):
        self.gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        img_gaussian = cv2.GaussianBlur(self.gray_img, (3, 3), 0)

        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])

        self.img_prewittx = cv2.filter2D(img_gaussian, -1, kernelx)
        self.img_prewitty = cv2.filter2D(img_gaussian, -1, kernely)

        combinationPrewit_xy = cv2.bitwise_or(self.img_prewittx, self.img_prewitty)
        self.pxy_ed_image = cv2.cvtColor(combinationPrewit_xy, cv2.COLOR_BGR2RGB)
        self.show_image(img=self.pxy_ed_image)
        self.stack.append(self.pxy_ed_image)

    def slx_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1)
        sobelx = np.uint8(np.absolute(sobelx))
        self.sxview_image = cv2.cvtColor(sobelx, cv2.COLOR_BGR2RGB)
        self.sx_image = ImageTk.PhotoImage(Image.fromarray(self.sxview_image))
        self.sx_l.config(anchor=CENTER, image=self.sx_image)

    def sobelX(self):
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        # sobelx = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=1)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1)
        sobelx = np.uint8(np.absolute(sobelx))
        self.filtered_image = cv2.cvtColor(sobelx, cv2.COLOR_BGR2RGB)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def sly_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1)
        sobely = np.uint8(np.absolute(sobely))
        self.syview_image = cv2.cvtColor(sobely, cv2.COLOR_BGR2RGB)
        self.sy_image = ImageTk.PhotoImage(Image.fromarray(self.syview_image))
        self.sy_l.config(anchor=CENTER, image=self.sy_image)

    def sobelY(self):
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        # sobely = cv2.Sobel(gray, cv2.CV_8U, 0, 1, ksize=1)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1)
        sobely = np.uint8(np.absolute(sobely))
        self.filtered_image = cv2.cvtColor(sobely, cv2.COLOR_BGR2RGB)
        self.show_image(img=self.filtered_image)
        self.stack.append(self.filtered_image)

    def slxy_filter(self):
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=1)
        sobelx = np.uint8(np.absolute(sobelx))
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=1)
        sobely = np.uint8(np.absolute(sobely))
        sobelxy = cv2.bitwise_or(sobelx, sobely)
        self.sxyview_image = cv2.cvtColor(sobelxy, cv2.COLOR_BGR2RGB)
        self.sxy_image = ImageTk.PhotoImage(Image.fromarray(self.sxyview_image))
        self.sxy_l.config(anchor=CENTER, image=self.sxy_image)

    def sobelXY(self):
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        sobel_y = np.array([[-1, -5, -1], [0, 0, 0], [1, 5, 1]])
        sobel_x = np.array([[-1, 0, 1], [-5, 0, 5], [-1, 0, 1]])
        sobely = cv2.filter2D(gray, -1, sobel_y)
        sobelx = cv2.filter2D(gray, -1, sobel_x)
        sobelCombine = cv2.bitwise_or(sobelx, sobely)
        self.sxy_ed_image = cv2.cvtColor(sobelCombine, cv2.COLOR_BGR2RGB)
        self.show_image(img=self.sxy_ed_image)
        self.stack.append(self.sxy_ed_image)

    def compare_show(self):
        if (self.var1.get() == 1) and (self.var2.get() == 1) and (self.var3.get() == 0):
            # print("CS")
            self.canny_sobel()

        elif (self.var1.get() == 1) and (self.var2.get() == 0) and (self.var3.get() == 1):
            # print("CP")
            self.canny_prewitt()

        elif (self.var1.get() == 0) and (self.var2.get() == 1) and (self.var3.get() == 1):
            # print("SP")
            self.sobel_prewitt()

        elif (self.var1.get() == 1) and (self.var2.get() == 1) and (self.var3.get() == 1):
            # print("CSP")
            self.canny_sobel_prewitt()

        else:
            # print("none")
            messagebox.showerror("PAINTO says ", "Please select at least 2 to compare!")

    def canny_sobel(self):
        top = Toplevel()
        top.title("CANNY vs SOBEL")
        top.geometry("700x400")
        top.iconbitmap('moonicon_.ico')
        top.resizable(0, 0)
        img1 = self.c_image
        img2 = self.sxy_image
        label1 = Label(top, width=300, height=250, anchor=CENTER, image=img1)
        label1.place(x=60, y=30)
        word1 = Label(top, text="CANNY", width=10, height=3)
        word1.place(x=170, y=330)
        label2 = Label(top, width=300, height=250, anchor=CENTER, image=img2)
        label2.place(x=360, y=30)
        word2 = Label(top, text="SOBEL", width=10, height=3)
        word2.place(x=470, y=330)
        top.mainloop()

    def canny_prewitt(self):
        top = Toplevel()
        top.title("CANNY vs PREWITT")
        top.geometry("700x400")
        top.iconbitmap('moonicon_.ico')
        top.resizable(0, 0)
        img1 = self.c_image
        img2 = self.pxy_image
        label1 = Label(top, width=300, height=250, anchor=CENTER, image=img1)
        label1.place(x=60, y=30)
        word1 = Label(top, text="CANNY", width=10, height=3)
        word1.place(x=170, y=330)
        label2 = Label(top, width=300, height=250, anchor=CENTER, image=img2)
        label2.place(x=360, y=30)
        word2 = Label(top, text="PREWITT", width=10, height=3)
        word2.place(x=470, y=330)
        top.mainloop()

    def sobel_prewitt(self):
        top = Toplevel()
        top.title("SOBEL vs PREWITT")
        top.geometry("700x400")
        top.iconbitmap('moonicon_.ico')
        top.resizable(0, 0)
        img1 = self.sxy_image
        img2 = self.pxy_image
        label1 = Label(top, width=300, height=250, anchor=CENTER, image=img1)
        label1.place(x=60, y=30)
        word1 = Label(top, text="SOBEL", width=10, height=3)
        word1.place(x=170, y=330)
        label2 = Label(top, width=300, height=250, anchor=CENTER, image=img2)
        label2.place(x=360, y=30)
        word2 = Label(top, text="PREWITT", width=10, height=3)
        word2.place(x=470, y=330)
        top.mainloop()

    def canny_sobel_prewitt(self):
        top = Toplevel()
        top.title("CANNY vs SOBEL vs PREWITT")
        top.geometry("1000x400")
        top.iconbitmap('moonicon_.ico')
        top.resizable(0, 0)
        img1 = self.c_image
        img2 = self.sxy_image
        img3 = self.pxy_image
        label1 = Label(top, width=300, height=250, anchor=CENTER, image=img1)
        label1.place(x=60, y=30)
        word1 = Label(top, text="CANNY", width=10, height=3)
        word1.place(x=170, y=330)
        label2 = Label(top, width=300, height=250, anchor=CENTER, image=img2)
        label2.place(x=360, y=30)
        word2 = Label(top, text="SOBEL", width=10, height=3)
        word2.place(x=470, y=330)
        label3 = Label(top, width=300, height=250, anchor=CENTER, image=img3)
        label3.place(x=660, y=30)
        word3 = Label(top, text="PREWITT", width=10, height=3)
        word3.place(x=770, y=330)
        top.mainloop()

###########################################################################################

    def segmentation(self):
        self.top = Toplevel()
        self.top.title('Selection')
        self.top.configure(bg='#FFFFFF')
        self.top.geometry("500x200+80+500")
        self.top.resizable(0, 0)
        self.play()

        semantic_frame = LabelFrame(self.top, text='Semantic', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        semantic_frame.pack(side=LEFT, padx=15, pady=10)
        c_button = Button(semantic_frame, text="Regular", command=self.semantic)
        c_button.pack(side=LEFT, padx=15, pady=10)
        c2_button = Button(semantic_frame, text="Overlay", command=self.semantic_ovl)
        c2_button.pack(side=LEFT, padx=15, pady=10)
        instance_frame = LabelFrame(self.top, text='Instance', font=('arial', 15), bd=5, relief=RIDGE, bg='white')
        instance_frame.pack(side=LEFT, padx=15, pady=10)
        f_button = Button(instance_frame, text="Face", command=self.face_detect)
        f_button.pack(side=LEFT, padx=15, pady=10)
        p_button = Button(instance_frame, text="Regular", command=self.instance)
        p_button.pack(side=LEFT, padx=15, pady=10)
        p_button = Button(instance_frame, text="Overlay", command=self.instance_ovl)
        p_button.pack(side=LEFT, padx=15, pady=10)
        self.top.mainloop()

    def face_detect(self):
        faceimg = self.filename
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        img = cv2.imread(faceimg)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 7)
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w, y+h), (255, 0, 0), 2)
        self.show_image(img=img)
        self.stack.append(img)

    def semantic(self):
        self.segimg = self.filename
        segment_img = semantic_segmentation()
        segment_img.load_pascalvoc_model("deeplabv3_xception_tf_dim_ordering_tf_kernels.h5")
        segmask, output = segment_img.segmentAsPascalvoc(self.segimg)
        self.show_image(img=output)
        self.stack.append(output)

    def semantic_ovl(self):
        self.segimg = self.filename
        segment_img = semantic_segmentation()
        segment_img.load_pascalvoc_model("deeplabv3_xception_tf_dim_ordering_tf_kernels.h5")
        segmask, output = segment_img.segmentAsPascalvoc(self.segimg, overlay=True)
        self.show_image(img=output)
        self.stack.append(output)

    def instance(self):
        self.segimg = self.filename
        int_img = instance_segmentation()
        int_img.load_model("mask_rcnn_coco.h5")
        segmask, output = int_img.segmentImage(self.segimg)
        self.show_image(img=output)
        self.stack.append(output)

    def instance_ovl(self):
        self.segimg = self.filename
        int_img = instance_segmentation()
        int_img.load_model("mask_rcnn_coco.h5")
        segmask, output = int_img.segmentImage(self.segimg, show_bboxes=True)
        self.show_image(img=output)
        self.stack.append(output)

###########################################################################################

    def object_detect(self):
        self.play()
        img = self.original_image
        img = cv2.resize(img, (600, 400))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 13, 15, 15)

        edged = cv2.Canny(gray, 30, 200)
        contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        screenCnt = None

        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)

            if len(approx) == 4:
                screenCnt = approx
                break

        if screenCnt is None:
            detected = 0
            print("No contour detected")
        else:
            detected = 1

        if detected == 1:
            cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 3)

        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1)
        new_image = cv2.bitwise_and(img, img, mask=mask)

        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

        self.text = pytesseract.image_to_string(Cropped, config='--psm 11')
        img = cv2.resize(img, (500, 300))
        Cropped = cv2.resize(Cropped, (400, 200))
        cv2.imshow('car', img)
        cv2.imshow('Cropped', Cropped)
        cv2.imwrite('Cropped_.jpg', Cropped)
        self.detected_cpn()

    def detected_cpn(self):
        top = Toplevel()
        top.title('Number')
        top.geometry('320x100+200+100')
        top.resizable(0, 0)
        top.configure(bg='#FFFFFF')
        number = self.text
        lbl1 = Label(top, text="Detected License Plate Number", font=("arial", 15))
        lbl1.place(x=15, y=10)
        lbl2 = Label(top, text=str(number), font=("arial", 15))
        lbl2.place(x=100, y=50)
        top.mainloop()

    # def measure(self, image):
    #     img = image
    #     blur = cv2.GaussianBlur(img, (9, 9), 0)
    #     edged = cv2.Canny(blur, 50, 100)
    #     edged = cv2.dilate(edged, None, iterations=1)
    #     edged = cv2.erode(edged, None, iterations=1)
    #     # Find contours
    #     cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #     cnts = imutils.grab_contours(cnts)
    #     # Sort contours from left to right as leftmost contour is reference object
    #     (cnts, _) = contours.sort_contours(cnts)
    #     # Remove contours which are not large enough
    #     cnts = [x for x in cnts if cv2.contourArea(x) > 100]
    #
    #     ref_object = cnts[0]
    #     box = cv2.minAreaRect(ref_object)
    #     box = cv2.boxPoints(box)
    #     box = np.array(box, dtype="int")
    #     box = perspective.order_points(box)
    #     (tl, tr, br, bl) = box
    #     dist_in_pixel = euclidean(tl, tr)
    #     dist_in_cm = 2
    #     pixel_per_cm = dist_in_pixel / dist_in_cm
    #
    #     for cnt in cnts:
    #         box = cv2.minAreaRect(cnt)
    #         box = cv2.boxPoints(box)
    #         box = np.array(box, dtype="int")
    #         box = perspective.order_points(box)
    #         (tl, tr, br, bl) = box
    #         cv2.drawContours(img, [box.astype("int")], -1, (0, 0, 255), 2)
    #         mid_pt_horizontal = (tl[0] + int(abs(tr[0] - tl[0]) / 2), tl[1] + int(abs(tr[1] - tl[1]) / 2))
    #         mid_pt_verticle = (tr[0] + int(abs(tr[0] - br[0]) / 2), tr[1] + int(abs(tr[1] - br[1]) / 2))
    #         wid = euclidean(tl, tr) / pixel_per_cm
    #         ht = euclidean(tr, br) / pixel_per_cm
    #         cv2.putText(img, "{:.1f}cm".format(wid), (int(mid_pt_horizontal[0] - 15), int(mid_pt_horizontal[1] - 10)),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    #         cv2.putText(img, "{:.1f}cm".format(ht), (int(mid_pt_verticle[0] + 10), int(mid_pt_verticle[1])),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    #
    #     self.show_images([img], "SIZE")

    def thinning(self):
        self.play()
        self.is_grey_scale()
        image_binary = self.thin_image < 0.5
        out_thin = morphology.thin(image_binary)
        data = np.arange(9).reshape((3, 3))
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        plt.axis('off')
        plt.imshow(out_thin, cmap='gray')
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        a = filedialog.asksaveasfilename(filetypes=(("PNG Image", "*.png"), ("All Files", "*.*")), defaultextension='.png', title="Window-2")
        plt.savefig(a, bbox_inches=extent)
        plt.show()

    def is_grey_scale(self):
        path = self.filename
        img = cv2.imread(path)
        r, g, b = cv2.split(img)
        # spliting b,g,r and getting differences between them
        r_g = np.count_nonzero(abs(r - g))
        r_b = np.count_nonzero(abs(r - b))
        g_b = np.count_nonzero(abs(g - b))
        diff_sum = float(r_g + r_b + g_b)
        # finding ratio of diff_sum with respect to size of image
        ratio = diff_sum / img.size
        if ratio > 0.005:
            label = 'color'
            # print(label)
            self.thin_image = img_as_float(color.rgb2gray(io.imread(path)))
        else:
            label = 'grey'
            # print(label)
            self.thin_image = img_as_float((io.imread(path)))

    def measuretool(self):
        top = Toplevel()
        top.title('Selection')
        top.geometry('100x150')
        top.resizable(0, 0)
        top.configure(bg='#FFFFFF')
        self.play()
        btn1 = Button(top, text='Canny', width=10, command=self.canny_measure)
        btn2 = Button(top, text='Sobel', width=10, command=self.sobel_measure)
        btn3 = Button(top, text='Prewitt', width=10, command=self.prewitt_measure)
        btn1.pack(pady=5)
        btn2.pack(pady=5)
        btn3.pack(pady=5)
        top.mainloop()

    def canny_measure(self):
        image_canny = self.original_image
        gray = cv2.cvtColor(image_canny, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        edged = cv2.Canny(blur, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        self.sort_contours(image_canny, cnts, "CANNY")

    def sobel_measure(self):
        image_sobel = self.original_image
        gray = cv2.cvtColor(image_sobel, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        sobelx = cv2.Sobel(blur, cv2.CV_64F, 1, 0, ksize=1)
        sobelx = np.uint8(np.absolute(sobelx))
        sobely = cv2.Sobel(blur, cv2.CV_64F, 0, 1, ksize=1)
        sobely = np.uint8(np.absolute(sobely))
        sobelxy = cv2.bitwise_or(sobelx, sobely)
        edged = cv2.dilate(sobelxy, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        self.sort_contours(image_sobel, cnts, "SOBEL")

    def prewitt_measure(self):
        image_prewitt = self.original_image
        gray = cv2.cvtColor(image_prewitt, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        img_prewittx = cv2.filter2D(blur, -1, kernelx)
        img_prewitty = cv2.filter2D(blur, -1, kernely)
        pxy = cv2.bitwise_or(img_prewittx, img_prewitty)
        edged = cv2.dilate(pxy, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        self.sort_contours(image_prewitt, cnts, "PREWITT")

    def sort_contours(self, image, cnt, edged):
        # Sort contours from left to right as leftmost contour is reference object
        img = image
        cnts = cnt
        edge_name = edged
        (cnts, _) = contours.sort_contours(cnts)
        # Remove contours which are not large enough
        cnts = [x for x in cnts if cv2.contourArea(x) > 100]
        ref_object = cnts[0]
        box = cv2.minAreaRect(ref_object)
        box = cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)
        (tl, tr, br, bl) = box
        dist_in_pixel = euclidean(tl, tr)
        dist_in_cm = 2
        pixel_per_cm = dist_in_pixel / dist_in_cm

        # Draw remaining contours

        for cnt in cnts:
            box = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            box = perspective.order_points(box)
            (tl, tr, br, bl) = box
            cv2.drawContours(img, [box.astype("int")], -1, (0, 0, 255), 2)
            mid_pt_horizontal = (tl[0] + int(abs(tr[0] - tl[0]) / 2), tl[1] + int(abs(tr[1] - tl[1]) / 2))
            mid_pt_verticle = (tr[0] + int(abs(tr[0] - br[0]) / 2), tr[1] + int(abs(tr[1] - br[1]) / 2))
            wid = euclidean(tl, tr) / pixel_per_cm
            ht = euclidean(tr, br) / pixel_per_cm
            cv2.putText(img, "{:.1f}cm".format(wid), (int(mid_pt_horizontal[0] - 15), int(mid_pt_horizontal[1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            cv2.putText(img, "{:.1f}cm".format(ht), (int(mid_pt_verticle[0] + 10), int(mid_pt_verticle[1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            self.show_images([img], edge_name)

    def show_images(self, images, name):
        ed = name
        for i, img in enumerate(images):
            cv2.imshow("image_" + str(ed), img)
            cv2.moveWindow("image_" + str(ed), 400, 400)
            cv2.imwrite("image_" + str(ed) + ".jpg", img)
            cv2.waitKey(0)
            # cv2.destroyAllWindows()

###########################################################################################

    def undo(self):
        self.play()
        self.stack.pop()
        self.show_image(self.stack[-1])

    def mode(self):
        if self.switch_mode:
            self.root.configure(background='#dbf3fa')
            self.leftdes.configure(bg='#b7e9f7')
            self.rightdes.configure(bg='#b7e9f7')
            self.switch_mode = False
            self.play()
        else:
            self.root.configure(background='#444444')
            self.leftdes.configure(bg='#333333')
            self.rightdes.configure(bg='#333333')
            self.switch_mode = True
            self.play()


if __name__=="__main__":
    root = Tk()
    Painto(root)
    root.mainloop()
