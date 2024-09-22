import time  # Importa la biblioteca para manejar el tiempo
import ntptime  # Importa la biblioteca para obtener la hora de un servidor NTP
import wifimgr  # Importa la biblioteca para gestionar la conexión WiFi
from max7219 import Matrix8x8 as M  # Importa la clase para controlar el display MAX7219
from machine import Pin, SPI  # Importa las clases para manejar pines y SPI

# Configuración del SPI y del MAX7219
"""
# Descomentar para usar el ESP32 o Pico W
# Configuración para ESP32 y Pico W: DIN=GPIO 3, CLOCK=GPIO 2, CS= GPIO 5
spi = SPI(0, baudrate=10000000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3))
ss = Pin(5, Pin.OUT)
"""

# Descomentar para usar el 8266
# Configuración para 8266: DIN=GPIO 13, CLOCK=GPIO 14, CS= GPIO 15
spi = SPI(1, baudrate=10000000, polarity=0, phase=0)  # Configuración del SPI
ss = Pin(15, Pin.OUT)  # Pin para seleccionar el chip MAX7219

# Inicialización del display MAX7219
display = M(spi, ss, 4)  # Crea un objeto de display con 4 matrices
display.brightness(1)  # Ajuste del brillo del display (1 a 15)
display.fill(0)  # Limpia el display
display.show()  # Actualiza el display

def display_initial_time():
    """Muestra '00:00' en el display inicial."""
    display.fill(0)  # Limpia el display
    display_text_on_range(0, 1, "00", offset_x=1, offset_y=0, color=1)  # Muestra horas
    display_text_on_range(2, 3, "00", offset_x=-17, offset_y=0, color=1)  # Muestra minutos
    display.rect(15, 1, 2, 2, 1)  # Dibuja un indicador para horas
    display.rect(15, 5, 2, 2, 1)  # Dibuja un indicador para minutos
    display.show()  # Actualiza el display

def connect_wifi():
    """Conecta a la red WiFi."""
    try:
        print("Conectando a la red WiFi...")  # Mensaje de conexión
        wlan = wifimgr.get_connection()  # Intenta obtener la conexión WiFi
        if wlan is None:  # Si no se conecta
            raise Exception("¡Error! No se pudo conectar a la red WiFi.")
        print("Conexión WiFi establecida:", wlan.ifconfig())  # Imprime la dirección IP
        return True  # Conexión exitosa
    except Exception as e:
        print("Error al conectar a la red WiFi:", e)  # Imprime el error
        return False  # Conexión fallida

def get_ntp_time():
    """Obtiene la hora desde el servidor NTP."""
    try:
        print("Obteniendo la hora desde el servidor NTP...")  # Mensaje de obtención de hora
        ntptime.settime()  # Sincroniza el reloj interno con el NTP
        return time.localtime()  # Devuelve la hora local
    except Exception as e:
        print("Error al obtener la hora desde NTP:", e)  # Imprime el error
        return None  # Retorna None si falla

def display_text_on_range(start_matrix, end_matrix, text, offset_x=0, offset_y=0, color=1):
    """Muestra texto en un rango de matrices del display."""
    num_matrices = end_matrix - start_matrix + 1  # Número de matrices a usar
    text_length = len(text)  # Longitud del texto
    total_space = num_matrices * 8  # Espacio total disponible

    # Ajustar el texto si es demasiado largo
    if text_length > total_space:
        text = text[:total_space]  # Trunca el texto si es necesario

    for idx in range(start_matrix, end_matrix + 1):  # Itera sobre las matrices
        start_col = (idx - start_matrix) * 8  # Columna inicial
        end_col = start_col + 8  # Columna final
        segment = text[start_col:end_col]  # Segmento de texto a mostrar
        display.text(segment, start_col - offset_x, offset_y, color)  # Muestra el segmento en el display
        display.show()  # Actualiza el display

def display_time_on_matrix(datetime_tuple):
    """Muestra la hora y minutos en dos displays separados."""
    if datetime_tuple is not None:  # Si se obtuvo la hora
        buenos_aires_hour = (datetime_tuple[3] - 3) % 24  # Ajuste para Buenos Aires (UTC-3)
        hour_str = "{:02d}".format(buenos_aires_hour)  # Formatea la hora
        minute_str = "{:02d}".format(datetime_tuple[4])  # Formatea los minutos
        display.fill(0)  # Limpia el display
        display_text_on_range(0, 1, hour_str, offset_x=1, offset_y=0, color=1)  # Muestra horas
        display_text_on_range(2, 3, minute_str, offset_x=-17, offset_y=0, color=1)  # Muestra minutos
        display.show()  # Actualiza el display

def blink_time_indicator():
    """Parpadea los indicadores de hora en el display."""
    for _ in range(2):  # Parpadea dos veces
        display.rect(15, 1, 2, 2, 1)  # Dibuja un rectángulo para las horas
        display.rect(15, 5, 2, 2, 1)  # Dibuja un rectángulo para los minutos
        display.show()  # Actualiza el display
        time.sleep(1)  # Espera 1 segundo
        display.rect(15, 1, 2, 2, 0)  # Borra el rectángulo de horas
        display.rect(15, 5, 2, 2, 0)  # Borra el rectángulo de minutos
        display.show()  # Actualiza el display
        time.sleep(1)  # Espera 1 segundo

# Mostrar "00:00" al iniciar
display_initial_time()  # Llama a la función para mostrar la hora inicial

# Intentar conectar a la red WiFi
if connect_wifi():  # Si se conecta exitosamente
    current_time = get_ntp_time()  # Obtiene la hora actual
    display_time_on_matrix(current_time)  # Muestra la hora en el display

# Bucle principal
while True:
    blink_time_indicator()  # Parpadea los indicadores de hora
    
    if connect_wifi():  # Intenta conectar a la red WiFi
        current_time = get_ntp_time()  # Obtiene la hora actual
        display_time_on_matrix(current_time)  # Muestra la hora en el display
    else:
        print("Esperando conexión a la red WiFi...")  # Mensaje si no se conecta
