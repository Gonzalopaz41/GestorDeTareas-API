

from flask import Flask, request, jsonify, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_super_segura'
DATABASE = 'tareas.db'

# CONFIGURACION DE BASE DE DATOS

def obtener_conexion():
    
    # Obtiene conexion a la base de datos SQLite
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_db():
    # Inicializa la base de datos con las tablas necesarias
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contraseña_hash TEXT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de tareas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            completada BOOLEAN DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    conexion.commit()
    conexion.close()
    print("[BD] Base de datos inicializada")

# FUNCIONES DE AUTENTICACION

def verificar_credenciales():
    # Decorador para verificar autenticacion basica

    def decorador(f):
        @wraps(f)
        def verificar(*args, **kwargs):
            auth = request.authorization
            
            if not auth or not auth.username or not auth.password:
                return jsonify({'error': 'Credenciales requeridas'}), 401
            
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE usuario = ?', (auth.username,))
            usuario = cursor.fetchone()
            conexion.close()
            
            if not usuario or not check_password_hash(usuario['contraseña_hash'], auth.password):
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
            
            # Pasar el usuario al endpoint
            kwargs['usuario_id'] = usuario['id']
            kwargs['usuario_nombre'] = usuario['usuario']
            return f(*args, **kwargs)
        return verificar
    return decorador

# ENDPOINTS DE AUTENTICACION

@app.route('/registro', methods=['POST'])
def registro():
    
    # Endpoint de registro de nuevos usuarios
    # Recibe: {"usuario": "nombre", "contraseña": "1234"}

    datos = request.get_json()
    
    if not datos or not datos.get('usuario') or not datos.get('contraseña'):
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    
    usuario = datos.get('usuario')
    contraseña = datos.get('contraseña')
    
    # Validar longitud minima
    if len(usuario) < 3:
        return jsonify({'error': 'Usuario debe tener minimo 3 caracteres'}), 400
    
    if len(contraseña) < 4:
        return jsonify({'error': 'Contraseña debe tener minimo 4 caracteres'}), 400
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Hashear contraseña antes de guardar
        contraseña_hash = generate_password_hash(contraseña)
        
        cursor.execute('''
            INSERT INTO usuarios (usuario, contraseña_hash)
            VALUES (?, ?)
        ''', (usuario, contraseña_hash))
        
        conexion.commit()
        conexion.close()
        
        return jsonify({'mensaje': f'Usuario {usuario} registrado exitosamente'}), 201
        
    except sqlite3.IntegrityError:
        return jsonify({'error': 'El usuario ya existe'}), 409

@app.route('/login', methods=['POST'])
def login():
    # Endpoint de inicio de sesion
    # Verifica credenciales y retorna mensaje de bienvenida

    datos = request.get_json()
    
    if not datos or not datos.get('usuario') or not datos.get('contraseña'):
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    
    usuario = datos.get('usuario')
    contraseña = datos.get('contraseña')
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE usuario = ?', (usuario,))
    usuario_bd = cursor.fetchone()
    conexion.close()
    
    if not usuario_bd or not check_password_hash(usuario_bd['contraseña_hash'], contraseña):
        return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
    
    return jsonify({
        'mensaje': f'Bienvenido {usuario}',
        'usuario_id': usuario_bd['id']
    }), 200

# ENDPOINTS DE TAREAS

@app.route('/tareas', methods=['GET'])
def mostrar_tareas():
    """
    Muestra HTML de bienvenida con interfaz simple
    """
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gestor de Tareas</title>
        <style>
            body { font-family: Arial; margin: 40px; background-color: #f0f0f0; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; }
            h1 { color: #333; }
            .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }
            code { background: #f5f5f5; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Gestor de Tareas - API REST</h1>
            
            <div class="info">
                <h2>Endpoints disponibles:</h2>
                <p><strong>Registro:</strong> POST /registro</p>
                <code>{"usuario": "juan", "contraseña": "1234"}</code>
                
                <p><strong>Login:</strong> POST /login</p>
                <code>{"usuario": "juan", "contraseña": "1234"}</code>
                
                <p><strong>Ver Tareas:</strong> GET /tareas/lista</p>
                <p>Requiere autenticacion basica</p>
                
                <p><strong>Crear Tarea:</strong> POST /tareas/crear</p>
                <code>{"titulo": "Mi tarea"}</code>
                <p>Requiere autenticacion basica</p>
                
                <p><strong>Completar Tarea:</strong> PUT /tareas/completar/ID</p>
                <p>Requiere autenticacion basica</p>
                
                <p><strong>Eliminar Tarea:</strong> DELETE /tareas/eliminar/ID</p>
                <p>Requiere autenticacion basica</p>
            </div>
            
            <div class="info">
                <h3>Instrucciones de uso:</h3>
                <p>1. Registrate con POST /registro</p>
                <p>2. Inicia sesion con POST /login</p>
                <p>3. Usa los endpoints de tareas con autenticacion basica</p>
                <p>4. Usuario y contraseña se envian en Authorization: Basic [base64]</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/tareas/lista', methods=['GET'])
@verificar_credenciales()
def listar_tareas(usuario_id, usuario_nombre):
    # Lista todas las tareas del usuario autenticado

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute('''
        SELECT id, titulo, completada, fecha_creacion
        FROM tareas
        WHERE usuario_id = ?
        ORDER BY fecha_creacion DESC
    ''', (usuario_id,))
    
    tareas = cursor.fetchall()
    conexion.close()
    
    lista_tareas = [
        {
            'id': tarea['id'],
            'titulo': tarea['titulo'],
            'completada': bool(tarea['completada']),
            'fecha_creacion': tarea['fecha_creacion']
        }
        for tarea in tareas
    ]
    
    return jsonify({
        'usuario': usuario_nombre,
        'total_tareas': len(lista_tareas),
        'tareas': lista_tareas
    }), 200

@app.route('/tareas/crear', methods=['POST'])
@verificar_credenciales()
def crear_tarea(usuario_id, usuario_nombre):
    # Crea una nueva tarea para el usuario autenticado
    # Requiere: {"titulo": "..."}

    datos = request.get_json()
    
    if not datos or not datos.get('titulo'):
        return jsonify({'error': 'Titulo es requerido'}), 400
    
    titulo = datos.get('titulo')
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO tareas (usuario_id, titulo)
        VALUES (?, ?)
    ''', (usuario_id, titulo))
    
    conexion.commit()
    tarea_id = cursor.lastrowid
    conexion.close()
    
    return jsonify({
        'mensaje': 'Tarea creada exitosamente',
        'tarea_id': tarea_id,
        'titulo': titulo
    }), 201

@app.route('/tareas/completar/<int:tarea_id>', methods=['PUT'])
@verificar_credenciales()
def completar_tarea(tarea_id, usuario_id, usuario_nombre):
    # Marca una tarea como completada
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # Verificar que la tarea pertenece al usuario
    cursor.execute('''
        SELECT id FROM tareas WHERE id = ? AND usuario_id = ?
    ''', (tarea_id, usuario_id))
    
    tarea = cursor.fetchone()
    if not tarea:
        conexion.close()
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    # Actualizar tarea
    cursor.execute('''
        UPDATE tareas SET completada = 1 WHERE id = ?
    ''', (tarea_id,))
    
    conexion.commit()
    conexion.close()
    
    return jsonify({'mensaje': 'Tarea marcada como completada'}), 200

@app.route('/tareas/eliminar/<int:tarea_id>', methods=['DELETE'])
@verificar_credenciales()
def eliminar_tarea(tarea_id, usuario_id, usuario_nombre):
    # Elimina una tarea del usuario autenticado

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # Verificar que la tarea pertenece al usuario
    cursor.execute('''
        SELECT id FROM tareas WHERE id = ? AND usuario_id = ?
    ''', (tarea_id, usuario_id))
    
    tarea = cursor.fetchone()
    if not tarea:
        conexion.close()
        return jsonify({'error': 'Tarea no encontrada'}), 404
    
    # Eliminar tarea
    cursor.execute('DELETE FROM tareas WHERE id = ?', (tarea_id,))
    conexion.commit()
    conexion.close()
    
    return jsonify({'mensaje': 'Tarea eliminada exitosamente'}), 200

# MANEJO DE ERRORES

@app.errorhandler(404)
def no_encontrado(error):
    """
    Maneja errores 404
    """
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def error_servidor(error):
    """
    Maneja errores 500
    """
    return jsonify({'error': 'Error interno del servidor'}), 500

# MAIN

if __name__ == '__main__':
    # Inicializar BD si no existe
    if not os.path.exists(DATABASE):
        inicializar_db()
    else:
        print("[BD] Base de datos ya existe")
    
    print("[SERVIDOR] Iniciando API en http://localhost:5000")
    print("[SERVIDOR] Presiona Ctrl+C para detener")
    
    app.run(debug=True, host='localhost', port=5000)
