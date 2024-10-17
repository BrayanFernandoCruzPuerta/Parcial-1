# Nombre del estudiante: Brayan Fernando Cruz Puerta.
# Código del estudiante: 2041217.
# Clase: Sistemas Operativos.

from collections import deque

"""
Para realizar este programa, utilizaré el paradigma de Programación Orientada a Objetos (POO).
Este enfoque consiste en abstraer objetos de la vida real y adaptarlos a un entorno en el que puedan integrarse en nuestro programa,
llevando esos objetos con todas sus características al software para utilizarlos según nuestras necesidades.
Por ejemplo, si necesitamos una pelota como objeto en nuestro programa, esta debe tener sus características propias y útiles, como la capacidad de rebotar.
Dado que existen pelotas de diferentes tamaños, primero se crea una clase que sirve como molde para los objetos.
La clase define las características comunes, como el tamaño, permitiendo crear múltiples pelotas que se diferencien por esta propiedad.
"""

class Proceso:
    def __init__(self, etiqueta, burstTime, arrivalTime, queue, prioridad):
        self.etiqueta = etiqueta  # Identificador del proceso.
        self.burstTime = burstTime  # Tiempo de CPU necesario para completar el proceso.
        self.arrivalTime = arrivalTime  # Tiempo de llegada del proceso.
        self.queue = queue  # Número de la cola en la que se encuentra el proceso.
        self.prioridad = prioridad  # Prioridad del proceso (mayor número = mayor prioridad).
        self.remainingTime = burstTime  # Tiempo restante para completar el proceso.
        self.completionTime = 0  # Tiempo en el que el proceso se completa.
        self.waitingTime = 0  # Tiempo de espera.
        self.responseTime = -1  # Tiempo de respuesta (primera vez que se ejecuta).
        self.turnaroundTime = 0  # Turnaround Time (tiempo total desde llegada hasta fin).

class MLQ:
    def __init__(self):
        """
        Clase que representa el algoritmo Multi-Level Queue (MLQ).
        Se crean tres colas, cada una con su política de planificación.
        """
        self.colas = {1: deque(), 2: deque(), 3: deque()}  # Diccionario de colas.
        self.currentTime = 0  # Tiempo actual del sistema.
        self.procesos = []  # Lista de todos los procesos cargados.
        self.procesosPendientes = []  # Lista de procesos que aún no han llegado (AT > currentTime)

    def cargarProcesos(self, archivo):
        # Carga los procesos desde un archivo de texto.
        with open(archivo, 'r') as f: # Nombre del archivo que contiene los procesos.
            for linea in f:
                if linea.startswith("#") or not linea.strip():  # Ignorar comentarios y líneas vacías.
                    continue
                etiqueta, bt, at, q, pr = linea.strip().split(";")
                proceso = Proceso(etiqueta, int(bt), int(at), int(q), int(pr))
                self.procesosPendientes.append(proceso)  # Guardamos los procesos pendientes.

        # Ordenamos los procesos por tiempo de llegada.
        self.procesosPendientes.sort(key=lambda p: p.arrivalTime)

    def moverProcesosALaCola(self):
        # Mueve los procesos pendientes que ya han llegado (AT <= currentTime) a sus respectivas colas.
        while self.procesosPendientes and self.procesosPendientes[0].arrivalTime <= self.currentTime:
            proceso = self.procesosPendientes.pop(0)
            self.colas[proceso.queue].append(proceso)

    def ejecutar(self):
        # Ejecuta el algoritmo MLQ usando Round Robin y FCFS según la cola.
        procesosTerminados = []  # Lista para almacenar los procesos que han terminado.
        
        # Mientras haya procesos pendientes o procesos en las colas.
        while self.procesosPendientes or any(self.colas.values()):
            # Mover procesos que ya hayan llegado (AT <= currentTime) a sus respectivas colas.
            self.moverProcesosALaCola()

            # Si todas las colas están vacías, avanzar el tiempo al próximo proceso pendiente.
            if not any(self.colas.values()):
                if self.procesosPendientes:
                    self.currentTime = self.procesosPendientes[0].arrivalTime
                continue

            # Iterar sobre cada cola por prioridad.
            for q, cola in self.colas.items():
                if not cola:  # Si la cola está vacía, pasar a la siguiente.
                    continue

                proceso = cola.popleft()  # Sacar el primer proceso de la cola.

                # Si es la primera vez que el proceso se ejecuta, calcular su tiempo de respuesta.
                if proceso.responseTime == -1:
                    proceso.responseTime = max(0, self.currentTime - proceso.arrivalTime)

                # Cola 1: Round Robin (Quantum = 3).
                if q == 1:
                    quantum = 3
                    tiempoEjecucion = min(quantum, proceso.remainingTime)
                    proceso.remainingTime -= tiempoEjecucion
                    self.currentTime += tiempoEjecucion

                    # Si el proceso no ha terminado, devolverlo a la cola.
                    if proceso.remainingTime > 0:
                        cola.append(proceso)
                    else:
                        proceso.completionTime = self.currentTime
                        proceso.turnaroundTime = proceso.completionTime - proceso.arrivalTime
                        proceso.waitingTime = proceso.turnaroundTime - proceso.burstTime
                        procesosTerminados.append(proceso)

                # Cola 2: Round Robin (Quantum = 5).
                elif q == 2:
                    quantum = 5
                    tiempoEjecucion = min(quantum, proceso.remainingTime)
                    proceso.remainingTime -= tiempoEjecucion
                    self.currentTime += tiempoEjecucion

                    # Si el proceso no ha terminado, devolverlo a la cola.
                    if proceso.remainingTime > 0:
                        cola.append(proceso)
                    else:
                        proceso.completionTime = self.currentTime
                        proceso.turnaroundTime = proceso.completionTime - proceso.arrivalTime
                        proceso.waitingTime = proceso.turnaroundTime - proceso.burstTime
                        procesosTerminados.append(proceso)

                # Cola 3: First-Come, First-Served (FCFS).
                elif q == 3:
                    # FCFS ejecuta el proceso hasta que se complete.
                    self.currentTime += proceso.remainingTime
                    proceso.remainingTime = 0
                    proceso.completionTime = self.currentTime
                    proceso.turnaroundTime = proceso.completionTime - proceso.arrivalTime
                    proceso.waitingTime = proceso.turnaroundTime - proceso.burstTime
                    procesosTerminados.append(proceso)

                # Procesos han sido movidos, entonces salir de esta iteración.
                break

        return procesosTerminados # Lista de procesos terminados con sus métricas actualizadas.

    def generarSalida(self, procesosTerminados, archivoSalida):
        # Genera un archivo de salida con los detalles de la ejecución de cada proceso.
        totalWT = totalCT = totalRT = totalTAT = 0  # Variables para acumular métricas.
        
        with open(archivoSalida, 'w') as f:  # Nombre del archivo de salida.
            f.write("# etiqueta; BT; AT; Q; Pr; WT; CT; RT; TAT\n")  # Lista de procesos terminados con sus métricas calculadas.
            for p in procesosTerminados:
                # Escribir los detalles de cada proceso.
                f.write(f"{p.etiqueta}; {p.burstTime}; {p.arrivalTime}; {p.queue}; {p.prioridad}; "
                        f"{p.waitingTime}; {p.completionTime}; {p.responseTime}; {p.turnaroundTime}\n")
                
                # Acumular las métricas para calcular promedios.
                totalWT += p.waitingTime
                totalCT += p.completionTime
                totalRT += p.responseTime
                totalTAT += p.turnaroundTime

            # Calcular y escribir los promedios.
            n = len(procesosTerminados)
            f.write(f"WT={totalWT/n:.2f}; CT={totalCT/n:.2f}; RT={totalRT/n:.2f}; TAT={totalTAT/n:.2f};\n")

# Ejemplo de uso.
if __name__ == "__main__":
    # Solicitar al usuario el nombre del archivo de entrada.
    archivoEntrada = input("Por favor, ingresa el nombre del archivo de entrada: ")

    mlq = MLQ()
    mlq.cargarProcesos(archivoEntrada)  # Cargar procesos desde el archivo indicado por el usuario.
    
    procesosTerminados = mlq.ejecutar()  # Ejecutar el algoritmo MLQ.
    
    # Generar el archivo de salida con el mismo nombre base que el archivo de entrada.
    archivoSalida = f"salida_{archivoEntrada}"  # Generar el nombre del archivo de salida.
    mlq.generarSalida(procesosTerminados, archivoSalida)  # Crear el archivo de salida.

    print(f"El archivo de salida ha sido generado: {archivoSalida}")