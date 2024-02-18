# from .llm import AsyncServer
from chatglm_src.serv import run
# import uvicorn
import argparse
# import pathlib

parser = argparse.ArgumentParser(description='Start a chatglm server.')
parser.add_argument('-p','--port', type=int, default=15001, help='port number')
parser.add_argument("-w",'--worker', type=int, default=1, help='worker number')
# parser.add_argument("-n","--name", default="chatglm", help="llm's name")
# parser.add_argument("-e","--extend", nargs="*", help="load extend models , like 'emotion' 'ner' in ~/.cache/ ")


def main():
    args = parser.parse_args()
    # if args.extend:
    #     for i in args.extend:
    #         AsyncServer.load_model(i)
    # AsyncServer.start(port=args.port, model_path=args.model_path, name=args.name)
    # uvicorn.run(app, host="0.0.0.0", port=args.port, workers=args.worker)
    
    run(port=args.port, workers=args.worker)