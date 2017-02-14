---
layout: post
title: RunLoop:文档翻译(一)
date: 2016-10-15
categories: IOS

---

## Run Loops
RunLoop是与线程关联的基本结构的一部分。runloop是一个事件处理循环，用于安排任务和协调接收即将到来的事件。一个runloop的目的是当有任务要处理时保持你的线程繁忙，当没有任务时让它休眠。

runloop的管理并不是完全自动的。你仍然需要设计你的代码用来在一个合适的事件下开启runloop和响应即将到来的事件。Cocoa和Core Foundation都提供runloop对象来帮助你配置和管理你线程的runloop。你的应用不需要明确的的创建这些对象。每次线程(包括主线程)都有一个关联的runloop对象。仅仅辅助线程(主线程之外的线程)需要明确的去运行它们的runloop。在主线程上，作为应用启动进程的一部分，应用框架会自动设置和运行runloop。

下面的部分为runloop提供更详细的信息以及如何为你的应用配置runloop。更多详细的信息，请参考`NSRunLoop`和`CFRunLoop`.

## Anatomy of a Run Loop

顾名思义，runloop是线程进入和响应将要到来的事件处理的一个循环。你的代码提供了用于实现runloop实际循环部分的控制语句。在你的runloop中，你使用一个runloop对象来执行事件处理代码，接收事件并调用安装好的处理。

runloop接收两种不同source的事件。input sources 发送异步事件，通常消息来自另一线程或者不同的应用。Timer sources发送同步事件，事件发生在一个预定的时间或重复的时间间隔。当事件到达的时候，这两种类型的source都使用一个指定的处理程序来执行事件。

图3-1 展示一个runloop的结构和各种sources。input source 发送异步事件给对应的处理，并调用runUntilDate:(NSRunLoop对象来调用)方法在未来的某个日期退出。Timer sources发送事件给它们的处理程序，但是不造成runloop退出。

![](http://7xqijx.com1.z0.glb.clouddn.com/runloop-3-1.png?imageView/2/w/800)


除了处理input source, runloop也生成关于runloop行为的通知。被注册的runloop的观察者能够接收到这些runloop通知，并在线程上使用这些通知去做额外的处理。在你的线程上，你能使用Core Foundation去安装runloop的observers。

接下来的部分提供了关于runloop的组成的更详细的信息，以及操作时的model。也描述了在处理事件期间产生的不同的通知。

### Run Loop Modes

一个runloop的mode是被监控的input sources，timers和被通知的observers的集合。每一次运行runloop，你需要指定一个mode。在runloop运行的过程中，仅仅与该mode关联的的sources被监控，被允许去传递它们的事件。(类似的，仅仅与该mode关联的observers被runloop通知)。与其他mode关联的source持有新的事件直到runloop运行在一个对应的mode上。

在你的代码中，你通过名称来识别modes。在Cocoa和Core Foundation中都定义了一个默认的mode和一些通常使用的mode。在你的代码中，使用这些mode对应的字符串来指定mode。你能定义一个自定义的mode，通过简单的指定一个自定义的字符串作为mode的名字。虽然你指定给自定义mode的名字是随意的，但是mode的内容不是随意的。你必须确保给你创建的自定义mode添加一个或多个input source, timers 或 observers,以使你创建的mode有效。

在runloop运行的过程中，你可以使用modes去过滤你不想要的sources的事件。大部分的时间，你会运行你的runloop在系统定义的`default`的mode下。一个ModalPanel(与OS X相关)可以运行在`modal`mode下，当在这个mode中时，仅仅与Modal Panel相关的source能给线程发送事件。在时间严格的操作过程中，对于辅助线程，你可以使用自定义的modes去阻止低优先级的source发送事件。

 注意: modes是基于事件的source来区分的，而不是通过事件的类型来区分。例如，你不能使用modes来匹配鼠标事件或者键盘事件，你可以使用modes去监听不同的端口，临时暂停timers，或者改变sources，observers。

表3-1 列举了被Cocoa和Core Foundation定义的标准的modes，以及对应mode的描述，并列举了在你代码中指定对应mode时所需的常量。

```
表3-1 预定义的runloop mode

1. Default: NSDefaultRunLoopMode (Cocoa), kCFRunLoopDefaultMode (Core Foundation)
     大部分操作默认的mode，大部分时间，你应该使用这个mode区开启你的runloop，配置你的sources
  
2. Connection: NSConnectionReplyMode (Cocoa)
     Cocoa使用这个mode监听NSConnection对象的回复。你很少会使用到这个mode。
3. Modal:NSModalPanelRunLoopMode (Cocoa)
     Cocoa使用这个mode去识别用于modal pannels的事件(os x)
4. Event tracking: NSEventTrackingRunLoopMode (Cocoa)
     Cocoa使用这个mode去限制即将到来的事件--在鼠标拖动或其他类型的用户界面滑动期间。
5. Common modes: NSRunLoopCommonModes (Cocoa) kCFRunLoopCommonModes(Core Foundation)
     这是一个通用modes的配置组，可以理解为runloop mode的集合。将一个input source与这个mode关联，也就是把input source与这个组中的每一个mode关联。对于Cocoa应用，这个集合默认包括defaut,modal以及 event tracking modes。Core Foundation最初仅仅包括default mode。你可以使用CFRunLoopAddCommonMode函数添加自定义mode到这个集合中。
 
```

### Input Sources

input sources 发送异步事件给你的线程。事件的source是基于input source的类型的，input source分为两类。
`Port-Based Sources`监听应用的Mach端口。`Custom Source`监听自定义源的事件。这两种sources唯一的不同是怎样发送信号。`Port-based sources`是基于内核自动发送信号，`custom sources`必须从另一个线程手动发送信号。

当你创建一个input source时，你把它指派给runloop中的一个或多个mode。mode中的input source时刻被监控。大部分时候，你的runloop运行在一个default mode下，但你也可以指定自定义的model。如果一个input source不在当前被监控的mode里，它产生的任何事件都被保持，直到runloop运行在对应的mode下运行。

接下来的部分描述了一些input sources。

#### Port-Based Sources
Cocoa和Core Foundation通过使用与端口相关的对象和函数，为创建基于端口的input sources提供内置的支持。例如，在Cocoa中，你不需要直接创建一个input source。你简单的创建一个port对象并且使用NSPort的方法添加这个port到这个runloop中。这个port对象为你处理所需要的input source的创建和配置。

在Core Foundation中，你必须手动的创建port和它的runloop source。在这两种情况下，你使用与port类型相关的函数来创建合适的对象。

对于如何设置和配置自定义的`port-based sources`,  请参见下面的`Configuring a Port-Based Input Source`。

#### Custom Input Sources

创建一个自定义的input source，你必须使用在Core Foundation中与CFRunLoopSourceRef类型相关联的函数。你使用一些回调函数来配置一个自定义的input source。 Core Foundation在不同的阶段调用这些函数来配置这个source，处理
将要到来的事件，并销毁这个source--在它将要从runloop中移除的时候。

当一个事件到达时，除了定义这个自定义source的行为之外，你还必须定义这个事件的发送机制。这个source的一部分运行在一个单独的线程，负责为input source提供数据，当数据准备好的时候，给它发送信号。事件的发送机制取决于你自己，但是不要过于复杂。？？？？这段的理解

对于如何创建一个自定义的input source，参见下面的`Defining a Custom Input Source.`


#### Cocoa Perform Selector Sources

除了` port-based sources`，Cocoa定义了一个自定义的input source允许你在任何一个线程执行一个方法。和` port-based sources`一样，执行方法的请求被序列化在目标线程中，减少了许多同步问题。与`port-based sources`不同，一个`perform selector source`在执行完方法后，从runloop中移除它自己。				
注意:在OS X v10.5之前， `perform selector sources`主要用于给主线程发送消息，但是在OS X v10.5(包括)以后和ios中，你能使用它们给任何线程发送消息。

当在另一个线程执行一个selector时，目标线程必须有一个活的runloop(也就是说执行selector的线程必须有有一个在运行的runloop)。对于你创建的线程，这意味着这个selector等待执行，直到你明确的运行目标线程的runloop。主线程自己自动 开启runloop，一旦应用调用`applicationDidFinishLaunching:`方法，你就可以在主线程分配调用selector。每一次runloop循环，runloop处理所有队列化的perform selector。而不是在每次runloop期间只处理一个perform selector。

```

表3-2 列举了`perform selectors`的相关方法。这些方法实际上并没有创建一个新的线程去执行selector。

1. 在该线程下一个runloop循环期间，在主线程中执行指定的selector。这些方法给你一个选择：是否阻塞当前线程直到这个selector被执行。
   performSelectorOnMainThread:withObject:waitUntilDone:
   performSelectorOnMainThread:withObject:waitUntilDone:modes:

2. 在任何线程执行指定的selector。这些方法给你一个选择：是否阻塞当前线程直到这个selector被执行。
   performSelector:onThread:withObject:waitUntilDone:
   performSelector:onThread:withObject:waitUntilDone:modes:
   
3. 在下一个runloop循环期间以及一个延迟时间之后，在当前线程执行一个指定的selector。由于它等待直到下一个runloop循环才去执行，这些方法也提供了一个距离当前正在执行的代码的延迟时间(延迟时间过完执行selector)。多个被队列化的selector按照入队的顺序一个一个被执行。
   performSelector:withObject:afterDelay:
   performSelector:withObject:afterDelay:inModes:
   
4. 使你能够取消使用`performSelector:withObject:afterDelay:`或`performSelector:withObject:afterDelay:inModes:`方法发送给当前线程的消息.
   cancelPreviousPerformRequestsWithTarget:
   cancelPreviousPerformRequestsWithTarget:selector:object:
   
```

更多详细的使用，参见`NSObject`

### Timer Sources

在将来的预设的时间时，Timers sources发送同步事件给你的线程。对于线程来说，timers是一个方式--通知自己去做一些事的。例如:一个搜索栏能够使用一个timer来启动一个自动搜索，一旦从用户输入开始过去了一定的时间，就可以自动搜索。这个间隔时间给用户一个机会，在搜索之前输入自己想要搜索的内容。

尽管它产生一个基于时间的通知，但是timer并不是实时机制。和input source一样，timers与runloop中对应的mode相关联。如果timer不在runloop的当前被监控的mode内，那么它不会触发直到runloop运行在timer支持的mode内。类似的，如果当runloop正在执行处理程序的时候，这个timer触发。此时timer等待直到下一次执行runloop循环去调用它的处理程序。如果runloop就没有运行，那么timer就不会触发。

你能设置timers只生成一次事件还是重复生成。一个重复的timer基于已经预先设定的触发时间自动的重新设置它自己的触发时间，而不是基于实际的触发时间。例如:一个timer被预先设定在一个特定的时间去触发，然后每5s触发一次。这个预先设定的触发时间将总是落后原来时间5s钟，即使实际触发的时间被延迟。如果触发时间延迟了很多次--它错过了一个或多个预先设定的时间。定时器仅仅为这段错过的时间触发一次，然后timer依据此次触发的时间，来设置下一次触发的预设时间。

对于更多配置timer sources的信息，请参考`Configuring Timer Sources`，`NSTimer`，`CFRunLoopTimer`。

### Run Loop Observers

当一个适当的同步或异步事件发生时，sources触发。与之相反，在runloop运行期间，runloop observers 在一个特定的位置触发。 你可以用observers来使你的线程为要执行的事件做好准备，或者在你的线程将要休眠之前为线程的休眠做好准备。在runloop，你可以将observers于下列的事件关联在一起。

* 当进入运行循环时
* 当这个runloop将要去执行一个timer时
* 当这个runloop将要执行一个input sources时
* 当这个runloop将要去休眠时
* 当线程已经被唤醒，但还没执行事件之前
* 从runloo中退出时

上述事件发生时都要通知观察者。

你能使用Core Foundation添加observers到应用中。要创建一个observers，你应该使用`CFRunLoopObserverRef`类型。这个类型保持对你自定义的回调函数和它感兴趣的活动的跟踪。

与timers类似，observers也可以使用一次或多次。只使用一次的observers使用后就从runloop中移除了。而一个重复的observers始终保留。你可以在创建的时候指定observers是使用一次，还是重复使用。

关于observers的例子，参见`Configuring the Run Loop`.更多详细的信息，参考`CFRunLoopObserverRef`类

### The Run Loop Sequence of Events

每次运行runloop，线程的runloop执行即将到来的时间并向observers发出通知。流程如下:

 1. 已经进入runloop时通知observers
 2. 已经准备好的timers将要触发时通知观察者
 3. 非port based类型的input sources将要触发时通知观察者
 4. 触发已经准备好的非port based类型的input sources
 5. 如果一个port based input source已经准备好去触发，就立即执行这个事件。
 6. runloop将要休眠时通知观察者
 7. 使线程休眠直到下面的事件之一发生
    * 一个port-based input source的事件到达。
    * 一个timer触发
    * 设定的runloop的超时时间到期
    * runloop明确被唤醒
 8. 线程已经醒来时通知观察者
 9. 执行将要到来的事件
    * 如果一个自定义的timer触发，就执行timer的事件，并回到第2步，重新执行runloop
    * 如果一个input source触发，就发送这个事件
    * 如果如果runloop明确被唤醒但是还没有超时，就回到第2步，重新执行runloop
 10. runloop已经退出时通知观察者。
 
 由于timer和input sources的观察者通知在实际事件发生前被发送，所以在通知的时间和事件发生的时间之间会有一个差值。如果这些事件之间的时间是严格的，你可以使用休眠和唤醒通知来帮助你关联在这些事件之间的时间。
 
 在runloop运行期间，由于定时器和其他周期性的事件被周期性的发送，要避免循环破坏这些事件的传递。典型的例子是:当你进行鼠标拖拽时，会执行`mouse-tracking`程序。定时器不会被触发直到`mouse-tracking`程序退出。
 
 
 使用runloop对象，可以使runloop明确的被唤醒。其他事件也可以造成runloop将被唤醒。例如:添加一个`non-port-based input source `的input source去唤醒runloop，目的是让这个input source能立即被执行,而不是让它等待直到一些其它的事件发生。??????(不理解)
 
## When Would You Use a Run Loop?

只有当你创建辅助线程的时候才需要明确的去运行runloop。对于主线程而言，runloop是基础结构中的关键性部分。因此，主线程自动开启了runloop。

对于辅助线程,你需要决定是否一个runloop是必须的。如果是，那么请配置并运行runloop。如果不是，就不用运行。
例如:如果你使用一个线程执行一些预先定义的长时间的任务时，应该避免开启runloop。runloop用于你想要和你的线程有更多的交互的情况。如果你要做下面任何一件事，你需要开启runloop。

 * 使用ports或者自定义的input source 去和其他的线程通信
 * 在线程中使用timers
 * 在Cocoa应用中，使用任何`performSelector… `方法
 * 让线程执行周期性的任务

如果你限制使用runloop，配置和安装时简单的。和所有的线程编程一样，你需要有一个的计划在适当的情况下去退出你的线程。通过让线程自己退出从而干净的结束线程，这总是比强制使线程终止更好。在Run Loop对象中描述了，如何配置和退出runloop。

### Using Run Loop Objects

一个run loop对象提供了添加input sources，timers,observers到runloop中，然后运行runloop的主要的接口。每一个线程都有一个runloo对象和它关联。在Cocoa中，这个对象是`NSRunLoop`类的一个实例对象。在Core Foundation中，它是一个`CFRunLoopRef`类型的指针。

### Getting a Run Loop Object

你可以使用下列方法，从当前线程中得到一个runloop。
 * 在Cocoa中，使用`NSRunLoop`的类方法`currentRunLoop`得到runloop对象
 * 在Core Foundation中使用`CFRunLoopGetCurrent`函数.
 
你可以通过NSRunLoop类的`getCFRunLoop`实例方法得到`CFRunLoopRef`类型的runloop对象.


### Configuring the Run Loop

在一个辅助线程运行一个runloop之前，你必须添加至少一个input source 或者timer到runloop中。如果一个runloop中没有任何被监控的sources，当你尝试运行的时候，runloop会立即退出。

除了安装sources，你也可以安装observers并且使用它们去监控runloop不同的执行阶段. 为了安装一个runloop的observe，你需要创建一个`CFRunLoopObserverRef`类型的数据并且使用`CFRunLoopAddObserver`函数把它添加到你的runloop中.即使是在Cocoa应用中，runloop observers也必须使用Core Foundation来被创建。

表3-1 展示了一个线程添加一个observer到它的runloop中的主要过程。这个例子的目的是向你展示如何创建一个observe,所以下面的代码简单设置了一个observer去监控runloop的所有活动.

```
表 3-1  Creating a run loop observer

- (void)threadMain
{
    // The application uses garbage collection, so no autorelease pool is needed.
    NSRunLoop* myRunLoop = [NSRunLoop currentRunLoop];
 
    // Create a run loop observer and attach it to the run loop.
    CFRunLoopObserverContext  context = {0, self, NULL, NULL, NULL};
    CFRunLoopObserverRef    observer = CFRunLoopObserverCreate(kCFAllocatorDefault,
            kCFRunLoopAllActivities, YES, 0, &myRunLoopObserver, &context);
 
    if (observer)
    {
        CFRunLoopRef    cfLoop = [myRunLoop getCFRunLoop];
        CFRunLoopAddObserver(cfLoop, observer, kCFRunLoopDefaultMode);
    }
 
    // Create and schedule the timer.
    [NSTimer scheduledTimerWithTimeInterval:0.1 target:self
                selector:@selector(doFireTimer:) userInfo:nil repeats:YES];
 
    NSInteger    loopCount = 10;
    do
    {
        // Run the run loop 10 times to let the timer fire.
        [myRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:1]];
        loopCount--;
    }
    while (loopCount);
}

```

当为一个长期的线程配置runloop时，最好添加至少一个input source去接收消息.尽管你能仅仅添加一个不重复timer来进入runloop，一旦timer触发后，timer通常变为无效的，然后runloop将退出.虽然添加一个能够重复的timer能够保持runloop长期运行，但是这将涉及到触发这个timer来周期性的唤醒你的线程，这实际上是另一种形式的轮询。相比之下，一个input source保持你的线程sleep，直到事件发生，这可能是更好的。

总结而言，如果要配置一个长期运行的runloop，添加一个input source要好过于添加timer。


### Starting the Run Loop

在你的应用中，为辅助线程开启runloop时有必要的。一个runloop必须有至少一个input source 或者 timer去监控.如果一个都没有，那么runloop会立即退出.

这里有一些方法去开启runloop,包括下列条件

 * 没有限定条件的
 * 一个限定时间
 * 一个指定的mode
 
没有任何限定条件的运行你的runloop是最简单的选择，但是也是最不可取的。没有限定条件的运行runloop使你的线程进入一个永久的循环中，这将使你对runloop本身有很小的控制。虽然你也能向runloop中添加input sources和timers,但是唯一一个停止这个runloo的方式就是kill它。同时此时也没有方法能够让这个runloop运行在一个自定义的model下.

使用一个超时的时间值来运行runloop比没有限定条件的运行runloop更好。当你使用一个超时时间时，一个runloop运行直到事件到达或者分配的时间到期。如果是一个事件到达，这个事件被分配给一个handler去执行，然后runloop立即退出.然后你的代码能够重启runloop来处理下一个事件。如果分配的时间过期，你可以简单的重启runloop或者使用这个时间去做任何需要的事情。

除了超时时间，你也可以使用一个指定的model来运行你的runloop。 modes和超时时间不是互斥的，并且当启动runloop的时候，两者能够同时被使用。modes限制了给runloop发送事件的sources的类型。


表3-2 展示了一个线程的主要架构，这个例子的关键部分展示了一个runloop的基本结构。

```
表3-2 Running a run loop
线程的主要架构
- (void)skeletonThreadMain
{

    // Set up an autorelease pool here if not using garbage collection.
    //如果不使用垃圾回收，那么设置一个自动释放池
    BOOL done = NO;
 
    // Add your sources or timers to the run loop and do any other setup.
    //添加你的sources或timers到runloop中，并做其他的设置。
    do
    {
        // Start the run loop but return after each source is handled.
        //开启runloop并返回结构，在每个source被处理后。
        SInt32    result = CFRunLoopRunInMode(kCFRunLoopDefaultMode, 10, YES);
 
        // If a source explicitly stopped the run loop, or if there are no
        // sources or timers, go ahead and exit.
        //如果一个source明确的停止这个runloop，或runloop已经没有sources，或timers，就退出。
        if ((result == kCFRunLoopRunStopped) || (result == kCFRunLoopRunFinished))
            done = YES;
 
        // Check for any other exit conditions here and set the
        // done variable as needed.
        
        //检查任何存在的其他条件，并根据需要设置done的值
    }
    while (!done);
    //done 为YES 退出这个 do while 的 run loop.
 
    // Clean up code here. Be sure to release any allocated autorelease pools.
    // 清理代码--确保去释放任何已经分配的自动释放池
}
 
```

递归的运行一个runloop是可能的。换句话说，你可以在一个input source 或者 timer的处理程序中调用 CFRunLoopRun, CFRunLoopRunInMode,或者任何NSRunLoop中启动runloop的方法.

 
### Exiting the Run Loop

这有两种方法使runloop在已经执行了一个事件之前退出.

* 用一个timeout value来配置这个runloop，让它运行.
* 直接告诉这个runloop去停止运行。

如果你要管理runloop的退出，那么使用一个timeout value是首选。指定一个合适的timeout value可以让runloop在退出之前完成它所有的正常处理，包括在退出之前向runloop的observers发送通知.

使用`CFRunLoopStop`函数明确的停止runloop产生一个和使用timeout value相似的结果。runloop发送remaining run-loop通知并退出。不同的是它可以使用`CFRunLoopStop`在你无条件限制开启的运行循环上.

虽然移除runloop的input sources和timers也可能造成runloop退出，但这是不可靠的。一些系统进程会添加一些input sources给runloop去处理需要的事件。因为你的代码并不知道那些input sources,所以runloop将不能移除这些input sources，这将阻止runloop退出。


### Thread Safety and Run Loop Objects

线程的安全性变化取决于你使用哪种API来处理你的runloop。在Core Foundation中的函数通常是线程安全的并且能在任何线程被调用。无论什么时候，如果你执行修改runloop配置的操作，从runloop所在的线程进行是一个好的做法。

Cocoa的NSRunLoop类不像Core Foundation那样具有与生俱来的线程安全性。如果你使用NSRunLoop类去修改你的runloop，你应该在同一个线程中去处理。添加一个input source 或者 timer到一个其他线程的runloop中可能造成莫名其妙的crash.

## Configuring Run Loop Sources

下面的部分展示在Cocoa和Core Foundation中如何配置不同类型的input sources。

### Defining a Custom Input Source

创建一个自定义的input source涉及到定义下列内容:
* 你想要input source处理的信息
* 一个调度程序(scheduler routine)--让感兴趣的客户端知道如何和你的input source联系
* 一个处理程序(handler routine)--执行被任何客户端发送的请求
* 一个取消程序(cancellation routine)--使你的input source失效

由于你创建一个自定义的input source给去执行自定义的信息，所以input source实际的配置是灵活的。对你的自定义的input source来说--调度，处理，取消程序总是你所需要的关键程序。然而，input source大部分的其余的行为都是发生在这些处理程序之外的。例如，由你决定如何传递数据给input source以及input source与其他线程通信的机制。

图3-2 展示了一个自定义input source的配置示例。在这个例子中，应用的主线程维护对input sources以及input sources的command buffer(命令缓存区)的引用，并且input sources安装到run loop中.当主线程中有一个任务想要交给工作线程时，它发送一个command给工作线程的command buffer以及任何工作线程执行任务所需要的信息(因为主线程和input sources的工作线程都有权访问command buffer，所以访问必须是同步的)。一旦一个command被发出，主线程发信号给input source并且唤醒工作线程的runloop。在收到唤醒command后，runloop调用input source的处理程序--来执行在command buffer内相应的命令.

![](http://7xqijx.com1.z0.glb.clouddn.com/runloop-3-2.png?imageView/2/w/800)


下面的部分展示了自定义input source的实现，并展示了你需要实现的关键代码

#### Defining the Input Source

定义一个自定义的input source需要使用Core Fundation的程序去配置source并且添加它到runloop中。尽管基本的处理是基于c函数，也不妨碍你用objective-c或c++去实现一些函数。

在图3-2中被介绍的input source使用一个objective-c对象来管理一个command buffer以及协调runloop。表3-3展示了这个对象的定义。这个`RunLoopSource`对象管理一个command buffer以及使用这个缓存区去接收来自其他线程的消息。这个表也展示了`RunLoopContext`对象--它仅仅是一个容器对象，被用于传递一个`RunLoopSource`对象和一个runloop引用给主线程.

```
表 3-3  The custom input source object definition

@interface RunLoopSource : NSObject
{
    CFRunLoopSourceRef runLoopSource;
    NSMutableArray* commands;
}
 
- (id)init;
- (void)addToCurrentRunLoop;
- (void)invalidate;
 
// Handler method
- (void)sourceFired;
 
// Client interface for registering commands to process
- (void)addCommand:(NSInteger)command withData:(id)data;
- (void)fireAllCommandsOnRunLoop:(CFRunLoopRef)runloop;
 
@end
 
// These are the CFRunLoopSourceRef callback functions.
void RunLoopSourceScheduleRoutine (void *info, CFRunLoopRef rl, CFStringRef mode);
void RunLoopSourcePerformRoutine (void *info);
void RunLoopSourceCancelRoutine (void *info, CFRunLoopRef rl, CFStringRef mode);
 
// RunLoopContext is a container object used during registration of the input source.
@interface RunLoopContext : NSObject
{
    CFRunLoopRef        runLoop;
    RunLoopSource*        source;
}
@property (readonly) CFRunLoopRef runLoop;
@property (readonly) RunLoopSource* source;
 
- (id)initWithSource:(RunLoopSource*)src andLoop:(CFRunLoopRef)loop;
@end

```
虽然是用objective-c代码管理这个自定义的input source，但是添加这个input source到runloop中还是需要基于c的函数。当你添加这个source到runloop中的时候，首先调用的函数被展示在表3-4中的.因为这个input source只有一个客户(主线程),在那个线程上，它使用调度函数去发送一个消息去让application的代理(Appdelegate)去注册它自己。当代理想要和这个input source通信的时候，它使用在RunLoopContext中的信息.

```
表 3-4  Scheduling a run loop source
void RunLoopSourceScheduleRoutine (void  * info, CFRunLoopRef rl, CFStringRef mode)
{
    RunLoopSource* obj = (RunLoopSource * )info;
    //application delegate
    AppDelegate*   del = [AppDelegate sharedAppDelegate];
    RunLoopContext* theContext = [[RunLoopContext alloc] initWithSource:obj andLoop:rl];
 
    [del performSelectorOnMainThread:@selector(registerSource:)
                                withObject:theContext waitUntilDone:NO];
}
```

最重要的回调的程序之一是当你的input source收到信号时，用来执行自定义数据的程序.表3-5展示了这个与RunLoopSource对象关联在一起的perform 回调程序.这个函数简单的转发这个请求给`sourceFired`方法去处理这个任务。然后`sourceFired`方法执行所有在command buffer中的命令。


```
表3-5在input source中执行任务
void RunLoopSourcePerformRoutine (void * info)
{
    RunLoopSource*  obj = (RunLoopSource*)info;
    [obj sourceFired];
}
```

如果你曾经用 `CFRunLoopSourceInvalidate`函数从runloop中移除你的input source，系统调用你的input source的取消程序。你能用这个程序去通知clients你的input source不再有效，这些clients应该移除对该input source的引用。表3-6展示了这个`取消回调程序`。这个函数发送另一个RunLoopContext对象给应用的delegate,这次是要求应用的delegate移除对这个source的引用。

```
表 3-6 取消一个input source
void RunLoopSourceCancelRoutine (void * info, CFRunLoopRef rl, CFStringRef mode)
{
    RunLoopSource* obj = (RunLoopSource* )info;
    AppDelegate* del = [AppDelegate sharedAppDelegate];
    RunLoopContext* theContext = [[RunLoopContext alloc] initWithSource:obj andLoop:rl];
 
    [del performSelectorOnMainThread:@selector(removeSource:)
                                withObject:theContext waitUntilDone:YES];
}
```
#### Installing the Input Source on the Run Loop

  表3-7显示了RunLoopSource的init和addToCurrentRunLoop的方法。Init方法创建CFRunLoopSourceRef的不透明类型，该类型必须被附加到run loop里面。它把RunLoopSource对象做为上下文引用参数，以便回调例程持有该对象的一个引用指针。输入源的安装只在工作线程调用addToCurrentRunLoop方法才发生，此时RunLoopSourceScheduledRoutine被调用。一旦输入源被添加到run loop，线程就运行run loop并等待事件。
  
```
表3-7 installing the run loop source
- (id)init
{
    CFRunLoopSourceContext    context = {0, self, NULL, NULL, NULL, NULL, NULL,
                                        &RunLoopSourceScheduleRoutine,
                                        RunLoopSourceCancelRoutine,
                                        RunLoopSourcePerformRoutine};
 
    runLoopSource = CFRunLoopSourceCreate(NULL, 0, &context);
    commands = [[NSMutableArray alloc] init];
 
    return self;
}
 
- (void)addToCurrentRunLoop
{
    CFRunLoopRef runLoop = CFRunLoopGetCurrent();
    CFRunLoopAddSource(runLoop, runLoopSource, kCFRunLoopDefaultMode);
}

```

#### Coordinating with Clients of the Input Source

为了使input source是有用的，你需要去维护它并从另一个线程给它发送信号。一个input source主要的功能是让与它关联的线程处于休眠中直到有任务要去处理。所以，有其他的线程知道这个input source并且能与这个input source通信是必要的。

通知clients知道你的输入源的方法之一是当你的input source第一次安装到runloop中时去发送注册请求。你可以注册你的input source到任意多个你想要的clients中。 (结合3-8的例子,你可以简单理解为把input source通过RunLoopContext对象注册到主线程中，使主线程知道这个input source，以便主线程与input source进行通信).

表3-8展示了定义在应用的delegate中的注册和移除source的方法。

```
表3-8 使用应用的delegate注册和移除一个input source

- (void)registerSource:(RunLoopContext*)sourceInfo;
{
    [sourcesToPing addObject:sourceInfo];
}
 
- (void)removeSource:(RunLoopContext*)sourceInfo
{
    id    objToRemove = nil;
 
    for (RunLoopContext* context in sourcesToPing)
    {
        if ([context isEqual:sourceInfo])
        {
            objToRemove = context;
            break;
        }
    }
 
    if (objToRemove)
        [sourcesToPing removeObject:objToRemove];
}

```


__注意:__

  1 `registerSource:`函数调用了先前定义在表3-4的 `RunLoopSourceScheduleRoutine`方法
  
  2 `removeSource:`函数调用了先前定义在表3-4的 `RunLoopSourceCancelRoutine`方法



#### Signaling the Input Source

在一个client交付它的数据给input source后，client必须给source发送信号并且唤醒source的runloop。给source发送信号使runloop知道这个source已经做好处理消息的准备。由于当信号发送的时候，线程可能在休眠，所以你应该总是明确的唤醒线程。如果不这样做，会导致input source延迟执行。

```
表3-9 唤醒runloop
- (void)fireCommandsOnRunLoop:(CFRunLoopRef)runloop
{
    CFRunLoopSourceSignal(runLoopSource);
    CFRunLoopWakeUp(runloop);
}

```

注意:你不应该尝试通过给一个自定义的input source发送信息来处理一个SIGHUP(挂断信号)或者进程级的信号。唤醒runloop的Core Foundation函数不是信号安全的，在你应用中的信号处理程序不应该被使用。更多关于信号处理程序的信息，请参考sigaction页。


### Configuring Timer Sources

为了创建一个timer source，你必须创建一个timer对象并把它放到你的runloop中。在Cocoa中，你使用NSTimer类去创建新的timer对象，在Core Foundation中你使用CFRunLoopTimerRef类型。NSTimer类是Core Foudation的一个简单扩展--提供了一些方便的功能。例如：能够使用一个方法来创建并安排一个timer。(scheduledTimerWithTimeInterval:target:selector:userInfo:repeats:)

在Cocoa中，你可以用下列任一方法同时创建并安排一个timer

* scheduledTimerWithTimeInterval:target:selector:userInfo:repeats:
* scheduledTimerWithTimeInterval:invocation:repeats:

这些方法创建并添加timer到当前的线程的runloop中的defult model中(`NSDefaultRunLoopMode`)。如果你想手动的安排一个timer，你能通过创建一个NSTimer对象，然后使用`addTimer:forMode:`方法把它添加到runloop中。这两种方法做基本一样的事情，区别在于对timer配置的控制权的大小。例如，如果你创建timer并添加手动添加它到runloop中，你可以使用其他的mode，而不是选择默认的mode。表3-10展示了创建timer的两种方法。第一个timer，等待1s后触发，然后每隔0.1s触发一次。第二个timer，每次间隔都是0.2s。

```
表3-10 使用NSTimer创建并安排timers

NSRunLoop* myRunLoop = [NSRunLoop currentRunLoop];
 
// Create and schedule the first timer.
NSDate* futureDate = [NSDate dateWithTimeIntervalSinceNow:1.0];
NSTimer* myTimer = [[NSTimer alloc] initWithFireDate:futureDate
                        interval:0.1
                        target:self
                        selector:@selector(myDoFireTimer1:)
                        userInfo:nil
                        repeats:YES];
[myRunLoop addTimer:myTimer forMode:NSDefaultRunLoopMode];
 
// Create and schedule the second timer.
[NSTimer scheduledTimerWithTimeInterval:0.2
                        target:self
                        selector:@selector(myDoFireTimer2:)
                        userInfo:nil
                        repeats:YES];
```

表3-11 展示了使用Core Foundation函数来配置timer所需的代码。尽管这个例子没有在context结构体中传递任何自定义的信息，但是你能使用这个结构体传递timer所需的任意的自定义的数据。要了解这个结构体内容的更多信息，请参考CFRunLoopTimer。

```
表3-11 使用Core Fundation创建并安排timer
FRunLoopRef runLoop = CFRunLoopGetCurrent();
CFRunLoopTimerContext context = {0, NULL, NULL, NULL, NULL};
CFRunLoopTimerRef timer = CFRunLoopTimerCreate(kCFAllocatorDefault, 0.1, 0.3, 0, 0,
                                        &myCFTimerCallback, &context);
 
CFRunLoopAddTimer(runLoop, timer, kCFRunLoopCommonModes);

```


### Configuring a Port-Based Input Source

在Cocoa和Core Foundation中提供基于端口的对象来进行线程之间或者进程之间的通信。接下来的部分向你展示怎样使用不同类型的端口来设置端口通信.


#### Configuring an NSMachPort Object

为了使用一个NSMachPort对象建立一个本地连接，你可以创建一个port对象并且把它添加到你的主线程的runloop中。当启动你的辅助线程时，你传递同一个对象给你线程的入口函数。辅助线程能使用同一对象将消息发送回你的主线程。

主线程的实现代码

表3-12 展示了主线程启动一个辅助线程的代码。因为Cocoa framework为了配置这个port和runloop执行了很多中间步骤，这个`launchThread`方法明显比Core Foundation的等效的方法更短。但是，这两者的功能几乎的等效的。唯一的不同是这个方法是直接发送NSPort对象，而不是发送这个本地port的名字给工作线程。

```
表3-12 主线程启动方法

- (void)launchThread
{   //创建一个Mach端口
    NSPort* myPort = [NSMachPort port];
    if (myPort)
    {
        // This class handles incoming port messages.
        //设置代替处理即将到来的port消息
        [myPort setDelegate:self];
 
         // Install the port as an input source on the current run loop.
         //将port作为input source安装到当前线程(主线程)
        [[NSRunLoop currentRunLoop] addPort:myPort forMode:NSDefaultRunLoopMode];
  
        // Detach the thread. Let the worker release the port.
        //分配一个新的线程,让MyWorkerClass在新的线程中去执行`LaunchThreadWithPort`方法
        //并在MyWorkerClass中释放这个端口。
        [NSThread detachNewThreadSelector:@selector(LaunchThreadWithPort:)
               toTarget:[MyWorkerClass class] withObject:myPort];
    }
}
```
为了在你的线程间建立一个双向通信的通道，你需要让工作线程发送自己的本地port给主线程--用一个check-in (签到)消息。接收这个check-in消息让你的主线程知道辅助线程的信息，同时也给你提供了一个发送消息到工作线程的方法。

表3-13 展示了这个关于主线程的方法--`handlePortMessage: `。当数据到达主线程的自己的本地端口，这个方法被调用。当 check-in消息到达的时候该方法从port信息中取出辅助线程的端口，并且保存它以便以后使用。

```
表3-13 处理Mach Port 消息
//定义消息id。
\#define kCheckinMessage 100
// Handle responses from the worker thread.
//处理来自工作线程的响应
- (void)handlePortMessage:(NSPortMessage * )portMessage
{
    unsigned int message = [portMessage msgid];
    NSPort* distantPort = nil;
 
    if (message == kCheckinMessage)
    {
        // Get the worker thread’s communications port.
        //得到工作线程的通信端口
        distantPort = [portMessage sendPort];
 
        // Retain and save the worker port for later use.
        //保存工作线程的端口供以后使用
       [self storeDistantPort:distantPort];
    }
    else
    {
        // Handle other messages.
    }
}

```

实现辅助线程代码

对于辅助线程，你必须配置这个线程并且使用指定的port将信息传递回主线程。

表3-14 展示了设置这个工作线程的代码。在为这个线程创建了一个自动释放池之后，这个方法创建了一个工作对象来驱动线程的执行。这个工作对象的`sendCheckinMessage:`（表3-15）方法为工作线程创建一个本地port，并且把一个check-in 消息发送回主线程。

```
表3-14 Launching the worker thread using Mach ports
+(void)LaunchThreadWithPort:(id)inData
{
    NSAutoreleasePool*  pool = [[NSAutoreleasePool alloc] init];
 
    // Set up the connection between this thread and the main thread.
    NSPort* distantPort = (NSPort*)inData;
 
    MyWorkerClass*  workerObj = [[self alloc] init];
    [workerObj sendCheckinMessage:distantPort];
    [distantPort release];
 
    // Let the run loop process things.
    do
    {
        [[NSRunLoop currentRunLoop] runMode:NSDefaultRunLoopMode
                            beforeDate:[NSDate distantFuture]];
    }
    while (![workerObj shouldExit]);
 
    [workerObj release];
    [pool release];
}
```
当使用NSMachPort时，本地和远程线程能使用同一port对象在线程之间进行单向通信。一个线程创建的本地端口成为另一个线程的远程端口。

表3-15展示了辅助线程的check-in程序。这个方法为将来通信设置了本地端口,然后把check-in发送回主线程。这个方法使用port对象(在`LaunchThreadWithPort`方法中接收的)作为消息的目标。

```
表3-15  Sending the check-in message using Mach ports
// Worker thread check-in method
//工作线程的check-in方法
- (void)sendCheckinMessage:(NSPort*)outPort
{
    // Retain and save the remote port for future use.
    [self setRemotePort:outPort];
 
    // Create and configure the worker thread port.
    NSPort* myPort = [NSMachPort port];
    [myPort setDelegate:self];
    [[NSRunLoop currentRunLoop] addPort:myPort forMode:NSDefaultRunLoopMode];
 
    // Create the check-in message.
    //官方的代码
  <!--  NSPortMessage* messageObj = [[NSPortMessage alloc] initWithSendPort:outPort
                                         receivePort:myPort components:nil];-->
    //我认为应该修改为下面的代码，才能解释通。
    NSPortMessage* messageObj = [[NSPortMessage alloc] initWithSendPort:myPort
                                         receivePort:outPort components:nil];
 
    if (messageObj)
    {
        // Finish configuring the message and send it immediately.
        [messageObj setMsgId:setMsgid:kCheckinMessage];
        [messageObj sendBeforeDate:[NSDate date]];
    }
}
```

注意:我认为`[[NSPortMessage alloc] initWithSendPort:outPort receivePort:myPort components:nil]`这句代码是有问题的，发送端口应该是`myPort`,接收端口应该是`outPort`。因为`outPort`是主线程的本地端口，而这条check-in消息就是发给主线程的。从表3-14也可以印证这点。


#### Configuring an NSMessagePort Object
要使用一个NSMessagePort对象建立一个本地连接，你不能简单的在线程之间传递port对象。远程的消息port必须通过名字来获取。在Cocoa中,使用一个指定的名字注册你的本地port并且传递这个名字给远程线程，目的是远程线程可以获取一个适当的port对象进行通信。表3-16 展示了port(NSMessagePort)的创建和注册过程。

```
表3-16 Registering a message port
NSPort* localPort = [[NSMessagePort alloc] init];
 
// Configure the object and add it to the current run loop.
//配置这个对象并添加它到当前的runloop中
[localPort setDelegate:self];
[[NSRunLoop currentRunLoop] addPort:localPort forMode:NSDefaultRunLoopMode];
 
// Register the port using a specific name. The name must be unique.
//用一个指定的名字来注册这个port，这个名字必须是唯一的。
NSString* localPortName = [NSString stringWithFormat:@"MyPortName"];
[[NSMessagePortNameServer sharedInstance] registerPort:localPort
                     name:localPortName];


```

#### Configuring a Port-Based Input Source in Core Foundation
这部分展示了如何使用Core Foundation在主线程和工作线程之间设置一个双向通信的通道。

表3-17 展示了通过主线程来启动工作线程的代码调用。代码首先设置一个`CFMessagePortRef`类型去监听来自工作线程的消息。工作线程需要端口的名字来建立连接，名字被传递给工作线程的入口函数。在当前用户上下文中，端口的名字应该是唯一的，否则，你可能会遇到冲突。

```
表3-17 Attaching a Core Foundation message port to a new thread

/#define kThreadStackSize        (8 *4096)
 OSStatus MySpawnThread()
{
    // Create a local port for receiving responses.
    //创建一个本地端口来接收响应
    CFStringRef myPortName;
    CFMessagePortRef myPort;
    CFRunLoopSourceRef rlSource;
    CFMessagePortContext context = {0, NULL, NULL, NULL, NULL};
    Boolean shouldFreeInfo;
 
    // Create a string with the port name.
    myPortName = CFStringCreateWithFormat(NULL, NULL, CFSTR("com.myapp.MainThread"));
 
    // Create the port.
    myPort = CFMessagePortCreateLocal(NULL,
                myPortName,
                &MainThreadResponseHandler,
                &context,
                &shouldFreeInfo);
 
    if (myPort != NULL)
    {
        // The port was successfully created.
        // Now create a run loop source for it.
        //通过端口来创建source
        rlSource = CFMessagePortCreateRunLoopSource(NULL, myPort, 0);
        
         if (rlSource)
        {
            // Add the source to the current run loop.
            //把source添加到当前runloop中
            CFRunLoopAddSource(CFRunLoopGetCurrent(), rlSource, kCFRunLoopDefaultMode);
 
            // Once installed, these can be freed.
            //一旦被安装这个port和source就可以释放了。
            CFRelease(myPort);
            CFRelease(rlSource);
        }
    }
 
    // Create the thread and continue processing.
    // 创建新的线程并执行
    MPTaskID        taskID;
    return(MPCreateTask(&ServerThreadEntryPoint,
                    (void*)myPortName,
                    kThreadStackSize,
                    NULL,
                    NULL,
                    NULL,
                    0,
                    &taskID));
}
 
```

随着端口的安装以及线程的启动，当主线程等待工作线程去check in的时候，主线程能够继续它的常规的执行。当这个check-in 消息到达的时候，它被分配给主线程的`MainThreadResponseHandler`函数(参见表3-18)。这个函数提取工作线程的接口名并创建了一个用于未来通信的通道。

```
表3-18 Receiving the checkin message

/#define kCheckinMessage 100
// Main thread port message handler
CFDataRef MainThreadResponseHandler(CFMessagePortRef local,
                    SInt32 msgid,
                    CFDataRef data,
                    void* info)
{
    if (msgid == kCheckinMessage)
    {
        CFMessagePortRef messagePort;
        CFStringRef threadPortName;
        CFIndex bufferLength = CFDataGetLength(data);
        UInt8* buffer = CFAllocatorAllocate(NULL, bufferLength, 0);
 
        CFDataGetBytes(data, CFRangeMake(0, bufferLength), buffer);
        //远程端口名(即工作线程的端口名)
        threadPortName = CFStringCreateWithBytes (NULL, buffer, bufferLength, kCFStringEncodingASCII, FALSE);
 
        // You must obtain a remote message port by name.
        //获取远程端口
        messagePort = CFMessagePortCreateRemote(NULL, (CFStringRef)threadPortName);
 
        if (messagePort)
        {
            // Retain and save the thread’s comm port for future reference.
            //保存远程端口
            AddPortToListOfActiveThreads(messagePort);
 
            // Since the port is retained by the previous function, release
            // it here.
            CFRelease(messagePort);
        }
 
        // Clean up.
        CFRelease(threadPortName);
        CFAllocatorDeallocate(NULL, buffer);
    }
    else
    {
        // Process other messages.
    }
 
    return NULL;
}
```

主线程配置好后，剩下的唯一的事情就是让新创建的工作线程创建自己的端口，并签到(check-in)。表3-19展示了工作线程的入口函数，这个函数创建了一个远程连接来回到主线程。然后，这个函数创建了一个本地端口，安装这个端口到这个线程的runloop中，发送一个包含本地端口名的check-in消息给主线程。

```
表3-19 Setting up the thread structures
//设置新线程(工作线程)的结构
OSStatus ServerThreadEntryPoint(void* param)
{
    // Create the remote port to the main thread.
    CFMessagePortRef mainThreadPort;
    CFStringRef portName = (CFStringRef)param;
    //根据传递过来的端口名，创建主线程的端口
    mainThreadPort = CFMessagePortCreateRemote(NULL, portName);
 
    // Free the string that was passed in param.
    CFRelease(portName);
 
    // Create a port for the worker thread.
    //创建一个工作线程的接口名字
    CFStringRef myPortName = CFStringCreateWithFormat(NULL, NULL, CFSTR("com.MyApp.Thread-%d"), MPCurrentTaskID());
 
    // Store the port in this thread’s context info for later reference.
    //保存这个mainThreadPort接口在线程的上下文信息中
    CFMessagePortContext context = {0, mainThreadPort, NULL, NULL, NULL};
    Boolean shouldFreeInfo;
    Boolean shouldAbort = TRUE;
    
    //创建工作线程的接口
    CFMessagePortRef myPort = CFMessagePortCreateLocal(NULL,
                myPortName,
                &ProcessClientRequest,
                &context,
                &shouldFreeInfo);
 
    if (shouldFreeInfo)
    {
        // Couldn't create a local port, so kill the thread.
        //不能创建本地端口，所以杀死线程
        MPExit(0);
    }
 
    CFRunLoopSourceRef rlSource = CFMessagePortCreateRunLoopSource(NULL, myPort, 0);
    if (!rlSource)
    {
        // Couldn't create a rlSource, so kill the thread.
        MPExit(0);
    }
 
    // Add the source to the current run loop.
    CFRunLoopAddSource(CFRunLoopGetCurrent(), rlSource, kCFRunLoopDefaultMode);
 
    // Once installed, these can be freed.
    CFRelease(myPort);
    CFRelease(rlSource);
 
    // Package up the port name and send the check-in message.
    CFDataRef returnData = nil;
    CFDataRef outData;
    CFIndex stringLength = CFStringGetLength(myPortName);
    UInt8* buffer = CFAllocatorAllocate(NULL, stringLength, 0);
 
    CFStringGetBytes(myPortName,
                CFRangeMake(0,stringLength),
                kCFStringEncodingASCII,
                0,
                FALSE,
                buffer,
                stringLength,
                NULL);
 
    outData = CFDataCreate(NULL, buffer, stringLength);
 
    CFMessagePortSendRequest(mainThreadPort, kCheckinMessage, outData, 0.1, 0.0, NULL, NULL);
 
    // Clean up thread data structures.
    CFRelease(outData);
    CFAllocatorDeallocate(NULL, buffer);
 
    // Enter the run loop.
    CFRunLoopRun();
}
```

一旦它进入自己的runloop中，所有将来发送到这个线程的端口的事件都会被`ProcessClientRequest`函数处理.这个函数的实现依赖于工作线程的类型，在这并没有展示。

## 参考



* [苹果Run Loops文档](https://developer.apple.com/library/mac/documentation/Cocoa/Conceptual/Multithreading/RunLoopManagement/RunLoopManagement.html#//apple_ref/doc/uid/10000057i-CH16-SW18)


     
  
  
 
  
  