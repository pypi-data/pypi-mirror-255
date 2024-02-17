
from astrotoolz.out.file import to_text_file
from astrotoolz.tools.timeline.timeline import Timeline


class TimelinePrinter():
    
    def __init__(self, timeline: Timeline):
        self.timeline = timeline
        self.str = self._generate_str()
        
    def _generate_str(self) -> str:
        str = ""
        
        for group, events in self.timeline.grouped_events.items():
            formatted_date = group.strftime('%A, %b %d %Y')
            str+= f'{formatted_date}:\n'
            str += ''.join([f'{i + 1}. {e.__repr__()} \n------------\n' for i, e in enumerate(events)]) + '\n'
        
        return str
        
    def print_to_console(self):
        print(self.str)
        
    def print_to_file(self, filename:str):
        to_text_file(filename, self.str)
        
    
        
    