---
layout: post
title: SDWebImage原理:Cache(一)
date: 2016-08-10
categories: IOS

---


## NSCache

### 概述

与NSMutableDictionary相似，NSCache对象是一个可变的集合，是用来存储键值对。NSCache提供了一些接口，来添加，移除objects，以及设置缓存的总成本(cost)和总数量。

NSCache与其他可变集合不同点在于:

* NSCache包含各种自动清除的策略来确保缓存不会使用太多系统的内存。如果其他应用需要内存，这些策略会从cache中移除一些objects,以尽可能的减少内存的占用。
* 不用lock这个cache对象，在不同的线程中都可以添加,移除和查询objects.

可以使用NSCache对象临时存储那些创建比较耗费性能(expensive)的临时数据。重用这些数据有助于改善性能，因为这些数据不用重新计算了。然而这些数据对应用而言不是关键的，如果内存紧张的会被废弃掉。如果某些数据被废弃掉，那么再次需要时就要重新计算。

### 相关API

* 添加和移除对象
 
        objectForKey:
        setObject:forKey:
        setObject:forKey:cost:
        removeObjectForKey:
        removeAllObjects

* 相关属性
   
        name:NSCache对象本身的名字
        totalCostLimit:缓存的所有对象最大的总成本
        countLimit:缓存的所有对象的最大数量。
        evictsObjectsWithDiscardedContent:是否自动清除可废弃的内容。默认是YES。
        
* NSCacheDelegate

        NSCache对象的代理所遵守的协议,协议方法cache:willEvictObject:在缓存的对象被移除时调用。

        

## NSFileManager

### 获取应用沙盒根路径

        NSString *homeDir=NSHomeDirectory();      
        NSLog(@"应用沙盒根目录路径: %@",homeDir); 
        
### 获取Documents目录路径

        NSString *documentDir = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, 
        NSUserDomainMask, YES) firstObject];
        NSLog(@"Documents目录路径: %@",documentDir); 

### 获取Library目录路径
         
        NSString *libraryDir = [NSSearchPathForDirectoriesInDomains(NSLibraryDirectory, 
        NSUserDomainMask, YES) firstObject];
        NSLog(@"library目录路径: %@",libraryDir);

### 获取Cache目录路径

        NSString *cacheDir = [NSSearchPathForDirectoriesInDomains(NSCachesDirectory, 
        NSUserDomainMask, YES) firstObject];
        NSLog(@"cache目录路径: %@",cacheDir);

### 获取Tmp目录路径

       NSString *tmpDir = NSTemporaryDirectory();
       NSLog(@"tmp目录路径:%@",tmpDir);
        
### 创建文件夹

       NSString *documentDir = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory,
       NSUserDomainMask, YES) firstObject]; 
       NSFileManager *fileManager = [NSFileManager defaultManager];
       NSString *testDir = [documentDir stringByAppendingPathComponent:@"test"];
       BOOL res=[fileManager createDirectoryAtPath:testDirectory 
       withIntermediateDirectories:YES attributes:nil error:nil];  
        if (res) {  
        NSLog(@"文件夹创建成功");  
           }else  
        NSLog(@"文件夹创建失败");}
        
        
* 创建文件夹的方法

         createDirectoryAtPath:withIntermediateDirectories:attributes:error:
         createDirectoryAtURL:withIntermediateDirectories:attributes:error:
       
         说明:在指定的路径下根据指定的attributes参数字典来创建目录，如果attributes为nil，那么对创建的目录的一系
         列属性(owner,group,permissions等等)使用默认的设置。如果attributes不为空，但是遗漏了某些属性没有
         设置，那么遗漏的属性也会采用默认的属性设置。
         
         1 permissions(权限)的设置与当前进程的umask(文件权限掩码)一致。
         2 owner ID被设置为进程的有效用户的id
         3 group ID被设置为父目录。
         
         path/url:创建的文件夹的路径
         createIntermediates:如果为YES，那么如果创建文件夹的中间路径不存在，就直接创建中间路径。
         如果为NO，那么如果中间路径不存在则创建失败
         attributes:指定新创建的目录以及创建的中间目录的文件属性。你通过attributes能设置文件的
         owner，group numbers,file permissions, modification date。如果attributes为nil，那么对
         创建的目录的一系、列属性使用默认的设置。如果attributes不为空，但是遗漏了某些属性没有设置，那么遗漏的
         属性也会采用默认的属性设置。         
         
### 获取某个文件夹下的所有内容

         NSString *documentDir = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory,
         NSUserDomainMask, YES) firstObject];
         NSArray *urlArr =  [fileManager contentsOfDirectoryAtURL:
         [NSURL URLWithString:documentDir] includingPropertiesForKeys:nil
         options:NSDirectoryEnumerationSkipsSubdirectoryDescendants  error:nil];
         NSLog(@"document目录下的内容路径",urlArr);  
         
 * 获取文件夹下所有内容文件夹的方法
 
         contentsOfDirectoryAtURL:includingPropertiesForKeys:options:error:
         
         说明:只能获取指定目录下的内容路径集合。该路径集合中并不包括，该目录下的子目录中的内容的路径。
         例如，该路径下有一个test目录，在test中有一个test.txt文件。该路径内容的路径集合，并不包括
         test.txt文件的路径。
         
         url:
         keys:
         mask:
         
         
         
         
         
         
         

         
         
         
       





