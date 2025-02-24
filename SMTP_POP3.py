import PySimpleGUI as sg
import socket
import ssl
import base64

sg.theme('DefaultNoMoreNagging')

login = "wiolona463@gmail.com"
password = ""
typeOF = 1
client = None

# -----------------------------------------------------------------------------
# завершение сеанса проверка
def quitDialogue(client):
      
    sendToServer(client, "QUIT")
    receiveFromServer(client)
    client.close()

# -----------------------------------------------------------------------------
# отправка команды на сервер
def sendToServer(client,command, argument = ""):
    
    client.send((command + argument + '\r\n').encode())
    
    print("CLIENT: " + command + argument + " CRLF")
    
    
    if typeOF == 1:
        logFile1.write("CLIENT: " + command + argument + " CRLF\n")
    else:
        logFile2.write("CLIENT: " + command + argument + " CRLF\n")
    
    

# -----------------------------------------------------------------------------
# ответ от сервера
def receiveFromServer(client):
    
    response = client.recv(1024)
    
    print("Server: %s" % response.decode('utf-8'))
    
    
    if typeOF == 1:
        logFile1.write("Server: %s\n" % response.decode('utf-8'))
    else:
        logFile2.write("Server: %s\n" % response.decode('utf-8'))
    
    
    
    return response.decode('utf-8')


# SMTP !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# формирования заголовка сообщения
def headerSMTP(login, msgDest, msgSub):

    return "FROM: " + login + "\r\n" + \
            "TO: " + msgDest + "\r\n" + \
            "SUBJECT: " + msgSub

# -----------------------------------------------------------------------------
# редактирование сообщения
def messageSMTP(message):
    
    elem = message.split("\n")
    
    new_message = ""
    
    for i in range(len(elem)):
        if elem[i] == '.':
            new_message = new_message + "..\n"
        else:
            new_message = new_message + elem[i] + "\n"
    
    return new_message

# -----------------------------------------------------------------------------
# AUTH LOGIN
# авторизация
def autSMTP(client):
    
    sendToServer(client, "AUTH LOGIN")
    response = receiveFromServer(client)
    
    # отправляем логин в формате base64
    encoded_login = base64.b64encode(login.encode()).decode()
    sendToServer(client, encoded_login)
    response = receiveFromServer(client)
    
    # отправляем пароль в формате base64
    encoded_password = base64.b64encode(password.encode()).decode()
    sendToServer(client, encoded_password)
    response = receiveFromServer(client)
    
    return response

# -----------------------------------------------------------------------------
# MAIL FROM
# отправка сообщения
def sendMessage(client, msgDest, msgSub, msg_text):
    
    # начало транзакции с указанием почтового ящика отправителя
    sendToServer(client, "MAIL FROM: ", "<" + login + ">")
    response = receiveFromServer(client)
    
    # указание получателя
    sendToServer(client, "RCPT TO: ", "<" + msgDest + ">")
    response = receiveFromServer(client)
    
    # начало передачи серверу сообщения
    sendToServer(client, "DATA")
    response = receiveFromServer(client)
    
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
    response = receiveFromServer(client)
    
    if response.find("OK") != -1:
        return True
    else:
        return False
    

# -----------------------------------------------------------------------------
# STARTTLS
# применение протокола TLS
def STARTTLS(client):
    
    sendToServer(client, "STARTTLS")
    receiveFromServer(client) # ответ от сервера
    
    return ssl.wrap_socket(client)
    

# -----------------------------------------------------------------------------
# EHLO
# отправка приветствия
def hello(client):
    
    sendToServer(client, "EHLO ", "localhost")
    receiveFromServer(client)

# -----------------------------------------------------------------------------
# начало работы с SMTP-клиентом
def startSMTP():
    
    global client
    
    host = 'smtp.gmail.com'
    port =  587
    
    client = socket.socket()
    client.connect((host, port))
    print("Connected to %s through %s port" % (host, port))
    logFile1.write("Connected to %s through %s port\n" % (host, port))
    response = receiveFromServer(client) # ответ от сервера
    
    hello(client)              # EHLO
    client = STARTTLS(client)  # STARTTLS
    response = autSMTP(client) # AUTH
    
    if response.find("Accepted") != -1:
        return True
    else:
        return False


# POP3 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# удаление сообщения
def messageDel(client, msg_number):
    
    sendToServer(client, "DELE ", msg_number)
    response = receiveFromServer(client)

# -----------------------------------------------------------------------------
# USER PASS 
# авторизация по протоколу POP
def autPOP(client, login, password):
    
    sendToServer(client, "USER ", login)
    response = receiveFromServer(client)

    sendToServer(client, "PASS ", password)
    response = receiveFromServer(client)
    
    return response

# -----------------------------------------------------------------------------
# RETR
# получение сообщения c заданным номером
def getMessage(client, msg_number):
    
    sendToServer(client, "RETR ", msg_number)
    response = ""
    while True:
        response = response + receiveFromServer(client)
        if response[-5:] == "\r\n.\r\n":
            break
        
    return response

# -----------------------------------------------------------------------------
# LIST
# вывод номеров сообщений и их размеров
def messageList(client):
    
    sendToServer(client, "LIST")
    response = ""
    pp = 0
    while True:
        response = response + "\n" + receiveFromServer(client)
        
        if response[-5:] == "\r\n.\r\n" or pp == 0 and response.find("OK") == -1:
            break
        pp = pp+1
        
    return response

# -----------------------------------------------------------------------------
# удаление с экрана сообщения
def delOrFindMessages(listMessage, n, typeOfWork = 1):
    
    mess = listMessage.split("\n")
    flag = False
    res = ""
    
    for i in range(len(mess)):
        
        pp = "Сообщение " + str(n)
        
        if mess[i].find(pp) == -1:
            res = res + mess[i] + "\n"
        else:
            flag = True
            
            if typeOfWork == 1:
                break
    
    return res, flag

# -----------------------------------------------------------------------------
# красивый вывод сообщений
def printMessages(listMessage):
    
    mess = listMessage.split("\n")[2:-2]
    res = ""
    
    for i in range(len(mess)):
        a = mess[i].split(" ")
        res = res + "Сообщение " + a[0] + " Размер " + a[1] + "\n"
    
    return res

# -----------------------------------------------------------------------------
# начало работы с POP3-клиентом
def startPOP3():
    
    global client
    
    # --- подключение к серверу
    host = "pop.gmail.com"
    port = 995

    client = socket.socket()
    client.connect((host, port))
    print("Connected to %s through %s port" % (host, port))
    logFile2.write("Connected to %s through %s port\n" % (host, port))

    client = ssl.wrap_socket(client)
    response = receiveFromServer(client)  # ответ от сервера
    
    response = autPOP(client, login, password)
    
    if response.find("OK") != -1:
        return True
    else:
        return False
    

# интерфейсы !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# окно авторизации
def authorizationWindow():

    simple_one = [
                    [sg.Text('_________________________________________________')],
                    [sg.Text('Логин: ')],
                    [sg.Input(size=(50, 1),key='login', default_text='wiolona463@gmail.com')],
                    [sg.Text('Пароль: ')],
                    [sg.Input(size=(50, 1),key='password', password_char='*', default_text='')],
                    [sg.Text('_________________________________________________')],
                    [sg.Button('Авторизация', key ='ok1')]
                ]
    
    return sg.Window('Авторизация', simple_one, location=(600,400), finalize=True)


# -----------------------------------------------------------------------------
# окно SMTP-клиента
def smtpWindow():

    simple_two = [
                    [sg.Button('Перейти к полученным сообщениям', key ='ok3')],
                    [sg.Text('_________________________________________________')],
                    [sg.Text('Кому: ')],
                    [sg.Input(size=(50, 1),key='to')],
                    [sg.Text('Тема: ')],
                    [sg.Input(size=(50, 1),key='subject')],
                    [sg.Text('Сообщение: ')],
                    [sg.Multiline(size=(50, 10),key='text')],
                    [sg.Text('_________________________________________________')],
                    [sg.Button('Отправить', key ='ok2')]
                ]
    
    return sg.Window('Отправить письмо', simple_two, location=(600,350), finalize=True)


# -----------------------------------------------------------------------------
# окно POP3-клиента
def popWindow():

    simple_three = [
                    [sg.Button('Перейти к окну отправки сообщений', key ='ok6')],
                    [sg.Text('_________________________________________________')],
                    [sg.Text('Полученные сообщения: ')],
                    [sg.Multiline(size=(50, 10),key='messages', disabled=True)],
                    [sg.Text('Прочитать сообщение номер: ')],
                    [sg.Input(size=(50, 1),key='take')],
                    [sg.Button('Прочитать', key ='ok4')],
                    [sg.Text('Удалить сообщение номер: ')],
                    [sg.Input(size=(50, 5),key='delete')],
                    [sg.Button('Удалить', key ='ok5')],
                    [sg.Text('_________________________________________________')]
                ]
    
    return sg.Window('Полученные сообщения', simple_three, location=(600,350), finalize=True)


# MAIN !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

logFile1 = open("smtp_1.log", "w")
logFile2 = open("pop3_1.log", "w")

window1, window2, window3 = authorizationWindow(), None, None

while True:
    
    window, event, values = sg.read_all_windows()
    
    if event in (None, 'Exit'):
        if client:
            quitDialogue(client)
        break
    
    # ---------------------------------------------------------------------
    # первоначальная авторизация и переход к smtp-клиенту
    
    elif event == 'ok1':
        
        if values['login'] == "" or values['password'] == "":
            sg.popup_ok("Необходимо заполнить поля")
        
        login = values['login']
        password = values['password']
        
        try:
            
            flag = startSMTP()
            
            if flag == True:
                typeOF = 1
                sg.popup_ok("Добро пожаловать")
                window1.close()
                window2 = smtpWindow()
            else:
                sg.popup_ok("Некоректный ввод логина или пароля")
            
        except socket.error:
            quitDialogue(client)
            sg.popup_ok("Что-то пошло не так")
    
    # ---------------------------------------------------------------------
    # отправка сообщения
    
    elif event == 'ok2':
        
        if values['to'] == "":
            sg.popup_ok("Необходимо заполнить информацию о получателе")
        
        try:
            
            msgDest = values['to']
            msgSub = values['subject']
            msg_text = messageSMTP(values['text'])
            flag = sendMessage(client, msgDest, msgSub, msg_text)

            flag == True             

            if flag == True:
                sg.popup_ok("Сообщение отправлено")
            else:
                sg.popup_ok("Невозможно отправить сообщение")
            
            
        except socket.error:
            sg.popup_ok("Что-то пошло не так")
    
    # ---------------------------------------------------------------------
    # переход к pop3-клиенту
    
    elif event == 'ok3':
        try:
            
            if client:
                quitDialogue(client)
            
            flag = startPOP3()
            
            listMessage = messageList(client)
            
            if flag == True:
                typeOF = 2
                window2.close()
                window3 = popWindow()
                m = printMessages(listMessage)
                window3['messages'].update(m)

            else:
                sg.popup_ok("Не удаётся подключится к pop3-серверу")
                flag = startSMTP()
            
        except:
            flag = startSMTP()
            sg.popup_ok("Что-то пошло не так")
            
    # ---------------------------------------------------------------------
    # просмотр сообщения
    
    elif event == 'ok4':
        try:
            
            flag = False
            
            if values['take'] == "":
                sg.popup_ok("Введите сообщение, которое необходимо прочитать")
            else:
                try:
                    num = int(values['take'])
                    flag = True
                except:
                    sg.popup_ok("Некорректно задан номер")
                finally:
                    
                    if flag == True:
                        
                        _, flag = delOrFindMessages(values['messages'], num)
                        
                        if flag == False:
                            sg.popup_ok("Нет сообщения с заданным номером")
                        else:
                            sg.popup_ok(getMessage(client, str(num)), title="Чтение сообщения")
        except:
            
            sg.popup_ok("Что-то пошло не так")
    
    # ---------------------------------------------------------------------
    # удаление сообщения
    elif event == 'ok5':
        
        try:
            
            flag = False
            
            if values['delete'] == "":
                sg.popup_ok("Введите сообщение, которое необходимо удалить")
            else:
                try:
                    num = int(values['delete'])
                    flag = True
                except:
                    sg.popup_ok("Некорректно задан номер")
                finally:
                    
                    if flag == True:
                        
                        m, flag = delOrFindMessages(values['messages'], num, 2)
                        
                        if flag == False:
                            sg.popup_ok("Нет сообщения с заданным номером")
                        else:
                            window3['messages'].update(m)
                            messageDel(client, str(num))
                            sg.popup_ok("Сообщение удалено")
        except:
            
            sg.popup_ok("Что-то пошло не так")
        
    # ---------------------------------------------------------------------
    # возврат в окно отправки сообщения
    elif event == 'ok6':
        
        try:
            
            if client:
                quitDialogue(client)
            
            flag = startSMTP()
            
            if flag == True:
                typeOF = 1
                window3.close()
                window2 = smtpWindow()

            else:
                sg.popup_ok("Не удаётся подключится к smtp-серверу")
                flag = startPOP3()
            
        except:
            flag = startPOP3()
            sg.popup_ok("Что-то пошло не так")
            
    

if window1:
    window1.close()
if window2:
    window2.close()
if window3:
    window3.close()
    
logFile1.close()
logFile2.close()
