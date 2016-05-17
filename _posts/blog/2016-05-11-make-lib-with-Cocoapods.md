---
layout: post
title: Cocoapods系列:使用Cocoapods制作静态库(三)
date: 2016-05-10
categories: IOS

---

## 为什么要用Cocoapods制作静态库呢？

我们本来就可以通过`xcode`来进行静态库，`Cocoapods`制作静态库主要是解决第三方冲突的问题。

当我们开发`sdk`的时候，假如我们的静态库中需要使用一个第三方库，我们把这个第三方库打包进我们的`lib`中，当别人在使用我们的`lib`，如果他的工程中也已经使用了这个第三方库，那么就会造成冲突。

假设现在有一个需求，我要开发一个`sdk`，其中的下载图片我想用`SDWebImage`。但是众所周知`SDWebImage`是一个非常常用的库，基本上大部分的App都会使用到。那么当我的`sdk`的`lib`中使用了`SDWebImage`后，如何保证它不和别人工程中的`SDWebImage`冲突?`重命名`这个第三方库的所有文件--这是唯一的解决方法。但是假如让我们一个一个文件的重命名这基本是一个不可能完成的任务，更何况还有库之间的依赖。`Cocoapods`给我们提供了解决方案，通过`Cocoapods`我们可以很方便的制作我们的静态库并且对第三方库进行重新命名。


## 使用Cocoapods创建lib


#### 创建工程

#### 执行命令`$ pod lib create VCocoapodsLib`，并回答四个问题

    What language do you want to use?? [ Swift / ObjC ]
    > ObjC

    Would you like to include a demo application with your library? [ Yes / No ]
     > Yes

    Which testing frameworks will you use? [ Specta / Kiwi / None ]
     > None

    Would you like to do view based testing? [ Yes / No ]
     > Yes
    What is your class prefix?
     > V
    
    
    
     [!] Invalid `Podfile` file: undefined method `inherit!' for #<Pod::Podfile:0x007fc4a5a4b660>. Updating CocoaPods might fix the issue.

    #  from /Users/chiyou/Desktop/VCocoapodsLib/Example/Podfile:7
    #  -------------------------------------------
    #    target 'VCocoapodsLib_Tests' do
    >      inherit! :search_paths
    #  
    #  -------------------------------------------
    如果出现上面的错误，只需在Example中打开Podfile文件并删除下面的内容即可
    
    target 'VCocoapodsLib_Tests' do
    inherit! :search_paths

    pod 'FBSnapshotTestCase'
    end
    
    

#### 打开VCocoapodsLib.podspec文件修改信息如下

     Pod::Spec.new do |s|
       s.name             = "VCocoapodsLib"
       s.version          = "0.1.0"
       s.summary          = "this is a demo for making a lib with cocoapods."

       s.description      = <<-DESC
     TODO: this is a demo for making a lib with cocoapods.
                       DESC

       s.homepage         = "/Users/chiyou/Desktop/VCocoapodsLib"
       s.license          = 'MIT'
       s.author           = { "lhjzzu" => "1822657131@qq.com" }
       s.source           = { :git => "/Users/chiyou/Desktop/VCocoapodsLib", 
       :tag => s.version.to_s }
       s.requires_arc = true
       s.platform     = :ios, '8.0'
       s.source_files = 'Pod/Classes/**/*.{h,m}'

       s.public_header_files = 'Pod/Classes/**/*.h'
       s.dependency 'SDWebImage'
     end

* 类库的源文件将位于`Pod/Classes`,资源文件位于`Pod/Assets`
* 可以修改`s.source_files`和`s.resource_bundles`来更换存放目录
* `s.public_header_files`用来公开的头文件的搜索位置
* `s.frameworks`和`s.libraries`指定依赖的SDK中的framework和类库
* `s.source`直接填工程夹文件所在路径
* `s.dependency`是必填的，不能没有依赖,否则这种方式就失去了意义(安装不通过)。



#### 进入Example文件夹，执行`pod install --verbose --no-repo-update`

#### 在工程中创建需要的源文件，并将源文件放到`Pod/Classes`中,如果有图片等资源文件，放到`Pod/Assets`中

####  进入Example文件夹，再次执行`pod install --verbose --no-repo-update`

#### 提交源码并打上标签

    $ cd /Users/chiyou/Desktop/VCocoapodsLib
    $  git add .
    $  git commit -m '0.1.0'
    $  git tag -a 0.1.0 -m '0.1.0' （标签要与podspec中的版本号一致）

#### 验证`.podspec文件`

    pod lib lint VCocoapodsLib.podspec  --allow-warnings --verbose
    --allow-warnings:忽略警告 --verbose:打印细节

#### 安装插件

`sudo gem install cocoapods-packager`安装插件

#### 打包

`pod package VCocoapodsLib.podspec  --library  --force`

- 其中`--library`指定打包成`.a`文件，如果不带上将会打包成`.framework`文件。`--force`是指强制覆盖
- 一般而言，我们先打包成`.framework`文件，来看看文件结构是否正确。
- 打包好的包使用的时候，第三方依赖库所需的`.framework`要导入到工程中

         例如AFNetworking需要导入SystemConfiguration.framework，MobileCoreServices.framework，security.framework，SDWebImage需要导入ImageIO.framework
- 如果打包的文件中使用分类(`UIView+Extesion`)文件，那么使用的时候要`target->build settings->Linking->other Linker Flags` 设置为`-ObjC`



这是我的工程[VCocoapodsLib](https://github.com/lhjzzu/VCocoapodsLibDemo),你可以下载进行参考.
我在`README.md`中说了一些使用这个库的注意事项.


注意:

 * 我遇到的问题是:当我们生成`.framework`文件查看文件结构是否正确时,当我们配置有的时候指定的公开的头文件并没有公开!当我们确认其他配置没有问题的时，这种情况下我们最好换一下版本号，然后重新打一个标签。再次生成`.framework`文件查看文件结构，一般可以解决问题。
 
 
* 步骤最好不要错，有的时候有一些扯淡的类似缓存的东西，所做的修改并没有在最终打包的`.framework`文件中显示出来.
 
* 如果遇到扯淡的类似缓存的问题，先参考第一步，如果不行，就把所有的工程全部删除，重新创建建立。
 
 
## 参考
* [使用CocoaPods开发并打包静态库](http://www.cnblogs.com/brycezhang/p/4117180.html)


     
  
  
 
  
  