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
#driver = selenium.webdriver.Firefox(r"C:\Users\Andrés\Downloads\geckodriver-v0.24.0-win64\geckodriver.exe")
driver = selenium.webdriver.Chrome()
driver.set_window_size(height=680, width=530)  # choose a resolution
geojson= r"C:\Users\Andrés\Desktop\mapa2.geojson"



dataframe_partida = pd.read_excel(
                r"C:\Users\Andrés\Desktop\informes\2019-05-21__11_02_28_informe.xlsx")
dataframe_partida.set_index('ID', inplace=True)

calles_medio= pd.read_excel(r"C:\Users\Andrés\Desktop\calles_medios.xls")
calles_medio.set_index('Name', inplace=True)

id_coche=165
secciones_intento=ast.literal_eval(dataframe_partida.loc[id_coche,'Secciones intento aparcamiento'])
utilidades=dataframe_partida.loc[id_coche,'Utilidades iteraciones'].replace("L","").replace("nan","-999")
utilidades=ast.literal_eval(utilidades)
for elemento,iteracion in zip(utilidades, count(0)):
    m = folium.Map(location=[43.463872, -3.798428], zoom_start=17,tiles='cartodbpositron')
    aparcamiento=dataframe_partida.loc[id_coche, 'Nodo aparcamiento']
    destino=dataframe_partida.loc[id_coche, 'Nodo destino']
    intento_aparcamiento=secciones_intento[iteracion]
    folium.Marker([calles_medio.loc[destino,'lat'], calles_medio.loc[destino,'long']], tooltip="Destino", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([calles_medio.loc[aparcamiento,'lat'], calles_medio.loc[aparcamiento,'long']], tooltip="Aparcamiento",icon=folium.Icon(color='red')).add_to(m)
    folium.Marker([calles_medio.loc[intento_aparcamiento,'lat'], calles_medio.loc[intento_aparcamiento,'long']], tooltip="Intento Aparcamiento",icon=folium.Icon(color='blue')).add_to(m)    
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
    m.save('mapa{}.html'.format(str(iteracion)))

    driver.get(r"C:\Users\Andrés\Desktop\mapa{}.html".format(str(iteracion)))
    driver.save_screenshot('screenshot{}.png'.format(str(iteracion)))
