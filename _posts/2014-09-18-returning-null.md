---
layout: post
title: 关于返回 Null 值的问题
description: 我感觉返回null值是有问题的，它大量的被使用在一个方法有不同的返回类型时。返回一个Null对象在某些情况下是合适的，但并不适合当你需要向客户端传送两种不同的东西的情形。
keywords: java, Null, 函数
categories : [java, reprints]
tags : [java, 技巧]
---

原文： [Returning Null](http://zdsbs.blogspot.com/2009/08/returning-null.html)

译文： [关于返回 Null 值的问题](http://www.aqee.net/returning-null/)

-------------------

我总感觉一个方法返回 `null` 值有问题。
当读了 Misko Hevery 关于 [how to think about OO](http://misko.hevery.com/2009/07/31/how-to-think-about-oo/)的博客文章后，又让我想起这个问题。

我感觉返回 `null` 值是有问题的，它大量的被使用在一个方法有不同的返回类型时。
简单的用谷歌搜索一下“returning null”，你就会发现有建议把返回类型做成一个null对象。
返回一个 `Null` 对象在某些情况下是合适的，但并不适合当你需要向客户端传送两种不同的东西的情形。

用 Misko 重构的一段代码来说明这个问题。
他重构的是一段登录代码(我非常喜欢他的过程)，这段代码大概是这个样子：

    Cookie login(Ldap ldap) {
        if ( ldap.auth(user, password) )
          return new Cookie(user);
        return null;
    }

从这段代码，可以看出两种情况(从结构上讲)

1. 如果认证通过, 客户端会被通知验证成功, 生成一个新的 Cookie
2. 如果认证失败, 则通过返回的null值通知客户端

客户端的方法应该是什么样的？

    public void authenticateUser(User user) {
        Cookie userCookie = user.login(ldap);
        if (userCookie == null) {
            //notify someone that auth failed
        } eles {
            //register them as logged in
        }
    }

我们在两个地方做了相同的事情，只是在语法上有稍微的不同，每个地方，我们都要检查验证是否成功。
如果我们使用 IoC（反向控制）模式，或“Tell Don’t Ask”模式或“Hollywood原则”，会如何？

    Cookie login(Ldap ldap, AuthenticationRegistry authenticationRegistry) {
        if ( ldap.auth(user, password) )
            authenticationRegistry.authSucceeded(new Cookie(user));
        authenticationRegistry.authFailed(user);
    }

客户端：

    public void authenticateUser(User user) {
        user.login(ldap,this);
    }

    public void authSucceeded(Cookie cookie) {
        //register them as logged in
    }

    public void authFailed(User user) {
        //register them as auth failed
    }

新代码稍微有点复杂，但我感觉它很清晰，实现的更直接。
现在我们的两个实体能够相互通信，我们定义了它们通信的方式。
我喜欢 Misko 的重构，我只是更进了一步。
好坏可以再讨论，但我想，如果你遇到了这种需要返回两种情况的方法时，IoC 是你应该的选择。
