# coding: utf8
from google_images_download import google_images_download   #importing the library
import sys, osc
from threading import Thread

class DownThread(Thread):
    def __init__(self, keyword, osc_client):
        Thread.__init__(self)
        self.keyword = keyword
        self.osc_client = osc_client
        
    def run(self):
        print("Searching for "+self.keyword)
        response = google_images_download.googleimagesdownload()   #class instantiation
        arguments = {"keywords":self.keyword,"limit":1,"print_urls":False, "no_directory":True, "type":"photo", "format":"jpg", "size":">4MP"}#"color_type":"black-and-white"} "usage_rights":"labeled-for-noncommercial-reuse-with-modification", "size": ">1024*768", "language":"French"   #creating list of arguments
        paths = response.download(arguments)   #passing the arguments to the function
        print(paths)   #printing absolute paths of the downloaded images
        p = str(paths.get(self.keyword))
        p = p.replace("'", "")
        p = p.replace("[", "")
        p = p.replace("]", "")
        self.osc_client.send("/keyword "+unicode(self.keyword).encode('utf-8'))
        self.osc_client.send("/path "+unicode(p).encode('utf-8'))

class GoogleImage:
    
    def __init__(self, osc_server_port=9860, osc_client_host='127.0.0.1', osc_client_port=9861):
        self.osc_server_port = osc_server_port
        self.osc_client_host = osc_client_host
        self.osc_client_port = osc_client_port
        self.osc_client = osc.Client(osc_client_host, osc_client_port)
        self.osc_server = osc.Server(host='0.0.0.0', port=osc_server_port, callback=self.osc_server_message)
        self.osc_server.run(non_blocking=True)
        
        print("GoogleImage Ready")
        
    def osc_server_message(self, message):
        #print(message)
        if message == '/exit':
            self.osc_server.shutdown()
            sys.exit(0)
        elif message == '/reset':
            self.osc_client.send("/googleimage/reset")
        else:
            self.search(message)
    
    def search(self, message):
        message = message.strip('\'')
        message = message.replace(",", " ")
        message = message.replace('à', "a")
        message = message.replace("â", "a")
        message = message.replace("é", "e")
        message = message.replace("è", "e")
        message = message.replace("ê", "e")
        message = message.replace("ë", "e")
        message = message.replace("î", "i")
        message = message.replace("ï", "i")
        message = message.replace("ô", "o")
        message = message.replace("ö", "o")
        message = message.replace("ù", "u")
        message = message.replace("ü", "u")
        message = message.replace("ç", "c")
        message = message.replace(")", " ")
        message = message.replace(", ", " ")
        message = message.replace("… ", " ")
        message = message.replace('\xe2\x80\x99', "'")
        
        thd = DownThread(message, self.osc_client);
        thd.start();
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        GoogleImage();
    elif len(sys.argv) == 4:
        GoogleImage(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    else:
        print('usage: %s <osc-server-port> <osc-client-host> <osc-client-port>')