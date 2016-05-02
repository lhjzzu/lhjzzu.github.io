---
layout: post
title: ios xcodebuil命令探析
date: 2016-04-29
categories: blog


---


## xcodebuild 

### 简介

 xcodebuild 编译code中的projects和workspaces
 
### 文档
 
 1 在终端中输入
 
 `man xcodebuild`
 
 2 下面是xcodebuild的部分文档
  
    NAME
     xcodebuild -- build Xcode projects and workspaces

    SYNOPSIS
     xcodebuild [-project name.xcodeproj]
                [[-target targetname] ... | -alltargets]
                [-configuration configurationname]
                [-sdk [sdkfullpath | sdkname]] [action ...]
                [buildsetting=value ...] [-userdefault=value ...]

     xcodebuild [-project name.xcodeproj] -scheme schemename
                [[-destination destinationspecifier] ...]
                [-destination-timeout value]
                [-configuration configurationname]
                [-sdk [sdkfullpath | sdkname]] [action ...]
                [buildsetting=value ...] [-userdefault=value ...]

     xcodebuild -workspace name.xcworkspace -scheme schemename
                [[-destination destinationspecifier] ...]
                [-destination-timeout value]
                [-sdk [sdkfullpath | sdkname]] [action ...]
                [buildsetting=value ...] [-userdefault=value ...]

     xcodebuild -version [-sdk [sdkfullpath | sdkname]] [infoitem]

     xcodebuild -showsdks

     xcodebuild -showBuildSettings
                [-project name.xcodeproj | [-workspace name.xcworkspace -scheme schemename]]

     xcodebuild -list [-project name.xcodeproj | -workspace name.xcworkspace]

     xcodebuild -exportArchive -archivePath xcarchivepath -exportPath
                destinationpath -exportOptionsPlist path

     xcodebuild -exportLocalizations -project name.xcodeproj -localizationPath
                path [[-exportLanguage language] ...]
     xcodebuild -importLocalizations -project name.xcodeproj -localizationPath
                path
         OS X                            March 19, 2015                            OS X
         
         

## xcodebuild命令

### xcodebuild -version [-sdk [sdkfullpath | sdkname]] [infoitem]

1 显示版本信息

`xcodebuild -version`


    Xcode 7.3
    Build version 7D175

2 显示某个sdk的版本信息

`xcodebuild -version -sdk iphoneos9.3`


    iPhoneOS9.3.sdk - iOS 9.3 (iphoneos9.3)
    SDKVersion: 9.3
    Path: /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/    SDKs/iPhoneOS9.3.sdk
    PlatformVersion: 9.3
    PlatformPath: /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform
    ProductBuildVersion: 13E230
    ProductCopyright: 1983-2016 Apple Inc.
    ProductName: iPhone OS
    ProductVersion: 9.3

3 注意:
    
   1 -sdk 对应的值可以通过下面的`xcodebuild -showsdks`来得到
   
   2 infoitem显示信息项，没有什么有意义的作用可以不管
    

### xcodebuild -showsdks

1 显示sdk

`xcodebuild -showsdks`



    OS X SDKs:
	   OS X 10.11                    	-sdk macosx10.11

    iOS SDKs:
	  iOS 9.3                       	-sdk iphoneos9.3

    iOS Simulator SDKs:
	  Simulator - iOS 9.3           	-sdk iphonesimulator9.3

    tvOS SDKs:
	  tvOS 9.2                      	-sdk appletvos9.2

    tvOS Simulator SDKs:
	  Simulator - tvOS 9.2          	-sdk appletvsimulator9.2

    watchOS SDKs:
	  watchOS 2.2                   	-sdk watchos2.2

    watchOS Simulator SDKs:
	  Simulator - watchOS 2.2       	-sdk watchsimulator2.2



### xcodebuild -showBuildSettings
   
  1 cd进Test工程文件夹,显示buildSettings
  
   `xcodebuild -showBuildSettings`
   

    Build settings for action build and target Test:
        ACTION = build
        AD_HOC_CODE_SIGNING_ALLOWED = NO
        ALTERNATE_GROUP = staff
        ALTERNATE_MODE = u+w,go-w,a+rX
        ALTERNATE_OWNER = chiyou
        ALWAYS_SEARCH_USER_PATHS = NO
        ALWAYS_USE_SEPARATE_HEADERMAPS = NO
        APPLE_INTERNAL_DEVELOPER_DIR = /AppleInternal/Developer
        APPLE_INTERNAL_DIR = /AppleInternal
        APPLE_INTERNAL_DOCUMENTATION_DIR = /AppleInternal/Documentation
        APPLE_INTERNAL_LIBRARY_DIR = /AppleInternal/Library
        APPLE_INTERNAL_TOOLS = /AppleInternal/Developer/Tools
        APPLICATION_EXTENSION_API_ONLY = NO
        APPLY_RULES_IN_COPY_FILES = NO
        ARCHS = armv7 arm64
        ARCHS_STANDARD = armv7 arm64
        ARCHS_STANDARD_32_64_BIT = armv7 arm64
        ARCHS_STANDARD_32_BIT = armv7
        ....
        
        
### xcodebuild -list [-project name.xcodeproj | -workspace name.xcworkspace]

 显示关于Test.xcodeproj的信息

`xcodebuild -list`



    Information about project "Test":
      Targets:
        Test
        TestTests
        TestUITests

    Build Configurations:
        Debug
        Release

    If no build configuration is specified and -scheme is not passed then "Release" is used.

    Schemes:
        Test



注意：

 1 在这里我们可以得到project的`targets`以及`schemes`以及`Build Configurations`

 2 `xcodebuild -list`与`xcodebuild -list -project Test.xcodeproj`相同，因为它默认取`Test.xcodeproj`
     
 3 如果有pods，`xcodebuild -list -workspace Test.xcworkspace`
 
 
###  xcodebuild [-project name.xcodeproj][[-target targetname] ... | -alltargets] [-configuration configurationname][-sdk [sdkfullpath | sdkname]] [action ...][buildsetting=value ...] [-userdefault=value ...]

 cd进Test工程文件

`xcodebuild -sdk iphoneos9.3`

下面是编译的大致流程:

     Check dependencies 
     —CompileC 编译各个.m文件
     —Ld build/Test.build/Release-iphoneos/Test.build/Objects-normal/armv7/Test normal armv7 
     —Ld build/Test.build/Release-iphoneos/Test.build/Objects-normal/arm64/Test normal arm64 
     —CreateUniversalBinary build/Release-iphoneos/Test.app/Test normal armv7\ arm64 
     —CompileStoryboard Test/Base.lproj/LaunchScreen.storyboard 
     —CompileStoryboard Test/Base.lproj/Main.storyboard
     —CompileAssetCatalog build/Release-iphoneos/Test.app Test/Assets.xcassets
     —ProcessInfoPlistFile build/Release-iphoneos/Test.app/Info.plist Test/Info.plist 
     —GenerateDSYMFile build/Release-iphoneos/Test.app.dSYM build/Release-iphoneos/Test.app/Test
     —LinkStoryboards 
     —ProcessProductPackaging /Users/chiyou/Library/MobileDevice/Provisioning\ Profiles/2504ed49-d99e-4f7a-bafb-bd1eb4bcea9e.mobileprovision build/Release-iphoneos/Test.app/embedded.mobileprovision 
     —Touch build/Release-iphoneos/Test.app 
     —ProcessProductPackaging /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS9.3.sdk/Entitlements.plist build/Test.build/Release-iphoneos/Test.build/Test.app.xcent 
     —CodeSign build/Release-iphoneos/Test.app 
       Signing Identity:     "iPhone Developer: zhida wu (8MR2HY4EQA)"
       Provisioning Profile: "iOS Team Provisioning Profile: *"
                      (2504ed49-d99e-4f7a-bafb-bd1eb4bcea9e) —Validate build/Release-iphoneos/Test.app  
     -Validate /Users/chiyou/Library/Developer/Xcode/DerivedData/Test-dyjdzvtgqgxtqechyirrgsrcuxma/Build/Products/Debug-iphoneos/Test.app              
     ** BUILD SUCCEEDED **



当出现`** BUILD SUCCEEDED **`时，代表编译成功，

1 这种情况下，默认的`-project`的值为`Test.xcodeproj`，默认的`-target`的值为`Test`，默认的`-configuration`对应的值为`Release`，默认的`action`为`build`

2 在Test文件夹下，生成`build`文件夹，在`build`中存在`Release-iphoneos`，`Test.build`两个文件夹，`Test.app`存在于`Release-iphoneos`中。

`xcodebuild -project  Test.xcodeproj -configuration Release -sdk iphoneos9.3 build `  

1 这种情况与`xcodebuild -sdk iphoneos9.3`等价

2 可以将`iphoneos9.3`换成`iphonesimulator9.3`，`build`下会生成`Release-iphonesimulator`文件夹，可以将`Release`换成`Debug`，`build`下会生成对应的`debug_xxx`文件夹

3 作用是编译生成`xx.app`文件


### xcodebuild -workspace name.xcworkspace -scheme schemename [[-destination destinationspecifier] ...] [-destination-timeout value] [-sdk [sdkfullpath | sdkname]] [action ...][buildsetting=value ...] [-userdefault=value ...]


`xcodebuild -workspace Test.xcworkspace -scheme Test -sdk iphoneos9.3 build`

1  -scheme的值可以通过xcodebuild -list -workspace Test.xcworkspace得到。

`xcodebuild -workspace Test.xcworkspace -scheme Test -sdk iphoneos9.3 archive`

1 生成一个`.xcarchive`文件,可以通过选择`window->organizer->Test` 可以看到我们的`.xcarchive`文件，右键`show in finder` 即可找到我们的文件.


### xcodebuild -exportArchive -archivePath MyMobileApp.xcarchive -exportPath ExportDestination -exportOptionsPlist 'export.plist'

     xcodebuild -exportArchive -archivePath /Users/chiyou/Library/Developer/Xcode/Archives/2016-05-02/Test.xcarchive -exportPath ~/desktop/ipa -exportOptionsPlist 'export.plist'

1 作用是将生成的.xcarchive文件，打包成ipa文件.

2 `-archivePath`的值即是`.xcarchive`文件的路径，可以打开xcode，选择`window->organizer->Test` 可以看到我们的`.xcarchive`文件，右键`show in finder` 即可找到我们的文件，可以看到文件的名字是`工程名+archive`的时间，我们要把名字改成容易识别的名字，例如把`Test 16-5-2 下午12.46.xcarchive`改为`Test.xcarchive`，否则识别不出来.

3 `-exportPath`对应的值为输出的ipa包的存放路径，本例中是在桌面上建立一个ipa文件夹。

4 `-exportOptionsPlist`对应的是`export.plist`文件，我们要建立一个`export.plist`文件，文件内输入`ExportDestination`，对应的值为输出ipa包的路径`~/desktop/ipa`。
 





     
  
  
 
  
  