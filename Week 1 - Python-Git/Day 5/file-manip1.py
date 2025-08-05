import os

if not os.path.exists('text.txt'):
    new_file = open('text.txt', 'x')
else:
    print("Already existing!")

with open ('text.txt', 'a') as file:
    file.writelines("\nThis is a new stuff")
    file.close

with open('text.txt', 'r') as file:
    #last_line = file.readlines()[-1]  # Presents as a list
    #first_line = file.readline()
    everything = file.read()

    print(everything)
    #print(last_line)
    #print(first_line)
    file.close()

