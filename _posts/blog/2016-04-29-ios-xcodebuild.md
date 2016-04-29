---
layout: post
title: ios xcodebuil命令探析
date: 2016-04-29
categories: blog


---


## xcodebuild 简介

 1 xcodebuild 编译code中的projects和workspaces
 
 2 在终端中输入
 
 `man xcodebuild`
 
 3下面是xcodebuild的部分文档
  
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





     
  
  
 
  
  