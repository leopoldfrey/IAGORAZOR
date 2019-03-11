# coding: utf8
import textrazor
import sys, osc

class Razor:

    def __init__(self, osc_server_port=9760, osc_client_host='127.0.0.1', osc_client_port=9761):
        self.osc_server_port = osc_server_port
        self.osc_client_host = osc_client_host
        self.osc_client_port = osc_client_port
        self.osc_client = osc.Client(osc_client_host, osc_client_port)
        self.osc_server = osc.Server(host='0.0.0.0', port=osc_server_port, callback=self.osc_server_message)
        self.osc_server.run(non_blocking=True)
        
        textrazor.api_key = "738a42fefbc1aab31b016b933c69a9afcf00d83a742aa994a4f8822e"

        self.razor_client = textrazor.TextRazor(extractors=["words", "entities", "topics"])
    
        self.osc_client.send("/razor/ready")
        
        print("Razor Ready")
        
    def osc_server_message(self, message):
        #print(message)
        if message == '/exit':
            self.osc_server.shutdown()
            sys.exit(0)
        elif message == '/reset':
            self.osc_client.send("/razor/reset")
            self.conversation = []
        elif message == '/analyze':
            self.analyze();
        else:
            self.add(message)
            

    def add(self, message):
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
        
        self.msg = message;
   

    def analyze(self):
        response = self.razor_client.analyze(self.msg)
        for wrd in response.words():
            #if wrd.part_of_speech == "NOUN" or wrd.part_of_speech == "ADJ":
            #print wrd.part_of_speech + " - "+ wrd.token
            self.osc_client.send(unicode("/razor/"+wrd.part_of_speech+" "+wrd.token))
        
        entities = list(response.entities())
        entities.sort(key=lambda x: x.relevance_score, reverse=True)
        seen = set()    
        
        for entity in entities:
            if entity.id not in seen:
                print entity.id, entity.relevance_score, entity.confidence_score, entity.freebase_types
                seen.add(entity.id)
                self.osc_client.send(unicode("/razor/entity "+entity.id).encode('utf-8'))
                #+" "+entity.relevance_score+" "+entity.confidence_score))
        
        for topic in response.topics():
            if topic.score > 0.5:
                print topic.label
                self.osc_client.send(unicode("/razor/topic "+topic.label))
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        Razor();
    elif len(sys.argv) == 4:
        Razor(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    else:
        print('usage: %s <osc-server-port> <osc-client-host> <osc-client-port>')