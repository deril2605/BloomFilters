CS5800 - Final Project
Exploring Bloom Filters for Username Validation in Large-Scale Systems

Satwik Shridhar Bhandiwad (NUID: 002920338)
Sukanya Nag (NUID: 002934094)
Deril Raju (NUID: 002914767)

==========================================================================================

To Run the project:
- Install all the necessary libraries using the command `pip install -r requirements.txt`
- In ip.csv file store all the existing usernames that would be present in the Database.
- Run the file using the command `python bloom.py ip.csv mmh3` for mm3 hashing (or)
`python bloom.py ip.csv sha256` for sha256 hashing.

==========================================================================================