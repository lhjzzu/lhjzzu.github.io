from optparse import OptionParser
import subprocess

def autoPush(message,branch):
    addCmd = 'git add .'
    process = subprocess.Popen(addCmd, shell = True)
    process.wait()
    commitCmd = 'git commit -m "%s"' %(message)
    process = subprocess.Popen(commitCmd, shell=True)
    process.wait()
    pushCmd = 'git push'
    process = subprocess.Popen(pushCmd, shell=True)
    process.wait()
    code = process.returncode
    if code != 0:
        print "error"
        autoPull(branch)
        pass
    else:
        print "success"

def autoPull(branch):
    pullCmd = 'git pull'
    process = subprocess.Popen(pullCmd, shell = True)
    process.wait()
    code = process.returncode
    if code != 0:
        print "error"
        setupStream(branch)
        pass
    else:
        print "success"

def setupStream(branch):
    setCmd = 'git branch --set-upstream-to=origin/%s %s' %(branch,branch)
    process = subprocess.Popen(setCmd, shell = True)
    process.wait()
    code = process.returncode
    if code != 0:
        print "error"
        pass
    else:
        print "success"
        autoPull(branch)

def autoFastForward(branch):
    fastForwardCmd = 'git push'
    process = subprocess.Popen(fastForwardCmd, shell = True)
    process.wait()
    code = process.returncode
    if code != 0:
        print "error"
        pass
    else:
        print "success"

def main():
    parser = OptionParser()
    parser.add_option("-m","--message", help="Commit Message",metavar="message")
    parser.add_option("-b","--branch", help="branch name",metavar="branch name")

    (options, args) = parser.parse_args()
    message = options.message
    branch = options.branch
    autoPush(message,branch)
if __name__ == '__main__':
	main()

