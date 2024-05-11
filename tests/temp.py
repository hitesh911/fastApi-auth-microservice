def contains_only_numbers(some_string):
    return some_string.isdigit()

# Example usage:
string1 = "12345"
string2 = "abc123"
string3 = "1.23"

print(contains_only_numbers(string1))  # True
print(contains_only_numbers(string2))  # False
print(contains_only_numbers(string3))  # False
