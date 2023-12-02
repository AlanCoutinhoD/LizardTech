# Librerias que se necesitan para los sensores
import smbus
import time
import  sys
import Adafruit_DHT as DHT
import datetime
import requests


from gpiozero import DistanceSensor
#Libreria de servomotor
import RPi.GPIO as GPIO
#Libreria para la camara
import cv2
# Librerias de telegram para usar el bot
import telepot
from telepot.loop import MessageLoop
# Inicializar Camara
sensor = DistanceSensor(echo=24, trigger=23)
cap = cv2.VideoCapture(0) 
# Declaracion de variables de los pines
DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value

# Start measurement at 4lx resolution. Time typically 16ms.
CONTINUOUS_LOW_RES_MODE = 0x13
# Start measurement at 1lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_1 = 0x10
# Start measurement at 0.5lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_2 = 0x11
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_1 = 0x20
# Start measurement at 0.5lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_2 = 0x21
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_LOW_RES_MODE = 0x23


# Define el número del pin GPIO al que está conectado el servo
servo_pin = 18

# Inicializa la biblioteca RPi.GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# Crea un objeto PWM con el pin y una frecuencia de 50 Hz
pwm = GPIO.PWM(servo_pin, 50)

# Inicializa el PWM con un pulso del 5% (posición neutral)
pwm.start(2)
#url de la api metodo POST
url = 'http://rest2023.creativesolution.com.mx:8080/api/data/emit'
#bus = smbus.SMBus(0) # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1
# Array de horas deseadas por revisar
horas_deseadas = ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00","20:00","22:00"]

#variable de sensor DHT11 temperatura y humedad
humid, temp = DHT.read_retry(DHT.DHT11,4)
def readLight(addr=DEVICE):
  # Read data from I2C interface
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE_1)
  return convertToNumber(data)

def convertToNumber(data):
  # Simple function to convertir 2 bytes of data
  # into a decimal number. Optional parameter 'decimals'
  # will round to specified number of decimal places.
  result=(data[1] + (256 * data[0])) / 1.2
  return (result)

def sensors():
    while True:
        lightLevell=readLight()
        ahora = datetime.datetime.now()
        hora_actual = ahora.strftime("%H:%M")
        print("Hora Actual: " + hora_actual)
        json_data = {
    "idUser":"6559c8f77f7404e603988fac",
    "temperatura":temp,
    "humedad":humid,
    "luxes":lightLevell,
    "hora":hora_actual
    }
     # Realiza la solicitud POST
        response = requests.post(url, json=json_data)

            # Imprime la respuesta
        print(response.text)
    
     #   print("Nivel De Iluminacion : " + format(lightLevell,'.2f') + " lx")
      #  print(f"Temperatura actual: {temp}°C")
       # print(f"Humedad actual: {humid}%")
        if lightLevell<100:
      #    bot.sendMessage(6339852558, "CUIDADO NO HAY ILUMINACION EN EL HABITAD")
          print("")
        elif lightLevell>300:
          bot.sendMessage(6339852558, "ES MUCHA LUZ")
          
        if hora_actual in horas_deseadas:
            json_data = {
        'idUser':'6559c8f77f7404e603988fac',
        'temperatura':temp,
        'humedad':humid,
        'luxes':lightLevell,
        'hora':hora_actual
        }
            # Realiza la solicitud POST
            response = requests.post('http://rest2023.creativesolution.com.mx:8080/api/data', json=json_data)

            # Imprime la respuesta
            print(response.text)
            time.sleep(60)
        else:
        
            time.sleep(5)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    lightLevel=readLight()
   # humid, temp = DHT.read_retry(DHT.DHT11,4)
   # print(temp,humid)
    print("Nivel De Iluminacion : " + format(lightLevel,'.2f') + " lx")
    time.sleep(0.5)

    if content_type == 'text':
        command = msg['text']
        # Puedes manejar diferentes comandos aquí
        if command =='/start':
            bot.sendMessage(chat_id, 'HOLA PUEDES USAR LOS SIGUIENTES COMANDOS: \n1. temperatura \n2. iluminacion \n3. humedad \n4. foto \n5. alimentar' '\n6. distancia')
            print(chat_id)        
        elif command == 'iluminacion':
            bot.sendMessage(chat_id, 'Nivel De Iluminacion Actual: ' + format(lightLevel,'.2f') + "lx")
        elif command == 'temperatura':
            bot.sendMessage(chat_id,f"Temperatura Actual: {temp}°C")
        elif command == 'humedad':
            bot.sendMessage(chat_id,f"Nivel De Humedad Actual: {humid} %")
        elif command == 'habitad':
            bot.sendMessage(chat_id, 'Nivel de iluminacion actual : ' + format(lightLevel, '.2f') + "lx"  + " Temperatura actual : " + "ejemplo ")
        elif command == 'foto':
            ret, frame = cap.read()
            cv2.imwrite('captura.jpg', frame)
            # Envia la imagen al chat de Telegram
            bot.sendPhoto(chat_id, open('captura.jpg', 'rb'))
        elif command == 'alimentar':
            bot.sendMessage(chat_id, 'Alimentando a Julio')
             # Mueve el servo a la posición de comida
            pwm.ChangeDutyCycle(8)
            time.sleep(7)
            pwm.ChangeDutyCycle(2)
            bot.sendMessage(chat_id, 'Alimentacion Terminada')
        elif command == 'distancia':
            bot.sendMessage(chat_id,f"Distancia: {sensor.distance * 100} cm") 
        else:
            bot.sendMessage(chat_id, 'No conozco ese comando prueba de nuevo')
# Token del bot (obtenido al crear el bot en BotFather)
TOKEN = '6852502047:AAFipPEPK5EYwWgnU7rkVqxjEHlp7vMXl4c'

# Crea el objeto de bot
bot = telepot.Bot(TOKEN)

# Registra la función de manejo de mensajes
MessageLoop(bot, handle).run_as_thread()
 
# Espera a que se presione Ctrl+C para detener el bot
print('Conectando al telegram...')
sensors()


while 1:
    time.sleep(10)




def main():

  while True:
   # lightLevel=readLight()
   # humid, temp = DHT.read_retry(DHT.DHT11,4)
   # print(temp,humid)
  #  print("Nivel De Iluminacion a : " + format(lightLevel,'.2f') + " lx")
    time.sleep(0.5)

if __name__=="__main__":
   main()
