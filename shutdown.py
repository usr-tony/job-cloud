import os

def shutdown():
    os.system('sudo shutdown -h now')

# this shutsdown the ec2 instance

if __name__ == '__main__':
    shutdown()