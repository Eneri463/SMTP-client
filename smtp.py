import socket
import ssl
import base64
import warnings
warnings.filterwarnings('ignore')

host = 'smtp.gmail.com'
port =  587
login = ""

# -----------------------------------------------------------------------------
# ввод сообщения
def messageSMTP():
    
    flag = True
    text = ""
    
    while flag:
        
        s = input()
        if s == '.':
            flag = False
        else:
            text += s
    
    return text

# -----------------------------------------------------------------------------
# отправка команды на сервер
def sendToServer(client, command, argument = ""):
    
    client.send((command + argument + '\r\n').encode())
    
    print("CLIENT: " + command + argument + " CRLF")
    
    logFile.write("CLIENT: " + command + argument + " CRLF\n")

# -----------------------------------------------------------------------------
# ответ от сервера
def receiveFromServer(client):
    
    response = client.recv(1024)
    
    print("Server: %s" % response.decode('utf-8'))
    
    logFile.write("Server: %s\n" % response.decode('utf-8'))
    
    return response.decode('utf-8')

# -----------------------------------------------------------------------------
# формирования заголовка сообщения
def headerSMTP(login, msgDest, msgSub):

    return "FROM: " + login + "\r\n" + \
            "TO: " + msgDest + "\r\n" + \
            "SUBJECT: " + msgSub

# -----------------------------------------------------------------------------
# авторизация
def aut(client):
    
    global login
    
    login = input("Username: ")
    password = input('Password: ')
    
    sendToServer(client, "AUTH LOGIN")
    receiveFromServer(client)
    
    # отправляем логин в формате base64
    encoded_login = base64.b64encode(login.encode()).decode()
    sendToServer(client, encoded_login)
    receiveFromServer(client)
    
    # отправляем пароль в формате base64
    encoded_password = base64.b64encode(password.encode()).decode()
    sendToServer(client, encoded_password)
    receiveFromServer(client)


# -----------------------------------------------------------------------------
# отправка сообщения
def sendMessage(client, login):
    
    msgDest = input("To: ")
    msgSub = input("Subject: ")
    print("Text: ")
    msg_text = messageSMTP()

    # начало транзакции с указанием почтового ящика отправителя
    sendToServer(client, "MAIL FROM: ", "<" + login + ">")
    receiveFromServer(client)
    
    # указание получателя
    sendToServer(client, "RCPT TO: ", "<" + msgDest + ">")
    receiveFromServer(client)
    
    # начало передачи серверу сообщения
    sendToServer(client, "DATA")
    receiveFromServer(client)
    
    # создаём заголовок сообщения
    msgHeader = headerSMTP(login, msgDest, msgSub)
    # отправляем заголовок
    sendToServer(client, msgHeader)
    # разделитель заголовка и сообщения
    sendToServer(client, "");
    # отправляем сообщение
    sendToServer(client, msg_text);
    # оповещаем о завершении сообщения
    sendToServer(client, ".")
    receiveFromServer(client)
    
    return login

# -----------------------------------------------------------------------------
# применение протокола TLS
def STARTTLS(client):
    
    sendToServer(client, "STARTTLS")
    receiveFromServer(client) # ответ от сервера
    
    return ssl.wrap_socket(client)
    

# -----------------------------------------------------------------------------
# отправка приветствия
def hello(client):
    
    sendToServer(client, "EHLO ", "localhost")
    receiveFromServer(client)

# -----------------------------------------------------------------------------
# завершение сеанса
def quitDialogue(client):
      
    sendToServer(client, "QUIT")
    receiveFromServer(client)
    client.close()

# -----------------------------------------------------------------------------
def main():
    
    try:
        # --- подключение к серверу
        
        client = socket.socket()
        client.connect((host, port))
        print("Connected to %s through %s port" % (host, port))
        logFile.write("Connected to %s through %s port\n" % (host, port))
        receiveFromServer(client) # ответ от сервера
    
        flag = True
        
        print("Доступные действия (введите номер команды или help): ")
        print("1 - EHLO localhost")
        print("2 - STARTTLS")
        print("3 - AUTH LOGIN")
        print("4 - Send message")
        print("5 - QUIT")
        print("help\n")
        
        while(flag):
            
            inputData = input("> ")
            command = inputData
            
            if command == "1":
                hello(client)
                
            elif command == "2":
                client = STARTTLS(client)
            
            elif command == "3":
                aut(client)
            
            elif command == "4":
                sendMessage(client, login)
            
            elif command == "5" or command == "!" or command == "exit" or command == "quit":
                flag = False
                quitDialogue(client)
            
            elif command == "help":
                
                print("1 - EHLO localhost")
                print("2 - STARTTLS")
                print("3 - AUTH LOGIN")
                print("4 - Send message")
                print("5 - QUIT")
                print("help\n")
                
            else:
                print("Некорректный ввод\n")
            
    except socket.error:
        print('Что-то пошло не так')
    finally:
        client.close()
        logFile.close()


logFile = open("smtp_1.log", "w")
main()