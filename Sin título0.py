import tkinter.ttk as ttk
import tkinter as tk
from PIL import ImageTk, Image
import os
from tkinter import Label
root = tk.Tk()
root2= tk.Toplevel()
pestañas = ttk.Notebook(root2)
marco = ttk.Frame(pestañas)
marco2 = ttk.Frame(pestañas)


ruta=r"E:\OneDrive - Universidad de Cantabria\Recordar GIST - VARIOS\Aparcamientos\SCRIPTS PARK\Datos_2019-05-23 12-25-17\vehiculo_ID.1\screenshot0.png"
#img = Image.open(ruta)
#img = img.resize((500, 500), Image.ANTIALIAS)
#img = ImageTk.PhotoImage(file = ruta)
img = ImageTk.PhotoImage(Image.open(ruta))
label=tk.Label(marco,image=img)
tk.Button(marco, text='txt').pack()
#label.image=img2

#label.photo=img2
label.pack()
tk.Label(marco2,image=img).pack()
tk.Button(marco2, text='txt').pack()
pestañas.add(marco, text="1")
pestañas.add(marco2, text="2=")
pestañas.pack(padx=10, pady=10)
root.mainloop()

