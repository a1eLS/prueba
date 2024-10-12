import pandas as pd
import random
import datetime

# Definición global de df
df = pd.read_csv("C:/Users/ALEJANDRO/Desktop/UDABOL II 2024 7mo SEM/Interligencia Aritificial/Cajero_Automatico/codigos.csv")

def generar_numero_clave():
    return random.randint(100000, 999999)

def guardar_numero_clave(numero_clave, pin, vencimiento):
    with open("numero_clave.txt", "a") as file:
        file.write(f"{numero_clave},{pin},{vencimiento}\n")

def validar_numero_clave(numero_clave_ingresado, pin):
    try:
        with open("numero_clave.txt", "r") as file:
            for linea in file:
                numero_clave_guardado, pin_guardado, vencimiento = linea.strip().split(',')
                if int(numero_clave_guardado) == numero_clave_ingresado and int(pin_guardado) == pin:
                    return True
    except FileNotFoundError:
        print("No se ha encontrado el archivo de números clave.")
    return False

def imprimir_recibo(tipo_operacion, pin, monto=0):
    saldo_final = df.loc[df["Pin"] == pin, "Saldo"].values[0]
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    recibo = f"""
    ------------------- Recibo -------------------
    Fecha y Hora: {fecha_hora}
    Tipo de Operación: {tipo_operacion}
    Monto: {monto} Bs
    Saldo Final: {saldo_final} Bs
    ----------------------------------------------
    Gracias por utilizar nuestros servicios.
    """
    
    opcion_recibo = input("¿Desea imprimir un recibo? (s/n): ").lower()
    
    if opcion_recibo == 's':
        nombre_archivo = f"recibo_{tipo_operacion}_{fecha_hora.replace(':', '').replace(' ', '_')}.txt"
        
        with open(nombre_archivo, "w") as file:
            file.write(recibo)
        
        print(f"Recibo guardado como {nombre_archivo}.")
    else:
        print("No se imprimió el recibo.")

def retirar_dinero(pin):
    saldo_actual = df.loc[df["Pin"] == pin, "Saldo"].values[0] 
    print(f"Su saldo actual es: {saldo_actual}")
    while True:
        try:
            monto_retirar = float(input("Monto a Retirar --> "))
        except ValueError:
            print("Monto inválido. Ingrese un número válido.")
            continue
        
        if monto_retirar > saldo_actual:
            print("No tiene suficiente saldo. Intente nuevamente.")
        else:
            df.loc[df["Pin"] == pin, "Saldo"] = saldo_actual - monto_retirar
            df.to_csv("C:/Users/ALEJANDRO/Desktop/UDABOL II 2024 7mo SEM/Interligencia Aritificial/Cajero_Automatico/codigos.csv", index=False)
            print("Retiro de dinero completado.")
            imprimir_recibo("Retiro de Dinero", pin, monto_retirar)
            break

def consultar_saldo(pin):
    saldo_actual = df.loc[df["Pin"] == pin, "Saldo"].values[0]
    print(f"Su saldo actual es: {saldo_actual} Bs")
    imprimir_recibo("Consulta de Saldo", pin)

def transferir_dinero(pin):
    saldo_actual = df.loc[df["Pin"] == pin, "Saldo"].values[0]
    print(f"Su saldo actual es: {saldo_actual}")

    while True:
        try:
            cuenta_destino = int(input("Ingrese el número de cuenta de destino: "))
            monto_transferir = float(input("Monto a Transferir --> "))
        except ValueError:
            print("Valor inválido. Intente nuevamente.")
            continue
        
        if monto_transferir > saldo_actual:
            print("No tiene suficiente saldo para transferir esa cantidad. Intente nuevamente.")
        else:
            if cuenta_destino in df["Numero"].values:
                df.loc[df["Pin"] == pin, "Saldo"] = saldo_actual - monto_transferir
                df.loc[df["Numero"] == cuenta_destino, "Saldo"] += monto_transferir
                df.to_csv("C:/Users/ALEJANDRO/Desktop/UDABOL II 2024 7mo SEM/Interligencia Aritificial/Cajero_Automatico/codigos.csv", index=False)
                print("Transferencia completada.")
                imprimir_recibo("Transferencia de Dinero", pin, monto_transferir)
                break
            else:
                print("Número de cuenta no válido. Intente nuevamente.")

def menu_cajero(pin):
    while True:
        print("---------------------ELIJA UNA OPCION DEL CAJERO--------------------")
        print("1. Consultar Saldo")
        print("2. Retirar Dinero")
        print("3. Transferir Dinero")
        print("4. Salir")
        try:
            opcion_cajero = int(input("--> "))
        except ValueError:
            print("Opción inválida. Ingrese un número válido.")
            continue
        
        match opcion_cajero:
            case 1:
                consultar_saldo(pin)
            case 2:
                retirar_dinero(pin)
            case 3:
                transferir_dinero(pin)
            case 4:
                print("Saliendo del menú del cajero...")
                return  # Sale del menú del cajero
            case _:
                print("Opción inválida, seleccione una nueva opción")

def validar_pin():
    print("Ingrese su PIN: ")
    try:
        pin = int(input())
    except ValueError:
        print("PIN inválido. Ingrese un número válido.")
        return False
    
    pin_correcto = False
    
    pin_encontrado = df.loc[df["Pin"] == pin, "Pin"]
    
    if not pin_encontrado.empty:
        if pin == df.loc[df["Pin"] == pin, "Pin"].values[0]:
            print("PIN Correcto")
            pin_correcto = True
            if not menu_cajero(pin):
                return False
    else:
        print("PIN Incorrecto")
        
    return pin_correcto    

def validar_tarjeta(tarjeta_a_validar):
    global df
    
    vigente_existe = False
    
    fecha_junta_tarjeta = df.loc[df["Numero"] == tarjeta_a_validar[0], "Vencimiento"]
    
    if not fecha_junta_tarjeta.empty:
        vigente_existe = True
        fecha_separada_tarjeta = tarjeta_a_validar[1].split("/")  
        
        if int(fecha_separada_tarjeta[1]) < datetime.datetime.now().year % 100:
            print("\n         ¡¡¡¡La tarjeta ha expirado!!!!\n")
            vigente_existe = False
        elif int(fecha_separada_tarjeta[0]) < datetime.datetime.now().month:
            print("La tarjeta ha expirado")
            vigente_existe = False
        else:
            print("Tarjeta Válida")
            vigente_existe = True
            cont = 0
            while cont < 2:
                if not validar_pin():
                    cont += 1
                else:
                    break
            if cont >= 2:
                print("Superaste el número de intentos, Tarjeta Bloqueada    :,(")
                
    else:
        print("La tarjeta no existe")
        
    return vigente_existe

def retiro_sin_tarjeta(pin):
    numero_clave = generar_numero_clave()
    vencimiento = datetime.datetime.now().strftime("%m/%y")
    guardar_numero_clave(numero_clave, pin, vencimiento)
    print("Número clave generado: ", numero_clave)
    print("Fecha de vencimiento: ", vencimiento)
    
    while True:
        try:
            numero_clave_ingresado = int(input("Ingrese el número clave generado: "))
        except ValueError:
            print("Número clave inválido. Intente nuevamente.")
            continue
        
        if validar_numero_clave(numero_clave_ingresado, pin):
            print("Número clave correcto. Accediendo al menú...")
            menu_cajero(pin)  # Accede al menú de retiro, consulta, etc.
            break
        else:
            print("Número clave incorrecto. Intente nuevamente.")

def crear_cuenta():
    global df
    
    while True:
        try:
            numero = int(input("Ingrese el número de cuenta nuevo: "))
            pin = int(input("Ingrese un PIN para su cuenta (4 dígitos): "))
            saldo_inicial = float(input("Ingrese el saldo inicial: "))
        except ValueError:
            print("Datos inválidos. Ingrese valores válidos.")
            continue
        
        if len(str(pin)) != 4:
            print("El PIN debe tener 4 dígitos. Intente nuevamente.")
            continue
        
        if numero in df["Numero"].values:
            print("El número de cuenta ya existe. Intente con otro número.")
            continue
        
        nueva_fila = pd.DataFrame({
            "Numero": [numero],
            "Pin": [pin],
            "Saldo": [saldo_inicial],
            "Vencimiento": ["12/25"]
        })
        
        df = pd.concat([df, nueva_fila], ignore_index=True)
        df.to_csv("C:/Users/ALEJANDRO/Desktop/UDABOL II 2024 7mo SEM/Interligencia Aritificial/Cajero_Automatico/codigos.csv", index=False)
        print("Cuenta creada exitosamente.")
        break

def main():
    while True:
        print("¡BIENVENIDO AL BANCO BENEFICIO!")
        print("---------------------Elija una opción--------------------")
        print("1. Crear tarjeta (Si no la tiene)")
        print("2. Ir a Cajero (Si ya tiene una tarjeta)")
        print("0. Salir")
        
        try:
            opcion_inicial = int(input())
        except ValueError:
            print("Opción inválida. Ingrese un número válido.")
            continue
        
        match opcion_inicial:
            case 1:
                crear_cuenta()
            case 2:
                print("---------------------Elija una opción--------------------")
                print("1. Usar Tarjeta Física")
                print("2. Retiro Sin Tarjeta")
                
                try:
                    opcion_tarjeta = int(input())
                except ValueError:
                    print("Opción inválida. Ingrese un número válido.")
                    continue
                
                if opcion_tarjeta == 1:
                    cont = 0
                    while cont < 2:
                        lista_tarjeta = []
                        lista_tarjeta.append(int(input("Ingrese el número de la tarjeta: ")))
                        lista_tarjeta.append(input("Ingrese la fecha de vencimiento de la tarjeta (MM/AA): "))
                        
                        if not validar_tarjeta(lista_tarjeta):
                            cont += 1
                        else:
                            break
                    if cont >= 2:
                        print("Superaste el número de intentos, Tarjeta Bloqueada    :,(")
                elif opcion_tarjeta == 2:
                    pin = int(input("Ingrese su PIN para generar un número clave: "))
                    if not df.loc[df["Pin"] == pin].empty:
                        retiro_sin_tarjeta(pin)
                    else:
                        print("PIN incorrecto.")
            case 0:
                print("Gracias por utilizar el servicio.")
                break
            case _:
                print("Opción inválida. Intente nuevamente.")
        
if __name__ == "__main__":
    main()
