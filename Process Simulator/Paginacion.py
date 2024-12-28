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
        self.contador_antiguo = 0
        self.pause_start_time = None
        self.total_pause_time = 0
        self.continue_start_time = None
        self.tiempo_inicio_quantum = None
        self.tecla_n_presionada = False
        self.tiempo_pausa = 0
        self.tiempo_total_pausa = 0
        self.memoria = [None] * 41 + [{'proceso_id': 'SO', 'pagina': None, 'espacio_usado': 5}] * 5
        
        self.crear_ventana_memoria()

        # Pedir el número de procesos
        self.num_procesos = simpledialog.askinteger("Input", "¿Cuántos procesos deseas generar?", minvalue=1)

        self.quantum = simpledialog.askinteger("Input", "¿Cuál es el quantum que quieres?", minvalue=1)

        # Generar los procesos automáticamente
        for _ in range(self.num_procesos):
            self.agregar_proceso()
            for proceso in self.procesos:
                proceso['tiempo_llegada'] = 0

        # Configuración de la interfaz
        self.setup_ui()

        self.root.bind('<p>', lambda event: self.pausar_simulacion())
        self.root.bind('<c>', lambda event: self.reanudar_simulacion())
        self.root.bind('<i>', lambda event: self.interrupcion())
        self.root.bind('<e>', lambda event: self.error())
        self.root.bind('<n>', lambda event: self.nuevo_proceso())
        self.root.bind('<b>', lambda event: self.mostrar_tabla())
        self.root.bind('<t>', lambda event: self.mostrar_estado_memoria())

    def setup_ui(self):
        # Crear widgets para mostrar la tabla de procesos pendientes
        self.label_pendientes = tk.Label(self.root, text="Procesos Pendientes")
        self.label_pendientes.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.text_pendientes = scrolledtext.ScrolledText(self.root, height=10, width=60)
        self.text_pendientes.grid(row=1, column=0, padx=10, pady=10)

        # Crear widgets para mostrar el proceso actual
        self.label_actual = tk.Label(self.root, text="Proceso Actual")
        self.label_actual.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.text_actual = tk.Text(self.root, height=10, width=30)
        self.text_actual.grid(row=1, column=1, padx=10, pady=10)

        self.label_bloqueados = tk.Label(self.root, text="Procesos Bloqueados")
        self.label_bloqueados.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        self.text_bloqueados = scrolledtext.ScrolledText(self.root, height=10, width=15)
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
        self.text_terminados = scrolledtext.ScrolledText(self.root, height=10, width=85)
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
            'tiempo_llegada': None,  # Tiempo de llegada
            'tiempo_inicio': None,  # Inicializa tiempo_inicio en None
            'tiempo_finalizacion': None,  # Para el tiempo de finalización
            'tiempo_transcurrido_quantum': 0,
            'quantum': int(self.quantum),
            'tamaño': random.randint(6, 26),  # Tamaño del proceso
            'marcos': {}  # Diccionario para los marcos asignados a este proceso
        }

        

        if self.cargar_proceso_en_memoria(proceso):
            self.procesos.append(proceso)


        self.id_proceso_actual += 1




    def actualizar_tablas(self):
        # Actualizar la tabla de procesos pendientes
        self.text_pendientes.delete(1.0, tk.END)
        self.text_pendientes.insert(tk.END, "ID Proceso\tOperación\tTiempo Estimado\tTiempo Transcurrido\n")
        self.text_pendientes.insert(tk.END, "-" * 50 + "\n")
        for proceso in self.procesos:  # Mostrar solo los primeros 4 procesos en pendientes
            self.text_pendientes.insert(tk.END, f"{proceso['id_proceso']}\t{proceso['a']} {proceso['operacion']} {proceso['b']}\t\t{proceso['tiempo_estimado']}\t\t{proceso['tiempo_transcurrido']}\n")

        # Actualizar la tabla de procesos bloqueados
        self.text_bloqueados.delete(1.0, tk.END)
        self.text_bloqueados.insert(tk.END, "ID\tTiempo\n")
        self.text_bloqueados.insert(tk.END, "-" * 15 + "\n")
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
        self.text_terminados.insert(tk.END, "-" * 85 + "\n")
        for terminado in self.procesos_terminados:
            self.text_terminados.insert(tk.END, f"{terminado['id_proceso']}\t{terminado['operacion']}\t\t{terminado['resultado']}\t {terminado['tiempo_llegada']}\t   {terminado['tiempo_finalizacion']}\t       {terminado['tiempo_retorno']}\t       {terminado['tiempo_respuesta']}\t      {terminado['tiempo_espera']}\t     {terminado['tiempo_servicio']}\n")

        # Actualizar el contador de procesos en espera
        self.label_procesos_espera.config(text=f"Procesos nuevos: {len(self.procesos_espera)}")

    def actualizar_contadores(self):
        if self.total_start_time and not self.simulador_finalizado and not self.paused:
            # Calcular el tiempo total del programa sin duplicar el valor
            tiempo_total_programa = int(time.time() - self.total_start_time) + self.total_elapsed_time - self.total_pause_time
            self.label_tiempo_programa.config(text=f"Tiempo Total del Programa: {tiempo_total_programa}s")

            if self.proceso_actual:
                tiempo_transcurrido = int(time.time() - self.start_time)
                self.label_tiempo_transcurrido.config(text=f"Tiempo Transcurrido: {tiempo_transcurrido}s")
                tiempo_restante = max(0, self.proceso_actual['tiempo_estimado'] - tiempo_transcurrido)
                self.label_tiempo_restante.config(text=f"Tiempo Restante: {tiempo_restante}s")

                # Calcular el tiempo transcurrido en el quantum
                tiempo_transcurrido_quantum = int(time.time() - self.tiempo_inicio_quantum) - self.tiempo_total_pausa
                self.proceso_actual['tiempo_transcurrido_quantum'] = max(0, self.proceso_actual['quantum'] - tiempo_transcurrido_quantum)
                
                # Si el quantum se agota antes de que el proceso termine
                if tiempo_restante > 0:
                    if self.proceso_actual['tiempo_transcurrido_quantum'] == 0:
                        self.cambio_contexto(tiempo_transcurrido)
                else:
                    self.terminar_proceso(self.proceso_actual) 

            # Si hay más procesos bloqueados, actualizarlos
            for proceso in self.procesos_bloqueados:
                if 'tiempo_bloqueado_start' in proceso and not self.paused:
                    # Ajustar el tiempo bloqueado sin considerar el tiempo pausado
                    tiempo_bloqueado_transcurrido = int(time.time() - proceso['tiempo_bloqueado_start']) - self.tiempo_total_pausa
                    proceso['tiempo_bloqueado'] = max(0, 7 - tiempo_bloqueado_transcurrido)
                    if proceso['tiempo_bloqueado'] <= 0:
                        # Mover el proceso a la lista de pendientes
                        self.desbloquear_proceso(proceso)
                pass  # Aquí va tu lógica de bloqueo/desbloqueo

            self.actualizar_tablas()

            # Volver a ejecutar la actualización en un segundo
            if not self.paused and not self.simulador_finalizado:
                self.root.after_id = self.root.after(1000, self.actualizar_contadores)

    
    def cambio_contexto(self, tiempo_transcurrido):
        print('Cambio de contexto: proceso enviado al final de la cola')
        self.tiempo_total_pausa = 0
        if self.proceso_actual:
            self.proceso_actual['tiempo_transcurrido']  = tiempo_transcurrido
            self.proceso_actual['tiempo_transcurrido_quantum'] = self.quantum  # Restablecer quantum
            self.procesos.append(self.proceso_actual)  # Mover proceso al final de la cola
            self.proceso_actual = None
            self.actualizar_tablas()
            self.procesar_proceso()  # Procesar el siguiente proceso


    def ejecutar_procesos(self):
        if not self.simulador_finalizado:
            self.procesar_proceso()

    def procesar_proceso(self):
        if self.procesos and not self.paused:
            if not self.proceso_actual:
                # Obtener el siguiente proceso de la lista
                self.proceso_actual = self.procesos.pop(0)
                if self.proceso_actual['tiempo_inicio'] == None:
                    tiempo_inicio = int(time.time() - self.total_start_time) + self.total_elapsed_time - self.total_pause_time
                    self.proceso_actual['tiempo_inicio'] = tiempo_inicio

                self.tiempo_inicio_quantum = time.time()  # El tiempo de inicio del quantum

                # Actualizar el tiempo de inicio
                self.start_time = time.time() - self.proceso_actual['tiempo_transcurrido']
                self.actualizar_tablas()

                # Calcular el tiempo restante
                tiempo_restante = self.proceso_actual['tiempo_estimado'] - self.proceso_actual['tiempo_transcurrido']

                # Actualizar los contadores inmediatamente con el tiempo transcurrido y restante
                self.actualizar_contadores()
                # Programar actualizaciones periódicas de los contadores
                self.root.after(1000, self.actualizar_contadores)
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

            resultado = round(resultado,2)

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

            self.liberar_memoria_proceso(proceso)
            
            self.proceso_actual = None

            # Si hay procesos en la lista de espera, agregar el siguiente proceso a la lista de pendientes
            if self.procesos_espera:
                siguiente_proceso = self.procesos_espera.pop(0)
                if self.cargar_proceso_en_memoria(siguiente_proceso):
                    siguiente_proceso['tiempo_llegada'] = int(time.time() - self.total_start_time) + self.total_elapsed_time - self.total_pause_time
                    self.procesos.append(siguiente_proceso)
                    self.actualizar_ventana_memoria() 

            self.actualizar_tablas()
            
            # Llamar a procesar_proceso para asegurarnos de que el siguiente proceso se ejecute
            self.procesar_proceso()

            if not self.procesos and not self.procesos_espera and not self.procesos_bloqueados and not self.proceso_actual:
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

            self.liberar_memoria_proceso(self.proceso_actual)
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
                if self.cargar_proceso_en_memoria(siguiente_proceso):
                    if siguiente_proceso['tiempo_llegada'] == None:
                        siguiente_proceso['tiempo_llegada'] = int(time.time() - self.total_start_time) + self.total_elapsed_time - self.total_pause_time
                        self.procesos.append(siguiente_proceso)
                        self.actualizar_ventana_memoria()

            self.procesar_proceso()

    def pausar_simulacion(self):
        print('Simulación pausada')
        self.tiempo_total_pausa = 0
        self.paused = True
        if self.root.after_id:
            self.root.after_cancel(self.root.after_id)  # Detener actualizaciones
        # Registrar el tiempo de inicio de la pausa
        self.pause_start_time = int(time.time())
        self.tiempo_pausa = int(time.time())
        if self.proceso_actual:
            # Guardar el tiempo transcurrido del proceso actual
            self.proceso_actual['tiempo_transcurrido'] += int(time.time() - self.start_time)
        # Guardar el tiempo total transcurrido del programa antes de la pausa
        self.total_elapsed_time += int(time.time() - self.total_start_time)

    def reanudar_simulacion(self):
        print('Simulación reanudada')
        self.paused = False
        self.continue_start_time = int(time.time())
        self.tiempo_total_pausa += int(time.time() - self.tiempo_pausa)
        if self.proceso_actual:
            # Reanudar el proceso desde el tiempo transcurrido acumulado
            self.start_time = time.time() - self.proceso_actual['tiempo_transcurrido']
        # Reanudar el tiempo total del programa desde el acumulado
        self.total_start_time = time.time()

        self.actualizar_contadores()  # Reanudar actualizaciones
        self.procesar_proceso()  # Reanudar el procesamiento del lote

    def mostrar_tabla(self):
        self.pausar_simulacion()  # Pausar la simulación

        # Crear una nueva ventana para mostrar la tabla
        ventana_tabla = tk.Toplevel(self.root)
        ventana_tabla.title("Tabla de Procesos")

        text_tabla = scrolledtext.ScrolledText(ventana_tabla, height=20, width=150)
        text_tabla.grid(row=0, column=0, padx=10, pady=10)

        # Cabecera de la tabla
        text_tabla.insert(tk.END, "ID\tEstado\tOperación\tResultado\tLlegada\tFinalización\tRetorno\tEspera\tServicio\tRestante CPU\tRespuesta\n")
        text_tabla.insert(tk.END, "-" * 100 + "\n")

        if self.proceso_actual:
            estado = "En ejecución"
            resultado = "En progreso"
            #self.proceso_actual['tiempo_transcurrido'] = int(time.time() - self.start_time)
            #tiempo_total_programa = int(time.time() - self.total_start_time) + self.total_elapsed_time - self.total_pause_time
            tiempo_total_programa = self.total_elapsed_time
            tiempo_espera = tiempo_total_programa - self.proceso_actual['tiempo_llegada'] - self.proceso_actual['tiempo_transcurrido']
            restante_cpu = max(0, self.proceso_actual['tiempo_estimado'] - self.proceso_actual['tiempo_transcurrido'])
            tiempo_respuesta = self.proceso_actual['tiempo_inicio'] - self.proceso_actual['tiempo_llegada'] if self.proceso_actual['tiempo_inicio'] is not None else "N/A"
            text_tabla.insert(tk.END, f"{self.proceso_actual['id_proceso']}\t|{estado}|\t|{self.proceso_actual['a']} {self.proceso_actual['operacion']} {self.proceso_actual['b']}|\t|{resultado}|\t|{self.proceso_actual['tiempo_llegada']}|\t|N/A|\t|N/A|\t|{tiempo_espera}|\t|{self.proceso_actual['tiempo_transcurrido']}|\t|{restante_cpu}|\t|{tiempo_respuesta}|\n")
        
        # Recorrer todos los procesos pendientes, bloqueados, terminados y en espera
        for proceso in self.procesos:
            estado = "Pendiente"
            resultado = "En progreso"  # Resultado aún no calculado
            tiempo_transcurrido = int(time.time() - self.start_time)
            tiempo_espera = tiempo_total_programa - proceso['tiempo_llegada'] - proceso['tiempo_transcurrido']
            restante_cpu = max(0, proceso['tiempo_estimado'] - proceso['tiempo_transcurrido'])
            tiempo_respuesta = proceso['tiempo_inicio'] - proceso['tiempo_llegada'] if proceso['tiempo_inicio'] is not None else "N/A"
            text_tabla.insert(tk.END, f"{proceso['id_proceso']}\t{estado}\t{proceso['a']} {proceso['operacion']} {proceso['b']}\t{resultado}\t{proceso['tiempo_llegada']}\tN/A\tN/A\t{tiempo_espera}\t{proceso['tiempo_transcurrido']}\t{restante_cpu}\t{tiempo_respuesta}\n")

        for proceso in self.procesos_bloqueados:
            estado = "Bloqueado"
            resultado = "En progreso"
            tiempo_transcurrido = int(time.time() - self.start_time)
            tiempo_espera = tiempo_total_programa - proceso['tiempo_llegada'] - proceso['tiempo_transcurrido']
            restante_cpu = max(0, proceso['tiempo_estimado'] - proceso['tiempo_transcurrido'])
            tiempo_respuesta = proceso['tiempo_inicio'] - proceso['tiempo_llegada'] if proceso['tiempo_inicio'] is not None else "N/A"
            text_tabla.insert(tk.END, f"{proceso['id_proceso']}\t{estado}\t{proceso['a']} {proceso['operacion']} {proceso['b']}\t{resultado}\t{proceso['tiempo_llegada']}\tN/A\tN/A\t{tiempo_espera}\t{proceso['tiempo_transcurrido']}\t{restante_cpu}\t{tiempo_respuesta}\n")

        for proceso in self.procesos_espera:
            estado = "En espera"
            resultado = "En progreso"
            restante_cpu = max(0, proceso['tiempo_estimado'] - proceso['tiempo_transcurrido'])
            tiempo_respuesta = proceso['tiempo_inicio'] - proceso['tiempo_llegada'] if proceso['tiempo_inicio'] is not None else "N/A"
            text_tabla.insert(tk.END, f"{proceso['id_proceso']}\t{estado}\t{proceso['a']} {proceso['operacion']} {proceso['b']}\t{resultado}0\t{proceso['tiempo_llegada']}\tN/A\tN/A\tN/A\tN/A\tN/A\t{tiempo_respuesta}\n")

        for proceso in self.procesos_terminados:
            estado = "Terminado"
            resultado = proceso['resultado']
            tiempo_retorno = proceso['tiempo_retorno']
            tiempo_espera = proceso['tiempo_espera']
            tiempo_servicio = proceso['tiempo_servicio']
            tiempo_respuesta = proceso['tiempo_respuesta']
            text_tabla.insert(tk.END, f"{proceso['id_proceso']}\t{estado}\t{proceso['operacion']}\t{resultado}\t{proceso['tiempo_llegada']}\t{proceso['tiempo_finalizacion']}\t{tiempo_retorno}\t{tiempo_espera}\t{tiempo_servicio}\t0\t{tiempo_respuesta}\n")

        # Deshabilitar la edición del texto de la tabla
        text_tabla.config(state=tk.DISABLED)

    def nuevo_proceso(self):
        self.tecla_n_presionada = True
        self.agregar_proceso()

        if not self.proceso_actual:
            self.procesar_proceso()


    def iniciar_simulacion(self):
        self.total_start_time = time.time()
        self.ejecutar_procesos()
        self.actualizar_contadores()

    def dividir_proceso_en_paginas(self, proceso):
        paginas = []
        tamaño_restante = proceso['tamaño']
        while tamaño_restante > 0:
            paginas.append(min(tamaño_restante, 5))  # Cada página tiene máximo 5 unidades
            tamaño_restante -= 5
        return paginas

    def verificar_marcos_disponibles(self, paginas_necesarias):
        marcos_libres = [i for i, marco in enumerate(self.memoria) if marco is None]
        return len(marcos_libres) >= paginas_necesarias
    
    def cargar_proceso_en_memoria(self, proceso):
        paginas = self.dividir_proceso_en_paginas(proceso)  # Divide el proceso en páginas de tamaño <= 5
        if not self.verificar_marcos_disponibles(len(paginas)):
            print("No hay suficiente espacio en memoria para el proceso.")
            self.procesos_espera.append(proceso)
            return False

        # Asignar marcos libres a las páginas del proceso
        marcos_libres = [i for i, marco in enumerate(self.memoria) if marco is None]
        proceso['marcos'] = {}
        for i, pagina in enumerate(paginas):
            marco = marcos_libres.pop(0)
            self.memoria[marco] = {
                'proceso_id': proceso['id_proceso'],
                'pagina': i,
                'espacio_usado': pagina  # Cantidad de unidades usadas por la página
            }
            proceso['marcos'][i] = marco

        try:
            if proceso['tiempo_llegada'] == None:
                proceso['tiempo_llegada'] = int(time.time() - self.total_start_time) + self.total_elapsed_time - self.total_pause_time
        except:
            print()
        
        # Actualizar la ventana de memoria tras cargar el proceso
        self.actualizar_ventana_memoria()
        return True

    def liberar_memoria_proceso(self, proceso):
        # Liberar los marcos ocupados por las páginas del proceso terminado
        for marco in proceso['marcos'].values():
            self.memoria[marco] = None  # Libera el marco, marcándolo como disponible

        self.actualizar_ventana_memoria()

    def crear_ventana_memoria(self):
        # Crear la ventana de memoria persistente
        self.ventana_memoria = tk.Toplevel(self.root)
        self.ventana_memoria.title("Estado de Memoria")
        
        # Crear un widget de texto desplazable para mostrar el estado de la memoria
        self.texto_memoria = scrolledtext.ScrolledText(self.ventana_memoria, height=60, width=50)
        self.texto_memoria.grid(row=0, column=0, padx=10, pady=10)
        
        # Llama a actualizar el estado de la memoria al abrir la ventana
        self.actualizar_ventana_memoria()

    def actualizar_ventana_memoria(self):
        # Actualizar el contenido del widget de texto en la ventana de memoria
        self.texto_memoria.config(state=tk.NORMAL)  # Habilita edición temporal para actualizar
        self.texto_memoria.delete(1.0, tk.END)
        
        # Título y encabezado de la tabla
        self.texto_memoria.insert(tk.END, "Marco\tEstado\tProceso\tPágina\tEspacio Usado\n")
        self.texto_memoria.insert(tk.END, "-" * 50 + "\n")
        
        # Recorrer los marcos de memoria y mostrar su estado
        for i, marco in enumerate(self.memoria):
            if marco is None:
                estado = "Libre"
                proceso_id = "-"
                pagina = "-"
                espacio_usado = "0/5"
            else:
                estado = "Ocupado"
                proceso_id = marco['proceso_id']
                pagina = marco['pagina']
                espacio_usado = f"{marco['espacio_usado']}/5"  # Mostrar el espacio usado por la página
            
            # Agregar la información del marco al texto
            self.texto_memoria.insert(tk.END, f"{i}\t{estado}\t{proceso_id}\t{pagina}\t{espacio_usado}\n")
        
        # Desactivar la edición del texto para evitar modificaciones accidentales
        self.texto_memoria.config(state=tk.DISABLED)

    def mostrar_estado_memoria(self):
        self.pausar_simulacion()


if __name__ == "__main__":
    root = tk.Tk()
    simulador = SimuladorProcesos(root)
    simulador.iniciar_simulacion()
    root.mainloop()