import time
import ntptime
import wifimgr
from max7219 import Matrix8x8 as M
from machine import Pin, SPI
"""
#sacar comillas para usar el el esp32 o pico w
# Configuración del SPI y del MAX7219
#conexion para esp32 y pico DIN=GPIO 3 CLOCK=GPIO 2 CS= GPIO 5
spi = SPI(0, baudrate=10000000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3))
ss = Pin(5, Pin.OUT)
"""
#sacar comillas para usar el 8266
#conexion DIN=GPIO 13 CLOCK=GPIO 14 CS= GPIO 15

# Configuración del SPI  y del MAX7219
spi = SPI(1, baudrate=10000000, polarity=0, phase=0)
ss = Pin(15, Pin.OUT)

# Inicialización del display MAX7219
display = M(spi, ss, 4)
display.brightness(1)  # Ajuste del brillo (1 a 15)
display.fill(0)
display.show()


def display_initial_time():
    #Muestra '00:00' en el display inicial
    display.fill(0)
    display_text_on_range(0, 1, "00", offset_x=1, offset_y=0, color=1)
    display_text_on_range(2, 3, "00", offset_x=-17, offset_y=0, color=1)
    display.rect(15, 1, 2, 2, 1)
    display.rect(15, 5, 2, 2, 1)
    display.show()

def connect_wifi():
    """Conecta a la red WiFi."""
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

def get_ntp_time():
    """Obtiene la hora desde el servidor NTP."""
    try:
        print("Obteniendo la hora desde el servidor NTP...")
        ntptime.settime()
        return time.localtime()
    except Exception as e:
        print("Error al obtener la hora desde NTP:", e)
        return None

def display_text_on_range(start_matrix, end_matrix, text, offset_x=0, offset_y=0, color=1):
    """Muestra texto en un rango de matrices del display."""
    num_matrices = end_matrix - start_matrix + 1
    text_length = len(text)
    total_space = num_matrices * 8

    # Ajustar el texto si es demasiado largo
    if text_length > total_space:
        text = text[:total_space]

    for idx in range(start_matrix, end_matrix + 1):
        start_col = (idx - start_matrix) * 8
        end_col = start_col + 8
        segment = text[start_col:end_col]
        display.text(segment, start_col - offset_x, offset_y, color)
        display.show()

def display_time_on_matrix(datetime_tuple):
    """Muestra la hora y minutos en dos displays separados."""
    if datetime_tuple is not None:
        buenos_aires_hour = (datetime_tuple[3] - 3) % 24  # Ajuste para Buenos Aires (UTC-3)
        hour_str = "{:02d}".format(buenos_aires_hour)
        minute_str = "{:02d}".format(datetime_tuple[4])
        display.fill(0)
        display_text_on_range(0, 1, hour_str, offset_x=1, offset_y=0, color=1)
        display_text_on_range(2, 3, minute_str, offset_x=-17, offset_y=0, color=1)
        display.show()

def blink_time_indicator():
    """Parpadea los indicadores de hora en el display."""
    for _ in range(2):
        display.rect(15, 1, 2, 2, 1)
        display.rect(15, 5, 2, 2, 1)
        display.show()
        time.sleep(1)
        display.rect(15, 1, 2, 2, 0)
        display.rect(15, 5, 2, 2, 0)
        display.show()
        time.sleep(1)

# Mostrar "00:00" al iniciar
display_initial_time()

# Intentar conectar a la red WiFi
if connect_wifi():
    current_time = get_ntp_time()
    display_time_on_matrix(current_time)

# Bucle principal
while True:
    blink_time_indicator()
    
    if connect_wifi():
        current_time = get_ntp_time()
        display_time_on_matrix(current_time)
    else:
        print("Esperando conexión a la red WiFi...")






