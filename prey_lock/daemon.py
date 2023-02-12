import logging
from collector.collector import Collector

def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, filename='./logs/collector.txt')
    collector = Collector()
    collector.run()

if __name__ == "__main__":
    main()
