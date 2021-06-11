import time

class Timer(object):
    def start(self):
        if hasattr(self,'interval'):
            del self.interval
        self.start_time=time.time()

    def stop(self):
        if hasattr(self, 'start_time'):
            self.interval=time.time()-self.start_time
            del self.start_time
            sc_interval="{:e}".format(self.interval)
            print("Temps d'execution: %s s" %(sc_interval))