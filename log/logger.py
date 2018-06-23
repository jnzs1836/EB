class Logger:
    def __init__(self, filename , path = './logs'):
        self.filename = filename
        self.path = path
        self.log_func = print

    def info(self,message):
        self.log_func(message)