from flask import Flask,render_template,request,redirect,flash,session,abort
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xHs7GMdeIMZkgj3cW4FK'

#database_config

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'e7posto'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

#created_functions

def validate_cpf(cpf):

    cpf = [int(i) for i in cpf]

    if cpf.count(cpf[0])==len(cpf):
        return False
    
    for i in range(9, 11):
        value = sum((cpf[num] * ((i+1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != cpf[i]:
            return False

    return True

def generate_random_code():
    chars = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join([random.choice(chars) for i in range(15)])

#Routes

@app.route("/")
def root():
    return redirect('/home')
        
@app.route("/login",methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT ID,PASSWORD,ISMASTER FROM USERS WHERE USERNAME='%s'"%(username))
        user = cur.fetchone()
        cur.close()

        if not(user and bcrypt.check_password_hash(user[1],password)):
            error = 'Usuário ou senha inválidos'
        else:
            if user[2] == 1:
                session['admin'] = user[0]
                return redirect('/admin')
            else:
                session['user'] = user[0]
                return redirect('/home')
    return render_template('login.html',error=error)

@app.route('/register',methods=['GET','POST'])
def register():
    errors = []
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        cpf = request.form['cpf'].replace('-','').replace('.','')

        cur = mysql.connection.cursor()

        cur.execute("SELECT ID FROM USERS WHERE USERNAME='%s'"%(username))
        if cur.fetchone():
            errors.append('Usuário já existente, escolha outro nome')
        if len(username)<5 or len(username)>20:
            errors.append('O username deve ter entre 5 e 20 caracteres')
        if len(password)<7 or len(password)>20:
            errors.append('A senha deve ter entre 7 e 20 caracteres')
        if password!=password_confirm:
            errors.append('Senhas não batem')
        cur.execute("SELECT ID FROM USERS WHERE CPF='%s'"%(cpf))
        if cur.fetchone():
            errors.append('CPF já usado')
        elif not validate_cpf(cpf):
            errors.append('CPF inválido')
        
        if not errors:
            password = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute("INSERT INTO USERS(USERNAME,PASSWORD,CPF) VALUES ('%s','%s','%s')"%(username,password,cpf))
            mysql.connection.commit()  
            cur.close()

            flash('Usuário criado com sucesso!')
            return redirect('/login')
        cur.close()

    return render_template('cadastro.html',errors=errors)

@app.route('/forgetpassword')
def forget_password():
    return render_template('recu_senha.html')

@app.route('/home',methods=['GET','POST'])
def user_home():
    if 'user' in session:
        if request.method=='POST':
            return redirect('buy/%s'%(request.form['voucher_id']))

        cur = mysql.connection.cursor()
        cur.execute('SELECT QUANTITY,PRICE,ID FROM VOUCHERS')
        vouchers = cur.fetchall()

        cur.execute('select QUANTITY,CODE FROM USERVOUCHERS JOIN VOUCHERS ON VOUCHER_ID=VOUCHERS.ID WHERE USER_ID=%i AND USED=0 ORDER BY QUANTITY'%(session['user']))
        uservouchers_avaliable = cur.fetchall()
        cur.execute('select QUANTITY,CODE FROM USERVOUCHERS JOIN VOUCHERS ON VOUCHER_ID=VOUCHERS.ID WHERE USER_ID=%i AND USED=1 ORDER BY QUANTITY'%(session['user']))
        uservouchers_used = cur.fetchall()

        cur.close()

        return render_template(
            'inicial.html',vouchers=vouchers,uservouchers_avaliable=uservouchers_avaliable,uservouchers_used=uservouchers_used
            )

    elif 'admin' in session:
        return redirect('/admin')
    return redirect('/login')

@app.route('/buy/<int:id>',methods=['GET','POST'])
def buy_voucher(id):
    if 'user' in session:
        if request.method=='POST':
            cur = mysql.connection.cursor()
            random_code = generate_random_code()

            cur.execute("INSERT INTO USERVOUCHERS(CODE,USER_ID,VOUCHER_ID) VALUES('%s',%s,%i)"%(random_code,session['user'],id))
            mysql.connection.commit()
            cur.close()

            flash("Voucher comprado com sucesso!")
            return redirect('/home')

        return render_template('pagamento.html')

    return redirect("/login")

@app.route('/admin',methods=['GET','POST'])
def admin():
    if 'admin' in session:
        error=None
        cur = mysql.connection.cursor()

        if request.method=='POST':
            code = request.form['code']
            cur.execute("SELECT USED,QUANTITY FROM USERVOUCHERS JOIN VOUCHERS ON VOUCHER_ID=VOUCHERS.ID WHERE CODE='%s'"%(code))
            to_check_code = cur.fetchone()

            if not to_check_code:
                error = 'Código inválido'
            elif to_check_code[0]==1:
                error = 'Código já utilizado'
            else:
                cur.execute("UPDATE USERVOUCHERS SET USED=1 WHERE CODE='%s'"%(code))
                mysql.connection.commit()
                flash('Compra de %i litros aprovada!'%(to_check_code[1]))

        
        cur.execute('SELECT QUANTITY,PRICE,ID FROM VOUCHERS ORDER BY PRICE')
        vouchers = cur.fetchall()
        cur.close()

        return render_template('inicialmaster.html',vouchers=vouchers,error=error)

    elif 'user' in session:
        return redirect('/home')
    return redirect('/login')

@app.route('/admin/addvoucher',methods=['GET','POST'])
def admin_add_voucher():
    if 'admin' in session:
        error = None
        if request.method=='POST':
            quantity = request.form['quantity']
            price = request.form['price']

            cur = mysql.connection.cursor()

            cur.execute('SELECT ID FROM VOUCHERS WHERE PRICE=%s AND QUANTITY=%s'%(price,quantity))
            if cur.fetchone():
                error = 'Já existe um Voucher com essas características'
            elif int(quantity)<=0 or int(price)<=0:
                error = 'Valores inválidos'
            else:
                cur.execute('INSERT INTO VOUCHERS(PRICE,QUANTITY) VALUES(%s,%s)'%(price,quantity))
                mysql.connection.commit()
                cur.close()

                flash('Voucher criado com sucesso!')
                return redirect('/admin')
            cur.close()

        return render_template('adicionarvoucher.html',error=error)

    elif 'user' in session:
        return redirect('/home')

    return redirect('/login')

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user',None)
    elif 'admin' in session:
        session.pop('admin',None)
    return redirect('/login')

@app.route('/admin/delete_voucher/<int:id>',methods=['POST','GET'])
def delete_voucher(id):
    if request.method=='POST' and 'admin' in session:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM USERVOUCHERS WHERE VOUCHER_ID=%i'%(id))
        mysql.connection.commit()

        cur.execute('DELETE FROM VOUCHERS WHERE ID=%i'%(id))
        mysql.connection.commit()

        cur.close()
        flash('Voucher deletado com sucesso!')
        return redirect('/admin')

    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)