list = [[4,3,2],[3,5,6]]
def j():
    global list
    s = list[1]
    a(s)
def a(s1):
    s1[2] = 100
j()
print(list)