from .podman import getenv

def serve():
    myenv = {}
    myenv = getenv(myenv)
    print(myenv)
    print("Serving")

