from math import log
import csv
from sys import maxsize, argv
import numpy as np
from re import search
from bitarray import bitarray
import mmh3
import hashlib

"""
Simple bloom filter. Based on a few hash functions

"""

# Hash Function
def mult_method(item: object, hash_size: int=maxsize, seed=0):
    return (id(item) + seed**2) % hash_size + 1


# n = number of elements to insert
# f = the false positive rate
# m = number of bits in a Bloom filter
def load_data():
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
    # size is the max num of elements in the filter
    # fp is the false positive probability
    def __init__(self, size, fp_rate, hash_function):
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
        return int(-log(self.fp_rate)*self.size/(log(2)**2))
    
    def hash_count(self):
        return int(self.__bit_size*log(2)/self.size)

    def add_item(self, item):
        for seed in range(self.__hash_count):
            if self.hash_function == "mmh3":
                index = mmh3.hash(item, seed) % self.__bit_size
            elif self.hash_function == "sha256":
                index = int(hashlib.new("sha256", f"{item}-{seed}".encode('utf-8')).hexdigest(),16) % self.__bit_size
            self.bit_array[index] = 1
 
    def check(self, item):
        for seed in range(self.__hash_count):
            if self.hash_function == "mmh3":
                index = mmh3.hash(item, seed) % self.__bit_size
            elif self.hash_function == "sha256":
                index = int(hashlib.new("sha256", f"{item}-{seed}".encode('utf-8')).hexdigest(),16) % self.__bit_size
            if self.bit_array[index] == 0:
                return False
        return True

    def add_array(self, array):
        try:
            for item in array.tolist():
                self.add_item(item[0])
        except TypeError:
            print("Array must be a numpy array (ndarray)")
            exit()

    def check(self, item):
        for i in range(self.__hash_count):
            if self.hash_function == "mmh3":
                index = mmh3.hash(item[0], i) % self.__bit_size
            elif self.hash_function == "sha256":
                index = int(hashlib.new("sha256", f"{item[0]}-{i}".encode('utf-8')).hexdigest(),16) % self.__bit_size
            if self.bit_array[index] == 0:
                return False
        return True


def combined_data(arr_1, arr_2):
    combined_data = np.column_stack((arr_1, arr_2))
    return combined_data


def main():
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

