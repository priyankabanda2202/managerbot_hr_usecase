import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# from logger.logger import log
from src.data_parsing.data_parsing import GetAndStroreData



class Watcher:
    DIRECTORY_TO_WATCH = "./source_files/"
    
    def __init__(self):
        self.observer = Observer()
        
    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")
            
        self.observer.join()
        
class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        # elif event.event_type == 'created':
        #     # Take any action here when a file is first created.
        #     print("Received created event - %s." % event.src_path)


        elif event.event_type == 'modified':

            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)
            '''Need to write the DB name which ever is coming as in source file'''
            # print(event.src_path)
            # print()
            db_name = os.path.basename(os.path.dirname(event.src_path))
            # print(db_name)
            GetAndStroreData(db_name).create_doc_embeddings()
            
            
if __name__ == '__main__': 
    # Create an instance of the Watcher class
    w = Watcher()
    # Run the watcher on a specific directory or file
    w.run()
    