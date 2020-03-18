from bs4 import BeautifulSoup
import requests
import sys
import json
import urllib
import os
import urllib.request
import subprocess
from colorama import Fore, init, Style, Back
init()
cont_detectados =0
lista_detectados=list()
#hilo principal de ejecucion
def start(usuario = None):
	
	usuario = obtener_usuario()
	url = "http://www.twitter.com/" + usuario
	print("\n\nDescargando imagenes de los tweets de "  + Back.GREEN +'@'+ usuario.upper(), Back.RESET)
	response = None
	try:
		response = requests.get(url)
	except Exception as e:
		print(repr(e))
		sys.exit(1)
    
	soup = BeautifulSoup(response.text, 'lxml')
	
	if soup.find("div", {"class": "errorpage-topbar"}):
		print("\n\n Error: usuario no existe.")
		sys.exit(1)
	tweets = obtener_tweets_data(usuario, soup)


#descargar imagenes
	for tweet in tweets:
		descarga_img(tweet)
	print(str(len(tweets))+" tweets revisados.")

#imprimiendo archivos .JPG detectados
	print (Fore.RED + Style.BRIGHT + 'Archivos .JPG sospechosos detectados: ' + str(cont_detectados), Fore.RESET)
	print(*lista_detectados)

# Analisis a los archivos PNG a la carpeta con imagenes descargadas con STEGEXPOSE	
	while True:
	    RespuestaUsuario= input('\nQUIERES REALIZAR UN ANALISIS DE ARCHIVOS .PNG S/N.: ')
	    if RespuestaUsuario.lower() == 's':
	    	print(Fore.RED + Style.BRIGHT + 'Archivos .PNG Sospechosos detectados... '+Fore.RESET)
	    	stegexpose=subprocess.run('java -jar "C:\\Users\\ALEXANDER\\Desktop\\Herramientas stego\\StegExpose-master\\StegExpose.jar" "C:\\Users\\ALEXANDER\\Desktop\\TFM\\descargas-twitter"', shell=True, universal_newlines=True)
	    	
	    	break
	    elif RespuestaUsuario.lower() == 'n':
	    	print("\n\nListo...")
	    	break
	    else:
	    	print('Opcion equivocada, Intentalo de nuevo...')

#Implementacion de seguridad - REDIMENSION DE IMAGENES
	while True:
		
		RespuestaUsuario= input('\nQUIERES HACER UN REDIMENCIONAMIENTO DE LAS IMAGENES SOSPECHOSAS S/N..:')
		if RespuestaUsuario.lower() == 's':
			
			for nombre in lista_detectados:
				archivo=str(nombre[:19])
				print ('IMG_'+archivo)
				subprocess.run('magick mogrify -resize 99% "C:\\Users\\ALEXANDER\\Desktop\\TFM\\descargas-twitter\\IMG_"'+ archivo, shell=True, universal_newlines=True)
			
			print((Fore.GREEN + Style.BRIGHT +'Archivos modificados con exito... ')+Fore.RESET)
			break
		elif RespuestaUsuario.lower() == 'n':
			print("\n\nListo... Imagenes sin modificaciones")
			break
		else:
			print('Opcion equivocada, Seleccione S o N...')

#Mensaje por defecto si el usuario no existe o no ingresa usuario
def uso_script():
	msg = """
	Por favor usar el script con la siguiente sintaxis.
	python <nombre_script.py> <usuario_twitter>
	"""
	print(msg)
	sys.exit(1)

#obtener todos los tweets de cada pagina
def obtener_pag_tweets(soup):
	#tweets_list = list()
	tweets = soup.find_all('div',{'class':'AdaptiveMediaOuterContainer'})
	return tweets

#recorrer todas las paginas pasando la paginacion
def obtener_tweets_data(usuario, soup):
	tweets_list = list()
	tweets_list.extend(obtener_pag_tweets(soup))
	#print(tweets_list)

	next_pointer = soup.find("div", {"class": "stream-container"})["data-min-position"]
	while True:
		next_url = "https://twitter.com/i/profiles/show/" + usuario + \
                   "/timeline/tweets?include_available_features=1&" \
                   "include_entities=1&max_position=" + next_pointer + "&reset_error_state=false"
	
		next_response = None
		try:
			next_response = requests.get(next_url)
		except Exception as e:
			# En caso de haber algun problema con Request.
			print(e)
			return tweets_list

		tweets_data = next_response.text
		#print(tweets_data)
		tweets_obj = json.loads(tweets_data)
		if not tweets_obj["has_more_items"] and not tweets_obj["min_position"]:
			# se usa dos puntos de revision en caso de no existir mas items o existir varios items en cada tweet
			print("\nRevisados todos los Tweets")
			break

		next_pointer = tweets_obj["min_position"]
		html = tweets_obj["items_html"]
		soup = BeautifulSoup(html, 'lxml')
		tweets_list.extend(obtener_pag_tweets(soup))
		
	
	return tweets_list

# descargando cada una de la imagenes en carpeta especifica (tw_img)e identificar si los archivos jpeg contienen algo
def descarga_img(tweet):
	
	img = tweet.find_all('img')
	for src in img:
		try:
			print('Descargando.......')
			print(src.get('src'))
			temp = src.get('src')	
			filename = str(temp)[28:]
			
			imagefile =open("./descargas-twitter/IMG_" + filename,'wb')
			imagefile.write(urllib.request.urlopen(temp).read())
			imagefile.close()
			# Analisis con stegdetect a los archivos jpeg
			
			if str(filename[-4:])== '.jpg':
				stegdetect=subprocess.run('stegdetect -s 5 "C:\\Users\\ALEXANDER\\Desktop\\TFM\\descargas-twitter\\IMG_"' + filename, shell=True, capture_output=True, text=True)
			#Presentacion de resultados
				respuesta = (str(stegdetect.stdout)[75:83])
				if respuesta == 'negative':
					print(Fore.GREEN + Style.BRIGHT+(str(stegdetect.stdout)[53:]), Fore.RESET)
				else:
					print(Fore.RED + Style.BRIGHT+(str(stegdetect.stdout)[53:]), Fore.RESET)
					global cont_detectados
					lista_detectados.append((stegdetect.stdout)[53:])
					cont_detectados = cont_detectados +1
					
		except:
			print("Algo salio mal. Intente nuevamente...")
						
#validar nombre de usuario ingresado y colocar en minuscula
def obtener_usuario():
    # si el usuario no es valido o no cumple con los parametros minimos de un usuario twitter 
    if len(sys.argv) < 2:
        uso_script()
    usuario = sys.argv[1].strip().lower()
    if not usuario:
        uso_script()

    return usuario

start()
