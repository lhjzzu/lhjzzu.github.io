from optparse import OptionParser
import subprocess
import requests

#configuration for iOS build setting
CODE_SIGN_IDENTITY = "iPhone Distribution: Hangzhou Riguan Apparel Co.,ltd (V9LX9F46VG)"
PROVISIONING_PROFILE = "a97416b6-a868-44c7-8bd5-5847954305bb"
CONFIGURATION = "release"
SDK = "iphoneos"

# configuration for pgyer
PGYER_UPLOAD_URL = "http://www.pgyer.com/apiv1/app/upload"
DOWNLOAD_BASE_URL = "http://www.pgyer.com"
USER_KEY = "b836bbd8c0cb96463a6ef0895061c3c9"
API_KEY = "0607f8bf8233b5665255acf59f16cdf6"

def cleanBuildDir(buildDir):
	cleanCmd = "rm -r %s" %(buildDir)
	process = subprocess.Popen(cleanCmd, shell = True)
	process.wait()
	print "cleaned buildDir: %s" %(buildDir)


def parserUploadResult(jsonResult):
	resultCode = jsonResult['code']
	if resultCode == 0:
		downUrl = DOWNLOAD_BASE_URL +"/"+jsonResult['data']['appShortcutUrl']
		print "Upload Success"
		print "DownUrl is:" + downUrl
	else:
		print "Upload Fail!"
		print "Reason:"+jsonResult['message']

def uploadIpaToPgyer(ipaPath):
    print "ipaPath:"+ipaPath
    files = {'file': open(ipaPath, 'rb')}
    headers = {'enctype':'multipart/form-data'}
    payload = {'uKey':USER_KEY,'_api_key':API_KEY,'publishRange':'2','isPublishToPublic':'2', 'password':''}
    print "uploading...."
    r = requests.post(PGYER_UPLOAD_URL, data = payload ,files=files,headers=headers)
    if r.status_code == requests.codes.ok:
         result = r.json()
         parserUploadResult(result)
    else:
        print 'HTTPError,Code:'+r.status_code

def buildProject(project, target, output):
	buildCmd = 'xcodebuild -project %s -target %s -sdk %s -configuration %s build CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s"' %(project, target, SDK, CONFIGURATION, CODE_SIGN_IDENTITY, PROVISIONING_PROFILE)
	process = subprocess.Popen(buildCmd, shell = True)
	process.wait()

	signApp = "./build/%s-iphoneos/%s.app" %(CONFIGURATION, target)
	signCmd = "xcrun -sdk %s -v PackageApplication %s -o %s" %(SDK, signApp, output)
	process = subprocess.Popen(signCmd, shell=True)
	(stdoutdata, stderrdata) = process.communicate()

	uploadIpaToPgyer(output)
	cleanBuildDir("./build")

def buildWorkspace(workspace, scheme, output):
	process = subprocess.Popen("pwd", stdout=subprocess.PIPE)
	(stdoutdata, stderrdata) = process.communicate()
	buildDir = stdoutdata.strip() + '/build'
	print "buildDir: " + buildDir
	buildCmd = 'xcodebuild -workspace %s -scheme %s -sdk %s -configuration %s build CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s" SYMROOT=%s' %(workspace, scheme, SDK, CONFIGURATION, CODE_SIGN_IDENTITY, PROVISIONING_PROFILE, buildDir)
	process = subprocess.Popen(buildCmd, shell = True)
	process.wait()

	signApp = "./build/%s-iphoneos/%s.app" %(CONFIGURATION, scheme)
	signCmd = "xcrun -sdk %s -v PackageApplication %s -o %s" %(SDK, signApp, output)
	process = subprocess.Popen(signCmd, shell=True)
	(stdoutdata, stderrdata) = process.communicate()

	uploadIpaToPgyer(output)
	cleanBuildDir(buildDir)

def xcbuild(options):
	project = options.project
	workspace = options.workspace
	target = options.target
	scheme = options.scheme
	output = options.output

	if project is None and workspace is None:
		pass
	elif project is not None:
		buildProject(project, target, output)
	elif workspace is not None:
		buildWorkspace(workspace, scheme, output)

def autoPush():
    addCmd = 'git add .'
    process = subprocess.Popen(addCmd, shell = True)
    process.wait()
    commitCmd = 'git commit -m "456"'
    process = subprocess.Popen(commitCmd, shell=True)
    process.wait()
    pushCmd = 'git push'



def main():

    autoPush()


if __name__ == '__main__':
	main()