---
layout: post
title: AFNetworking原理:NSURLSession(四)
date: 2016-07-29
categories: IOS

---


## NSURLSession

### 基本介绍

NSURLConnection在iOS9被宣布弃用,苹果建议使用NSURLSession。AFNetworking的3.x版本也已经将NSURLConnection的相关内容去掉，使用NSURLSession来进行网络请求。


### NSURLSession的基本使用

1. 创建NSURLSession

        NSURLSession *session= [NSURLSession sessionWithConfiguration:[NSURLSessionConfiguration defaultSessionConfiguration] delegate:self delegateQueue:[[NSOperationQueue alloc] init]];


2. 根据NSURLSession对象创建任务(NSURLSessionTask)

        NSURLSessionDataTask *task = [session dataTaskWithURL:[NSURL URLWithString:@"http://www.baidu.com"]];


3. 执行task

        [task resume];
       
     
### NSURLSessionConfiguration


#### NSURLSessionConfiguration种类
用于创建会话的时候，进行会话配置，有三种方式

1. 默认的会话配置:

        + (NSURLSessionConfiguration *)defaultSessionConfiguration
        
        返回默认的配置，这实际上与NSURLConnection的网络协议栈是一样的，具有相同的共享NSHTTPCookieStorage，共享NSURLCache和共享NSURLCredentialStorage。
        

2. 临时的会话配置

        + (NSURLSessionConfiguration *)ephemeralSessionConfiguration;
        
        返回一个预设配置，没有持久性存储的缓存，Cookie或证书。这对于实现像"秘密浏览"功能的功能来说，是很理想的。


3. 后台会话配置

        + (NSURLSessionConfiguration *)backgroundSessionConfigurationWithIdentifier:(NSString *)identifier
        
        它会创建一个后台会话。后台会话不同于常规的，普通的会话，它甚至可以在应用程序挂起，退出，
        崩溃的情况下运行上传和下载任务。初始化时指定的标识符，被用于向任何可能在进程外恢复后台传输的守护进程提供上下文。



#### NSURLSessionConfiguration重要的属性 

##### General Properties

1. `identifier`: 后台会话配置的标识

2. `HTTPAdditionalHeaders`:用request发送的一个附加的头字典,可以理解为代替NSURLRequest的 `setValue:forHTTPHeaderField:`来告诉服务器有关客户端的附加信息。默认是nil


        这个属性可以给基于这个会话配置的所有的会话，制定附加的头。例如你可以设置 `User-Agent`，使你基于这个会话配置的每个会话的请求都自动添加上`User-Agent`. 一个NSURLSession对象被用来处理HTTP协议的各个方面，因此，你不应该修改下面的字段。
        Authorization ，Connection， Host， WWW-Authenticate 
        
        另外，如果你上传的body data是确定的(例如body是NSData类型)，你需要设置`Content-Length`的值。
        如果同样的头字段出现在这个字典和request对象中，那么以request对象中对应的值为准。


3. `networkServiceType`:对标准的网络流量，网络电话，语音，视频，以及由一个后台进程使用的流量进行了区分。大多数应用程序都不需要设置这个

4. `allowsCellularAccess`:在蜂窝网络下是否允许连接。

5. `timeoutIntervalForRequest`: 请求的超时时间

6. `timeoutIntervalForResource`:一个资源请求花费的最大时间

##### Cookie Policies

1. `HTTPCookieAcceptPolicy`:枚举类型，决定cookies什么时候应该被接受
    
         typedef NS_ENUM(NSUInteger, NSHTTPCookieAcceptPolicy) {
         NSHTTPCookieAcceptPolicyAlways,
         NSHTTPCookieAcceptPolicyNever,
         NSHTTPCookieAcceptPolicyOnlyFromMainDocumentDomain
         };
         NSHTTPCookieAcceptPolicyAlways:接受所有的cookies
         NSHTTPCookieAcceptPolicyNever:拒绝所有的cookies
         NSHTTPCookieAcceptPolicyOnlyFromMainDocumentDomain:仅仅接受来自main document domain的cookies


2. `HTTPCookieStorage`:cookies的存储类，NSHTTPCookieStorage类型，用于存储这个会话的cookies

3. `HTTPShouldSetCookies`:BOOL值，决定是否requests应该这个会话配置中取HTTPCookieStorage存储的cookies。默认是YES


##### Security Policies

1. `TLSMaximumSupportedProtocol`:当进行请求时，客户端支持的最大的TLS协议版本。

2. `TLSMinimumSupportedProtocol`:当进行请求时，客户端支持的最小的TLS协议版本。

3. `URLCredentialStorage`:是会话使用的证书存储，为认证挑战提供证书。默认情况下，NSURLCredentialStorage 的+ sharedCredentialStorage 会被使用使用，这与NSURLConnection是相同的


#####  Caching Policies

1. `URLCache`:这个URL cache为在会话中的requests提供已经缓存过的responses。

2. `requestCachePolicy`:一个枚举类，决定什么时间返回从cache中返回一个response。

        typedef NS_ENUM(NSUInteger, NSURLRequestCachePolicy)
        {
            NSURLRequestUseProtocolCachePolicy = 0,

            NSURLRequestReloadIgnoringLocalCacheData = 1,
            NSURLRequestReloadIgnoringLocalAndRemoteCacheData = 4, // Unimplemented
            NSURLRequestReloadIgnoringCacheData = NSURLRequestReloadIgnoringLocalCacheData,

            NSURLRequestReturnCacheDataElseLoad = 2,
            NSURLRequestReturnCacheDataDontLoad = 3,

            NSURLRequestReloadRevalidatingCacheData = 5, // Unimplemented
        };
        1 NSURLRequestUseProtocolCachePolicy
        
        指定被定义在 protocol implementation中缓存的逻辑，这个缓存逻辑被用于特定的URL加载请求。这是默认的网址加载请求的缓  
        存政策。如果缓存不存在，直接从服务端获取。如果缓存存在，会根据response中的Cache-Control字段判断下一步操作，如: 
        Cache-Control字段为must-revalidata, 则询问服务端该数据是否有更新，无更新的话直接返回给用户缓存数据，若已更新，则请
        求服务端.
        
        2 NSURLRequestReloadIgnoringLocalCacheData 
        
        忽略本地缓存数据，直接请求服务端.
        与NSURLRequestReloadIgnoringCacheData一样
        
        3 略本地缓存，代理服务器以及其他中介，直接请求源服务端.
        NSURLRequestIgnoringLocalAndRemoteCacheData
        
        4 NSURLRequestReturnCacheDataElseLoad
        有缓存就使用，不管其有效性(即忽略Cache-Control字段), 无则请求服务端.
        
        5 NSURLRequestReturnCacheDataDontLoad
        死活加载本地缓存. 没有就失败. (确定当前无网络时使用)
        
        6 NSURLRequestReloadRevalidatingCacheData
        缓存数据必须得得到服务端确认有效才使用(貌似是NSURLRequestUseProtocolCachePolicy中的一种情况)
        
        Tips: URL Loading System默认只支持如下5中协议: 其中只有http://和https://才有缓存策略.
        (1) http:// (2) https:// (3) ftp:// (4) file:// (5) data://


##### Supporting Background Transfers


1. `sessionSendsLaunchEvents`:BOOL值，指定是否后台传输完成之后，启动或唤醒app。

2. `discretionary`:一个BOOL值，决定后台任务是否能够为了系统最优性能，而被自由安排。


##### Supporting Custom Protocols

1. `protocolClasses`:一组额外的协议，用于在会话中处理请求。

##### Supporting Custom Protocols


1. `HTTPMaximumConnectionsPerHost`:并发连接主机的最大数量，是 Foundation 框架中URL加载系统的一个新的配置选项。它曾经被用于NSURLConnection管理私人连接池。现在有了NSURLSession，开发者可以在需要时限制连接到特定主机的数量

2. `HTTPShouldUsePipelining`:也出现在NSMutableURLRequest，它可以被用于开启HTTP管道，这可以显着降低请求的加载时间，但是由于没有被服务器广泛支持，默认是禁用的

3. `connectionProxyDictionary`:包含会话中的代理的信息的字典。指定了会话连接中的代理服务器。同样地，大多数面向消费者的应用程序都不需要代理，所以基本上不需要配置这个属性关于连接代理的更多信息可以在 CFProxySupport Reference 找到。



### NSURLSession的代理

#### 各个代理之间的关系示意图

![](http://7xqijx.com1.z0.glb.clouddn.com/NSURLSessionDelegate.png?imageView/2/w/800)
   
#### NSURLSessionDelegate

* URLSession:didBecomeInvalidWithError:
   
        会话接收的最后一个消息。会话会变无效，因为系统性的错误或者明确的被指定无效，在这种情况下error的值为nil。

* URLSession:didReceiveChallenge:completionHandler:

        当一个认证挑战连接发生的时候，这个代理将给客户端一个机会去提供身份验证凭证（authentication 
        credentials）。如果没有实现将执行默认的处理
        (NSURLSessionAuthChallengePerformDefaultHandling)。
       
* URLSessionDidFinishEventsForBackgroundURLSession:

        如果应用收到`-application:handleEventsForBackgroundURLSession:completionHandler:`的消息，
        这个代理方法将收到这个消息用以表明:该会话中，所有过去队列化的消息已经被交付。此时去调用
        completionHandler或者去进行内部更新后调用completionHandler都是安全的。

#### NSURLSessionTaskDelegate

* URLSession:task:willPerformHTTPRedirection:newRequest:completionHandler:

        重定向一个不同的URL上。传递修改好的Request去执行completionHandler去允许重定向。或者传递nil给
        completionHandler不允许重定向。

* URLSession:task:didReceiveChallenge:completionHandler:

        当一个认证挑战连接发生的时候，这个代理将给客户端一个机会去提供身份验证凭证（authentication 
        credentials）。如果没有实现将执行默认的处理
        (NSURLSessionAuthChallengePerformDefaultHandling)。

* URLSession:task:needNewBodyStream:

        当因为某一请求的body stream而造成身份验证失败的时候，可能需要传递一个新的body stream.

* URLSession:task:didSendBodyData:totalBytesSent:totalBytesExpectedToSend:

        bytesSent:这次发送的数据长度
        totalBytesSent:已经发送的数据总长度
        totalBytesExpectedToSend:期望发送的数据的总长度

        周期性的去通知代理数据上传的进度
        
* URLSession:task:didFinishCollectingMetrics:

        当完成收集统计信息后调用。
        
* URLSession:task:didCompleteWithError:

        一个特定任务调用的消息，如果error为nil，表明没有错误发生并且任务已经完成。
        对于这个error的官方定义:服务器的错误不会通过这个error进行报告。这个error是客户端这边的错误，
        例如不能解析域名或连接主机。

        注意:如果我们网络连接是正常的，但是进行请求的时候，会报网络未连接的错误，而且服务端并没有收到我们的请
        求。这是因为服务器不稳定，客户端进行连接的时候不能解析域名或连接到主机。
        
        
#### NSURLSessionDataDelegate

* URLSession:dataTask:didReceiveResponse:completionHandler:

        将NSURLSessionResponseDisposition的值传递给completionHandler进行回调，来控制任务的行为.
        
        typedef NS_ENUM(NSInteger, NSURLSessionResponseDisposition) {
            NSURLSessionResponseCancel = 0,   
            NSURLSessionResponseAllow = 1,  
            NSURLSessionResponseBecomeDownload = 2, 
            NSURLSessionResponseBecomeStream  = 3, 
         }  
            
         NSURLSessionResponseCancel:取消response的载入，同[task cancel].
         NSURLSessionResponseAllow:允许response的载入.
         NSURLSessionResponseBecomeDownload:把该request变为download task.
         NSURLSessionResponseBecomeStream:把该request变为stream task.


* URLSession:dataTask:didBecomeDownloadTask:

        通知这个data Task已经变成download task。
   
* URLSession:dataTask:didBecomeStreamTask:

        通知这个data Task已经变成stream task。

* URLSession:dataTask:didReceiveData:

        通知代理此次已经接收到的data。


* URLSession:dataTask:willCacheResponse:completionHandler:

        将NSCachedURLResponse传递给completionHandler进行回调，去缓存响应的数据。或者传递nil，不去缓存。



#### NSURLSessionDownloadDelegate

* URLSession:downloadTask:didFinishDownloadingToURL:

        当下载任务完成的时候被调用，这个代理将把这个文件从被给的位置copy或者移动一个新的位置。因为这个文件将
        被移除，当这个代理消息返回的时候。 `URLSession:task:didCompleteWithError:`仍然会被调用


* URLSession:downloadTask:didWriteData:totalBytesWritten:totalBytesExpectedToWrite:

        bytesWritten:这次写入的数据长度
        totalBytesWritten:已经写入的数据总长度
        totalBytesExpectedToWrite:期望写入的数据的总长度
        
        周期性的通知下载的进度


* URLSession:downloadTask:didResumeAtOffset:expectedTotalBytes:

        当一个下载任务已经被恢复的时候调用，如果一个下载任务因出错而失败，这个error中的userInfo字典中的
        NSURLSessionDownloadTaskResumeData对应的value，即为resume data。




#### NSURLSessionStreamDelegate

* URLSession:readClosedForStreamTask:

        表明数据流的连接中读数据的一边已经关闭。


* URLSession:writeClosedForStreamTask:

        表明数据流的连接中写数据的一边已经关闭。

* URLSession:betterRouteDiscoveredForStreamTask:
     
        系统已经发现了一个更好的连接主机的路径

* URLSession:streamTask:didBecomeInputStream:outputStream:

        被给的task已经完成，并且从底层的网络连接中创建inputStream，outputStream。这将在所有队列化的I/O
        被完成后调用，此后这个streamTask将不接受任何代理消息。



### NSURLSessionTask

#### 各个Task之间的继承关系

![](http://7xqijx.com1.z0.glb.clouddn.com/NSURLSessionTask.png?imageView/2/w/850)

#### NSURLSessionTask属性和方法

* `taskIdentifier`:任务标识
* `originalRequest`:最初的Request
* `currentRequest`:当前的Request，有可能和最初的不同
* `response`:如果没有收到response，值为nil
* `countOfBytesReceived`:已经接收的字节数
* `countOfBytesSent`:已经发送的字节数
* `countOfBytesExpectedToSend`:被期望发送的字节数
* `countOfBytesExpectedToReceive`:期望接收的字节数
* `state`:任务的状态

        typedef NS_ENUM(NSInteger, NSURLSessionTaskState) {
            NSURLSessionTaskStateRunning = 0,                     
            NSURLSessionTaskStateSuspended = 1,
            NSURLSessionTaskStateCanceling = 2,                
            NSURLSessionTaskStateCompleted = 3,                 
        }
        
        NSURLSessionTaskStateRunning:任务处于正在执行状态
        NSURLSessionTaskStateSuspended:任务处于被挂起状态
        NSURLSessionTaskStateCanceling:任务处于被取消状态，将调用URLSession:task:didCompleteWithError:方法
        NSURLSessionTaskStateCompleted:任务处于已经完成状态
        

* `state`:任务的状态
* `priority`:优先级.

        NSURLSessionTaskPriorityDefault
        NSURLSessionTaskPriorityLow
        NSURLSessionTaskPriorityHigh
   
   
### NSURLSession创建Task

#### NSURLSessionDataTask

* dataTaskWithRequest:
* dataTaskWithURL:
* dataTaskWithRequest:completionHandler:
* dataTaskWithURL:completionHandler:

#### NSURLSessionUploadTask

* uploadTaskWithRequest:fromFile:
* uploadTaskWithRequest:fromData:
* uploadTaskWithStreamedRequest:
* uploadTaskWithRequest:fromFile:completionHandler:
* uploadTaskWithRequest:fromData:completionHandler:


#### NSURLSessionDownloadTask

* downloadTaskWithRequest:
* downloadTaskWithURL:
* downloadTaskWithResumeData:
* downloadTaskWithRequest:completionHandler:
* downloadTaskWithURL:completionHandler:
* downloadTaskWithResumeData:completionHandler:

#### NSURLSessionStreamTask

* streamTaskWithHostName:port:
* streamTaskWithNetService:



## AFURLSessionManager

### 基本结构图


![](http://7xqijx.com1.z0.glb.clouddn.com/NSURLSessionManager.png?imageView/2/w/850)


### AFURLSessionManagerTaskDelegate 


* AFURLSessionManagerTaskDelegate作为task的管理者，每一个task有一个对应的管理者
* 它监控着task的发送或接收数据的进度
         
        uploadProgress/downloadProgress，
        countOfBytesReceived
        countOfBytesExpectedToReceive
        countOfBytesSent
        countOfBytesExpectedToSend
        fractionCompleted
    
* 它遵守协议`NSURLSessionTaskDelegate`, `NSURLSessionDataDelegate`, `NSURLSessionDownloadDelegate`，并实现了下面3个协议方法。
    
        在AFURLSessionManager对应的代理方法中，调用AFURLSessionManagerTaskDelegate的代理方法
                
        1 URLSession:dataTask:didReceiveData:
        
          通过该方法收集请求得到的data（即self.mutableData）。
          
        2 URLSession:downloadTask:didFinishDownloadingToURL:
        
          通过外界定义的AFURLSessionDownloadTaskDidFinishDownloadingBlock生成，
          下载完成后文件的目的路径(self.downloadFileURL)
        
        
        3 URLSession:task:didCompleteWithError:
        
         如果普通任务没有发生错误，那么就用AFURLSessionManager的responseSerializer对data进行数据
         生成JSON数据responseObject，然后通过self.completionHandler将responseObject回调出去。
         
         如果下载任务没有发生错误，那么就用self.downloadFileURL即为responseObject，
         然后通过self.completionHandler将responseObject回调出去。    
        
        
        
### AFURLSessionManager核心源码
        
        








