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
        print "Push error,you need pull from the origin branch"
        autoPull(branch)
        pass
    else:
        print "Push success"

def autoPull(branch):
    pullCmd = 'git pull'
    process = subprocess.Popen(pullCmd, shell = True)
    process.wait()
    code = process.returncode
    if code != 0:
        print "Pull error, you must setup the steam between the current branch with the orign branch"
        setupStream(branch)
        pass
    else:
        print "Pull success"
        autoFastForward(branch)

def setupStream(branch):
    setCmd = 'git branch --set-upstream-to=origin/%s %s' %(branch,branch)
    process = subprocess.Popen(setCmd, shell = True)
    process.wait()
    code = process.returncode
    if code != 0:
        print "setupStream error"
        pass
    else:
        print "setupStream sucess, pull again"
        autoPull(branch)

def autoFastForward(branch):
    fastForwardCmd = 'git push'
    process = subprocess.Popen(fastForwardCmd, shell = True)
    process.wait()
    code = process.returncode
    if code != 0:
        print "fastForward error, you must resolve conflict, finally execute this script again"
        pass
    else:
        print "fastForward success"




def main():
    parser = OptionParser()
    parser.add_option("-m","--message", help="Commit Message",metavar="message")
    parser.add_option("-b","--branch", help="branch name",metavar="branch name")


    (options, args) = parser.parse_args()
    message = options.message
    branch = options.branch
    if branch is None:
        branch = 'master'
    else:
        pass
    if message is not None and branch is not None:
        autoPush(message,branch)
    else:
        print "error message and branch can't be None"
        pass

if __name__ == '__main__':
	main()

