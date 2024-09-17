import time
import ntptime
import wifimgr
from max7219 import Matrix8x8 as M
from machine import Pin, SPI

# Configuración del SPI y del MAX7219
spi = SPI(0, baudrate=10000000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3))
ss = Pin(5, Pin.OUT)

# Inicialización del display MAX7219
display = M(spi, ss, 4)
display.brightness(10)  # Ajuste del brillo (1 a 15)
display.fill(0)
display.show()
time.sleep(0.5)

# Función para conectar a la red WiFi usando wifimgr
def connect_wifi():
    try:
        print("Conectando a la red WiFi...")
        wlan = wifimgr.get_connection()
        if wlan is None:
            raise Exception("¡Error! No se pudo conectar a la red WiFi.")
        print("Conexión WiFi establecida:", wlan.ifconfig())
        return True
    except Exception as e:
        print("Error al conectar a la red WiFi:", e)
        return False

# Función para obtener la hora desde el servidor NTP
def get_ntp_time():
    try:
        print("Obteniendo la hora desde el servidor NTP...")
        ntptime.settime()
        return time.localtime()
    except Exception as e:
        print("Error al obtener la hora desde NTP:", e)
        return None

# Función para mostrar texto en un rango de matrices
def display_text_on_range(start_matrix, end_matrix, text, offset_x=0, offset_y=0, color=1):
    #display.fill(0)  # Limpiar todas las matrices
    num_matrices = end_matrix - start_matrix + 1
    
    # Ajustar el texto para que quepa en el rango de matrices
    text_length = len(text)
    total_space = num_matrices * 8  # Cada matriz tiene 8 columnas de ancho

    # Ajustar el texto si es demasiado largo
    if text_length > total_space:
        text = text[:total_space]

    for idx in range(start_matrix, end_matrix + 1):
        start_col = (idx - start_matrix) * 8
        end_col = start_col + 8
        segment = text[start_col:end_col]
        display.text(segment, start_col - offset_x, offset_y, color)
    
    display.show()

# Función para mostrar la hora y minutos en dos displays separados
def display_time_on_matrix(datetime_tuple):
    if datetime_tuple is not None:
        buenos_aires_hour = (datetime_tuple[3] - 3) % 24  # Ajuste de hora para Buenos Aires (UTC-3)
        hour_str = "{:02d}".format(buenos_aires_hour)
        minute_str = "{:02d}".format(datetime_tuple[4])
        display.fill(0)
        # Mostrar la hora en las primeras dos matrices (0 y 1)
        display_text_on_range(0, 1, hour_str, offset_x=1, offset_y=0, color=1)
        display_text_on_range(2, 3, minute_str, offset_x=-17, offset_y=0, color=1)
        display.show()

def segundero():
    display.rect(15,1,2,2,1)
    display.rect(15,5,2,2,1)
    display.show()
    time.sleep(1)
    display.rect(15,1,2,2,0)
    display.rect(15,5,2,2,0)
    display.show()
    time.sleep(1)

# Bucle principal
while True:
    segundero()
    # Intentar conectar a la red WiFi
    if connect_wifi():
        # Si la conexión WiFi es exitosa, obtener la hora desde NTP
        current_time = get_ntp_time()
    
        # Mostrar la hora en la matriz LED solo si se obtuvo correctamente
    if current_time is not None:
        display_time_on_matrix(current_time)
    
    # Esperar un minuto antes de intentar nuevamente (60 segundos)
    time.sleep(1)
    