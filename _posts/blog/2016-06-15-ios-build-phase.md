---
layout: post
title: ios打包--build过程探析（一）
date: 2016-06-15
categories: IOS


---

## build 过程控制
一般来说，当你选择打开xcode工程并且选择工程文件的时候，会在 project editor 顶部显示出 6 个 tabs：General, Capabilities, Info, Build Settings, Build Phases 以及 Build Rules。对我们的build过程来说，后三项与build紧密相关。

## build Phases解析

### build phases 代表将代码转变为可执行文件的最高规则，
![](http://7xqijx.com1.z0.glb.clouddn.com/1.png)

### 下图对各项过程进行简单介绍
![build Phases解析](http://7xqijx.com1.z0.glb.clouddn.com/build%2BPhases.png)

至此，build过程并没有结束，还有code sigining以及packageing阶段。总的来说我们可以把build过程分为编译，链接，
code signing ，packageing四个阶段。


## build Rules

 Build rules 指定了不同的文件类型该如何编译。一般不许要开发者进行设置，如果想要详细了解，请参考[这篇文章](http://objccn.io/issue-6-1/)

## build setting

    Prefix Header ->${SRCROOT}/工程名/文件名.pch
    Framework Search Paths -> $(PROJECT_DIR)/DV/Frameworks/Lib/QQSDK）
    Header Search Paths -> "${PODS_ROOT}/Headers/Public/AFNetworking"
    Library Search Paths -> $(PROJECT_DIR)/DV/Frameworks/Lib/PingcooSDK
       
  | 名字       | 对应的宏定义    |       说明      |
  |:----------|:--------------|:---------------|   
  |Architecture |   ARCHS     |选择的架构        |
  |Valid Architectures |  VALID_ARCHS |可用的架构|
  |Build Active Architecture Only |  ONLY_ACTIVE_ARCH |值为YES或NO,如果是YES代表只有一种架构，如果为No，那么架构就是Architecture的设置|
  |configuration|CONFIGURATION|值为debug或者release|
  |Other Linker Flags|OTHER_LDFLAGS|默认值为None,如果我们的库中有对某一分类的扩展，需要指定值为-ObjC或者-force_load或者-all_load，更详细的信息可以参考[这篇文章](http://small.qiang.blog.163.com/blog/static/978493072013112571950/)|
  |Enable Bitcode|ENABLE_BITCODE|跟苹果对我们包的优化有关，默认为YES.如果你设为YES，但是导入的第三库却不支持Enable Bitcode那么，编译的时候就会报错，这个时候设置为No即可,具体可以参考[这篇文章](http://www.jianshu.com/p/3e1b4e2d06c6)|
  |Code Signing Identity|CODE_SIGN_IDENTITY|选择证书|
  |Provisioning Profile|PROVISIONING_PROFILE|选择对用的配置文件|
  
先列举我常用的，以后会继续补充,这些宏定义是为了我们在终端中进行命令行操作时，根据需要来执行，它会覆盖xcode工程中对应的设置.

## 参考文章

* [Build 过程](http://objccn.io/issue-6-1/)
* [Build Setting Reference](https://developer.apple.com/library/mac/documentation/DeveloperTools/Reference/XcodeBuildSettingRef/1-Build_Setting_Reference/build_setting_ref.html#//apple_ref/doc/uid/TP40003931-CH3-SW105)







     
  
  
 
  
  