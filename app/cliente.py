
import requests
import json
from getpass import getpass
import base64

# URL base de la API
BASE_URL = 'http://localhost:5000'

# Variables globales
usuario_autenticado = None
contraseña_autenticada = None

# FUNCIONES DE AUTENTICACION

def obtener_auth_header():
#    Crea header de autenticacion basica

    if not usuario_autenticado or not contraseña_autenticada:
        return None
    
    credenciales = f'{usuario_autenticado}:{contraseña_autenticada}'
    credenciales_base64 = base64.b64encode(credenciales.encode()).decode()
    return {'Authorization': f'Basic {credenciales_base64}'}

def registrarse():
    # Registra un nuevo usuario 
    
    print("\n=== REGISTRO DE USUARIO ===")
    usuario = input("Ingresa usuario: ").strip()
    contraseña = getpass("Ingresa contraseña: ")
    
    if not usuario or not contraseña:
        print("[ERROR] Usuario y contraseña no pueden estar vacios")
        return False
    
    try:
        respuesta = requests.post(
            f'{BASE_URL}/registro',
            json={'usuario': usuario, 'contraseña': contraseña}
        )
        
        if respuesta.status_code == 201:
            print("[EXITO] Usuario registrado exitosamente")
            return True
        else:
            datos = respuesta.json()
            print(f"[ERROR] {datos.get('error', 'Error desconocido')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al servidor")
        return False

def iniciar_sesion():
    # Inicia sesion con un usuario existente

    global usuario_autenticado, contraseña_autenticada
    
    print("\n=== INICIO DE SESION ===")
    usuario = input("Ingresa usuario: ").strip()
    contraseña = getpass("Ingresa contraseña: ")
    
    if not usuario or not contraseña:
        print("[ERROR] Usuario y contraseña no pueden estar vacios")
        return False
    
    try:
        respuesta = requests.post(
            f'{BASE_URL}/login',
            json={'usuario': usuario, 'contraseña': contraseña}
        )
        
        if respuesta.status_code == 200:
            usuario_autenticado = usuario
            contraseña_autenticada = contraseña
            datos = respuesta.json()
            print(f"[EXITO] {datos.get('mensaje')}")
            return True
        else:
            datos = respuesta.json()
            print(f"[ERROR] {datos.get('error', 'Error desconocido')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al servidor")
        return False

def cerrar_sesion():
    # Cierra la sesion actual

    global usuario_autenticado, contraseña_autenticada
    usuario_autenticado = None
    contraseña_autenticada = None
    print("[INFO] Sesion cerrada")

# FUNCIONES DE TAREAS

def listar_tareas():
    # Lista todas las tareas del usuario autenticado

    if not usuario_autenticado:
        print("[ERROR] Debes iniciar sesion primero")
        return
    
    auth = obtener_auth_header()
    
    try:
        respuesta = requests.get(
            f'{BASE_URL}/tareas/lista',
            headers=auth
        )
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            print(f"\n=== TAREAS DE {datos['usuario']} ===")
            print(f"Total de tareas: {datos['total_tareas']}\n")
            
            if not datos['tareas']:
                print("No tienes tareas registradas")
                return
            
            for tarea in datos['tareas']:
                estado = "[X]" if tarea['completada'] else "[ ]"
                print(f"{estado} ID: {tarea['id']} | {tarea['titulo']}")
        else:
            datos = respuesta.json()
            print(f"[ERROR] {datos.get('error', 'Error desconocido')}")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al servidor")

def crear_tarea():
    
    # Crea una nueva tarea

    if not usuario_autenticado:
        print("[ERROR] Debes iniciar sesion primero")
        return
    
    print("\n=== CREAR TAREA ===")
    titulo = input("Titulo: ").strip()
    
    if not titulo:
        print("[ERROR] El titulo es requerido")
        return
    
    auth = obtener_auth_header()
    
    try:
        respuesta = requests.post(
            f'{BASE_URL}/tareas/crear',
            headers=auth,
            json={'titulo': titulo}
        )
        
        if respuesta.status_code == 201:
            datos = respuesta.json()
            print(f"[EXITO] {datos.get('mensaje')}")
        else:
            datos = respuesta.json()
            print(f"[ERROR] {datos.get('error', 'Error desconocido')}")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al servidor")

def completar_tarea():
    # Marca una tarea como completada
    
    if not usuario_autenticado:
        print("[ERROR] Debes iniciar sesion primero")
        return
    
    try:
        tarea_id = int(input("\nIngresa ID de la tarea a completar: "))
    except ValueError:
        print("[ERROR] ID invalido")
        return
    
    auth = obtener_auth_header()
    
    try:
        respuesta = requests.put(
            f'{BASE_URL}/tareas/completar/{tarea_id}',
            headers=auth
        )
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            print(f"[EXITO] {datos.get('mensaje')}")
        else:
            datos = respuesta.json()
            print(f"[ERROR] {datos.get('error', 'Error desconocido')}")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al servidor")

def eliminar_tarea():
    # Elimina una tarea

    if not usuario_autenticado:
        print("[ERROR] Debes iniciar sesion primero")
        return
    
    try:
        tarea_id = int(input("\nIngresa ID de la tarea a eliminar: "))
    except ValueError:
        print("[ERROR] ID invalido")
        return
    
    auth = obtener_auth_header()
    
    try:
        respuesta = requests.delete(
            f'{BASE_URL}/tareas/eliminar/{tarea_id}',
            headers=auth
        )
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            print(f"[EXITO] {datos.get('mensaje')}")
        else:
            datos = respuesta.json()
            print(f"[ERROR] {datos.get('error', 'Error desconocido')}")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al servidor")

# MENU PRINCIPAL

def mostrar_menu():
    # Muestra el menu principal
    
    print("\n" + "="*50)
    print("GESTOR DE TAREAS - API REST")
    print("="*50)
    
    if usuario_autenticado:
        print(f"Usuario autenticado: {usuario_autenticado}")
        print("\nOpciones:")
        print("1. Ver tareas")
        print("2. Crear tarea")
        print("3. Completar tarea")
        print("4. Eliminar tarea")
        print("5. Cerrar sesion")
        print("0. Salir")
    else:
        print("\nOpciones:")
        print("1. Registrarse")
        print("2. Iniciar sesion")
        print("0. Salir")
    
    opcion = input("\nSelecciona una opcion: ").strip()
    return opcion

def main():
    # Funcion principal del cliente
    
    print("\n[INFO] Conectando a API en http://localhost:5000")
    
    while True:
        opcion = mostrar_menu()
        
        if usuario_autenticado:
            if opcion == '1':
                listar_tareas()
            elif opcion == '2':
                crear_tarea()
            elif opcion == '3':
                completar_tarea()
            elif opcion == '4':
                eliminar_tarea()
            elif opcion == '5':
                cerrar_sesion()
            elif opcion == '0':
                print("[INFO] Adios!")
                break
            else:
                print("[ERROR] Opcion invalida")
        else:
            if opcion == '1':
                registrarse()
            elif opcion == '2':
                iniciar_sesion()
            elif opcion == '0':
                print("[INFO] Adios!")
                break
            else:
                print("[ERROR] Opcion invalida")

if __name__ == '__main__':
    main()
