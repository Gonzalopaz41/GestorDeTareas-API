# Sistema de Gestion de Tareas con API REST

## Instalacion

```bash
pip install flask requests werkzeug
```

## Ejecucion

### Terminal 1: Iniciar servidor

```bash
python servidor.py
```

### Terminal 2: Ejecutar cliente

```bash
python cliente.py
```

## Funcionalidades

- Registro de usuarios con contraseñas hasheadas
- Inicio de sesion con autenticacion basica
- Crear tareas
- Listar tareas
- Marcar tareas como completadas
- Eliminar tareas
- Datos persistentes en SQLite

## Endpoints de la API

### Autenticacion

- POST /registro - Registrar nuevo usuario
- POST /login - Iniciar sesion

### Tareas (requieren autenticacion)

- GET /tareas - Ver interfaz HTML
- GET /tareas/lista - Listar todas las tareas
- POST /tareas/crear - Crear nueva tarea
- PUT /tareas/completar/<id> - Completar una tarea
- DELETE /tareas/eliminar/<id> - Eliminar una tarea

## Estructura de la BD

### Tabla usuarios

- id: INTEGER PRIMARY KEY
- usuario: TEXT UNIQUE
- contraseña_hash: TEXT (nunca en texto plano)
- fecha_creacion: TIMESTAMP

### Tabla tareas

- id: INTEGER PRIMARY KEY
- usuario_id: INTEGER (FK a usuarios)
- titulo: TEXT
- completada: BOOLEAN
- fecha_creacion: TIMESTAMP

## Por que hashear contraseñas?

1. Seguridad: Si la BD se compromete, las contraseñas no se ven
2. Integridad: Verificar sin exponer contraseña original
3. Estandar: Practica obligatoria en seguridad web
4. Irreversible: Las contraseñas no se pueden recuperar

## Ventajas de SQLite

1. Facil de usar: No requiere instalacion de servidor
2. Portable: Base de datos en un solo archivo
3. Confiable: Transacciones ACID implementadas
4. Perfecto para desarrollo: Ideal para proyectos pequeños
5. Integrado: Viene con Python por defecto

#Pruebas

1. Registrar usuario:

  <img width="400" height="300" alt="Image" src="https://github.com/user-attachments/assets/cf3f867c-3bd1-4700-92cd-1c02136ebdc1" />

2. Login de Usuario:

  <img width="400" height="300" alt="Image" src="https://github.com/user-attachments/assets/efe4134b-458b-4f60-bee4-a5a9c5e260e3" />

3. Crear tarea:

  <img width="400" height="300" alt="Image" src="https://github.com/user-attachments/assets/559f2e6c-2b9a-418a-b675-58f7774ce3e8" />

4. Ver tareas:

  <img width="400" height="300" alt="Image" src="https://github.com/user-attachments/assets/2784d5e2-5748-43f2-b27e-cd8c19e6239f" />
