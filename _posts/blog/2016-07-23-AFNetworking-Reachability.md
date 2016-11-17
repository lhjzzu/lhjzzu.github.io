---
layout: post
title: AFNetworking原理:Reachability(二)
date: 2016-07-21
categories: IOS

---

## AFNetworkReachabilityManager

### 主要作用
主要用于监听当前的网络状态，通过这个类客户端可以获取当前的网络状态。定义了一个`AFNetworkReachabilityStatus`的枚举类型，这个枚举类型的各个值，主要是根据系统的枚举类`SCNetworkReachabilityFlags`的值对应转化而来。

```
typedef NS_ENUM(NSInteger, AFNetworkReachabilityStatus) {
    AFNetworkReachabilityStatusUnknown          = -1,//未知网络
    AFNetworkReachabilityStatusNotReachable     = 0, //无网
    AFNetworkReachabilityStatusReachableViaWWAN = 1, //手机网络2G/3G/4G
    AFNetworkReachabilityStatusReachableViaWiFi = 2, //wifi
};


```




### 基本的属性和方法

```
属性

networkReachabilityStatus:枚举值，AFNetworkReachabilityStatus类型，当前网络的状态.
reachable:BOOL值，代表网络是否可用
reachableViaWWAN:BOOL值，当前网络是否是手机网络
reachableViaWiFi:BOOL值当前网络是否是wifi

方法

+ (instancetype)sharedManager; 单例方法
+ (instancetype)manager; 类初始化方法
+ (instancetype)managerForDomain:(NSString *)domain; 根据域名进行初始化
+ (instancetype)managerForAddress:(const void *)address; 根据socket地址进行初始化
- (instancetype)initWithReachability:(SCNetworkReachabilityRef)reachability 根据SCNetworkReachabilityRef进行初始化

- (void)startMonitoring; //开始监听
- (void)stopMonitoring;  //停止监听
- (void)setReachabilityStatusChangeBlock:(nullable void (^)(AFNetworkReachabilityStatus status))block; //设置回调的block，当网络状态改变的时候会进行调用

//将SCNetworkReachabilityFlags转化成AFNetworkReachabilityStatus类型
 AFNetworkReachabilityStatusForFlags(SCNetworkReachabilityFlags flags)
 
// 网络状态改变时调用这个方法，发出通知（AFNetworkingReachabilityDidChangeNotification）
AFPostReachabilityStatusChange(SCNetworkReachabilityFlags flags, AFNetworkReachabilityStatusBlock block)
 
//网络状态改变时，runloop回调这个方法，这个方法内部调用上面的AFPostReachabilityStatusChange()方法
AFNetworkReachabilityCallback(SCNetworkReachabilityRef __unused target, SCNetworkReachabilityFlags flags, void *info)



2个常量
AFNetworkingReachabilityDidChangeNotification:状态改变的通知
AFNetworkingReachabilityNotificationStatusItem:通知传递的字典的key，对应的值为当前网络的状态。

```


### 核心代码

通过系统的类`SCNetworkReachabilityRef`,`SCNetworkReachabilityFlags`来得到网络的状态。


#### 将SCNetworkReachabilityFlags转化成AFNetworkReachabilityStatus类型
```
static AFNetworkReachabilityStatus AFNetworkReachabilityStatusForFlags(SCNetworkReachabilityFlags flags) {
    BOOL isReachable = ((flags & kSCNetworkReachabilityFlagsReachable) != 0);
    BOOL needsConnection = ((flags & kSCNetworkReachabilityFlagsConnectionRequired) != 0);
    BOOL canConnectionAutomatically = (((flags & kSCNetworkReachabilityFlagsConnectionOnDemand ) != 0) || ((flags & kSCNetworkReachabilityFlagsConnectionOnTraffic) != 0));
    BOOL canConnectWithoutUserInteraction = (canConnectionAutomatically && (flags & kSCNetworkReachabilityFlagsInterventionRequired) == 0);
    BOOL isNetworkReachable = (isReachable && (!needsConnection || canConnectWithoutUserInteraction));

   AFNetworkReachabilityStatus status = AFNetworkReachabilityStatusUnknown;
    if (isNetworkReachable == NO) {
        //无网
        status = AFNetworkReachabilityStatusNotReachable;
    }
 #if	TARGET_OS_IPHONE
    else if ((flags & kSCNetworkReachabilityFlagsIsWWAN) != 0) {
        //手机网络
        status = AFNetworkReachabilityStatusReachableViaWWAN;
    }
 #endif
    else {
        //wifi
        status = AFNetworkReachabilityStatusReachableViaWiFi;
    }

    return status;
}

```

#### SCNetworkReachabilityRef的基本用法

1 SCNetworkReachabilityContext的结构

```
typedef struct {
	CFIndex		version;
	void *		__nullable info;
	const void	* __nonnull (* __nullable retain)(const void * info);
	void		( *  __nullable release)(const void * info);
	CFStringRef	__nonnull (* __nullable copyDescription)(const void *info);
} SCNetworkReachabilityContext;

```

* 第一个参数代表版本号
* 第二个参数接受一个void * 类型的值，做为上下文中传递的信息
* 第三个参数是一个函数 目的是对info做retain操作，
* 第四个参数是一个函数，目的是对info做release操作
* 第五个参数是一个函数，根据info获取Description字符串

2  设置SCNetworkReachabilityRef在runloop中回调函数

```
Boolean
SCNetworkReachabilitySetCallback		(
						SCNetworkReachabilityRef			target,
						SCNetworkReachabilityCallBack	__nullable	callout,
						SCNetworkReachabilityContext	* __nullable	context
						)		

```


* target:获取网络状态时，所要检查的目标
* callout:网络状态改变时，回调的block
* context:传入的上下文


3 将配置好的SCNetworkReachabilityRef，放入到runloop中


```

Boolean
SCNetworkReachabilityScheduleWithRunLoop	(
						SCNetworkReachabilityRef target,
						CFRunLoopRef			runLoop,
						CFStringRef			    runLoopMode
						
						）	
						
```


* target:获取网络状态时，所要检查的目标
* runLoop: runloop对象，一般为main runloop
* runLoopMode:值为kCFRunLoopCommonModes，通用的modes，即在任何情况下都能监测到网络的变化。



#### 在runloop中监测SCNetworkReachabilityRef的网络状态，并调用对应的回调函数



1 设置content

```
// content的*info
 __weak __typeof(self)weakSelf = self;
    AFNetworkReachabilityStatusBlock callback = ^(AFNetworkReachabilityStatus status) {
        __strong __typeof(weakSelf)strongSelf = weakSelf;

        strongSelf.networkReachabilityStatus = status;
        if (strongSelf.networkReachabilityStatusBlock) {
            strongSelf.networkReachabilityStatusBlock(status);
        }

 };

// 使*info引用计数增加的retain函数
static const void * AFNetworkReachabilityRetainCallback(const void *info) {
    return Block_copy(info);
}

//使*info引用计数减少的的release函数//
static void AFNetworkReachabilityReleaseCallback(const void *info) {
  if (info) {
        Block_release(info);
    }
}
SCNetworkReachabilityContext context = {0, (__bridge void *)callback, AFNetworkReachabilityRetainCallback, AFNetworkReachabilityReleaseCallback, NULL}; 

```



2 设置在runloop中的回调函数以及上下文

```
   // 传入定义好的AFNetworkReachabilityCallback回调函数,以及上下文context
    SCNetworkReachabilitySetCallback(self.networkReachability, AFNetworkReachabilityCallback, &context);
    

// 回调函数的定义
static void AFNetworkReachabilityCallback(SCNetworkReachabilityRef __unused target, SCNetworkReachabilityFlags flags, void *info) {
    //将context中的void *info，作为参数传递给AFPostReachabilityStatusChange，由context的定义知道
      //void *info即为AFNetworkReachabilityStatusBlock类型的block。
      
    AFPostReachabilityStatusChange(flags, (__bridge AFNetworkReachabilityStatusBlock)info);
}

// 调用block，并抛出通知
static void AFPostReachabilityStatusChange(SCNetworkReachabilityFlags flags, AFNetworkReachabilityStatusBlock block) {
    AFNetworkReachabilityStatus status = AFNetworkReachabilityStatusForFlags(flags);
    dispatch_async(dispatch_get_main_queue(), ^{
     //这个block即为context的*info参数
        if (block) {
            block(status);
        }
        NSNotificationCenter *notificationCenter = [NSNotificationCenter defaultCenter];
        NSDictionary *userInfo = @{ AFNetworkingReachabilityNotificationStatusItem: @(status) };
        [notificationCenter postNotificationName:AFNetworkingReachabilityDidChangeNotification object:nil userInfo:userInfo];
    });
}


```

3 将配置好的SCNetworkReachabilityRef，放入到runloop中


```
    SCNetworkReachabilitySchedulewithRunLoop(self.networkReachability, CFRunLoopGetMain(), kCFRunLoopCommonModes);
    

```

* target:获取网络状态时，所要检查的目标
* runLoop: runloop对象，一般为main runloop
* runLoopMode:值为kCFRunLoopCommonModes，通用的modes，即在任何情况下都能监测到网络的变化。




#### 移除runloop对监测SCNetworkReachabilityRef网络状态的监测

```
 SCNetworkReachabilityUnscheduleFromRunLoop(self.networkReachability, CFRunLoopGetMain(), kCFRunLoopCommonModes);


```






     
  
  
 
  
  