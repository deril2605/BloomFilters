from math import log
import csv
from sys import maxsize, argv
import numpy as np
from re import search
from bitarray import bitarray
import mmh3
import hashlib

def load_data():
    """
    Load data from a CSV file. The file path and the hash function name are provided as command line arguments.
    This function returns the data, the desired false positive rate, and the name of the hash function to use.
    
    """

    if len(argv) <= 2:
        print("""
Usage: bloom [DATABASE-PATH] [HASH-FUNCTION]
Basic bloom filter
Example: ./bloom-filter db_input.csv sha256
Example: ./bloom-filter db_input.csv mmh3
        """)
        exit()

    # first one are the input usernames
    try:
        with open(argv[1], 'r') as file:
            data_iter = csv.reader(file)    
            next(data_iter, None)  # skip the headers      
            i = [i for i in data_iter]
        data = np.array(i, dtype=str)

    except:
        print("Invalid path or file")
        exit()
    
    fp_rate = 0.005 
    return (data, fp_rate, argv[2])

class BloomFilter(object):
    """
    A class that represents a Bloom Filter.
    """
    
    def __init__(self, size, fp_rate, hash_function):
        """
        Initialize the Bloom Filter.
        size is the expected number of elements.
        fp_rate is the desired false positive rate.
        hash_function is the name of the hash function to use.
        """
        self.size = size
        self.fp_rate = fp_rate
        self.hash_function = hash_function
        self.__bit_size = self.bit_size() # M
        self.__hash_count = self.hash_count() # K
        self.bit_array = bitarray(self.__bit_size)
        self.bit_array.setall(0)
 
    # m = size of bit array
    # n = expected number of items
    # p = probability percentage represented as a decimal
    # k = number of hash functions required

    def bit_size(self):
        """
        Calculate the size of the bit array required for the Bloom Filter.
        """
        return int(-log(self.fp_rate)*self.size/(log(2)**2))
    
    def hash_count(self):
        """
        Calculate the number of hash functions required for the Bloom Filter.
        """
        return int(self.__bit_size*log(2)/self.size)

    def add_item(self, item):
        """
        Add an item to the Bloom Filter.
        """
        for seed in range(self.__hash_count):
            if self.hash_function == "mmh3":
                index = mmh3.hash(item, seed) % self.__bit_size
            elif self.hash_function == "sha256":
                index = int(hashlib.new("sha256", f"{item}-{seed}".encode('utf-8')).hexdigest(),16) % self.__bit_size
            self.bit_array[index] = 1
 
    def check(self, item):
        """
        Check if an item is probably in the Bloom Filter.
        """
        for seed in range(self.__hash_count):
            if self.hash_function == "mmh3":
                index = mmh3.hash(item, seed) % self.__bit_size
            elif self.hash_function == "sha256":
                index = int(hashlib.new("sha256", f"{item}-{seed}".encode('utf-8')).hexdigest(),16) % self.__bit_size
            if self.bit_array[index] == 0:
                return False
        return True

    def add_array(self, array):
        """
        Add all items from a numpy array to the Bloom Filter.
        """
        try:
            for item in array.tolist():
                self.add_item(item[0])
        except TypeError:
            print("Array must be a numpy array (ndarray)")
            exit()

    def check(self, item):
        """
        Check if an item is probably in the Bloom Filter.
        """
        for i in range(self.__hash_count):
            if self.hash_function == "mmh3":
                index = mmh3.hash(item[0], i) % self.__bit_size
            elif self.hash_function == "sha256":
                index = int(hashlib.new("sha256", f"{item[0]}-{i}".encode('utf-8')).hexdigest(),16) % self.__bit_size
            if self.bit_array[index] == 0:
                return False
        return True

def main():
    """
    The main function.
    """
    data, fp_rate, hash_function = load_data()
    print(f"Using {hash_function} for hashing")
    # Hard coded values
    data_set_length = len(data)

    Filter = BloomFilter(data_set_length, fp_rate, hash_function)
    Filter.add_array(data)

    while True:
        username = input("Please enter a username to check: ")

        # Check the username against the filter
        if Filter.check([username]):
            print("This username is probably in the DB, please enter another username.")
        else:
            print("This username is not in the DB. It will be added now.")
            print("Exiting program...")
            
            # Add the username to the filter
            Filter.add_item(username)
            
            # Add the username to the CSV file
            with open(argv[1], 'a') as file:  # argv[1] is the path to the input CSV file
                writer = csv.writer(file)
                writer.writerow([username])
            
            break

if __name__ == '__main__':
    main()

