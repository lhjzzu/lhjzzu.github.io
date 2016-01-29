---
layout: post
title: SVPullToRefresh 详解
date: 2016-01-27
categories: blog


---

做ios开发一直在用SVPullToRefresh这个刷新框架，可是一直没有看过关于关于SVPullToRefresh内部的具体实现。最近看了一下，尚有一些没看懂，现在就已经看懂的部分来说，整理一下设计思路。


##### 一、 就框架结构而言
<font color = 'bb0000'>SVPullToRefresh</font>对**UISCrollView**做了两个扩展类。<font color = 'bb0000'>UIScrollView+SVPullToRefresh</font>和<font color = 'bb0000'>UIScrollView+SVInfiniteScrolling</font>

##### 二、 <font color = 'bb0000'>UIScrollView+SVPullToRefresh</font>的设计思路
  1. 设计整体思想 
  
	  在.h文件中,定义了一个**SVPullToRefreshView**类作为刷新的控件，并且给将这个控件添加到**UISCrollView**上。通过KVO，让**SVPullToRefreshView**对象作为观察者来观察**UISCrollView**的**frame**和**contentOffset**的变化，根据**frame**和**contentOffset**的变化来做出响应状态的改变。
	  
  2. UIScrollView (SVPullToRefresh)扩展的解析
  
 {% highlight ruby linenos %}
@interface UIScrollView (SVPullToRefresh)
- (void)addPullToRefreshWithActionHandler:(void (^)(void))actionHandler;
- (void)triggerPullToRefresh;
@property (nonatomic, strong, readonly) SVPullToRefreshView *pullToRefreshView;
@property (nonatomic, assign) BOOL showsPullToRefresh;
@end
 {% endhighlight %}
 
	   1 外部调用的- (void)addPullToRefreshWithActionHandler:(void (^)(void))actionHandler给UISCrollView添加刷新控件。
	   
	   2 调用- (void)triggerPullToRefresh ，用代码来触发刷新
	   
	   3 pullToRefreshView为只读属性，获取到刷新控件，方便调用刷新控件的方法或者改变刷新控件的某些状态。
	   
	   4 showsPullToRefresh是否显示刷新控件，默认为YES。
  



     
  
  
 
  
  