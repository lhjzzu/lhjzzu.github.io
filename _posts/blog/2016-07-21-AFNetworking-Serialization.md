---
layout: post
title: AFNetworking原理:Serialization(一)
date: 2016-07-21
categories: IOS

---

## AFURLRequestSerialization

其主要作用是为我们进行网络请求构建了一个配置好的NSMutableURLRequest。

### 主要的类

一 声明了两个C语言方法

 `AFPercentEscapedStrin`