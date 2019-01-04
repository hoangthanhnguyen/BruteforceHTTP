import mechanize, re, threading
from core.tbrowser import startBrowser
from core.utils import printf, die
from core.actions import fread, fwrite

try:
	from Queue import Queue
except ImportError:
	from queue import Queue
"""
support url:
https://free-proxy-list.net/
"""

# BUG: import modules error


def getNewProxy(PROXY_PATH):
	
	def parse_proxy(response):
		try:
			re_ip = r"\b(?:\d{1,3}\.){3}\d{1,3}\b<\/td><td>\d{1,5}"
			result = re.findall(re_ip, response, re.MULTILINE)
			result = [element.replace("</td><td>", ":") for element in result]
			return result
		except Exception as error:
			die("[x] GetProxy: Error while parsing proxies.", error)
			
	def checProxyConnProvider(url = "https://free-proxy-list.net/"):
		try:
			printf("[+] Connecting to %s." %(url))

			getproxy = startBrowser()

			getproxy.open(url)
			printf("[*] Gathering proxies completed.", "good")
			return getproxy.response().read()

		except Exception as error:
			die("[x] GetProxy: Error while connecting to proxy server!", error)
		finally:
			getproxy.close()
			

	try:
		listproxy = parse_proxy(checProxyConnProvider())
	except:
		listproxy = ""
	finally:
		try:
			listproxy = "\n".join(listproxy)
			printf("[+] Saving to %s" %(PROXY_PATH))
			fwrite(PROXY_PATH, listproxy)
			printf("[*] Data saved!", "good")

		except Exception as error:
			die("[x] GetProxy: Error while writting data", error)


def check(options, PROXY_PATH):
	
	def do_job(jobs):
		for job in jobs:
			job.start()
		for job in jobs:
			job.join()

	def checProxyConn(proxyAddr, target, result, verbose):
		try:
			proxyTest = startBrowser()
			proxyTest.set_proxies({"http": proxyAddr})

			if verbose:
				printf("[+] Trying: %s" %(proxyAddr))

			proxyTest.open(options.url)

			if verbose:
				printf("[*] Success: %s" %(proxyAddr), "good")
			result.put(proxyAddr)

		except Exception as error:
			if verbose:
				printf("[x] %s %s" %(proxyAddr, error), "bad")
		finally:
			try:
				proxyTest.close()
			except:
				pass
	try:
		
		proxylist = fread(PROXY_PATH).split("\n")
				
		workers = []
		result = Queue()
		for tryProxy in proxylist:
			if len(workers) == options.threads:
				do_job(workers)
				del workers[:]
			
			worker = threading.Thread(
				target = checProxyConn,
				args = (tryProxy, options.url, result, options.verbose)
			)

			worker.daemon = True
			workers.append(worker)
			
		do_job(workers)
		del workers[:]

	except KeyboardInterrupt as error:
		printf("[x] Terminated by user!", "bad")
		import os
		os._exit(0)
	
	except Exception as error:
		die("[x] GetProxy: Error while checking proxy connection to target", error)

	finally:
		try:
			printf("[+] Write working proxies")
			fwrite(PROXY_PATH, "\n".join(list(result.queue)))
			printf("[*] Write working proxies completed", "good")
		except Exception as err:
			die("[x] GetProxy: Error while writing result", err)

def main(options):
	try:
		import data
		save = "%s/liveproxy.txt" %(data.__path__[0])
		getNewProxy(save)
		if options.url:
			check(options, save)
	except Exception as err:
		die("[x] GetProxy: Runtime error", err)
