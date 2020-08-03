from multiprocessing.connection import Client
#from multiprocessing.connection import Listener
import multiprocessing
#from multiprocessing import Queue
import time
#from array import array
##from multiprocessing import Manager
import pandas as pd
from tkinter import *
from tkinter.ttk import Treeview, Scrollbar
from itertools import count
#import asyncio
#import threading
import traceback
from socket import socket, AF_INET, SOCK_STREAM
from marshal import loads
from queue import Empty
import copy
#import folium
#import ast
#from itertools import count
#import selenium.webdriver
#import time
import test_mapas
import os
from datetime import datetime
#import webbrowser
import sys
import logging
logging.basicConfig(filename=r"rec37.txt",
                    level=logging.DEBUG)
#driver = selenium.webdriver.Firefox(r"C:\Users\Andrés\Downloads\geckodriver-v0.24.0-win64\geckodriver.exe")
logging.error(f"ruta_local: {os.getcwd()}")
from_excel=False


df_mostrar = None


class TkinterApp(object):
    def __init__(self, q, q2):
        self.txt_mostrar = ('Parked cars',
                            'Cars travelling for 1st parking',
                            'Non parking cars',
                            'Cars searching parking',
                            'Free slots')
        self.lista_labels_actualizar = list()
        self.window = Tk()
        self.window.resizable(False, False)
        self.window.title("Park results")
        #generamos la carpeta para guardar los datos
        self.ruta_carpeta = os.getcwd()+"\\Datos_{}".format(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
        if not os.path.exists(self.ruta_carpeta):
            os.makedirs(self.ruta_carpeta)
        for texto, contador in zip(self.txt_mostrar, count(0)):
            self.txt_numero = StringVar()
            self.txt_numero.set(0)
            self.lista_labels_actualizar.append(self.txt_numero)
            Label(
                self.window,
                text=texto).grid(
                column=0,
                row=contador,
                padx=10,
                pady=10)
            Label(
                self.window,
                textvariable=self.txt_numero,
                borderwidth=2,
                relief="solid",
                width=5).grid(
                column=1,
                row=contador,
                padx=10)
        Button(
            self.window,
            text="Open parked cars",
            command=lambda: self.callback()).grid(
            row=5,
            columnspan=2,
            pady=20)
        self.window.after(1, self.comprobar_cola, q)
        self.window.after(1, self.lanzar_ventana_tabla_aparcados, q2)

    def comprobar_cola(self, c_queue):
        try:
            datos_cola = c_queue.get(0)
            print("rec: ",datos_cola)
            self.lista_labels_actualizar[datos_cola[0]].set(str(datos_cola[1]))
        except Exception as e:
            pass
        finally:
            self.window.after(1, self.comprobar_cola, c_queue)

    def callback(self):
        t2 = multiprocessing.Process(target=envia_peticion, args=(q2,))
        t2.start()
        # creamos una conexion inversa con el otro hilo
    def abrir_ventana_mapas(self, dataframe):
        test_mapas.lanza_mapa(self, dataframe, self.ruta_carpeta, from_excel)
        
    def OnDoubleClick(self, event):
        global df_mostrar
        try:
            df_interno = df_mostrar.round(2)
            item = self.tabla.identify('item', event.x, event.y)
            valor = int(self.tabla.item(item, "text"))
            fila = df_interno.loc[valor, :]
            # una vez clickado se abre una ventana con todos los datos de ese
            # vehiculo
            ventana_detalle = Toplevel()
            ventana_detalle.resizable(False, False)
            ventana_detalle.title("Vehicle details " + str(valor))
            mostrar = (
                "Hora Entrada",
                "T busqueda real",
                "Nodo destino",
                "Nodo aparcamiento",
                "Distancia entre nodos",
                "Intentos aparcamiento",
                "Tarifa",
                "Hora aparcamiento",
                "Duracion aparcamiento",
                "Parking",
                "Secciones intento aparcamiento",
                "Seccion de paso")
            mostrar_eng = (
                "Entry simulation hour",
                "Search time",
                "Destination node",
                "Parking node",
                "Distance between nodes",
                "Parking atteempts",
                "Tariff",
                "Parking simulation hour",
                "Parking duration",
                "off-street Parking",
                "Sections attempted",
                "Park in a cross section?")
            for texto, texto_eng, contador in zip(mostrar, mostrar_eng,count(0)):
                Label(
                    ventana_detalle,
                    text=texto_eng).grid(
                    column=0,
                    row=contador,
                    padx=10,
                    pady=10)
                Label(
                    ventana_detalle,
                    text=fila[texto],
                    borderwidth=2,
                    relief="solid",
                    width=70).grid(
                    column=1,
                    row=contador,
                    padx=10)
            Button(
                ventana_detalle,
                text="Show maps",
                command=lambda: self.abrir_ventana_mapas(fila)).grid(
                row=12,
                columnspan=2,
                pady=20)
        except BaseException:
            print(traceback.print_exc())

    def lanzar_ventana_tabla_aparcados(self, cola2):
        global df_mostrar
        try:
            diccionario = cola2.get(0)
            if from_excel:
                diccionario = pd.read_excel(
                    r"C:\Users\Tablet\Desktop\2020-06-02__14_06_16_informe.xlsx")
                df_mostrar = copy.deepcopy(diccionario)
##                print(df_mostrar)
                df_mostrar.set_index('ID', inplace=True)
            else:
                df_mostrar = copy.deepcopy(diccionario)
                df_mostrar.set_index('ID', inplace=True)
            
#            print(df_mostrar.head())
            self.ventana = Toplevel()
            self.ventana.title('Coches aparcados')
            self.ventana.resizable(False, False)
            self.tabla = Treeview(
                self.ventana,
                columns=(
                    "car",
                    "destination",
                    "park",
                    "attempts"))
            self.tabla['show'] = 'headings'
            for columna in ("car",
                    "destination",
                    "park",
                    "attempts"):
                self.tabla.column(columna, width=100, anchor='c')
            self.vsb = Scrollbar(
                self.ventana,
                orient="vertical",
                command=self.tabla.yview)
            self.vsb.pack(side='right', fill='y')
            self.tabla.bind('<Double-1>', self.OnDoubleClick)
            self.tabla.configure(yscrollcommand=self.vsb.set)
            self.tabla.heading("car", text="Car number")
            self.tabla.heading("destination", text="Destination node")
            self.tabla.heading("park", text="Parking node")
            self.tabla.heading("attempts", text="Attempts")
            for index, coche in diccionario.iterrows():
                self.tabla.insert(
                    "",
                    END,
                    text=coche["ID.1"],#str(index),
                    values=(
                        coche["ID.1"],
                        coche["Nodo destino"],
                        coche["Nodo aparcamiento"],
                        coche["Intentos aparcamiento"]))#str(index),
            self.tabla.pack()

        except Empty:
            pass
        except Exception as e:
            print(traceback.print_exc())
        finally:
            self.window.after(1, self.lanzar_ventana_tabla_aparcados, cola2)


# Data Generator which will generate Data
def GenerateData(q):
    for i in range(10):
        print("Generating Some Data, Iteration %s" % (i))
        time.sleep(2)
        q.put("Some Data from iteration %s \n" % (i))


def recibe_datos(cola):
    no_con = True
    while no_con:
        try:
            address = ('localhost', 6005)
            conn = Client(address)
            while True:
                datos_recibidos = conn.recv()
#                print("datos_recibidos ", datos_recibidos)
                cola.put(datos_recibidos)
                no_con = False
            conn.close()
        except BaseException:
            pass
#            print(traceback.print_exc())
#            print('No se puede conectar')


def envia_peticion(cola):  # Estamos creando un proceso Python cada vez que pulsamos
    if from_excel:
        cola.put(True)
    else:
#         el botón. No es óptimo.
        puerto=int(sys.argv[1])
        host = 'localhost'    # The remote host
        port = puerto           # The same port as used by the server
        respuestas = []
        tamaño_del_bufer = 524288
        with socket(AF_INET, SOCK_STREAM) as s:
            print('Socket')
            s.connect((host, port))
            respuesta = None
            while respuesta != b"Fin":
                s.sendall(b'g')
                respuesta = s.recv(tamaño_del_bufer)
                respuestas.append(respuesta)
    #            print("Recibí en bruto", respuesta)
            print("Cerrando socket.")
        if respuestas:
            texto = loads(respuestas[0])
            df=pd.read_json(texto)
            cola.put(df)
        #print("Lo enviado fue:", texto)


if __name__ == '__main__':
    # Queue which will be used for storing Data
    q = multiprocessing.Queue()
    q2 = multiprocessing.Queue()
    multiprocessing.freeze_support()
    q.cancel_join_thread()  # or else thread that puts data will not term
    q2.cancel_join_thread()
    t1 = multiprocessing.Process(target=recibe_datos, args=(q,))
    t1.start()
    gui = TkinterApp(q, q2)
    gui.window.mainloop()
    t1.join()
