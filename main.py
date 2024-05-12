from flask import Flask, render_template, redirect, url_for, make_response, request
from datetime import datetime
from sqlalchemy import func, desc
from io import BytesIO
from flask_login import LoginManager,current_user
from auth import auth_bp
from models import db, Registro, User


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Esta es una clave secreta de ejemplo, debes usar una diferente y segura en tu aplicación
app.config.from_pyfile('config.py')
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(auth_bp)


@app.route('/')
def index():
    with app.app_context():
        total = db.session.query(func.sum(Registro.monto)).scalar() or 0.0
        registros = Registro.query.filter_by(user_id=current_user.id).order_by(desc(Registro.fecha)).all()

    return render_template('registro.html', registros=registros, total=total)


@app.route('/generar_informe_pdf', methods=['GET'])
def generar_informe_pdf():
    registros = Registro.query.filter_by(user_id=current_user.id).order_by(desc(Registro.fecha)).all()

    response = make_response(generar_pdf(registros))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=informe.pdf'
    return response


from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def generar_pdf(registros):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Definir los encabezados de la tabla
    encabezados = ["Fecha", "Monto", "Descripción", "Tipo"]
    data = [encabezados]

    # Agregar cada registro como una fila en la tabla
    for registro in registros:
        data.append([registro.fecha.strftime('%Y-%m-%d'), registro.monto, registro.descripcion, registro.tipo])

    # Crear la tabla y aplicar estilos
    tabla = Table(data)
    tabla.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    # Agregar la tabla al documento
    elements.append(tabla)

    # Construir el PDF
    doc.build(elements)

    buffer.seek(0)
    return buffer



@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    with app.app_context():
        total = db.session.query(func.sum(Registro.monto)).scalar() or 0.0

        if request.method == 'POST':
            monto = float(request.form['monto'])
            fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
            descripcion = request.form['descripcion']
            tipo = request.form['tipo']

            # Obtener el usuario actualmente autenticado
            usuario_actual = current_user

            nuevo_registro = Registro(monto=monto, fecha=fecha, descripcion=descripcion, tipo=tipo, user_id=usuario_actual.id)
            db.session.add(nuevo_registro)
            db.session.commit()

            return redirect(url_for('agregar'))

    return render_template('agregar.html', total=total)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
