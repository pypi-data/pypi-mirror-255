import numpy_financial as npf

class Evaluacion:
    def __init__(self, analisis):
        self.analisis = analisis

    def calcular_ingreso_neto(self, ingreso):
        ingreso_neto = ingreso * 0.87
        return round(ingreso_neto, 2)

    def calcular_costo_neto(self, costo):
        costo_neto = costo * 0.87
        return round(costo_neto, 2)

    def calcular_gasto_neto(self, gasto):
        gasto_neto = gasto * 0.87
        return round(gasto_neto, 2)

    def calcular_interes_neto(self, interes):
        interes_neto = interes * 0.87
        return round(interes_neto, 2)

    def calcular_depreciacion_neto(self, depreciacion):
        depreciacion_neto = depreciacion * 1  # Este valor no se ajusta, ¿es correcto?
        return round(depreciacion_neto, 2)

    def calcular_impuesto_transacciones(self, ingreso):
        it = ingreso * 0.03
        return round(it, 2)

    def calcular_flujo(self, ingreso, costo, it, gasto, interes, iue):
        flujo = ingreso - costo - it - gasto - interes - iue
        return round(flujo, 2)

# Ingresar montos generales
inversion = float(input("Ingrese el monto de la inversión total: "))
periodo = int(input("Ingrese la cantidad de años del proyecto: "))
wacc = float(input("Ingrese la tasa de descuento con decimales utilizando el separador punto (.): "))

# Inicializar listas para almacenar los valores de cada período
ingresos = []
costos = []
gastos = []
intereses = []
depreciaciones = []
flujos = []

# Solicitar los montos para cada período
for i in range(1, periodo + 1):
    ingreso = float(input(f"Ingrese el monto que proyecta facturar el año {i}: "))
    costo = float(input(f"Ingrese el monto del costo el año {i}: "))
    gasto = float(input(f"Ingrese el monto del gasto el año {i}: "))
    interes = float(input(f"Ingrese el monto del interés el año {i}: "))
    depreciacion = float(input(f"Ingrese el monto de la depreciación el año {i}: "))

    ingresos.append(ingreso)
    costos.append(costo)
    gastos.append(gasto)
    intereses.append(interes)
    depreciaciones.append(depreciacion)

# Crear instancia de la clase Evaluacion
evaluacion = Evaluacion("Análisis")

# Calcular e imprimir ingresos netos, costos netos, IUE, gastos netos, intereses netos y depreciación para cada período
for i in range(periodo):
    ingreso_neto = evaluacion.calcular_ingreso_neto(ingresos[i])
    costo_neto = evaluacion.calcular_costo_neto(costos[i])
    gasto_neto = evaluacion.calcular_gasto_neto(gastos[i])
    interes_neto = evaluacion.calcular_interes_neto(intereses[i])
    depreciacion_neto = evaluacion.calcular_depreciacion_neto(depreciaciones[i])
    it = evaluacion.calcular_impuesto_transacciones(ingresos[i])
    uai = ingreso_neto - costo_neto - it - gasto_neto - interes_neto - depreciacion_neto
    iue = uai * 0.25
    uneta = uai - iue
    flujo = evaluacion.calcular_flujo(ingresos[i], costos[i], it, gastos[i], intereses[i], iue)
    flujos.append(flujo)
    tir = round(npf.irr([-inversion] + flujos), 5)
    tasa, cf =  wacc, [-inversion] + flujos
    van = npf.npv(tasa, cf).round(5)
    ir = (van+inversion)/inversion

    print(f"El ingreso neto del año {i + 1} es: {ingreso_neto}")
    print(f"El costo neto del año {i + 1} es: {costo_neto}")
    print(f"El gasto neto del año {i + 1} es: {gasto_neto}")
    print(f"El interés neto del año {i + 1} es: {interes_neto}")
    print(f"La depreciación del año {i + 1} es: {depreciacion_neto}")
    print(f"La UAI del año {i + 1} es: {uai}")
    print(f"El IUE del año {i + 1} es: {iue}")
    print(f"La Utilidad Neta del año {i + 1} es: {uneta}")
    print(f"El Impuesto a las Transacciones del año {i + 1} es: {it}")
    print(f"El flujo del año {i + 1} es: {flujo}")
    print("La TIR es:", tir)
    print("El VAN es:", van)
    print("El Periodo de Recuperación es:", ir)
