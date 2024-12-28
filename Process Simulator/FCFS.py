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
        self.procesos_bloqueados = []
        self.procesos_espera = []  # Lista de procesos en espera
        self.proceso_actual = None
        self.id_proceso_actual = 1  # ID autoincremental
        self.start_time = None
        self.start_bloqued_time = None
        self.total_start_time = None
        self.simulador_finalizado = False
        self.paused = False
        self.root.after_id = None  # Variable para controlar las actualizaciones periódicas
        self.total_elapsed_time = 0  # Tiempo total transcurrido antes de la pausa
        self.root.after_id_block = None
        

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

        # Crear widgets para mostrar el proceso actual
        self.label_actual = tk.Label(self.root, text="Proceso Actual")
        self.label_actual.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.text_actual = tk.Text(self.root, height=10, width=50)
        self.text_actual.grid(row=1, column=1, padx=10, pady=10)

        self.label_bloqueados = tk.Label(self.root, text="Procesos Bloqueados")
        self.label_bloqueados.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        self.text_bloqueados = scrolledtext.ScrolledText(self.root, height=10, width=30)
        self.text_bloqueados.grid(row=1, column=3, padx=10, pady=10)

        # Labels para mostrar el tiempo transcurrido y tiempo total del programa
        self.label_procesos_espera = tk.Label(self.root, text="Procesos en Espera: 0")
        self.label_procesos_espera.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.label_tiempo_transcurrido = tk.Label(self.root, text="Tiempo Transcurrido: 0s")
        self.label_tiempo_transcurrido.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.label_tiempo_restante = tk.Label(self.root, text="Tiempo Restante: 0s")
        self.label_tiempo_restante.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.label_tiempo_programa = tk.Label(self.root, text="Tiempo Total del Programa: 0s")
        self.label_tiempo_programa.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Crear widgets para mostrar la tabla de procesos terminados
        self.label_terminados = tk.Label(self.root, text="Procesos Terminados")
        self.label_terminados.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.text_terminados = scrolledtext.ScrolledText(self.root, height=10, width=90)
        self.text_terminados.grid(row=4, column=0, padx=10, pady=10)

    def agregar_proceso(self):
        operaciones = ["+", '-', '*', '/', '%']
        proceso = {
            'id_proceso': self.id_proceso_actual,
            'a': random.randint(1, 100),
            'b': random.randint(1, 100),
            'operacion': random.choice(operaciones),
            'tiempo_estimado': random.randint(5, 20),
            'tiempo_transcurrido': 0,
            'tiempo_bloqueado': 0,
            'tiempo_bloqueado_start': 0,
            'tiempo_llegada': None, # Tiempo de llegada
            'tiempo_inicio': None,  # Para calcular el tiempo de respuesta
            'tiempo_finalizacion': None  # Para el tiempo de finalización
        }
        if len(self.procesos) < 5:
            # Si hay menos de 5 procesos en pendientes, agregar directamente
            proceso['tiempo_llegada'] = 0
            self.procesos.append(proceso)
        else:
            # Si ya hay 5 procesos en pendientes, agregar a la lista de espera
            self.procesos_espera.append(proceso)
        self.id_proceso_actual += 1

    def actualizar_tablas(self):
        # Actualizar la tabla de procesos pendientes
        self.text_pendientes.delete(1.0, tk.END)
        self.text_pendientes.insert(tk.END, "ID Proceso\tOperación\tTiempo Estimado\tTiempo Transcurrido\n")
        self.text_pendientes.insert(tk.END, "-" * 50 + "\n")
        for proceso in self.procesos:
            self.text_pendientes.insert(tk.END, f"{proceso['id_proceso']}\t{proceso['a']} {proceso['operacion']} {proceso['b']}\t\t{proceso['tiempo_estimado']}\t\t{proceso['tiempo_transcurrido']}\n")

        # Actualizar la tabla de procesos bloqueados
        self.text_bloqueados.delete(1.0, tk.END)
        self.text_bloqueados.insert(tk.END, "ID Proceso\tTiempo Bloqueado\n")
        self.text_bloqueados.insert(tk.END, "-" * 50 + "\n")
        for bloqueado in self.procesos_bloqueados:
            self.text_bloqueados.insert(tk.END, f"{bloqueado['id_proceso']}\t{bloqueado['tiempo_bloqueado']}\n")

        # Actualizar la tabla del proceso actual
        self.text_actual.delete(1.0, tk.END)
        if self.proceso_actual:
            self.text_actual.insert(tk.END, f"ID Proceso: {self.proceso_actual['id_proceso']}\n")
            self.text_actual.insert(tk.END, f"Operación: {self.proceso_actual['a']} {self.proceso_actual['operacion']} {self.proceso_actual['b']}\n")
            self.text_actual.insert(tk.END, f"Tiempo Estimado: {self.proceso_actual['tiempo_estimado']}\n")

        # Actualizar la tabla de procesos terminados
        self.text_terminados.delete(1.0, tk.END)
        self.text_terminados.insert(tk.END, "ID Proceso\tOperación\tResultado\tLlegada\tFinalizacion\tRetorno\tRespuesta\tEspera\tServicio\n")
        self.text_terminados.insert(tk.END, "-" * 50 + "\n")
        for terminado in self.procesos_terminados:
            self.text_terminados.insert(tk.END, f"{terminado['id_proceso']}\t{terminado['operacion']}\t\t{terminado['resultado']}\t {terminado['tiempo_llegada']}\t   {terminado['tiempo_finalizacion']}\t       {terminado['tiempo_retorno']}\t       {terminado['tiempo_respuesta']}\t      {terminado['tiempo_espera']}\t     {terminado['tiempo_servicio']}\n")

        # Actualizar el contador de procesos en espera
        self.label_procesos_espera.config(text=f"Procesos en Espera: {len(self.procesos_espera)}")


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

            # Actualizar el tiempo bloqueado de cada proceso bloqueado
            for proceso in self.procesos_bloqueados:
                if 'tiempo_bloqueado_start' in proceso:
                    tiempo_bloqueado_transcurrido = int(time.time() - proceso['tiempo_bloqueado_start'])
                    proceso['tiempo_bloqueado'] = max(0, 7 - tiempo_bloqueado_transcurrido)  # Asegurarse de que sean 7 segundos

                    if proceso['tiempo_bloqueado'] <= 0:
                        # Mover el proceso a la lista de pendientes
                        self.desbloquear_proceso(proceso)

            # Actualizar la tabla de procesos
            self.actualizar_tablas()

            # Programar la siguiente actualización
            if not self.paused and not self.simulador_finalizado:
                self.root.after(1000, self.actualizar_contadores)


    def ejecutar_procesos(self):
        if not self.simulador_finalizado:
            self.procesar_proceso()

    def procesar_proceso(self):
        try:
            if self.procesos[-1]['tiempo_llegada'] == None:
                self.procesos[-1]['tiempo_llegada'] = int(time.time() - self.total_start_time) + self.total_elapsed_time
                print(self.procesos[-1]['tiempo_llegada'], self.procesos[-1]['id_proceso'])
        except:
            print()

        if self.procesos and not self.paused:
            if not self.proceso_actual:
                # Obtener el siguiente proceso de la lista
                self.proceso_actual = self.procesos.pop(0)
                if self.proceso_actual['tiempo_inicio'] == None:
                    tiempo_inicio = int(time.time() - self.total_start_time) + self.total_elapsed_time
                    self.proceso_actual['tiempo_inicio'] = tiempo_inicio

                # Actualizar el tiempo de inicio
                self.start_time = time.time() - self.proceso_actual['tiempo_transcurrido']
                self.actualizar_tablas()

                # Calcular el tiempo restante
                tiempo_restante = self.proceso_actual['tiempo_estimado'] - self.proceso_actual['tiempo_transcurrido']

                # Actualizar los contadores inmediatamente con el tiempo transcurrido y restante
                self.actualizar_contadores()

                # Programar actualizaciones periódicas de los contadores
                self.root.after(1000, self.actualizar_contadores)

                # Programar la finalización del proceso según el tiempo estimado
                self.root.after(tiempo_restante * 1000, self.terminar_proceso, self.proceso_actual)
            else:
                # Si ya hay un proceso en ejecución, esperar 1 segundo y volver a intentar
                self.root.after(1000, self.procesar_proceso)
        else:
            # Si no hay más procesos
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

                # Calcular el tiempo de finalización
            proceso['tiempo_finalizacion'] = int(time.time() - self.total_start_time) + self.total_elapsed_time

            # Calcular tiempos
            tiempo_llegada = proceso['tiempo_llegada']
            tiempo_finalizacion = proceso['tiempo_finalizacion']
            tiempo_respuesta = int(proceso['tiempo_inicio']) - tiempo_llegada
            tiempo_retorno = tiempo_finalizacion - tiempo_llegada
            tiempo_servicio = proceso['tiempo_estimado']
            tiempo_espera = tiempo_retorno - tiempo_servicio  # tiempo_retorno - tiempo de servicio


            self.procesos_terminados.append({
            'id_proceso': proceso['id_proceso'],
            'operacion': f"{proceso['a']} {proceso['operacion']} {proceso['b']}",
            'resultado': resultado,
            'tiempo_llegada': tiempo_llegada,
            'tiempo_finalizacion': tiempo_finalizacion,
            'tiempo_retorno': tiempo_retorno,
            'tiempo_respuesta': tiempo_respuesta,
            'tiempo_espera': tiempo_espera,
            'tiempo_servicio': tiempo_servicio
        })

            self.proceso_actual = None

            # Si hay procesos en la lista de espera, agregar el siguiente proceso a la lista de pendientes
            if self.procesos_espera:
                siguiente_proceso = self.procesos_espera.pop(0)
                self.procesos.append(siguiente_proceso)

            self.actualizar_tablas()
            
            # Llamar a procesar_proceso para asegurarnos de que el siguiente proceso se ejecute
            self.procesar_proceso()

            if not self.procesos and not self.procesos_espera and not self.procesos_bloqueados:
                print("Simulador finalizado.")
                self.simulador_finalizado = True

                # Detener la actualización del contador de tiempo total
                if self.root.after_id:
                    self.root.after_cancel(self.root.after_id)



    def desbloquear_proceso(self, proceso):
        print(f"Proceso {proceso['id_proceso']} desbloqueado y movido a la lista de pendientes")
        self.procesos_bloqueados.remove(proceso)  # Quitar de la lista de bloqueados
        self.procesos.append(proceso)  # Agregar a la lista de pendientes
        if not self.proceso_actual:
            self.ejecutar_procesos()
            self.actualizar_tablas()

    def interrupcion(self):
        print('Interrupción: proceso enviado al final de la cola')
        if self.proceso_actual:
            self.proceso_actual['tiempo_transcurrido'] += int(time.time() - self.start_time)
            self.proceso_actual['tiempo_bloqueado_start'] = time.time()  # Registrar el tiempo actual
            self.proceso_actual['tiempo_bloqueado'] = 7  # Establecer tiempo total bloqueado a 7 segundos
            self.procesos_bloqueados.append(self.proceso_actual)
            self.proceso_actual = None
            self.actualizar_tablas()
            self.procesar_proceso()

    def error(self):
        print('Error: proceso cancelado')
        if self.proceso_actual:

            # Calcular el tiempo de finalización
            self.proceso_actual['tiempo_finalizacion'] = int(time.time() - self.total_start_time) + self.total_elapsed_time

            # Calcular tiempos
            tiempo_llegada = self.proceso_actual['tiempo_llegada']
            tiempo_finalizacion = self.proceso_actual['tiempo_finalizacion']
            tiempo_respuesta = int(self.proceso_actual['tiempo_inicio']) - tiempo_llegada
            tiempo_retorno = tiempo_finalizacion - tiempo_llegada
            tiempo_servicio = int(time.time() - self.start_time)
            tiempo_espera = tiempo_retorno - tiempo_servicio  # tiempo_retorno - tiempo de servicio

            self.procesos_terminados.append({
            'id_proceso': self.proceso_actual['id_proceso'],
            'operacion': f"{self.proceso_actual['a']} {self.proceso_actual['operacion']} {self.proceso_actual['b']}",
            'resultado': 'Error',
            'tiempo_llegada': tiempo_llegada,
            'tiempo_finalizacion': tiempo_finalizacion,
            'tiempo_retorno': tiempo_retorno,
            'tiempo_respuesta': tiempo_respuesta,
            'tiempo_espera': tiempo_espera,
            'tiempo_servicio': tiempo_servicio
        })

            self.proceso_actual = None
            self.actualizar_tablas()

            if not self.procesos and not self.procesos_bloqueados:
                print("Simulador finalizado.")
                self.simulador_finalizado = True

                # Detener la actualización del contador de tiempo total
                if self.root.after_id:
                    self.root.after_cancel(self.root.after_id)

                return
            
            if self.procesos_espera:
                siguiente_proceso = self.procesos_espera.pop(0)
                self.procesos.append(siguiente_proceso)

            self.procesar_proceso()

    def pausar_simulacion(self):
        global tiempo_restante
        print('Simulación pausada')
        self.paused = True
        if self.root.after_id:
            self.root.after_cancel(self.root.after_id)  # Detener actualizaciones

        if self.proceso_actual:
            # Guardar el tiempo transcurrido del proceso actual
            self.proceso_actual['tiempo_transcurrido'] += int(time.time() - self.start_time)

        # Guardar el tiempo total transcurrido del programa antes de la pausa
        self.total_elapsed_time += int(time.time() - self.total_start_time)

    def reanudar_simulacion(self):
        print('Simulación reanudada')
        self.paused = False
        if self.proceso_actual:
            # Reanudar el proceso desde el tiempo transcurrido
            self.start_time = time.time() - self.proceso_actual['tiempo_transcurrido']

        # Reanudar el tiempo total del programa desde el acumulado
        self.total_start_time = time.time()

        self.actualizar_contadores()  # Reanudar actualizaciones
        self.procesar_proceso()  # Reanudar el procesamiento del lote

    def iniciar_simulacion(self):
        self.total_start_time = time.time()
        self.ejecutar_procesos()
        self.actualizar_contadores()

if __name__ == "__main__":
    root = tk.Tk()
    simulador = SimuladorProcesos(root)
    simulador.iniciar_simulacion()
    root.mainloop()
