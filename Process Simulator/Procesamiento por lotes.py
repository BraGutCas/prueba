import tkinter as tk
from tkinter import scrolledtext
import time
import os

class SimuladorProcesos:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Procesos")

        # Variables para almacenar los datos
        self.procesos = []
        self.procesos_terminados = []
        self.lote_procesos = []
        self.proceso_actual = None
        self.ids = set()
        self.iniciando = True
        self.procesos_pendientes = []
        self.lotes_totales = 0
        self.lotes_pendientes = 0
        self.start_time = None
        self.total_start_time = None
        contador_terminados = 1

        # Configuración de la interfaz
        self.setup_ui()

    def setup_ui(self):
        # Crear widgets para mostrar la tabla de procesos pendientes
        self.label_pendientes = tk.Label(self.root, text="Procesos Pendientes")
        self.label_pendientes.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.text_pendientes = scrolledtext.ScrolledText(self.root, height=10, width=60)
        self.text_pendientes.grid(row=1, column=0, padx=10, pady=10)

        # Label para mostrar el número de lotes pendientes
        self.label_lotes = tk.Label(self.root, text="")
        self.label_lotes.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Crear widgets para mostrar el proceso actual
        self.label_actual = tk.Label(self.root, text="Proceso Actual")
        self.label_actual.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.text_actual = tk.Text(self.root, height=10, width=50)
        self.text_actual.grid(row=1, column=1, padx=10, pady=10)

        # Labels para mostrar el tiempo transcurrido, tiempo restante y tiempo total del programa
        self.label_tiempo_transcurrido = tk.Label(self.root, text="Tiempo Transcurrido: 0s")
        self.label_tiempo_transcurrido.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.label_tiempo_restante = tk.Label(self.root, text="Tiempo Restante: 0s")
        self.label_tiempo_restante.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.label_tiempo_programa = tk.Label(self.root, text="Tiempo Total del Programa: 0s")
        self.label_tiempo_programa.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Crear widgets para mostrar la tabla de procesos terminados
        self.label_terminados = tk.Label(self.root, text="Procesos Terminados")
        self.label_terminados.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.text_terminados = scrolledtext.ScrolledText(self.root, height=10, width=50)
        self.text_terminados.grid(row=4, column=0, padx=10, pady=10)

    def actualizar_tablas(self):
        # Actualizar la tabla de procesos pendientes
        self.text_pendientes.delete(1.0, tk.END)
        self.text_pendientes.insert(tk.END, "Nombre \t ID Proceso\t   Operación\t   Tiempo Estimado\n")
        self.text_pendientes.insert(tk.END, "-" * 50 + "\n")
        for proceso in self.lote_procesos:
            self.text_pendientes.insert(tk.END, f"{proceso['nombre']}\t\t{proceso['id_proceso']}\t{proceso['a']} {proceso['operacion']} {proceso['b']}\t\t{proceso['tiempo_estimado']}\n")

        # Actualizar el número de lotes pendientes
        self.label_lotes.config(text=f"Lotes restantes por procesar: {self.lotes_pendientes}")

        # Actualizar la tabla del proceso actual
        self.text_actual.delete(1.0, tk.END)
        if self.proceso_actual:
            self.text_actual.insert(tk.END, f"ID Proceso: {self.proceso_actual['id_proceso']}\n")
            self.text_actual.insert(tk.END, f"Programador: {self.proceso_actual['nombre']}\n")
            self.text_actual.insert(tk.END, f"Operación: {self.proceso_actual['a']} {self.proceso_actual['operacion']} {self.proceso_actual['b']}\n")
            self.text_actual.insert(tk.END, f"Tiempo Estimado: {self.proceso_actual['tiempo_estimado']}\n")

        # Actualizar el contador de tiempos
        self.actualizar_contadores()

        # Actualizar la tabla de procesos terminados
        self.text_terminados.delete(1.0, tk.END)
        self.text_terminados.insert(tk.END, "ID Proceso\t   Operación\t   Resultado\n")
        self.text_terminados.insert(tk.END, "-" * 50 + "\n")
        for i, terminado in enumerate(self.procesos_terminados, 1):
            self.text_terminados.insert(tk.END, f"{terminado['id_proceso']}\t\t{terminado['operacion']}\t\t{terminado['resultado']}\n")
            if i % 5 == 0:
                self.text_terminados.insert(tk.END, "-" * 50 + "\n")


    def actualizar_contadores(self):
        if self.total_start_time:
            tiempo_total_programa = int(time.time() - self.total_start_time)
            self.label_tiempo_programa.config(text=f"Tiempo Total del Programa: {tiempo_total_programa}s")

            if self.proceso_actual:
                tiempo_transcurrido = int(time.time() - self.start_time)
                self.label_tiempo_transcurrido.config(text=f"Tiempo Transcurrido: {tiempo_transcurrido}s")
                tiempo_restante = max(0, self.proceso_actual['tiempo_estimado'] - tiempo_transcurrido)
                self.label_tiempo_restante.config(text=f"Tiempo Restante: {tiempo_restante}s")
            else:
                self.label_tiempo_transcurrido.config(text="Tiempo Transcurrido: 0s")
                self.label_tiempo_restante.config(text="Tiempo Restante: 0s")

            
            self.root.after(1000, self.actualizar_contadores)

    def ejecutar_procesos(self):
        if self.iniciando:
            tamano_lote = 5
            self.lotes_totales = (len(self.procesos) + tamano_lote - 1) // tamano_lote
            self.lotes_pendientes = self.lotes_totales

            self.procesos_pendientes = self.procesos[:]
            self.lote_procesos = self.procesos[:tamano_lote]
            self.procesos = self.procesos[tamano_lote:]
            self.lotes_pendientes -= 1
            self.iniciando = False
            self.total_start_time = time.time()
            self.procesar_lote()
        else:
            self.procesar_lote()

    def procesar_lote(self):
        if self.lote_procesos:
            if not self.proceso_actual:
                self.proceso_actual = self.lote_procesos.pop(0)
                self.start_time = time.time()
                self.actualizar_tablas()
                self.root.after(1000, self.actualizar_contadores)
                self.root.after(self.proceso_actual['tiempo_estimado'] * 1000, self.terminar_proceso, self.proceso_actual)
            else:
                self.root.after(1000, self.procesar_lote)
        else:
            if self.proceso_actual is None and self.procesos:
                self.iniciar_siguiente_lote()
            else:
                self.root.after(1000, self.procesar_lote)

    def iniciar_siguiente_lote(self):
        tamano_lote = 5
        if self.procesos:
            self.lote_procesos = self.procesos[:tamano_lote]
            self.procesos = self.procesos[tamano_lote:]
            self.lotes_pendientes = (len(self.procesos) + tamano_lote - 1) // tamano_lote
            self.procesos_pendientes = self.lote_procesos[:]
            self.actualizar_tablas()
            self.procesar_lote()
        else:
            self.lote_procesos = []
            self.actualizar_tablas()

    def terminar_proceso(self, proceso):
        if self.proceso_actual:
            resultado = self.realizar_operacion(self.proceso_actual['a'], self.proceso_actual['b'], self.proceso_actual['operacion'])
            self.procesos_terminados.append({
                'id_proceso': self.proceso_actual['id_proceso'],
                'operacion': f"{self.proceso_actual['a']} {self.proceso_actual['operacion']} {self.proceso_actual['b']}",
                'resultado': resultado
            })
            self.proceso_actual = None
            self.actualizar_tablas()
            if self.lote_procesos or self.procesos:
                self.procesar_lote()
            else:
                self.actualizar_tablas()
            
        


    def realizar_operacion(self, a, b, op):
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        elif op == '/':
            return a / b if b != 0 else 'Error'
        elif op == '%':
            return a % b if b != 0 else 'Error'

def iniciar_simulador():
    root = tk.Tk()
    app = SimuladorProcesos(root)

    # Solicitar datos de procesos a la consola
    num_procesos = int(input("Dame el número de procesos: "))
    procesos = []

    for _ in range(num_procesos):
        nombre = input("Nombre del programador: ")
        while True:
            id_proceso = input("ID del proceso: ")
            if id_proceso in app.ids:
                print("Error: El ID del proceso ya existe. Por favor, ingresa un ID único.")
            else:
                app.ids.add(id_proceso)
                break

        a = int(input("Dame el 1er número: "))
        operaciones = ["+", '-', '*', '/', '%']
        while True:
            op = input("Operación a realizar (+,-,*,/,%): ")
            if op in operaciones:
                b = int(input("Dame el 2do número: "))
                if (op == '%' or op == '/') and (a == 0 or b == 0):
                    print("Error: No se permite modulo o dividir cuando uno de los operandos es 0. Ingresa otra operación o cambia los números.")
                else:
                    break
            else:
                print("Operación no válida. Por favor, intenta de nuevo.")

        tiempo_estimado = int(input("Tiempo máximo estimado para este proceso (en segundos): "))
        while tiempo_estimado <= 0:
            print("Error: El tiempo máximo estimado debe ser mayor que 0. Por favor, ingresa un valor válido.")
            tiempo_estimado = int(input("Tiempo máximo estimado para este proceso (en segundos): "))

        proceso = {
            'nombre': nombre,
            'id_proceso': id_proceso,
            'a': a,
            'b': b,
            'operacion': op,
            'tiempo_estimado': tiempo_estimado
        }
        procesos.append(proceso)

    app.procesos = procesos
    app.ejecutar_procesos()
    root.mainloop()

iniciar_simulador()

