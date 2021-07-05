from flask import Flask, render_template,request,redirect,url_for,flash
from flask_mysqldb import MySQL
from flask import send_from_directory
from datetime import datetime

import os

#Conexión para la base de datos local
app = Flask(__name__)
app.secret_key="secret_key"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'sistema'
#guardamos la importación de MySQL en la varibale mysql
mysql=MySQL(app)

#imortar os, para poder acceder a la carpeta de imagenes
#y asi poder actualizar las imagenes en la carpeta en el edit
CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA

#crear acceso para mostrar imagen en el index, se utiliza el siguiene paquete from flask import send_from_directory
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM empleados ')
    data = cur.fetchall()
    #print(data)
    cur.close()
    return render_template('empleados/index.html', empleados = data)



@app.route('/create')
def create():
    return render_template('empleados/create.html')



@app.route('/add_employee', methods=['POST'])
def add_employee():
    if request.method == "POST":
       nombre = request.form['nombre']
       correo = request.form['correo']
       foto = request.files['foto']

       if nombre == '' or correo == '' or foto == '':
           flash('Recuerda llenar los datos de los campos')
           return redirect(url_for('create'))

       #Esto es para nombrar la imagen con el tiempo de subida
       now = datetime.now()
       tiempo=now.strftime("%Y%H%M%S")
       if foto.filename != '':
           newnamepicture= tiempo+foto.filename
           foto.save("uploads/"+newnamepicture)
      #Aqui termina el renombramiento
       cur = mysql.connection.cursor()
       cur.execute('INSERT INTO empleados (id,nombre,correo,foto) VALUES (NULL,%s,%s,%s)',
       (nombre,correo,newnamepicture))
       mysql.connection.commit()
       return redirect('/')


@app.route('/delete/<string:id>')
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT foto FROM empleados WHERE id={0} ".format(id) )
    fila = cur.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    cur.execute('DELETE FROM empleados WHERE id={0}'.format(id))
    mysql.connection.commit()
    return redirect('/')


@app.route('/edit/<string:id>')
def edit(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM empleados WHERE id = {0}'.format(id))
    data = cur.fetchall()
    cur.close()
    #print(data[0])
    return render_template('empleados/edit.html', empleados=data)

@app.route('/update/<string:id>',methods=['POST'])
def update(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        foto = request.files['foto']
        id=request.form['id']


        cur = mysql.connection.cursor()

        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        #recuperar y modificar foto
        if foto.filename != '':
            newnamepicture = tiempo + foto.filename
            foto.save("uploads/" + newnamepicture)
            cur.execute("SELECT foto FROM empleados WHERE id={0} ".format(id))
            fila=cur.fetchall()
            os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
            cur.execute("UPDATE empleados SET foto=%s WHERE id=%s",(newnamepicture,id))
            mysql.connection.commit()


        cur.execute('UPDATE empleados SET nombre=%s,correo=%s WHERE id=%s',
        (nombre, correo, id))
        mysql.connection.commit()
        return redirect('/')








if __name__== '__main__':
    app.run(port=3000, debug=True)










