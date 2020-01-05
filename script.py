import pandas as pd
from selenium import webdriver
import time
import os
import chromedriver_binary  # sin necesidad de añadir a Path
import shutil
import os
opciones = webdriver.ChromeOptions()
prefs = {'download.default_directory': 'C:\\Users\\luisb\\Code-Font\\prueba\\dataset\\'}

opciones.add_experimental_option('prefs', prefs)
browser = webdriver.Chrome(options=opciones)

browser.get(
    "https://www.worldbank.org/en/projects-operations/procurement/debarred-firms#")
time.sleep(20)  # espera para buscar el boton

#verifico si el archivo existe
if os.path.isfile('C:/Users/luisb/Code-Font/prueba/dataset/Sanctioned individuals and firms.xlsx'):
    print("Eliminando archivo anterior...")
    os.remove(
        'C:/Users/luisb/Code-Font/prueba/dataset/Sanctioned individuals and firms.xlsx')
    #renombro para no borrar y no dañar el siguiente
browser.find_element_by_class_name("k-grid-excel").click()
#time.sleep(5)#deja abierta un momento mientras descarga
#browser.close()
print("Archivo en descarga...")
time.sleep(6)  # para esperar a que acabe la descarga

while os.path.isfile('C:/Users/luisb/Code-Font/prueba/dataset/Sanctioned individuals and firms.xlsx') == False:
    Print(".")

print("Archivo xlsx obtenido...")
df = pd.read_excel(
    "C:/Users/luisb/Code-Font/prueba/dataset/Sanctioned individuals and firms.xlsx", header=1)
df.rename(columns={'Ineligibility Period': 'Ineligibility Period From Date',
                   'Unnamed: 5': 'Ineligibility Period To Date'}, inplace=True)
#df.head()
df.shape
df = df.drop(df.index[0])  # elimino primera fila (trae headers)
# deveuvle suma de 1's (true), datos vacios
#reemplazar caracteres que dan conflicto al insertar en la tabla
print("Limpiando el dataset...")
df['Firm Name'] = df['Firm Name'].str.replace('“', '')
df['Firm Name'] = df['Firm Name'].str.replace('”', '')
df['Firm Name'] = df['Firm Name'].str.replace("'", ' ')
df['Address'] = df['Address'].str.replace("'", ' ')
df['Country'] = df['Country'].str.replace("'", ' ')
print("Limpieza completa")

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.types import String
import io
print("Iniciando conexion con PostgreSQL")
con = psycopg2.connect(database="prueba", user="postgres",
                       password="12345", host="127.0.0.1", port="5432")
cur = con.cursor()
print("Creando tabla (si no existe)")
cur.execute('''CREATE TABLE IF NOT EXISTS diccionario
(
    "firmname" TEXT,
    "additionalfirminfo" TEXT,
    "adress" TEXT,
    "country" TEXT,
    "ineligibilityperiodfromdate" TEXT,
    "ineligibilityperiodtodate" TEXT,
    "grounds" TEXT
);''')
print("Tabla creada")
con.commit()
con.close()
print("Inicio la carga de datos")
con = psycopg2.connect(database="prueba", user="postgres",
                       password="12345", host="127.0.0.1", port="5432")
cur = con.cursor()
i = 1
num = df.shape[0]
while i <= num:
    consulta = "INSERT INTO diccionario(firmname, additionalfirminfo,adress,country,ineligibilityperiodfromdate,ineligibilityperiodtodate,grounds) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
        df['Firm Name'][i], df['Additional Firm Info'][i], df['Address'][i], df['Country'][i],
        df['Ineligibility Period From Date'][i], df['Ineligibility Period To Date'][i], df['Grounds'][i])
    cur.execute(consulta)
    con.commit()
    i += 1

con.close()
print("Datos cargados con exito")
