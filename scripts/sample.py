from dotenv import load_dotenv
import os
load_dotenv()

myenv = os.getenv("MY_ENV", "default_value")
myenv2 = os.environ.get('MY_ENV2', 'default_value')

print(myenv)
print(myenv2)