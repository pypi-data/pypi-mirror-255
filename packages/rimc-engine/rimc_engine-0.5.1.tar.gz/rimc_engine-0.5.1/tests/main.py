from rimc_engine import open_apply_save, Recipe
import os
from datetime import datetime


def main():
    path = "orig/"    
    
    print(os.listdir(path))
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            # Get the current timestamp
            current_timestamp = round(datetime.timestamp(datetime.now())/10)
            print(current_timestamp)
            open_apply_save(f, suffix=str(current_timestamp))

        

if __name__ == "__main__":
    main()