from app import app
from flaskext.mysql import MySQL
 ### change this to local mysql password
mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root' ### change this to your local mysql user
app.config['MYSQL_DATABASE_PASSWORD'] = 'root' ### change this to your local mysql password
app.config['MYSQL_DATABASE_DB'] = ''
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
