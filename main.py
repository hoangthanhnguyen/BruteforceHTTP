#!/usr/bin/python

import sys, threading, time, os#, itertools
	
try:
	import mechanize, re
except ImportError as error:
	print(error)
	_, missing_moudle, _ = str(error).split("'")
	sys.exit("Try: sudo apt install python-%s" %(missing_moudle))
	
try:
	from core import actions, utils
	import httpbrute, options
except ImportError as error:
	print(error)
	sys.exit("Missing core module!")
	
	
########################## SSL 
#	https://stackoverflow.com/a/35960702
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
########################## End ssl

def main(setTargetURL, setUserlist, setPasslist, setNumberThreads):

	try:
		sizePasslist = actions.getObjectSize(setPasslist)

	except:
		#utils.printf("Can not get size of passlist", "bad")
		pass

	timeStarting = time.time()

	workers = []

	try:
		#lock = threading.Lock()
		#lock.acquire()
		#	Create thread list
		#usePasslist = list(itertools.islice(setPasslist, sizePasslist))
		usePasslist = setPasslist.readlines()

		for i in xrange(setNumberThreads):
			worker = threading.Thread(
				target = httpbrute.handle,
				args = (setTargetURL, setUserlist, usePasslist, sizePasslist)
			)
			# add threads to list
			workers.append(worker)
	except Exception as error:
		utils.die("Error while creating threads", error)

		#	Start all threads
	try:
		for worker in workers:
			worker.daemon = True
			worker.start()

	#except (KeyboardInterrupt, SystemExit):
	except KeyboardInterrupt:# as error:
		# for worker in workers:
		# 	worker.join()
		utils.die("Terminated by user!", KeyboardInterrupt)
		
	except SystemExit:# as error
		utils.die("Terminated by system!", SystemExit)

	except Exception as error:
		utils.die("Error while running", error)

	finally:
		try:
			for worker in workers:
				worker.join()
		except:
			pass
		############################################
		#	Get result
		#
		############################################

		# try:
		# 	credentials = processBruteForcing.actGetResult()
		#
		# 	#	check result
		# 	if len(credentials) == 0:
		# 		utils.printf("Password not found!", "bad")
		# 	else:
		# 		utils.printf("")
		# 		utils.print_table(("Username", "Password"), *credentials)
		# except:
		# 	#utils.printf("\nCan not get result.\n", "bad")
		# 	pass

		utils.printf("\nCompleted. Run time: %0.5s [s]\n" %(time.time() - timeStarting))

		########################################
		#	Clear resources
		#
		########################################

		try:
			setPasslist.close()
		except:
			pass
		try:
			setUserlist.close()
		except:
			pass

		sys.exit(0)

if __name__ == "__main__":
	current_dir = actions.getProjectRootDirectory(sys.argv[0])
	if current_dir:
		os.chdir(current_dir)
	setTargetURL, setUserlist, setPasslist, setNumberThreads = options.getUserOptions()
	main(setTargetURL, setUserlist, setPasslist, setNumberThreads)