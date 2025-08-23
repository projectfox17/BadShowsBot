import re

from modules.ShowData import ShowIDs


SHOW_HREF_PATTERN = re.compile(r"/(film|series)/(\d+)/")


class Parser:
    
    @staticmethod
    def get_page_shows(content: str) -> ShowIDs:
        
        show_ids = ShowIDs()
        matches: list[tuple[str]] = re.findall(SHOW_HREF_PATTERN, content)
        
        for cat, sid in matches:
            sid = int(sid)
            if cat == "film":
                show_ids.films.add(sid)
            elif cat == "series":
                show_ids.series.add(sid)
        
        return show_ids
