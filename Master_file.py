# import subprocess

# cmd = "python one_test_file.py"
# p = subprocess.Popen(cmd, shell=True)
# stdout, stderr = p.communicate()
# print(stdout)
# print(stderr)
try:
    exec(open('C:/Users/Lenovo/Desktop/BatchFiles/one_test_file.py').read())
except:
    print("Error in 1st file")
print("Master Done")
try:
    exec(open('C:/Users/Lenovo/Desktop/BatchFiles/second_test_file.py').read())
except:
    print("Error in second file.")