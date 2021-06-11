import mysql.connector
import commands as cmd

mydb=cmd.connect_db()
mycursor = mydb.cursor()

# On peut maintenant construire les query en utilisant le module cmd en faisant query=cmd.function(parameters)
# mycursor.execute(cmd.create_hh_table)

# mycursor.execute("SHOW TABLES")

# for x in mycursor:
#  print(x)



