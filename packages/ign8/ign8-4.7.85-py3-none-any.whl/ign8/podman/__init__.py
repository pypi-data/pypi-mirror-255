from .serve import serve
from .podman import getenv

def main():
    myenv = {}
    myenv = getenv(myenv)
    print(myenv)
    print("Serving")
    serve()
