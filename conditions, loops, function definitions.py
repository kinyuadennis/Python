import requests
from bs4 import BeautifulSoup
registration_number = input("Enter your registration number: ")
int(registration_number)
print("i will help you calculate your term 3 results")
if registration_number<=0:
    print("Please enter a valid registration number")
else:
    print("Be a serious student")
maths=input("Enter your marks for maths: ")
maths=int(maths)
def calculate_results(maths):
 if maths>=70:
       print("you passed in maths")
 if maths<70 and maths>=60:
          print("maths you scored a B+")
 if maths<60 and maths>=50:
             print(f"that's a grade {'B'}")
 elif maths<50:
              print(f"that's a grade {'C'}")
 else:
     print("you failed")
calculate_results(maths)


