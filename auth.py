from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user


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

        if User.query.filter_by(correo=correo).first() or User.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash('El usuario ya existe', 'error')
            return redirect(url_for('auth.registro'))

        if User.query.filter_by(correo=correo).first() or User.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash('El correo electrónico o el nombre de usuario ya están en uso', 'error')
            return redirect(url_for('auth.registro'))

        # Especificamos el método de hash de manera explícita
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        nuevo_usuario = User(nombre=nombre, apellido=apellido, tipo_documento=tipo_documento,
                             numero_documento=numero_documento, correo=correo, divisa=divisa,
                             nombre_usuario=nombre_usuario, password=hashed_password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('registro.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        usuario = User.query.filter_by(correo=correo).first()

        if usuario:
            if check_password_hash(usuario.password, password):
                flash('Inicio de sesión exitoso', 'success')
                login_user(usuario)  # Iniciar sesión del usuario
                return redirect(url_for('agregar'))  # Redirige al usuario a la página deseada después del inicio de sesión
            else:
                flash('Contraseña incorrecta', 'error')
                return redirect(url_for('auth.login'))
        else:
            flash('El usuario no existe', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')
