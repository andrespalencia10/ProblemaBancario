import simpy
import numpy as np
import pandas as pd

# Parámetros 
HORAS_DE_OPERACION = 8
MINUTOS_POR_HORA = 60
TIEMPO_TOTAL_SIMULACION = HORAS_DE_OPERACION * MINUTOS_POR_HORA
NUM_REPLICAS = 10

# Tiempos de servicio y llegada 
tiempos_servicio = {
    "Retiro": [1, 2, 3, 4],
    "Consignacion": [3, 3, 5, 7]
}
tiempos_llegada = {
    "Retiro": [1, 2, 3, 3],
    "Consignacion": [1, 2, 3, 4]
}
probabilidades = {
    "Retiro": [0.23, 0.40, 0.17, 0.20],
    "Consignacion": [0.10, 0.20, 0.30, 0.40]
}

# generar tiempo llegada 
def generar_tiempo_llegada(tipo_accion):
    return np.random.exponential(1 / np.random.choice(tiempos_llegada[tipo_accion], p=probabilidades[tipo_accion]))

# generar tiempo servicio 
def generar_tiempo_servicio(tipo_accion):
    return np.random.exponential(np.random.choice(tiempos_servicio[tipo_accion], p=probabilidades[tipo_accion]))

# simular atención en el cajero
def atencion_cajero(env, nombre, tipo_accion, tiempo_servicio, resultados):
    yield env.timeout(tiempo_servicio)
    resultados.append({
        "Cajero": nombre,
        "TipoAccion": tipo_accion,
        "TiempoServicio": tiempo_servicio,
        "TiempoEspera": env.now
    })

# Función principal 
def simulacion(env, cajeros, tipo_accion, resultados):
    while True:
        tiempo_llegada = generar_tiempo_llegada(tipo_accion)
        yield env.timeout(tiempo_llegada)
        cajero_disponible = np.random.choice(cajeros)
        tiempo_servicio = generar_tiempo_servicio(tipo_accion)
        env.process(atencion_cajero(env, cajero_disponible, tipo_accion, tiempo_servicio, resultados))

# Ejecutar 
def ejecutar_simulacion():
    resultados = []
    for _ in range(NUM_REPLICAS):
        env = simpy.Environment()
        cajeros = ["Cajero 1", "Cajero 2", "Cajero 3"]
        env.process(simulacion(env, cajeros, "Retiro", resultados))
        env.process(simulacion(env, cajeros, "Consignacion", resultados))
        env.run(until=TIEMPO_TOTAL_SIMULACION)
    return pd.DataFrame(resultados)

#  resultados 
resultados_simulacion = ejecutar_simulacion()

# Calcular estadísticas 
tiempos_promedio = resultados_simulacion.groupby('Cajero')['TiempoServicio'].mean()
promedio_usuarios = resultados_simulacion.groupby('TipoAccion').size() / NUM_REPLICAS
total_usuarios_por_repl = resultados_simulacion.groupby(['TipoAccion', 'Cajero']).size().unstack(fill_value=0)

tiempos_promedio, promedio_usuarios, total_usuarios_por_repl
