import os
from pathlib import Path
from multiprocessing import Process
from subprocess import Popen, PIPE, STDOUT
import tempfile
class Git:
    
    def __init__(self, querys):
        
        self.querys = querys
    
    def start(self):
        print("start download:"+str(self.querys))
        p = Process(target=self.down, args=(self.querys,))
        p.start()
        # p.join()

    

    def down(self, querys):
        for query in querys:
            
            msg = self.download(query)
            print(msg)

    async def async_log(self):
        f = Path(tempfile.tempdir) / "down.log"
        with open(f) as fp:
            for l in fp:
                yield l
    
    def download(self, name):
        try:
            assert name.startswith("https://modelscope.cn/")
            home = str((Path("~") / ".cache" ).expanduser())
            if "/" in name:
                p = Path(home) / name.rsplit("/")[-1]
                if p.exists():
                    os.popen("rm -rf "+str(p))
                
            cmd  = f"cd {home} && git clone  {name} "
            f = Path(tempfile.tempdir) / "down.log"
            with open(f, "w") as f:
                proc = Popen(cmd, shell=True, env=os.environ, stdout=f, stderr=f, close_fds=True)
                # proc.stdout.read()
                proc.wait()
                
                # os.spawnl(os.P_NOWAIT, cmd)

                
            return "ok"
        except AssertionError:
            return name+ " : error in repo must start with https://modelscope.cn/"
        except Exception as e:
            print(e)
            return str(e)
            