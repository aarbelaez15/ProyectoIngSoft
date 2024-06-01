from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import db, User
import re

auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        tipo_documento = request.form['tipo_documento']
        numero_documento = request.form['numero_documento']
        correo = request.form['correo']
        divisa = request.form['divisa']
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        password2 = request.form['password2']

        if password != password2:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('auth.registro'))

        if not validar_contrasena(password):
            flash('La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un carácter especial.', 'error')
            return redirect(url_for('auth.registro'))

        if User.query.filter_by(correo=correo).first() or User.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash('El correo electrónico o el nombre de usuario ya están en uso', 'error')
            return redirect(url_for('auth.registro'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        nuevo_usuario = User(
            nombre=nombre, apellido=apellido, tipo_documento=tipo_documento,
            numero_documento=numero_documento, correo=correo, divisa=divisa,
            nombre_usuario=nombre_usuario, password=hashed_password
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('registro.html')

def validar_contrasena(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[@$!%*?&.,]', password):
        return False
    return True

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        usuario = User.query.filter_by(correo=correo).first()

        if usuario:
            if check_password_hash(usuario.password, password):
                flash('Inicio de sesión exitoso', 'success')
                login_user(usuario)
                return redirect(url_for('agregar'))
            else:
                flash('Datos incorrectos', 'error')
                return redirect(url_for('auth.login'))
        else:
            flash('Datos incorrectos', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/recuperar-contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        numero_documento = request.form['numero_documento']
        correo = request.form['correo']
        nueva_contraseña = request.form['nueva_contraseña']
        nueva_contraseña2 = request.form['nueva_contraseña2']

        if nueva_contraseña != nueva_contraseña2:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('auth.recuperar_contrasena'))

        if not validar_contrasena(nueva_contraseña):
            flash('La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un carácter especial.', 'error')
            return redirect(url_for('auth.recuperar_contrasena'))

        usuario = User.query.filter_by(numero_documento=numero_documento, correo=correo).first()

        if usuario:
            usuario.password = generate_password_hash(nueva_contraseña)
            db.session.commit()
            flash('Se ha restablecido la contraseña con éxito.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('No se encontró ningún usuario con las credenciales proporcionadas.', 'error')

    return render_template('recuperar_contrasena.html')

