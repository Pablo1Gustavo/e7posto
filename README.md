# E7Posto
>#### Um pequeno e simples sistema feito em **Flask** para comprar,usar e gerenciar vouchers de um posto de gasolina.
>#### Feito em 2021 para a disciplina **Projeto de Desenvolvimento de Software**


Este projeto utiliza **Python 3.7.6** e as seguintes pacotes:
- Flask         1.1.2
- Flask-Bcrypt  0.7.1
- Flask-MySQLdb 0.2.0

Para instalar os pacotes utilizando o pip:
```
pip install flask==1.1.2
```
```
pip install flask_bcrypt==0.7.1
```
```
pip install flask_mysqldb==0.2.0
```

**Recomenda-se utilizar uma venv para testar o projeto**

Após baixar o projeto, basta ir no arquivo **'main.py'** e configurá-lo com as informações do seu banco.
```
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'e7posto
```

Lembre-se de antes criar o banco e as tabelas. O comando SQL está no arquivo **database.txt**
Após tudo configurado basta rodar o arquivo **'main.py'** e acessar seu localhost na porta 5000
