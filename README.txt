RoundUp is a program based on the roundup feature for increasing your savings.
RoundUp uses the plaid api to look at your transactions and then rounds the transactions up
to the nearest dollar if the amount is less than 250 and to the nearest 5 if the amount is greater.
The program will output the total amount rounded up.

Input plaid keys into the python files to run.

add_bank and roundup are two different programs:

add_bank.py is a webapp that is only used to add banks to the list of banks that have their transactions rounded.
add_bank.py saves all its data into a accounts.json file 

roundup is a terminal based program that will read the accounts.json and round up your transactions and output the total for you.
The amount being rounded to can be changed in the roundup function