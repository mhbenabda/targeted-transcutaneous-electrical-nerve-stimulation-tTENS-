import csv

def create_csv(filename):
        header = ['#','mode','polarity','source','amplitude[mA]','pulsewidth[us]','interpulse[us]','recovery[%]','frequency[Hz]','stimulationDuration[ms]','numTriggers','numRepetition','pain','accuracy']
        with open(filename, mode='w', newline='', encoding='utf-8') as datafile:
            writer = csv.writer(datafile)
            writer.writerow(header)

def write_to_csv(filename, rowString):
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=result.keys())
        writer.writerow(result)

def main():
     create_csv('experiment_data.csv')
        

if __name__ == "__main__":
    main()
