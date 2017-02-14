---
layout: post
title: ios打包--打包framework(六)
date: 2016-07-25
categories: IOS

---

> [上一篇文章](http://lhjzzu.github.io/2016/05/06/static-lib/) 已经对静态库做了详细的介绍，`.a`文件和`.framework`本质上都是`.a`文件以及隐藏的`.h`文件信息的集合(`.framework`还包括公开的头文件)。所以这篇文章就说一下，如何生成`.framework`文件。


## 通过Xcode生成`.framework`

* 建立一个名为`Framework`的框架工程文件。
* 像建立静态工程文件一样，在工程中建立对应的`.h`，`.m`文件并指定`.h`文件是公开还是隐藏，以及编译的内容，指定架构，指定是`release`还是`debug`，选择是真机还是模拟器,最终生成`Debug-iphoneos`,`Debug-iphonesimulator`,`Release-iphoneos`,`Release-iphonesimulator`,在每个文件夹下都有一个`Framework.framework`,在`Framework.framework`中有一个`Framework`文件.
* 查看信息

        $ lipo -info /Users/chiyou/Library/Developer/Xcode/DerivedData/Framework-eoafddjlyqpvlybbqrcajspbaabu/Build/Products/Release-iphonesimulator/Framework.framework/Framework
         Architectures in the fat file: /Users/chiyou/Library/Developer/Xcode/DerivedData/Framework-eoafddjlyqpvlybbqrcajspbaabu/Build/Products/Release-iphonesimulator/Framework.framework/Framework are: i386 x86_64 

* 合并，生成最终的`framework`文件
        
        1 在终端中输入下列命令，合并Framework文件
          $ lipo -create /Users/chiyou/Library/Developer/Xcode/DerivedData/
          Framework- eoafddjlyqpvlybbqrcajspbaabu/Build/Products/Release-iphoneos/
          Framework.framework/Framework /Users/chiyou/Library/Developer/Xcode/
          DerivedData/Framework-eoafddjlyqpvlybbqrcajspbaabu/Build/Products/
          Release-iphonesimulator/Framework.framework/Framework -o ~/desktop/框架/Framework 
        2 查看生成的Framework文件的信息
           $ lipo -info Framework
           
            Architectures in the fat file: /Users/chiyou/Desktop/框架/Framework 
            are: i386 x86_64 armv7 armv7s arm64 
        3 用生成的Framework文件替换掉Release-iphoneos中的Framework.framework下的Framework文件即可。
           
## 通过命令行`.framework`


* 建立一个名为`Framework`的框架工程文件。
* 工程中建立相应的文件，并制定.h文件是否隐藏，以及编译的内容。
* 生成`Release-iphoneos`文件夹

        $ xcodebuild -project Framework.xcodeproj -target Framework -sdk iphoneos -configuration Release ONLY_ACTIVE_ARCH="NO" ARCHS="armv7 armv7s arm64" VALID_ARCHS="armv7 armv7s arm64"
        
        
        ** BUILD SUCCEEDED ** 代表编译成功，可以看到工程文件夹下多了一个build文件夹,
        可以在其中查看相关信息。自己可以查看一下Framework的信息
        


* 生成`Release-iphonesimulator`文件夹

        $ xcodebuild -project Framework.xcodeproj -target Framework -sdk iphonesimulator -configuration Release ONLY_ACTIVE_ARCH="NO"
        
         ** BUILD SUCCEEDED ** 代表编译成功，可以看到工程文件夹下多了一个build文件夹。
        可以在其中查看相关信息。自己可以查看一下Framework的信息

* 合并，生成最终的`framework`文件(`同上`)
  
     

## 通过脚本来建立`.framework`

* 我写了一个脚本[autoFramework](https://github.com/lhjzzu/autoFramework)，你可以直接下载使用。
* cd进入工程文件夹，执行`$ python autoFramework.py -t xxx (工程名)`即可，`.framework`文件生成在工程文件夹下(也可以参考`README.md`)

     

## 参考


* [Build Setting Reference](https://developer.apple.com/library/mac/documentation/DeveloperTools/Reference/XcodeBuildSettingRef/1-Build_Setting_Reference/build_setting_ref.html#//apple_ref/doc/uid/TP40003931-CH3-SW105)
* [ios framework通用库的制作](http://www.2cto.com/kf/201403/282723.html)
* [ios打包--xcodebuild以及xcrun](http://lhjzzu.github.io/2016/04/29/ios-xcodebuild/)
     
  
  
 
  
  