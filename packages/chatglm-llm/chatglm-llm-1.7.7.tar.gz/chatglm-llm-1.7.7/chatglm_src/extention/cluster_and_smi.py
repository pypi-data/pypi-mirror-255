from sklearn.cluster import KMeans, DBSCAN

from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
# from websocket import create_connection
# import datetime
# import time
from hashlib import md5
import json
from termcolor import colored
import tqdm
import termcolor


def cluster(data, n_clusters=2,eps=0.5,min_samples=3, method='kmeans'):
    
    if method == 'kmeans':
        kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init='auto').fit(data)
        return kmeans.labels_
    elif method == 'dbscan':
        db = DBSCAN(metric='euclidean',eps=eps, min_samples=min_samples).fit(data)
        return db.labels_
    elif method == 'cosine':
        sim_vec = cosine_similarity(data).tolist()
    else:
        raise ValueError('method must be kmeans or dbscan')


def similarity(data, method='cosine'):
    if method == 'cosine':
        return cosine_similarity(data).tolist()
    elif method == 'euclidean':
        return euclidean_distances(data).tolist()
    else:
        raise ValueError('method must be cosine or euclidean')


# def papers(remote_host,texts, method="dbscan", eps=0.3, min_samples=3, n_clusters=2,filter_noise=None):
#     """
#     @method : str, default='dbscan' , can used 'kmeans' or 'dbscan' or 'cosine' or 'euclidean'
#         @eps : float, default=0.3, used in dbscan
#         @min_samples : int, default=3, used in dbscan
#         @n_clusters : int, default=2, used in kmeans
    
#     """
#     ws = create_connection(f"ws://{remote_host}:15000")
#     user_id = md5(time.asctime().encode()).hexdigest()
#     TODAY = datetime.datetime.now()
#     PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
#     ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
#     # time.sleep(0.5)
#     res = ws.recv()
#     if res != "ok":
#         print(colored("[info]:","yellow") ,res)
#         raise Exception("password error")
    
#     data = json.dumps({
#         "embed_documents":texts,
#         "method":method,
#         "n_clusters":n_clusters,
#         "filter_noise":filter_noise,
#         "eps":eps,
#         "min_samples":min_samples

#     })
#     msg = send_and_recv(data, ws)
#     return msg


def send_and_recv(data, ws):
    try:
        T = len(data)// 1024*102
        bart = tqdm.tqdm(total=T,desc=termcolor.colored(" + sending data","cyan"))
        bart.leave = False
        for i in range(0, len(data), 1024*102):
            bart.update(1)
            ws.send(data[i:i+1024*102])
        bart.clear()
        bart.close()
        ws.send("[STOP]")
        message = ""
        total = int(ws.recv())
        bar = tqdm.tqdm(desc=termcolor.colored(" + receiving data","cyan", attrs=["bold"]), total=total)
        bar.leave = False
        while 1:
            res = ws.recv()
            message += res
            bar.update(len(res))
            if message.endswith("[STOP]"):
                message = message[:-6]
                break
        
        bar.clear()
        bar.close()
        msg = json.loads(message)
        return msg
    except Exception as e:
        raise e