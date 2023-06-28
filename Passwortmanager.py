import pyperclip as pc
import hashlib as hl
import random
import string
import pwinput
#Funktion zur Umwandlung der Hashbytes in ein Passwort
def digest_to_pass(digest):
  chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12345678901234567890!?&%/§$()=+!§$%&/(=?-)"
  password=""
  for p in digest:
    password=password+chars[p%len(chars)]
  return password
#Passwortmanager-Klasse für die grundlegende Backend-Funktionalität
class PasswordManager:
  def __init__(self, salt, data):
    self.__salt = salt
    self.__data = data
    self.__prerounds = 100000
    self.__hashalgo = hl.sha3_512
    self.__password_out_length=16
  def unlock(self, password):
    self.__main_password=password
  def new_entry(self, service, username):
    self.__data.append({"service":service,"username":username})
    for i, dic in enumerate(self.__data):
      if dic["service"] == service and dic["username"]==username:
        index=i
    password=self.__hashalgo((self.__main_password+self.__salt).encode("utf-16")).digest()
    saltyhash=b""
    for i in range(self.__prerounds+index):
      password=self.__hashalgo(password+saltyhash).digest()
      if i==self.__prerounds/2:
        saltyhash=password
      pc.copy(digest_to_pass(password[(len(password)-self.__password_out_length):]))
    return service, username
  def get_list(self):
    return self.__data
  def get_password(self, index):
    password=self.__hashalgo((self.__main_password+self.__salt).encode("utf-16")).digest()
    saltyhash=b""
    for i in range(self.__prerounds+index):
      password=self.__hashalgo(password+saltyhash).digest()
      if i==self.__prerounds/2:
        saltyhash=password
    pc.copy(digest_to_pass(password[(len(password)-self.__password_out_length):]))
  def delete_entry(self, index):
    self.__data[index]={"service":"None", "username":"None"}
    filename="pm.db"
try:
#Wenn Datenbank-Datei vorhanden, öffne sie
  database=open(filename,"r")
  datalines=database.readlines()
  database.close()
  salt=datalines.pop(0)
  data=[]
  for line in datalines:
    data.append({"service":line.split()[0],"username":line.split()[1]})
except:
#Wenn Datenbank-Datei nicht geöffnet werden kann, weil nicht vorhanden, erstelle eine.
  database=open(filename,"w")
  salt=''.join(random.choice(string.ascii_letters+string.digits) for i in range(32))
  data=[]
  database.write(salt + "\n")
  database.close()
finally:
  database.close()
#Initialisieren der Passwortmanager-Klasse
pm=PasswordManager(salt,data)
#Eingabe des Master-Passworts
master_pass=pwinput.pwinput(prompt="Geben Sie das Master-Passwort ein: ")
while len(master_pass)<8:
  master_pass=pwinput.pwinput(prompt="Unter allen Umständen zu kurz... Geben Sie das Master-Passwort ein: ")
  pm.unlock(input("Geben Sie das Master-Passwort ein:"))
while True:
  print("Aktuelle Passwortliste:\n_____________________________________")
  for i, entry in enumerate(pm.get_list()):
    if entry["service"]!="None":
      print(" "+str(i)+" | Webseite: "+entry["service"]+" | Username: "+entry["username"])
  print("_____________________________________\nWas möchtest du machen?")
  print(" [Nummer]: Passwort erhalten")
  print(" new: Neuer Eintrag")
  print(" del [Nummer]: Eintrag löschen")
  print(" end: Programm schließen\n")
  command=input()
#Neuen Passwortmanager-Eintrag hinzufügen
  if command[:3]=="new":
    new_entry=input("Gib mit Leerzeichen getrennt den Namen der Webseite und den Usernamen oder Mail-Adresse, der auf der Webseite verwendet wird, ein:").split()
    pm.new_entry(new_entry[0],new_entry[1])
    database=open(filename,"a")
    database.write(new_entry[0]+" "+new_entry[1]+"\n")
    database.close()
    print("Neues Passwort kann jetzt mit Strg+V eingefügt werden!")
    input("Wenn du es nicht mehr brauchst, drücke Enter...")
    pc.copy('')
#Passwortmanager schließen
  elif command[:3]=="end":
    bye=["Tschau Kakao","Tschö mit Ö","Tschüssikowski","Auf Wiesbaden","Bis Spätersburg","Paris, Athen, auf Wiedersehen","Es ist wie ein Spiegel, man sieht sich","Schöne Grüße vom Tschüsseldienst","Tschüsli Müsli","See you later alligator, in a while crocodile","Bis Baldrian","Erst die Rechte, dann die Linke. Beide machen Winke, Winke","Ich verabscheue mich","Hasta la vista, Baby","Bis denne, Antenne","Tschüsselchen mit Küsselchen aufs Rüsselchen"]
    print(random.choice(bye))
    exit()
#Passwortmanager-Eintrag „löschen“
  elif command.split()[0]=="del" and command.split()[1].isnumeric:
    command=int(command.split()[1])
    if command>len(pm.get_list())-1 or pm.get_list()[command]["service"]=="None":
      input("\nDer gewählte Eintrag liegt außerhalb der Datenbank, bitte einen Wert aus der Liste wählen... Enter drücken...")
    else:
      pm.delete_entry(command)
      database=open(filename,"w")
      database.write(salt)
      for i, entry in enumerate(pm.get_list()):
        database.write(entry["service"]+" "+entry["username"]+"\n")
      database.close()
#Passwort nach Nummer erhalten
  elif command.isnumeric():
    command=int(command)
    if command>len(pm.get_list())-1 or pm.get_list()[command]["service"]=="None":
      input("\nDer gewählte Eintrag liegt außerhalb der Datenbank, bitte einen Wert aus der Liste wählen... Enter drücken...")
    else:
      pm.get_password(command)
      print("Passwort kann jetzt mit Strg+V eingefügt werden!")
      input("Wenn du es nicht mehr brauchst, drücke Enter...")
      pc.copy('')
#Bei fehlerhaftem Befehl
  else:
    print("Fehlerhafter Befehl... Sicher, dass es diesen Befehl gibt?")
