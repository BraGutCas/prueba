import datetime
from datetime import date

# Obtener la hora actual
hora_actual = datetime.datetime.now()
today = date.today()
fecha = today.strftime("%d/%m/%Y")

# Leer la hora anterior (si existe)
with open("registro_horas.txt", "r") as archivo:
    lineas = archivo.readlines()

if lineas:
    hora_anterior_str = lineas[-1].strip()  # Leer la última línea
    hora_anterior = datetime.datetime.fromisoformat(hora_anterior_str)
    
    # Calcular el tiempo transcurrido
    tiempo_transcurrido = hora_actual - hora_anterior
    
    # Guardar el tiempo transcurrido en un archivo de texto
    with open("tiempo_transcurrido.txt", "a") as archivo:
        archivo.write(str(fecha) + " " + str(tiempo_transcurrido) + "\n")
else:
    print("No se encontró un archivo de hora anterior.")

print("Proceso completado.")