import pandas as pd
from selenium import webdriver
import chromedriver_binary#sin necesidad de añadir a Path
import time

browser = webdriver.Chrome()#manejador
browser.get("https://www.worldbank.org/en/projects-operations/procurement/debarred-firms#")

time.sleep(15)#espera para buscar

rows_num = len(browser.find_elements_by_xpath('//*[@id="k-debarred-firms"]/div[3]/table/tbody/tr'))
print(rows_num)#numero total de datos

if rows_num == 0:
    print("Uff parece que la pagina no esta disponible actualmente")
    print("Intenta de nuevo mas tarde. Suele tardar un momento en actualizarse")

#====================== Obtencion de datos ============================================
#------- Arrays para almacenar
dic_firm_name =[]
dic_adress=[]
dic_country=[]
dic_date_from = []
dic_date_to= []
dic_grounds=[]

#------------ ciclos para extraer datos de la tabla
i=1
u=1
while i <= rows_num:
    #-------- Xpatch para extraer datos
    xname = '//*[@id="k-debarred-firms"]/div[3]/table/tbody/tr[{}]/td[1]'.format(i)
    xdirec = '//*[@id="k-debarred-firms"]/div[3]/table/tbody/tr[{}]/td[3]'.format(i)
    xcountry = '//*[@id="k-debarred-firms"]/div[3]/table/tbody/tr[{}]/td[4]'.format(i)
    xfromdate = '//*[@id="k-debarred-firms"]/div[3]/table/tbody/tr[{}]/td[5]'.format(i)
    xtodate = '//*[@id="k-debarred-firms"]/div[3]/table/tbody/tr[{}]/td[6]'.format(i)
    xgrounds = '//*[@id="k-debarred-firms"]/div[3]/table/tbody/tr[{}]/td[7]'.format(i)
    
    #obtengo los valores deseados y agrego a los arrays
    name = browser.find_element_by_xpath(xname).text
    direc = browser.find_element_by_xpath(xdirec).text
    contry = browser.find_element_by_xpath(xcountry).text
    fromdate = browser.find_element_by_xpath(xfromdate).text
    todate = browser.find_element_by_xpath(xtodate).text
    grounds = browser.find_element_by_xpath(xgrounds).text
    
    #---llenando arrays
    dic_firm_name.append(name)
    dic_adress.append(direc)
    dic_country.append(contry)
    dic_date_from.append(fromdate)
    dic_date_to.append(todate)
    dic_grounds.append(grounds)
    
    if (i%100 == 0):
        print("Van {}".format(i))
        print(dic_firm_name[i-1])

    i+=1

datos = {'FIRM NAME':dic_firm_name, 
         'ADDRESS':dic_adress, 
         'COUNTRY':dic_country,
         'INELIGIBITY_PERIOD_FROM':dic_date_from,
         'INELIGIBITY_PERIOD_TO':dic_date_to,
         'GROUNDS':dic_grounds}
dfwb = pd.DataFrame(datos)

#reemplazar caracteres que dan conflicto al insertar en la tabla
dfwb['FIRM NAME'] = dfwb['FIRM NAME'].str.replace('“','')
dfwb['FIRM NAME'] = dfwb['FIRM NAME'].str.replace('”','')
dfwb['FIRM NAME'] = dfwb['FIRM NAME'].str.replace("'",' ')
dfwb['ADDRESS'] = dfwb['ADDRESS'].str.replace("'",' ')
dfwb['COUNTRY'] = dfwb['COUNTRY'].str.replace("'",' ')
#se dejan los nan 

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.types import String
import io
con = psycopg2.connect(database="prueba", user="postgres", password="12345", host="127.0.0.1", port="5432")

cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS diccionario
(
    "firmname" TEXT,
    "adress" TEXT,
    "country" TEXT,
    "ineligibilityperiodfromdate" TEXT,
    "ineligibilityperiodtodate" TEXT,
    "grounds" TEXT
);''')
#    "additionalfirminfo" TEXT,
print("Tabla creada")
con.commit()
con.close()

con = psycopg2.connect(database="prueba", user="postgres",
                       password="12345", host="127.0.0.1", port="5432")
cur = con.cursor()
i = 0
num = dfwb.shape[0]
while i <= num-1:
    consulta = "INSERT INTO diccionario(firmname,adress,country,ineligibilityperiodfromdate,ineligibilityperiodtodate,grounds) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(
        dfwb['FIRM NAME'][i], dfwb['ADDRESS'][i],
        dfwb['COUNTRY'][i], dfwb['INELIGIBITY_PERIOD_FROM'][i], dfwb['INELIGIBITY_PERIOD_TO'][i], dfwb['GROUNDS'][i])
    cur.execute(consulta)
    con.commit()
    i += 1

con.close()
