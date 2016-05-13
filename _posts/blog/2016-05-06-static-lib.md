---
layout: post
title: ios打包--打包静态库(五)
date: 2016-05-06
categories: IOS

---


## 静态库的一点理解
* 当我们不想让我们的.m文件中的内容让别人看到时，可以打包成静态库，来保护我们的源码
* .a文件是.m文件编译成.o文件(目标文件)后的集合
* .a文件中还包含一个`__.SYMDEF`文件

## 建立静态库步骤

### 建立一个静态库工程
![](http://7xqijx.com1.z0.glb.clouddn.com/StaticLib.png)


### 建立相应的文件，并写入自己的代码
1 在`StaticLib.h`文件中添加`-(void)test`方法，在`StaticLib.m`文件中实现该方法
 
    - (void)test1
     {
       NSLog(@"打印test1");
     }
     
2 建立一个`SecondStaticLib`类，在`SecondStaticLib.h`文件中添加`-(void)test2`方法，在`SecondStaticLib.m`文件中实现该方法
 
    - (void)test2
     {
       NSLog(@"打印test2");
     }

### 指定头文件的隐藏和显示

1 点击工程`StaticLib->TARGETS->StaticLib->Build Phases->'+'->New Headers Phase->出现Headers ->点击Headers左边的箭头，出现Public，Private，Project三个选项`.
 
2 `Public`代表的是我们在工程中需要公开的头文件，`Project`代表的是我们在工程中需要隐藏的头文件.
将`StaticLib.h`拉入`Public`目录下，把`SecondStaticLib.h`拉倒`Project`目录下。

### 利用XCode生成.a文件

1 我们可以先看一下`buildSetting`下的`Architectures`的几个设置:

* `Architectures`代表我们现在选择的架构，分为debug和release两种，一般都设置为一样。
真机有`armv7，armv7s,arm64`三种架构. `armv7`指的是`iphone5`以下的设备，`armv7s`指的是`iPhone5`，`arm64`指定的是`iPhone5s`及以上的设备。一般而言，我们`xcode`工程中默认设置`Architectures`为`$(ARCHS_STANDARD)`，代表`armv7`以及`armv64`的两种架构,缺少armv7s这会使我们的工程运行在iPhone5设备上出问题。如果我们要使我们的`.a`文件包含这三种架构，那么需要点击`Architectures->other->输入armv7 armv7s arm64`。这种情况下我们生成的`.a`文件就是`armv7,armv7s,arm64`三种架构的。模拟器的两种架构`i386 x86_64`
,只要选择ios模拟器，并且`Build Active Architecture Only`为`NO`，那么生成的`.a`包就为`i386 x86_64`两种架构。
* `BaseSDK`一般采用系统默认的即可.
* `Build Active Architecture Only`系统默认`debug`设置为`YES`，`release`设置为`NO`。当值为YES的时候代表我们生成的`.a`文件只会采用一种架构(即`not fat file`)，如果值为`NO`,代表我们的生成的`.a`文件的架构与我们在`Architectures`选项设置的架构是相同的(fat file)。
* `Supported Platorm`采用系统默认的，设置为iOS即可
* `Vaild Architectures`代表所有可用的架构，默认即为`armv7，armv7s,arm64`三种


2 在`StaticLib->PROJECT->info->Deployment Target ->iOS Deployment Target->7.0`

代表最低支持7.0的系统。

3 我们可以看到`Products`文件夹下的`libStaticLib.a`文件是红色的，代表现在还没有这个文件，把我们的设备选择为`Generics iOS Device`,将`Run`选为`Debug`模式，点击`Run`.可以看到`libStaticLib.a`文件变为黑色.我们选择`libStaticLib.a`->`show in finder` 我们可以看到`Debug-iphoneos`下生成`libStaticLib.a`文件

     查看生成的.a文件的信息
  
    $lipo -info /Users/chiyou/Library/Developer/Xcode/DerivedData/StaticLib-aohnkijkogumceagdwbpcqbevzxf/Build/Products/Debug-iphoneos/libStaticLib.a
  
     Architectures in the fat file: /Users/chiyou/Library/Developer/Xcode/DerivedData/StaticLib-aohnkijkogumceagdwbpcqbevzxf/Build/Products/Debug-iphoneos/libStaticLib.a are: armv7  armv7s arm64 
     
     我们可以看到我们的架构是三种，但是我们debug模式下Build Active Architecture Only的值为YES，不是应该只有一种架构吗？这个问题先放在这里，我们接下来会提到。
     
 4 设备选择`Generics iOS Device`,将`Run`选为`Release`模式，点击`Run`.生成`Release-iphoneos`，其中有`libStaticLib.a`文件。
   
    查看生成的.a文件的信息
    
    lipo -info /Users/chiyou/Library/Developer/Xcode/DerivedData/StaticLib-aohnkijkogumceagdwbpcqbevzxf/Build/Products/Release-iphoneos/libStaticLib.a 
    
    Architectures in the fat file: /Users/chiyou/Library/Developer/Xcode/DerivedData/StaticLib-aohnkijkogumceagdwbpcqbevzxf/Build/Products/Release-iphoneos/libStaticLib.a are: armv7 armv7s arm64

假如`release`情况下`Build Active Architecture Only`也设置为`YES`,依然可以得到三种架构，这与上面是同一个问题。

 5 设备选择模拟器`iPhone4s及以上`，将`Run`选为`Debug`模式，点击`Run`.生成`Debug-iphonesimulator`，其中有`libStaticLib.a`文件。
 
    查看生成的.a文件的信息
    
    input file /Users/chiyou/Library/Developer/Xcode/DerivedData/StaticLib-aohnkijkogumceagdwbpcqbevzxf/Build/Products/Debug-iphonesimulator/libStaticLib.a is not a fat file
    Non-fat file: /Users/chiyou/Library/Developer/Xcode/DerivedData/StaticLib-aohnkijkogumceagdwbpcqbevzxf/Build/Products/Debug-iphonesimulator/libStaticLib.a is architecture: x86_64
    
    我们看到只有一种架构（not fat file），恰好符合我们的设置，那回到我们遗留的问题，是不是真机情况下`Build Active Architecture Only`设置为`YES`无效呢。我们似乎可以得出这样的结论。但真的是这样吗？我们先搁置一下。
    
 
6  设备选择模拟器`iPhone4s及以上`，将`Run`选为`Release`模式，点击`Run`.生成`Relese-iphonesimulator`，其中有`libStaticLib.a`文件。

    查看生成的.a文件的信息
    
    Architectures in the fat file: /Users/chiyou/Library/Developer/Xcode/DerivedData/StaticLib-aohnkijkogumceagdwbpcqbevzxf/Build/Products/Release-iphonesimulator/libStaticLib.a are: i386 x86_64 
    
假如release情况下`Build Active Architecture Only`也设置为YES，我们得到一种架构。

7 合并`release`模式下的`.a`文件


我们需要的包是能运行到任何设备上，不但运行在真机上而且能运行在模拟器上，但是我们可以看到无论生成的哪一种.a包的架构都是不完善的。所以我们要将`Release-iphoneos`和`Relese-iphonesimulator`情况下的.a文件进行合并，获得完整的架构。

假如我们`debug`模式下的`Build Active Architecture Only`设置为`NO`，合并那么生成的`.a`包也是架构完整的，也是可以用到我们的工程中的。

我认为它与`release`最终合并生成的`.a`文件的区别在于？

假如我们静态库源文件中的`.m`有宏定义`DEBUG`下的处理。那么`Release`模式会忽略这些处理。

     合并.a文件
     
     lipo -create /Users/chiyou/Library/Developer/Xcode/DerivedData/StaticLib-aohnkijkogumceagdwbpcqbevzxf/Build/Products/Release-iphoneos/libStaticLib.a /Users/chiyou/Library/Developer/Xcode/DerivedData/StaticLib-aohnkijkogumceagdwbpcqbevzxf/Build/Products/Release-iphonesimulator/libStaticLib.a -o ~/desktop/libStaticLib.a
     
     可以在桌面上找到我们生成的.a文件
     
     lipo -info ~/desktop/libStaticLib.a
     
     Architectures in the fat file: /Users/chiyou/desktop/libStaticLib.a are: armv7 armv7s i386 x86_64 arm64 
     
     可以看到我们生成的.a文件拥有所有的架构,可以运行在任何设备上.
     
     
小结:

其实我们只需要把`Build Active Architecture Only` 整个设置为`NO`，然后选择模拟器，运行一下，选择真机模式运行一下，将生成的`.a`文件合并到一起即可.



### 利用命令行生成.a文件

1 关于在`xcode`真机模式下，为什么`Build Active Architecture Only`为`YES`不起作用？

    cd进入工程文件夹
    $ xcodebuild -project StaticLib.xcodeproj -target StaticLib -sdk iphoneos -configuration Debug ONLY_ACTIVE_ARCH='YES' ARCHS='armv7 armv7s arm64' VALID_ARCHS='armv7 armv7s arm64'
    
    在工程文件夹中生成build文件夹,Debug-iphoneos下有.a文件
    
    $ lipo -info /Users/chiyou/Desktop/StaticLib/build/Release-iphoneos/libStaticLib.a
     
     input file /Users/chiyou/Desktop/StaticLib/build/Release-iphoneos/libStaticLib.a is not a fat file
     Non-fat file: /Users/chiyou/Desktop/StaticLib/build/Release-iphoneos/libStaticLib.a is architecture: armv7  
     
    
     ONLY_ACTIVE_ARCH即代表我们buildSetting中的`Build Active Architecture Only`，可以看到生成的.a文件只有一种架构。(release情况下也是如此)，那么由此回到我们遗留的问题，我猜测可能是由于xcode有bug，当真机情况下，选择`Build Active Architecture Only`为YES并没有起作用。
     
     ARCHS指的是我们选择真机情况下的架构
     VALID_ARCHS指的是我们选择真机情况下的有效的架构
     
     默认采用我们工程中的buildsetting中的设置，如果指定的话，就会覆盖我们工程中的设置。
     
2 `release`模式，选择真机的`.a`文件
    
    $ xcodebuild -project StaticLib.xcodeproj -target StaticLib -sdk iphoneos -configuration Release ONLY_ACTIVE_ARCH='NO' ARCHS='armv7 armv7s arm64' VALID_ARCHS='armv7 armv7s arm64'
    
    可以自己查看.a文件架构信息
    

3 `release`模式，模拟器
  
    $ xcodebuild -project StaticLib.xcodeproj -target StaticLib -sdk iphonesimulator -configuration Release ONLY_ACTIVE_ARCH='NO' ARCHS='i386 x86_64' VALID_ARCHS='i386 x86_64'
    
      可以自己查看.a文件架构信息
      
      模拟器的VALID_ARCHS和VALID_ARCHS默认即为'i386 x86_64'，所以后面两个参数可以不用设置
      
      
4 合并`.a`文件

     lipo -create /Users/chiyou/Desktop/StaticLib/build/Release-iphoneos/libStaticLib.a /Users/chiyou/Desktop/StaticLib/build/Release-iphonesimulator/libStaticLib.a -o ~/desktop/libStaticLib.a
     
     查看.a文件信息
     
     $ lipo -info /Users/chiyou/Desktop/libStaticLib.a 
     
     Architectures in the fat file: /Users/chiyou/Desktop/libStaticLib.a are: armv7 armv7s i386 x86_64 arm64
     
     
     

### 使用脚本生成.a文件

1 这是我写的脚本[autoLib](https://github.com/lhjzzu/autoLib)，你可以直接下载使用

2 cd进入静态库工程文件夹并且把`autoLib.py`放入其中
     
     $ python autobuild.py -t libStaticLib（工程名）
     
     如果执行成功
     
     ** BUILD SUCCEEDED **

     output: ~/desktop/libStaticLib.a
     
    会将生成的.a文件生成到桌面上
     
  
3 你可给`python autobuild.py -t`，配置一个别名，更方便使用。

    
    
 
## FAQ
 
### 为什么真机下`Build Active Architecture Only`为`YES`不起作用？

当我们采用命令行的时候真机模式下`Build Active Architecture Only`为`YES`是起作用的，所以猜测是xcode的bug

### 最终生成的.a,release模式和debug模式的区别?

我认为`.a`中的内容都是一样的，因为`.a`就是我们`.m`文件的集合，无论什么模式我们`.m`文件是不变的。所以它们之间的区别在与宏定义`DBUG`范围内的内容，在release下不做处理

### 假如我们的静态库某些类头文件被隐藏了，我们隐藏的头文件的信息在哪里？

我们可以查看我们.a文件中内部的信息

1 进入我们`libStaticLib.a`文件所在路径

2 生成只有一个架构信息的.a文件(例如:armv7),并输出到桌面

`$ lipo libStaticLib.a -thin armv7 -o ~/desktop/libStaticLib-armv7.a`

3 查看`libStaticLib-armv7.a`内部信息

 `$ ar -t ~/desktop/libStaticLib-armv7.a`
 
    __.SYMDEF
    StaticLib.o
    SecondStaticLib.o
我们可以看到除了`.o`文件外还多了一个`__.SYMDEF`文件，这不是一个通常意义的文本文件(不知道采用的什么编码),不能打开，无法查看里面的具体内容。所以我认为我们的隐藏的头文件的信息是放在`__.SYMDEF`.


### 假如我们的.a文件缺少架构(x86_64)，导入工程，并在iPhone6模拟器直接编译为什么成功？

我们可以看到，假设我们的.a文件没有`x86_64`架构,当我们把.a文件导入工程中后，在iPhone6模拟器直接编译成功。而当我们使用这个库的时候，在iPhone6模拟器编译，会报错缺少`x86_64`架构，那么我们可以得出在到工程编译的时候，假如我们的代码未使用这个`.a`文件，我们的编译过程就不会检查我们的`.a`文件是否有问题.

### 静态库依赖的问题?

假如有这样一个场景:我们要创建一个`B.a`静态库，但是我们的`B.a`依赖`A.a`，如果我们不想要把`A.a`文件打包到我们的`B.a`中。我们只需要导入`A.a`对应的.h文件即可。(实质上是只要`BuildPhase->Link Binary With Libraries中`不存在`A.a`即可)

### 静态库工程中Command+B检查文件是否存在以及是否重复?
 
文件的存在:
说回上一个问题:为什么只需导入`A.a`对应的`.h`文件即可？(下面所指的文件的索引必须在静态库工程中)

`#import "MyClass.h"`,这句话是导入我们的.h文件，所以在`Command+b`的过程中只是检查`.h`文件是否存在，就能保证编译通过。如果`.m`文件在`BuildPhase->Compile Source`中就会被编译，如果不存在那里就不会被编译.

**所以可以说检查某个类是否存在，就是检查.h文件是否存在。**


文件的重复:

1 假如我们在一个工程中通过`Command+n`创建新的文件，假如文件已经存在，那么会询问我们是否替换。这种情况当然不会存在文件重复的问题

2 假如我们工程中有`StaticLib.m`文件，我们导入`.a`文件也有`StaticLib.o`文件,那么我们编译的过程中会报`StaticLib.o`文件重复的问题. 假如`StaticLib.m`生成的`StaticLib.o`文件与在`.a`中`StaticLib.o`的内容是一样的，那么删除`StaticLib.m`文件即可

### 不同第三方.a冲突的处理?

一般而言是因为它们使用了同样的库，并且没有对库做任何处理，可以参考[这篇文章](http://www.ithao123.cn/content-767025.html)


## 参考


* [Build Setting Reference](https://developer.apple.com/library/mac/documentation/DeveloperTools/Reference/XcodeBuildSettingRef/1-Build_Setting_Reference/build_setting_ref.html#//apple_ref/doc/uid/TP40003931-CH3-SW105)
* [iOS 第三方库冲突的处理](http://www.ithao123.cn/content-767025.html)
* [ios打包--xcodebuild以及xcrun](http://www.lhjzzu.com/2016/04/29/ios-xcodebuild/)
     
  
  
 
  
  