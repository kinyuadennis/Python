name=input("Enter your name: ")
age=18
well_groomed= False
have_ID=False
if age>=18:
    print("Hello " + name+ " welcome this will be your school")
    if not have_ID and well_groomed:
        print(name, "you are well groomed see the admin immediately")
    else:
        print(name, "you are not a student in this school")
else:
    print("Hello " + last_name)