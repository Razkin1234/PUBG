from settings import *
c=0
for i in list(weapon_data.keys()):
    if 'sword' == i:
        break
    c += 1

print(list(weapon_data.keys())[c])
