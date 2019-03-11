import psutil,subprocess,commands,requests

#psutil.cpu_count()
#psutil.cpu_percent(interval=1, percpu=True)
#psutil.virtual_memory().percent
#psutil.disk_usage('/').percent
#psutil.net_io_counters()
#psutil.net_if_addrs()
#psutil.net_if_stats()
#psutil.boot_time()
try:
    res = requests.head('http://192.168.186.141:6000')
except:
    pass
print res.code