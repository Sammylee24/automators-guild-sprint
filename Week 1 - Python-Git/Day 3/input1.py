# Program to practice input collection
import getpass

name = input("Enter a name here: ")
age = input("Enter age here: ")
gender = input("Enter gender here (M or F): ")
password = getpass.getpass("please enter your password: ")

print("Name is", name)
print("Age is", age)
print("Gender is", gender)
print("Password is", password)

print("Your name is", name, "\b. Your age is", age, "\b, and your gender is", gender)
