from my_vector.vector import Vector

my_vector = Vector()
my_vector.push_back(1)
my_vector.push_back(2)
my_vector.push_back(3)

print(my_vector.size())    # Output: 3
print(my_vector.at(1))     # Output: 2
print(my_vector.front())   # Output: 1
print(my_vector.back())    # Output: 3

my_vector.pop_back()
print(my_vector.size())    # Output: 2
