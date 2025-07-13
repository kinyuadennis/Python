name = input("Enter your name: ")
position = input("Enter your work position: ")
working_days = input("Enter your work days: ")
working_days= int(working_days)
salary=working_days*1400
new_member=True
if working_days <= 0:
    print ("unfortunately you have not been present")

if working_days >= 1 and position == "IT Admin" :
   print(f"{name} you have been working on {working_days} days" + " this is your salary")
   print(salary)
if position != "IT Admin" :
    position = input("Are you new: ")
    if new_member :

        print ( name, "you must be new")
        




