# -*- coding: utf-8 -*-
"""
Created on Tue May 21 11:46:41 2019

@author: Andrés
"""

import pandas as pd
import numpy as np
import folium
import ast
from itertools import count
import selenium.webdriver
import tkinter as tk
from tkinter.ttk import Treeview, Scrollbar, Notebook, Frame
from selenium.webdriver.chrome.options import Options
from PIL import ImageTk, Image
import os
import webbrowser
from folium.plugins import AntPath
#driver = selenium.webdriver.Firefox(r"C:\Users\Andrés\Downloads\geckodriver-v0.24.0-win64\geckodriver.exe")



def lanza_mapa(self, dataframe, ruta_carpeta):
    colores=('blue','pink','orange','red','purple','yellow','green','brown','grey')
    id_vehiculo=str(dataframe.index[0])
    ruta_carpeta_vehiculo = ruta_carpeta+"\\vehiculo_{}".format(id_vehiculo)
    if not os.path.exists(ruta_carpeta_vehiculo):
        os.makedirs(ruta_carpeta_vehiculo)
    WINDOW_SIZE = "680,530"
    chrome_options = Options()  
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    
#    chrome_options.binary_location = CHROME_PATH
    #creamos 2 ventanas una para el cargando y otra para mostrar las pestañas
    ventana_mapas = tk.Toplevel()
    ventana_mapas.withdraw()
    ventana_carga= tk.Toplevel()
    tk.Label(ventana_carga, text='Cargando mapas').pack()
    ventana_carga.update()
    ventana_mapas.title("Mapas vehiculo " + id_vehiculo)
    pestañas = Notebook(ventana_mapas)
    # cargamos el selenium que de fondo va a renderizar los mapas 
    driver = selenium.webdriver.Chrome(chrome_options=chrome_options)
    #cargamos el geojson de base
    geojson= r"C:\Users\Andrés\Desktop\mapa2.geojson"
    
    dataframe_partida = dataframe
    
#    dataframe_partida.set_index('ID', inplace=True, drop = False)
    
    #cargamos los puntos medios de las calles y los puntos iniciales y finales para el path
    calles_medio= pd.read_excel(r"calles_medios.xls")
    calles_medio.set_index('Name', inplace=True)
    calles_inicio= pd.read_excel(r"calles_inicios.xls")
    calles_inicio.set_index('Name', inplace=True)
    calles_fin= pd.read_excel(r"calles_finales.xls")
    calles_fin.set_index('Name', inplace=True)
    
    id_coche=id_vehiculo
    
    #cargamos las secciones donde ha intentado aparcar
    print(type(dataframe_partida['Secciones intento aparcamiento']))
    print(dataframe_partida['Secciones intento aparcamiento'])
    secciones_intento=ast.literal_eval(dataframe_partida['Secciones intento aparcamiento'])
    utilidades=dataframe_partida['Utilidades iteraciones'].replace("L","").replace("nan","-999")
    utilidades=ast.literal_eval(utilidades)
    tracks_pintar=ast.literal_eval(dataframe_partida['track_secciones'])
    marcadores=[]
    tracks_seguidos=[]
    
    for elemento,iteracion in zip(utilidades, count(0)):
        #marco ventanas
        marco=Frame(pestañas)
        #se carga el mapa centrado en la zona ded estudio
        m = folium.Map(location=[43.463872, -3.798428], zoom_start=17,tiles='cartodbpositron')
        
        #extraemos el nodo final de aparcamiento y de destino así como el de intento de esta iteración
        aparcamiento=dataframe_partida['Nodo aparcamiento']
        destino=dataframe_partida['Nodo destino']
        intento_aparcamiento=secciones_intento[iteracion]
        
        #ponemos los marcadores de los sitios de paso el destino
        folium.Marker([calles_medio.loc[destino,'lat'], calles_medio.loc[destino,'long']], tooltip="Destino", permanet=True,icon=folium.Icon(color='green')).add_to(m)
#        folium.Marker([calles_medio.loc[aparcamiento,'lat'], calles_medio.loc[aparcamiento,'long']], tooltip="Aparcamiento",icon=folium.Icon(color='red')).add_to(m)
        marcador_paso=folium.Marker([calles_medio.loc[intento_aparcamiento,'lat'], calles_medio.loc[intento_aparcamiento,'long']], tooltip="Intento {}".format(str(iteracion)),permanet=True,icon=folium.Icon(color='blue'))    
        marcadores.append(marcador_paso)
        for x in marcadores:
            x.add_to(m)
        
        #se manipula el df de utilidades y se pinta haciendo una capa nueva 
        utilidades_fin=pd.DataFrame.from_dict(elemento['utilidades'], columns=[ 'util'],orient='index')
        utilidades_fin.reset_index(inplace=True)
        utilidades_fin['index']=utilidades_fin['index'].apply(lambda x: str(x))
        utilidades_fin.replace(-999,np.nan, inplace=True)
        folium.Choropleth(
            geo_data=geojson,
            data=utilidades_fin,
            columns=['index', 'util'],
            key_on='feature.properties.Name',
            fill_color='OrRd',
            legend_name='Utilidad',
        ).add_to(m)
        
        #cogemos el track del vehiculo que estamos siguiendo
        track_total=[]
        for seccion in tracks_pintar[iteracion]:
            track_total.append((calles_inicio.loc[seccion,'lat'],calles_inicio.loc[seccion,'long']))
            track_total.append((calles_fin.loc[seccion,'lat'],calles_fin.loc[seccion,'long']))    
        track_iter=AntPath(tuple(track_total),color= colores[iteracion])
        tracks_seguidos.append(track_iter)
        for viaje in tracks_seguidos:
            viaje.add_to(m)
        
        
        # se guarda el mapa y se saca el pantallazo
        ruta_mapa=ruta_carpeta_vehiculo+'mapa{}.html'.format(str(iteracion))
        m.save(ruta_mapa) 
        driver.get(ruta_mapa)
        ruta_imagen=ruta_carpeta_vehiculo+'\\screenshot{}.png'.format(str(iteracion))
        driver.save_screenshot(ruta_imagen)
        print(ruta_imagen)
        #añadimos una pestaña con el pantallazo y el enlace al mapa
        img = ImageTk.PhotoImage(Image.open(ruta_imagen))
        label=tk.Label(marco,text=ruta_imagen, image=img)
        label.image=img
        label.pack()
        tk.Label(marco,text='Se representan en azul los puntos de intento de aparcamiento del vehiculo, para una mejor visualización se recomienda ver el mapa interacitivo en el navegador').pack()
        tk.Button(marco, text="Abrir mapa en navegador",
                  command= lambda : webbrowser.open(ruta_mapa, new=2)).pack()
        pestañas.add(marco, text="Iteración {}".format(str(iteracion)), padding=10)
    
    
    driver.close()
    pestañas.pack(padx=10, pady=10)
    ventana_carga.destroy()
    ventana_mapas.deiconify()