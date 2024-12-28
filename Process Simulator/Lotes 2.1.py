import tkinter as tk
from tkinter import scrolledtext, simpledialog
import time
import random

class SimuladorProcesos:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Procesos")

        # Variables para almacenar los datos
        self.procesos = []
        self.procesos_terminados = []
        self.lote_procesos = []
        self.proceso_actual = None
        self.id_proceso_actual = 1  # ID autoincremental
        self.iniciando = True
        self.procesos_pendientes = []
        self.lotes_totales = 0
        self.lotes_pendientes = 0
        self.start_time = None
        self.total_start_time = None
        self.simulador_finalizado = False
        self.paused = False
        self.root.after_id = None  # Variable para controlar las actualizaciones periódicas
        self.total_elapsed_time = 0  # Tiempo total transcurrido antes de la pausa
        self.tiempo_trascurrido_proceso = None

        # Pedir el número de procesos
        self.num_procesos = simpledialog.askinteger("Input", "¿Cuántos procesos deseas generar?", minvalue=1)

        # Generar los procesos automáticamente
        for _ in range(self.num_procesos):
            self.agregar_proceso()

        # Configuración de la interfaz
        self.setup_ui()

        self.root.bind('<p>', lambda event: self.pausar_simulacion())
        self.root.bind('<c>', lambda event: self.reanudar_simulacion())
        self.root.bind('<i>', lambda event: self.interrupcion())
        self.root.bind('<e>', lambda event: self.error())

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

    def agregar_proceso(self):
        operaciones = ["+", '-', '*', '/', '%']
        proceso = {
            'id_proceso': self.id_proceso_actual,
            'a': random.randint(1, 100),
            'b': random.randint(1, 100),
            'operacion': random.choice(operaciones),
            'tiempo_estimado': random.randint(5, 20),
            'tiempo_transcurrido': 0  # Nuevo campo para el tiempo transcurrido
        }
        self.procesos.append(proceso)
        self.id_proceso_actual += 1


    def actualizar_tablas(self):
        # Actualizar la tabla de procesos pendientes
        self.text_pendientes.delete(1.0, tk.END)
        self.text_pendientes.insert(tk.END, "ID Proceso\tOperación\tTiempo Estimado\tTiempo Transcurrido\n")
        self.text_pendientes.insert(tk.END, "-" * 50 + "\n")
        for proceso in self.lote_procesos:
            self.text_pendientes.insert(tk.END, f"{proceso['id_proceso']}\t{proceso['a']} {proceso['operacion']} {proceso['b']}\t\t{proceso['tiempo_estimado']}\t\t{proceso['tiempo_transcurrido']}\n")

        # Actualizar el número de lotes pendientes
        self.label_lotes.config(text=f"Lotes restantes por procesar: {self.lotes_pendientes}")

        # Actualizar la tabla del proceso actual
        self.text_actual.delete(1.0, tk.END)
        if self.proceso_actual:
            self.text_actual.insert(tk.END, f"ID Proceso: {self.proceso_actual['id_proceso']}\n")
            self.text_actual.insert(tk.END, f"Operación: {self.proceso_actual['a']} {self.proceso_actual['operacion']} {self.proceso_actual['b']}\n")
            self.text_actual.insert(tk.END, f"Tiempo Estimado: {self.proceso_actual['tiempo_estimado']}\n")


        # Actualizar la tabla de procesos terminados
        self.text_terminados.delete(1.0, tk.END)
        self.text_terminados.insert(tk.END, "ID Proceso\tOperación\tResultado\n")
        self.text_terminados.insert(tk.END, "-" * 50 + "\n")
        for i, terminado in enumerate(self.procesos_terminados, 1):
            self.text_terminados.insert(tk.END, f"{terminado['id_proceso']}\t{terminado['operacion']}\t{terminado['resultado']}\n")
            if i % 5 == 0:
                self.text_terminados.insert(tk.END, "-" * 50 + "\n")

    def actualizar_contadores(self):
        if self.total_start_time and not self.simulador_finalizado and not self.paused:
            # Calcular el tiempo total del programa
            tiempo_total_programa = int(time.time() - self.total_start_time) + self.total_elapsed_time
            self.label_tiempo_programa.config(text=f"Tiempo Total del Programa: {tiempo_total_programa}s")

            if self.proceso_actual:
                tiempo_transcurrido = int(time.time() - self.start_time)
                self.label_tiempo_transcurrido.config(text=f"Tiempo Transcurrido: {tiempo_transcurrido}s")
                tiempo_restante = max(0, self.proceso_actual['tiempo_estimado'] - tiempo_transcurrido)
                self.label_tiempo_restante.config(text=f"Tiempo Restante: {tiempo_restante}s")
            else:
                self.label_tiempo_transcurrido.config(text="Tiempo Transcurrido: 0s")
                self.label_tiempo_restante.config(text="Tiempo Restante: 0s")

            # Programar la siguiente actualización solo si no está en pausa
            if not self.paused and not self.simulador_finalizado:
                self.root.after_id = self.root.after(1000, self.actualizar_contadores)

    def ejecutar_procesos(self):
        if self.iniciando:
            tamano_lote = 5
            self.lotes_totales = (len(self.procesos) + tamano_lote - 1) // tamano_lote
            self.lotes_pendientes = self.lotes_totales
            self.lote_procesos = self.procesos[:tamano_lote]
            self.procesos = self.procesos[tamano_lote:]
            self.lotes_pendientes -= 1
            self.iniciando = False
            self.total_start_time = time.time()
            self.procesar_lote()
        else:
            self.procesar_lote()

    def procesar_lote(self):
        if self.lote_procesos and not self.paused:
            if not self.proceso_actual:
                # Obtener el siguiente proceso del lote
                self.proceso_actual = self.lote_procesos.pop(0)
                
                # Actualizar el tiempo de inicio
                self.start_time = time.time() - self.proceso_actual['tiempo_transcurrido']
                self.actualizar_tablas()

                # Reanudar desde el tiempo transcurrido
                tiempo_restante = self.proceso_actual['tiempo_estimado'] - self.proceso_actual['tiempo_transcurrido']
                
                # Actualizar los contadores inmediatamente con el tiempo transcurrido y restante
                self.actualizar_contadores()

                # Programar actualizaciones periódicas de los contadores
                self.root.after(1000, self.actualizar_contadores)
                
                # Programar la finalización del proceso según el tiempo restante
                self.root.after(tiempo_restante * 1000, self.terminar_proceso, self.proceso_actual)
            else:
                # Si ya hay un proceso en ejecución, esperar 1 segundo y volver a intentar
                self.root.after(1000, self.procesar_lote)
        else:
            if self.lote_procesos:
                # Si el lote no ha terminado pero el proceso está en pausa
                self.root.after(1000, self.procesar_lote)
            elif self.procesos:
                # Si ya no hay procesos en el lote, cargar el siguiente lote de 5 procesos
                tamano_lote = 5
                self.lote_procesos = self.procesos[:tamano_lote]
                self.procesos = self.procesos[tamano_lote:]
                self.lotes_pendientes -= 1
                self.actualizar_tablas()
                self.procesar_lote()
            else:
                # Si no hay más procesos, actualizar las tablas
                self.actualizar_tablas()


    def terminar_proceso(self, proceso):
        if self.paused:
            return

        if proceso == self.proceso_actual:
            resultado = None
            if proceso['operacion'] == "+":
                resultado = proceso['a'] + proceso['b']
            elif proceso['operacion'] == "-":
                resultado = proceso['a'] - proceso['b']
            elif proceso['operacion'] == "*":
                resultado = proceso['a'] * proceso['b']
            elif proceso['operacion'] == "/":
                resultado = "Error" if proceso['b'] == 0 else proceso['a'] / proceso['b']
            elif proceso['operacion'] == "%":
                resultado = "Error" if proceso['b'] == 0 else proceso['a'] % proceso['b']

            self.procesos_terminados.append({
                'id_proceso': proceso['id_proceso'],
                'operacion': f"{proceso['a']} {proceso['operacion']} {proceso['b']}",
                'resultado': resultado
            })

            self.proceso_actual = None
            self.actualizar_tablas()

            if not self.lote_procesos and not self.procesos:
                print("Simulador finalizado.")
                self.simulador_finalizado = True

                # Detener la actualización del contador de tiempo total
                if self.root.after_id:
                    self.root.after_cancel(self.root.after_id)

                return

            self.procesar_lote()


    def interrupcion(self):
        print('interrupción: proceso enviado al final de la cola')
        if self.proceso_actual:
            self.proceso_actual['tiempo_transcurrido'] += int(time.time() - self.start_time)
            self.lote_procesos.append(self.proceso_actual)
            self.proceso_actual = None
            self.actualizar_tablas()
            self.procesar_lote()

    def error(self):
        print('error: proceso terminado con error')
        if self.proceso_actual:
            # Registrar el proceso con error
            self.procesos_terminados.append({
                'id_proceso': self.proceso_actual['id_proceso'],
                'operacion': f"{self.proceso_actual['a']} {self.proceso_actual['operacion']} {self.proceso_actual['b']}",
                'resultado': "Error"
            })

            self.proceso_actual = None
            self.actualizar_tablas()

            # Verificar si no hay más procesos pendientes
            if not self.lote_procesos and not self.procesos:
                print("Simulador finalizado.")
                self.simulador_finalizado = True

                # Detener la actualización del contador de tiempo total
                if self.root.after_id:
                    self.root.after_cancel(self.root.after_id)

                return

            # Continuar con el siguiente proceso en el lote
            self.procesar_lote()

    def pausar_simulacion(self):
        print("Pausa...... Presione c para continuar")
        self.paused = True
        if self.root.after_id:
            self.root.after_cancel(self.root.after_id)  # Detener actualizaciones

        if self.proceso_actual:
            # Guardar el tiempo transcurrido del proceso actual
            self.proceso_actual['tiempo_transcurrido'] += int(time.time() - self.start_time)

        # Guardar el tiempo total transcurrido del programa antes de la pausa
        self.total_elapsed_time += int(time.time() - self.total_start_time)

    def reanudar_simulacion(self):
        print("Simulacion continuada...")
        self.paused = False
        if self.proceso_actual:
            # Reanudar el proceso desde el tiempo transcurrido
            self.start_time = time.time() - self.proceso_actual['tiempo_transcurrido']

        # Reanudar el tiempo total del programa desde el acumulado
        self.total_start_time = time.time()

        self.actualizar_contadores()  # Reanudar actualizaciones
        self.procesar_lote()  # Reanudar el procesamiento del lote

    def run(self):
        self.root.after(1000, self.ejecutar_procesos)
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorProcesos(root)
    app.run()