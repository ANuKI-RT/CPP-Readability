from enum import Enum


class Command(Enum):
    CRAWL = 'crawl'
    METRICS = 'metrics'
    READABILITY = 'readability'
    EXTRACT_READABILITY = 'extract-readability'

    def __str__(self):
        return self.value
