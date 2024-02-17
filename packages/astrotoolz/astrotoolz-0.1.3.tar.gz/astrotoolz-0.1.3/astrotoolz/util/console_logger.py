import logging

class ConsoleLogger:
    
    def __init__(self, name):
        # Create logger
        self.logger = logging.getLogger(name)
        
        # Set default level
        self.logger.setLevel(logging.DEBUG)
        
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Add formatter to console handler
        ch.setFormatter(formatter)
        
        # Add console handler to logger
        self.logger.addHandler(ch)
        
    def debug(self, msg):
        self.logger.debug(msg)
        
    def info(self, msg):    
        self.logger.info(msg)