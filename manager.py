
from DeepQA import chatbot


chatbotPath="/home/hungarian_horntail/Scripts/mainProject/bot/bot2/interface/Remember-Bot/DeepQA"


def initialize_bot():
	t=chatbot.Chatbot()

	print(type(t))


	_chatbot=t.main(['--modelTag', 'server', '--test', 'daemon', '--rootDir', chatbotPath])
	print("Bot initialized")
	return t


#print(type(_chatbot))


def ask_bot(sentence,t):
        if t:
            return str((t.daemonPredict(str(sentence))))
        else:
            print("Error. Bot not instantiated")

