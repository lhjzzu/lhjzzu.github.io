---
layout: post
title: Cocoapods系列:一个社会化SDK(四)
date: 2016-09-29
categories: IOS

---

## 前言

我们在做应用的时候，经常要集成第三方登录和分享这些功能，主要有微信，QQ，微博这三个社交平台。如果我们一个一个的进行集成无疑工作量是挺大的，而且即便是我们曾经集成过，并且把这些社交功能的代码封装的很好，要把原来的代码集成过来也是要做一些配置的。那么这时我们可以用cocoapods来管理我们封装好的社交功能的代码，也即是做一个社会化的组件。例如，友盟这样的组件用起来就很方便，但是我们不知道它内部的实现，并且有什么问题的话，还要依赖于它的更新。那为什么不做一个自己的组件呢？我做了一个社交组件`VSocial`，里面只是简单集成了微信，QQ，微博这三个平台的登录和分享功能，提供出来，仅供参考。(当然我们还是不鼓励重复造轮子，但是真正自己独立做出一个组件的时候，对个人的提升还是很有帮助的)


## 基本结构

如下图所示:

![](http://7xqijx.com1.z0.glb.clouddn.com/VSocial.png)


* 其核心主要包括`VSocial`,`VTencentSocialManager`,`VWeiXinSocialManager`,`VWeiBoSocailManager`这几个管理类.
* `VTencentSocialManager`,`VWeiXinSocialManager`,`VWeiBoSocailManager`是分别用来管理QQ,微信,微博的相关操作，内部封装的对应的sdk的相关逻辑。
* `registerWithAppId:`来进行应用注册。所传入的appId是从info.plist文件的URL Types中设置对应的scheme。
* `handleOpenURL:withCompletion:`qq通过URL启动App时来传递数据。
* `qqSocialWithReq:withType:withCompletion`调起登录/分享
*  `VSocial`的`registerSocailApp`内部调用了QQ，微信，微博的`registerWithAppId:`方法，它会去读`info.plist`中填入的对应的`scheme`。
*  `VSocial`的`handleOpenURL:withCompletion`方法，其内部根据url的scheme来分别调用QQ，微信，微博的`registerWithAppId:`方法。
*  `VSocial`的`socialWithReq:withType:withCompletion`方法，根据传入的req和type来进行不同应用的登录分享操作.

## 数据类型

**1 VSocialAction**

    /**
     *  操作指:登录和分享
     */
    typedef NS_ENUM(NSInteger, VSocialAction) {
        VSOCIALACTION_LOGIN = 0, //登录
        VSOCIALACTION_SHARE      //分享
    };

**2 VSocialActionType**

    typedef NS_ENUM(NSInteger, VSocialActionType) {
        VSOCIALACTIONTYPE_WB = 100,    //微博
        VSOCIALACTIONTYPE_WX = 101,    //微信
        VSOCIALACTIONTYPE_FRIEND= 102, //朋友圈
        VSOCIALACTIONTYPE_QQ = 103,    //qq
        VSOCIALACTIONTYPE_ZONE= 104,   //qq空间
        VSOCIALACTIONTYPE_COPY= 105,   //复制链接
        VSOCIALACTIONTYPE_UNKNOW= 106  //未知类型
    };


**3 VSocialActionStatus**

    typedef NS_ENUM(NSInteger, VSocialActionStatus) {
        VSOCIALACTIONSTATUS_SUCCESS = 1000, //操作成功
        VSOCIALACTIONSTATUS_CANCEL = 1001,  //操作取消
        VSOCIALACTIONSTATUS_FAILURE = 1002, //操作失败
        VSOCIALACTIONSTATUS_INVAILD = 1003  //操作错误（调起组件时）
    };

**4 VSocialActionReq** 

```
@interface VSocialActionReq : NSObject
/**
 * 在开放平台注册生成的appSecret（微信登录需要传入）
 */
@property (nonatomic,copy) NSString *appSecret;
/**
 *  如果登录微博的时候要传入redirectURI（微博开放平台:应用信息->高级信息->授权回调页）
 */
@property (nonatomic,copy) NSString *redirectURI;
/**
 *  操作(登录或分享,默认为登录)
 */
@property (nonatomic, assign) VSocialAction action;
/**
 *  分享页面的链接（如果是登录，不用传入）
 */
@property (nonatomic,copy) NSString *shareURL;
/**
 *  分享的图片的链接（如果是登录，不用传入）
 */
@property (nonatomic,copy) NSString *shareImgUrl;


/**
 * 分享的内容（如果是登录，不用传入）
 */
@property (nonatomic,copy) NSString *shareText;
/**
 *  分享的标题（如果是登录，不用传入）
 */
@property (nonatomic,copy) NSString *shareTitle;

@end

```

**5 VSocialCompletion**

```
/**
 *  操作完成的回调
 *
   msg:      操作后返回的信息
   type:     按钮的类型
   status:   操作后返回的状态
   infoDic:  社交应用返回的信息
 *
 */
typedef void(^VSocialCompletion) (NSDictionary *infoDic,VSocialActionType type,VSocialActionStatus status,NSString *msg);

```


## 网络请求

微信登录时需要发送请求来获取相关信息，分享时需要下载图片(只提供了图片链接分享)，所以封装了`VNetworkManager.framework`,其内部封装了请求数据和下载图片的两个方法。而这两个方法的实现中是封装的`AFNetworking`，以及`SDWebImage`.如何封装请参考[Cocoapods系列:使用Cocoapods制作静态库(三)](http://www.lhjzzu.com/2016/05/10/make-lib-with-Cocoapods/)


## UI界面

**1 登录界面**

* `UIView+VLoginSocial`对UIView进行了扩展,提供`v_showSocialLoginViewWithFrame:withCompletion:`方法来进行登录视图的调用

![](http://7xqijx.com1.z0.glb.clouddn.com/login.png?imageView/2/w/300)



**2 分享界面**

* `UIViewController+VShareSocial`对UIViewController进行了扩展,提供`v_showSocialShareViewWithReq:withCompletion:`方法来进行登录视图的调用.

![](http://7xqijx.com1.z0.glb.clouddn.com/share.png?imageView/2/w/300)


## 使用

已经添加了pods支持，具体的使用--请参考[VSocial](https://github.com/lhjzzu/VSocial)，我已经在README.md中将其用法说的非常详细了.

## 扩展

同样的做了一个支付的组件[VPay](https://github.com/lhjzzu/VPay)，集成了微信支付，支付宝支付，和银联支付，其内部的架构和`VSocial`是一样的，有兴趣可以看一下。



## 参考

* [Cocoapods系列:使用Cocoapods制作静态库(三)](http://www.lhjzzu.com/2016/05/10/make-lib-with-Cocoapods/)


     
  
  
 
  
  