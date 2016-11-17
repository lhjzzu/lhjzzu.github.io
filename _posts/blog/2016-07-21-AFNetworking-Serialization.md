---
layout: post
title: AFNetworking原理:Serialization(一)
date: 2016-07-21
categories: IOS

---

## AFURLRequestSerialization

## 基本介绍
 其主要作用是为我们进行网络请求构建了一个配置好的NSMutableURLRequest。
  
## 主要的类

### 一 声明了两个C语言方法


 * `AFPercentEscapedStringFromString(NSString *string)`:去除非法字符并且对特殊字符进行编码 
 * `AFQueryStringFromParameters(NSDictionary *parameters)`: 将参数字典序列化为查询字符串(query),即   
      `key=value&key=value...`的形式
 
 
### 二 声明了两个协议

 #### AFURLRequestSerialization 
 
       
          AFURLRequestSerialization遵守NSSecureCoding,NSCopying协议。所以遵守该协议的类只要实现      NSSecureCoding,NSCopying对应的方法，就可以进行归档和copy了。

         `AFHTTPRequestSerializer`遵守该协议，同样`AFHTTPRequestSerializer`的子类 `AFJSONRequestSerializer`,`AFPropertyListRequestSerializer`遵守该协议，并实现协议方法
        `requestBySerializingRequest:withParameters:error:`
 
          协议方法`requestBySerializingRequest:withParameters:error:`:处理参数字典，并设置`Content-Type`,组成网络请求`NSURLRequest`并返回.



#### AFMultipartFormData
  

          AFStreamingMultipartFormData遵守该协议,并实现下列协议方法，上传文件数据。

          appendPartWithFileURL:name:error:
          appendPartWithFileURL:name:fileName:mimeType:error:
          appendPartWithInputStream:name:fileName:length:mimeType:
          appendPartWithFileData:name:fileName:mimeType:     
          appendPartWithFormData:name:(NSString *)name;
          appendPartWithHeaders:body:(NSData *)body;
                          

### 三 AFHTTPRequestSerializer 

#### 遵守AFHTTPRequestSerializer协议
#### 属性 & 方法

##### 定义
```
.h文件中
stringEncoding:encode参数字典时的编码类型。默认为NSUTF8StringEncoding
allowsCellularAccess:是否允许无线蜂窝访问，默认为YES
cachePolicy:被创建的NSURLRequest的缓存政策，默认为NSURLRequestUseProtocolCachePolicy
HTTPShouldHandleCookies:被创建的NSURLRequest是否使用默认的cookies处理,默认为YES
HTTPShouldUsePipelining:被创建的NSURLRequest在从一个早前的传输中收到响应之前是否能继续传输数据，默认是NO。
networkServiceType:被创建的NSURLRequest的网络服务类型,默认值为NSURLNetworkServiceTypeDefault。
timeoutInterval:被创建的NSURLRequest的超时时间，默认是60s。
通过设置上述属性，来设置NSURLRequest的对应的属性。

HTTPRequestHeaders:即为序列化的NSURLRequest的allHTTPHeaderFields.
HTTPMethodsEncodingParametersInURI:默认'GET'，'HEAD'，'DELETE'方法将把参数字典字典序列化为查询字符串.

serializer类方法
setValue:forHTTPHeaderField:设置http的header中的键值对
valueForHTTPHeaderField:获取http的header中的键对应的值
setAuthorizationHeaderFieldWithUsername:password:设置http的head中的Authorization字段的值。
clearAuthorizationHeader:清除http的head中的Authorization字段对应的值
setQueryStringSerializationWithStyle:设置序列化参数字典的方式。
setQueryStringSerializationWithBlock:设置序列化参数字典的block方法
requestWithMethod:URLString:parameters:error: 创建NSURLRequest，处理参数字典，设置NSURLRequest的headers以及各项属性，返回配置好的NSURLRequest用于网络请求。
multipartFormRequestWithMethod:URLString:parameters:constructingBodyWithBlock:error: 上传多格式数据。
requestWithMultipartFormRequest:writingStreamContentsToFile:completionHandler: 将给定的NSURLRequest中的内容写入到给定的路径下的文件中。

.m文件中
mutableHTTPRequestHeaders:存储添加到http的headers中的键值对
queryStringSerializationStyle:序列化的风格，现在只有一种默认风格AFHTTPRequestQueryStringDefaultStyle.
queryStringSerialization:设置序列化参数字典的block方法
mutableObservedChangedKeyPaths:将从外部设置的属性名存储在该集合中。


```

##### 核心方法:requestWithMethod:URLString:parameters:error:

```
- (NSMutableURLRequest *)requestWithMethod:(NSString *)method
                                 URLString:(NSString *)URLString
                                parameters:(id)parameters
                                     error:(NSError *__autoreleasing *)error
{
    NSParameterAssert(method);
    NSParameterAssert(URLString);

    NSURL *url = [NSURL URLWithString:URLString];

    NSParameterAssert(url);
    //1 创建NSMutableURLRequest
    NSMutableURLRequest *mutableRequest = [[NSMutableURLRequest alloc] initWithURL:url];
    mutableRequest.HTTPMethod = method;
    //2 设置NSURLRequest对应的属性
    for (NSString *keyPath in AFHTTPRequestSerializerObservedKeyPaths()) {
        if ([self.mutableObservedChangedKeyPaths containsObject:keyPath]) {
            [mutableRequest setValue:[self valueForKeyPath:keyPath] forKey:keyPath];
        }
    }
    //3 调用协议方法requestBySerializingRequest:withParameters:error:,将配置好的NSMutableURLRequest返回。
    mutableRequest = [[self requestBySerializingRequest:mutableRequest withParameters:parameters error:error] mutableCopy];
	return mutableRequest;
}



- (NSURLRequest *)requestBySerializingRequest:(NSURLRequest *)request
                               withParameters:(id)parameters
                                        error:(NSError *__autoreleasing *)error
{
    NSParameterAssert(request);

    NSMutableURLRequest *mutableRequest = [request mutableCopy];
    //1 设置HTTP的header
    [self.HTTPRequestHeaders enumerateKeysAndObjectsUsingBlock:^(id field, id value, BOOL * __unused stop) {
        if (![request valueForHTTPHeaderField:field]) {
            [mutableRequest setValue:value forHTTPHeaderField:field];
        }
    }];
    NSString *query = nil;
    //2 处理参数字典，生成query
    if (parameters) {
        //如果有自定义的序列化方法
        if (self.queryStringSerialization) {
            NSError *serializationError;
            query = self.queryStringSerialization(request, parameters, &serializationError);

            if (serializationError) {
                if (error) {
                    *error = serializationError;
                }

                return nil;
            }
        } else {
            switch (self.queryStringSerializationStyle) {
                case AFHTTPRequestQueryStringDefaultStyle:
                   //调用默认的序列化处理方法
                    query = AFQueryStringFromParameters(parameters);
                    break;
            }
        }
    }
    //3 如果是'GET', 'HEAD', 'DELETE'方法，就拼接到URL后面，如果不是就设置为HTTPBody.
    if ([self.HTTPMethodsEncodingParametersInURI containsObject:[[request HTTPMethod] uppercaseString]]) {
        if (query && query.length > 0) {
            mutableRequest.URL = [NSURL URLWithString:[[mutableRequest.URL absoluteString] stringByAppendingFormat:mutableRequest.URL.query ? @"&%@" : @"?%@", query]];
        }
    } else {
        // #2864: an empty string is a valid x-www-form-urlencoded payload
        if (!query) {
            query = @"";
        }
        if (![mutableRequest valueForHTTPHeaderField:@"Content-Type"]) {
            [mutableRequest setValue:@"application/x-www-form-urlencoded" forHTTPHeaderField:@"Content-Type"];
        }
        [mutableRequest setHTTPBody:[query dataUsingEncoding:self.stringEncoding]];
    }
    return mutableRequest;
}



```


##### 核心方法:multipartFormRequestWithMethod:URLString:parameters:constructingBodyWithBlock:error:


```
- (NSMutableURLRequest *)multipartFormRequestWithMethod:(NSString *)method
                                              URLString:(NSString *)URLString
                                             parameters:(NSDictionary *)parameters
                              constructingBodyWithBlock:(void (^)(id <AFMultipartFormData> formData))block
                                                  error:(NSError *__autoreleasing *)error
{
    NSParameterAssert(method);//一般为POST方法
    NSParameterAssert(![method isEqualToString:@"GET"] && ![method isEqualToString:@"HEAD"]);
    //1 创建NSMutableURLRequest 
    NSMutableURLRequest *mutableRequest = [self requestWithMethod:method URLString:URLString parameters:nil error:error];
    //2 创建AFStreamingMultipartFormData
    __block AFStreamingMultipartFormData *formData = [[AFStreamingMultipartFormData alloc] initWithURLRequest:mutableRequest stringEncoding:NSUTF8StringEncoding];
    //3 如果参数字典存在，处理参数字典。
    if (parameters) {
        for (AFQueryStringPair *pair in AFQueryStringPairsFromDictionary(parameters)) {
            NSData *data = nil;
            if ([pair.value isKindOfClass:[NSData class]]) {
                data = pair.value;
            } else if ([pair.value isEqual:[NSNull null]]) {
                data = [NSData data];
            } else {
                data = [[pair.value description] dataUsingEncoding:self.stringEncoding];
            }

            if (data) {
                //调用代理方法,创建AFHTTPBodyPart。
                [formData appendPartWithFormData:data name:[pair.field description]];
            }
        }
    }
    //4 回调block
    if (block) {
        //调用代理方法,创建AFHTTPBodyPart。
        block(formData);
    }
   
   //5 调用requestByFinalizingMultipartFormData返回组成好的NSMutableURLRequest.
   return [formData requestByFinalizingMultipartFormData];
}


```

### 四  AFJSONRequestSerializer


```
writingOptions:写的类型.

协议方法: requestWithMethod:URLString:parameters:error: 

- (NSURLRequest *)requestBySerializingRequest:(NSURLRequest *)request
                               withParameters:(id)parameters
                                        error:(NSError *__autoreleasing *)error
{
    NSParameterAssert(request);
    //1 如果为'GET','HEAD','DELETE'请求
    if ([self.HTTPMethodsEncodingParametersInURI containsObject:[[request HTTPMethod] uppercaseString]]) {
        return [super requestBySerializingRequest:request withParameters:parameters error:error];
    }

    NSMutableURLRequest *mutableRequest = [request mutableCopy];
    //2 设置header
    [self.HTTPRequestHeaders enumerateKeysAndObjectsUsingBlock:^(id field, id value, BOOL * __unused stop) {
        if (![request valueForHTTPHeaderField:field]) {
            [mutableRequest setValue:value forHTTPHeaderField:field];
        }
    }];
    //3 设置Content-Type为application/json
    if (parameters) {
        if (![mutableRequest valueForHTTPHeaderField:@"Content-Type"]) {
            [mutableRequest setValue:@"application/json" forHTTPHeaderField:@"Content-Type"];
        }
        //4 设置HTTPBody
        [mutableRequest setHTTPBody:[NSJSONSerialization dataWithJSONObject:parameters options:self.writingOptions error:error]];
    }

    return mutableRequest;
}



```

### 五  AFPropertyListRequestSerializer

```

fomart:属性列表的格式,枚举类型NSPropertyListFormat
writeOptions:写入的类型

协议方法: requestWithMethod:URLString:parameters:error: 

- (NSURLRequest *)requestBySerializingRequest:(NSURLRequest *)request
                               withParameters:(id)parameters
                                        error:(NSError *__autoreleasing *)error
{
    NSParameterAssert(request);
    //1 如果为'GET','HEAD','DELETE'请求
    if ([self.HTTPMethodsEncodingParametersInURI containsObject:[[request HTTPMethod] uppercaseString]]) {
        return [super requestBySerializingRequest:request withParameters:parameters error:error];
    }

    NSMutableURLRequest *mutableRequest = [request mutableCopy];
    //2 设置header
    [self.HTTPRequestHeaders enumerateKeysAndObjectsUsingBlock:^(id field, id value, BOOL * __unused stop) {
        if (![request valueForHTTPHeaderField:field]) {
            [mutableRequest setValue:value forHTTPHeaderField:field];
        }
    }];
    //3 设置Content-Type为application/x-plist
    if (parameters) {
        if (![mutableRequest valueForHTTPHeaderField:@"Content-Type"]) {
            [mutableRequest setValue:@"application/x-plist" forHTTPHeaderField:@"Content-Type"];
        }
        //4 设置HTTPBody
        [mutableRequest setHTTPBody:[NSPropertyListSerialization dataWithPropertyList:parameters format:self.format options:self.writeOptions error:error]];
    }

    return mutableRequest;
}



```


### 六 上传文件相关的类 


#### AFHTTPBodyPart

```
 1个或多个AFHTTPBodyPart组装成输入流(AFMultipartBodyStream)，作为NSMutableURLRequest的HTTPBodyStream。

stringEncoding:编码类型
headers: 外界传入
boundary:分界标识符
body: 外界传入
bodyContentLength:body的长度
inputStream:输入流
hasInitialBoundary:是否是初始分界线
hasFinalBoundary:是否是结束分界线
bytesAvailable:是否有字节可用
contentLength:内容的长度
_phase: 枚举类，AFEncapsulationBoundaryPhase(处理开始/中间分界线的阶段),AFHeaderPhase(处理head的阶段),AFBodyPhase(处理body的阶段),AFFinalBoundaryPhase(处理结束分界线的阶段),
_inputStream:输入流
_phaseReadOffset:不同阶段的偏移量

readData:intoBuffer:maxLength: 当_phaseReadOffset长度>=data的长度时，进入到下一个阶段。
read:maxLength: 通过调用readData:intoBuffer:maxLength:遍历各个阶段,最终返回所读的总字节数，并在各个阶段将分界线数据,header数据,body数据读入到给定的buffer中。

```

#### 上传文件的数据组装格式

```
上传文件的数据组装格式

//分界标识符
static NSString * AFCreateMultipartFormBoundary() {
    return [NSString stringWithFormat:@"Boundary+%08X%08X", arc4random(), arc4random()];
}
//回车、换行
static NSString * const kAFMultipartFormCRLF = @"\r\n";

//初始分界线
static inline NSString * AFMultipartFormInitialBoundary(NSString *boundary) {
    return [NSString stringWithFormat:@"--%@%@", boundary, kAFMultipartFormCRLF];
}

//中间的分界线
static inline NSString * AFMultipartFormEncapsulationBoundary(NSString *boundary) {
    return [NSString stringWithFormat:@"%@--%@%@", kAFMultipartFormCRLF, boundary, kAFMultipartFormCRLF];
}
//结束分界线
static inline NSString * AFMultipartFormFinalBoundary(NSString *boundary) {
    return [NSString stringWithFormat:@"%@--%@--%@", kAFMultipartFormCRLF, boundary, kAFMultipartFormCRLF];
}

例如
分界线:Boundary+15494D89731AF29C
初始分界线:--Boundary+15494D89731AF29C\r\n
中间的分界线:\r\n--Boundary+15494D89731AF29C\r\n
结束分界线:\r\n--Boundary+15494D89731AF29C--\r\n


参数:parameters = @{@"content": @"哈哈哈哈哈哈哈哈哈",
                   @"contentId":@"123456"}
2张图片:1.png 2.png 

//上传文件的数据组装格式

--Boundary+15494D89731AF29C

Content-Disposition: form-data; name="content"

哈哈哈哈哈哈哈哈哈

--Boundary+15494D89731AF29C

Content-Disposition: form-data; name="contentId"

123456

--Boundary+15494D89731AF29C

Content-Disposition: form-data; name="pic1"; filename="1.png"
Content-Type: image/png

<89504e47 0d0a1a0a 0000000d 49484452 00000b40 00000708 08020000 002086d7 4200000c 19694343 50494343 29 1123f6d8 4e6e6660 a4acced8 91dcfca8 51dfae3c b8c06475 c01ea5b3 2647c8f8 63ef0479 11d1326e 380e4281 2ff0034c 20822d19 648374c0 6befafeb 87bf6423 01800584 20157081 e58866d4 234e3ac2 87cf2850 00fe8488 0b72c7fc 7ca4a35c 900ff55f c6b4b2a7 2548918e e64b3d32 c01388b3 704ddc03 77c343e1 d30b365b dc197719 f5632a8e ce4af427 fa118388 0144b331 1e6cc83a 133621e0 fd1b5d08 ecb9303b 0917fe68 0edfe211 9e103a09 8f083708 62c21d10 0b1e4ba3 8c58cde2 150a7f60 ce045380 18460b18 c92e19c6 ec1bb5c1
....>

--Boundary+15494D89731AF29C

Content-Disposition: form-data; name="pic2"; filename="2.png"
Content-Type: image/png

<53b9a5d 80dd22bb 7abb57f6 16f65cfb 9df6b71d e80e531c 963b343b 7c717472 143a563b f639193a 25396d77 bae5acea 1ce1bcca f9a20bc1 c5c76591 4ba3cb47 5747d73c d7a3ae7f b959ba65 b81d747b 36c96412 77d2be49 3deefaee 2cf73dee 620fa647 92c76e0f b1a79e27 cbb3dcf3 91978117 c76bbfd7 536f33ef 74ef43de 2f7dac7d 843e277c defbbafa 2ef06df2 c3fc02fd 8afddafd 55fc63fc b7f93f0c d00f480d a80a1808 74089c17 d8144408 0a095a17 742b583b 981d5c19 3c30d969 f282c92d 21d490a8 906d218f 42cd4385 a10d53d0 2993a76c 98723fcc 288c1f56 170ec283 c337843f 883089c8 89f86d2a 716ac4d4 b2a94f22 6d22e747 b646d1a3 66451d8c 7a17ed13 bd26fa5e 
....>


--Boundary+15494D89731AF29C--



```

#### 相关代码

```
//通过self.body得到inputStream
- (NSInputStream *)inputStream {
    if (!_inputStream) {
        if ([self.body isKindOfClass:[NSData class]]) {
            _inputStream = [NSInputStream inputStreamWithData:self.body];
        } else if ([self.body isKindOfClass:[NSURL class]]) {
            _inputStream = [NSInputStream inputStreamWithURL:self.body];
        } else if ([self.body isKindOfClass:[NSInputStream class]]) {
            _inputStream = self.body;
        } else {
            _inputStream = [NSInputStream inputStreamWithData:[NSData data]];
        }
    }

    return _inputStream;
}

//通过self.head得到headerString
- (NSString *)stringForHeaders {
    NSMutableString *headerString = [NSMutableString string];
    for (NSString *field in [self.headers allKeys]) {
        [headerString appendString:[NSString stringWithFormat:@"%@: %@%@", field, [self.headers valueForKey:field], kAFMultipartFormCRLF]];
    }
    [headerString appendString:kAFMultipartFormCRLF];

    return [NSString stringWithString:headerString];
}

// 内容的长度：分界线的length+head的length+body的length
- (unsigned long long)contentLength {
    unsigned long long length = 0;
    //1 前面的分界线的长度
    NSData *encapsulationBoundaryData = [([self hasInitialBoundary] ? AFMultipartFormInitialBoundary(self.boundary) : AFMultipartFormEncapsulationBoundary(self.boundary)) dataUsingEncoding:self.stringEncoding];
    length += [encapsulationBoundaryData length];
    //2 head的长度
    NSData *headersData = [[self stringForHeaders] dataUsingEncoding:self.stringEncoding];
    length += [headersData length];
    //3 body的length
    length += _bodyContentLength;
    //4 后面的分界线的长度 
    NSData *closingBoundaryData = ([self hasFinalBoundary] ? [AFMultipartFormFinalBoundary(self.boundary) dataUsingEncoding:self.stringEncoding] : [NSData data]);
    length += [closingBoundaryData length];

    return length;
}

//是否有可用的字节
- (BOOL)hasBytesAvailable {
    // Allows `read:maxLength:` to be called again if `AFMultipartFormFinalBoundary` doesn't fit into the available buffer
    if (_phase == AFFinalBoundaryPhase) {
        return YES;
    }

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wcovered-switch-default"
    switch (self.inputStream.streamStatus) {
        case NSStreamStatusNotOpen:
        case NSStreamStatusOpening:
        case NSStreamStatusOpen:
        case NSStreamStatusReading:
        case NSStreamStatusWriting:
            return YES;
        case NSStreamStatusAtEnd:
        case NSStreamStatusClosed:
        case NSStreamStatusError:
        default:
            return NO;
    }
#pragma clang diagnostic pop
}


//通过调用readData:intoBuffer:maxLength:遍历各个阶段,最终返回所读的总字节数，并在各个阶段将分界线数据,header数据,body数据读入到给定的buffer中。

- (NSInteger)read:(uint8_t *)buffer
        maxLength:(NSUInteger)length
{
    NSInteger totalNumberOfBytesRead = 0;

    if (_phase == AFEncapsulationBoundaryPhase) {
        NSData *encapsulationBoundaryData = [([self hasInitialBoundary] ? AFMultipartFormInitialBoundary(self.boundary) : AFMultipartFormEncapsulationBoundary(self.boundary)) dataUsingEncoding:self.stringEncoding];
        //1 将前面的分界线数据写入到buffer中
        totalNumberOfBytesRead += [self readData:encapsulationBoundaryData intoBuffer:&buffer[totalNumberOfBytesRead] maxLength:(length - (NSUInteger)totalNumberOfBytesRead)];
    }

    if (_phase == AFHeaderPhase) {
        //2 将head写入到buffer中
        NSData *headersData = [[self stringForHeaders] dataUsingEncoding:self.stringEncoding];
        totalNumberOfBytesRead += [self readData:headersData intoBuffer:&buffer[totalNumberOfBytesRead] maxLength:(length - (NSUInteger)totalNumberOfBytesRead)];
    }

    if (_phase == AFBodyPhase) {
        NSInteger numberOfBytesRead = 0;
        //3 将body写入到buffer中
        numberOfBytesRead = [self.inputStream read:&buffer[totalNumberOfBytesRead] maxLength:(length - (NSUInteger)totalNumberOfBytesRead)];
        if (numberOfBytesRead == -1) {
            return -1;
        } else {
            totalNumberOfBytesRead += numberOfBytesRead;

            if ([self.inputStream streamStatus] >= NSStreamStatusAtEnd) {
                [self transitionToNextPhase];
            }
        }
    }

    if (_phase == AFFinalBoundaryPhase) {
        NSData *closingBoundaryData = ([self hasFinalBoundary] ? [AFMultipartFormFinalBoundary(self.boundary) dataUsingEncoding:self.stringEncoding] : [NSData data]);
        //4 将后面的分界线写入到buffer中
        totalNumberOfBytesRead += [self readData:closingBoundaryData intoBuffer:&buffer[totalNumberOfBytesRead] maxLength:(length - (NSUInteger)totalNumberOfBytesRead)];
    }

    return totalNumberOfBytesRead;
}


// 将data写入到buffer中，并判断是否执行到下一阶段。
- (NSInteger)readData:(NSData *)data
           intoBuffer:(uint8_t *)buffer
            maxLength:(NSUInteger)length
{
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wgnu"
    NSRange range = NSMakeRange((NSUInteger)_phaseReadOffset, MIN([data length] - ((NSUInteger)_phaseReadOffset), length));
    //1 将data写入到buffer中
    [data getBytes:buffer range:range];
#pragma clang diagnostic pop

    _phaseReadOffset += range.length;
    
    if (((NSUInteger)_phaseReadOffset) >= [data length]) {
    //2 移动到下一阶段
        [self transitionToNextPhase];
    }

    return (NSInteger)range.length;
}

//判断是否移动到下一阶段
- (BOOL)transitionToNextPhase {
    if (![[NSThread currentThread] isMainThread]) {
        dispatch_sync(dispatch_get_main_queue(), ^{
            [self transitionToNextPhase];
        });
        return YES;
    }

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wcovered-switch-default"
    switch (_phase) {
        case AFEncapsulationBoundaryPhase:
            _phase = AFHeaderPhase;
            break;
        case AFHeaderPhase:
            [self.inputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSRunLoopCommonModes];
            [self.inputStream open];
            _phase = AFBodyPhase;
            break;
        case AFBodyPhase:
            [self.inputStream close];
            _phase = AFFinalBoundaryPhase;
            break;
        case AFFinalBoundaryPhase:
        default:
            _phase = AFEncapsulationBoundaryPhase;
            break;
    }
    _phaseReadOffset = 0;
#pragma clang diagnostic pop

    return YES;
}




```


#### AFMultipartBodyStream

```
继承于NSInputStream，遵守NSStreamDelegate协议.最终将组装成的AFMultipartBodyStream赋值给NSMutableURLRequest去发起网络请求。

numberOfBytesInPacket:自定义的总的字节数
delay:每个遍历HTTPBodyParts数组时的休眠的时间，默认为0
inputStream:
contentLength:内容的长度
empty:HTTPBodyParts是否为空
stringEncoding:编码类型
HTTPBodyParts:存放AFHTTPBodyPart数组
HTTPBodyPartEnumerator:HTTPBodyParts的枚举器
currentHTTPBodyPart:当前的AFHTTPBodyPart
outputStream:输出流
buffer:缓冲区数据
setInitialAndFinalBoundaries:设置HTTPBodyParts的分界线。
appendHTTPBodyPart: 将HTTPBodyPart添加到HTTPBodyParts数组中.

//将HTTPBodyParts中的数据遍历读入到buffer中
- (NSInteger)read:(uint8_t *)buffer
        maxLength:(NSUInteger)length
{
    if ([self streamStatus] == NSStreamStatusClosed) {
        return 0;
    }

    NSInteger totalNumberOfBytesRead = 0;

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wgnu"
    while ((NSUInteger)totalNumberOfBytesRead < MIN(length, self.numberOfBytesInPacket)) {
        if (!self.currentHTTPBodyPart || ![self.currentHTTPBodyPart hasBytesAvailable]) {
        //[self.HTTPBodyPartEnumerator nextObject] 下一个对象
            if (!(self.currentHTTPBodyPart = [self.HTTPBodyPartEnumerator nextObject])) {
                break;
            }
        } else {
            NSUInteger maxLength = MIN(length, self.numberOfBytesInPacket) - (NSUInteger)totalNumberOfBytesRead;
            //将当前的currentHTTPBodyPart数据读入到buffer中
            NSInteger numberOfBytesRead = [self.currentHTTPBodyPart read:&buffer[totalNumberOfBytesRead] maxLength:maxLength];
            if (numberOfBytesRead == -1) {
                self.streamError = self.currentHTTPBodyPart.inputStream.streamError;
                break;
            } else {
                totalNumberOfBytesRead += numberOfBytesRead;

                if (self.delay > 0.0f) {
                    [NSThread sleepForTimeInterval:self.delay];
                }
            }
        }
    }
#pragma clang diagnostic pop

    return totalNumberOfBytesRead;
}

//获取内容的长度，作为NSMutbleURLRequest的head的Content-Length的值。
- (unsigned long long)contentLength {
    unsigned long long length = 0;
    for (AFHTTPBodyPart *bodyPart in self.HTTPBodyParts) {
        length += [bodyPart contentLength];
    }

    return length;
}

```

#### AFStreamingMultipartFormData

```
request:NSMutableURLRequest
stringEncoding:编码类型 
boundary;分界标识符
bodyStream:AFMultipartBodyStream类型，最终作为request的HTTPBodyStream。


遵守AFMultipartFormData协议，实现对应的协议方法


- (BOOL)appendPartWithFileURL:(NSURL *)fileURL
                         name:(NSString *)name
                     fileName:(NSString *)fileName
                     mimeType:(NSString *)mimeType
                        error:(NSError * __autoreleasing *)error
{
    NSParameterAssert(fileURL);
    NSParameterAssert(name);
    NSParameterAssert(fileName);
    NSParameterAssert(mimeType);
    //0 对应的是否文件存在
    if (![fileURL isFileURL]) {
        NSDictionary *userInfo = @{NSLocalizedFailureReasonErrorKey: NSLocalizedStringFromTable(@"Expected URL to be a file URL", @"AFNetworking", nil)};
        if (error) {
            *error = [[NSError alloc] initWithDomain:AFURLRequestSerializationErrorDomain code:NSURLErrorBadURL userInfo:userInfo];
        }

        return NO;
    } else if ([fileURL checkResourceIsReachableAndReturnError:error] == NO) {
        NSDictionary *userInfo = @{NSLocalizedFailureReasonErrorKey: NSLocalizedStringFromTable(@"File URL not reachable.", @"AFNetworking", nil)};
        if (error) {
            *error = [[NSError alloc] initWithDomain:AFURLRequestSerializationErrorDomain code:NSURLErrorBadURL userInfo:userInfo];
        }

        return NO;
    }
    NSDictionary *fileAttributes = [[NSFileManager defaultManager] attributesOfItemAtPath:[fileURL path] error:error];
    if (!fileAttributes) {
        return NO;
    }

    NSMutableDictionary *mutableHeaders = [NSMutableDictionary dictionary];
    //1 设置AFHTTPBodyPart的header:Content-Disposition Content-Type，作为上传的数据的一部分
    [mutableHeaders setValue:[NSString stringWithFormat:@"form-data; name=\"%@\"; filename=\"%@\"", name, fileName] forKey:@"Content-Disposition"];
    [mutableHeaders setValue:mimeType forKey:@"Content-Type"];
    //2 创建AFHTTPBodyPart
    AFHTTPBodyPart *bodyPart = [[AFHTTPBodyPart alloc] init];
    bodyPart.stringEncoding = self.stringEncoding;
    bodyPart.headers = mutableHeaders;
    bodyPart.boundary = self.boundary;
    bodyPart.body = fileURL;
    bodyPart.bodyContentLength = [fileAttributes[NSFileSize] unsignedLongLongValue];
    //3 加入bodyStream的数组中
    [self.bodyStream appendHTTPBodyPart:bodyPart];

    return YES;
}

- (void)appendPartWithInputStream:(NSInputStream *)inputStream
                             name:(NSString *)name
                         fileName:(NSString *)fileName
                           length:(int64_t)length
                         mimeType:(NSString *)mimeType
{
    NSParameterAssert(name);
    NSParameterAssert(fileName);
    NSParameterAssert(mimeType);
    
    //1 设置AFHTTPBodyPart的header:Content-Disposition Content-Type，作为上传的数据的一部分
    NSMutableDictionary *mutableHeaders = [NSMutableDictionary dictionary];
    [mutableHeaders setValue:[NSString stringWithFormat:@"form-data; name=\"%@\"; filename=\"%@\"", name, fileName] forKey:@"Content-Disposition"];
    [mutableHeaders setValue:mimeType forKey:@"Content-Type"];
    //2 创建AFHTTPBodyPart
    AFHTTPBodyPart *bodyPart = [[AFHTTPBodyPart alloc] init];
    bodyPart.stringEncoding = self.stringEncoding;
    bodyPart.headers = mutableHeaders;
    bodyPart.boundary = self.boundary;
    bodyPart.body = inputStream;
    bodyPart.bodyContentLength = (unsigned long long)length;
    //3 加入bodyStream的数组中
    [self.bodyStream appendHTTPBodyPart:bodyPart];
}

- (void)appendPartWithFileData:(NSData *)data
                          name:(NSString *)name
                      fileName:(NSString *)fileName
                      mimeType:(NSString *)mimeType
{
    NSParameterAssert(name);
    NSParameterAssert(fileName);
    NSParameterAssert(mimeType);
    //1 设置AFHTTPBodyPart的header:Content-Disposition Content-Type，作为上传的数据的一部分
    NSMutableDictionary *mutableHeaders = [NSMutableDictionary dictionary];
    [mutableHeaders setValue:[NSString stringWithFormat:@"form-data; name=\"%@\"; filename=\"%@\"", name, fileName] forKey:@"Content-Disposition"];
    [mutableHeaders setValue:mimeType forKey:@"Content-Type"];

    [self appendPartWithHeaders:mutableHeaders body:data];
}

- (void)appendPartWithFormData:(NSData *)data
                          name:(NSString *)name
{
    NSParameterAssert(name);
    //1 设置AFHTTPBodyPart的header:Content-Disposition 作为上传的数据的一部分 
    NSMutableDictionary *mutableHeaders = [NSMutableDictionary dictionary];
    [mutableHeaders setValue:[NSString stringWithFormat:@"form-data; name=\"%@\"", name] forKey:@"Content-Disposition"];

    [self appendPartWithHeaders:mutableHeaders body:data];
}

- (void)appendPartWithHeaders:(NSDictionary *)headers
                         body:(NSData *)body
{
    NSParameterAssert(body);
    //1 创建AFHTTPBodyPart
    AFHTTPBodyPart *bodyPart = [[AFHTTPBodyPart alloc] init];
    bodyPart.stringEncoding = self.stringEncoding;
    bodyPart.headers = headers;
    bodyPart.boundary = self.boundary;
    bodyPart.bodyContentLength = [body length];
    bodyPart.body = body;
    //2 加入bodyStream的数组中
    [self.bodyStream appendHTTPBodyPart:bodyPart];
}

//给NSMutableURLRequest设置Content-Type，Content-Length,以及HTTPBodyStream，并返回NSMutableURLRequest进行网络请求。

- (NSMutableURLRequest *)requestByFinalizingMultipartFormData {
    if ([self.bodyStream isEmpty]) {
        return self.request;
    }

    //1 重置开始和结束的分界线
    [self.bodyStream setInitialAndFinalBoundaries];
    //2 设置HTTPBodyStream
    [self.request setHTTPBodyStream:self.bodyStream];
    //3 设置request的head的Content-Type。从self.boundary的值，我们可以识别上传的数据的分界线。以便服务器正确的取出数据。
    [self.request setValue:[NSString stringWithFormat:@"multipart/form-data; boundary=%@", self.boundary] forHTTPHeaderField:@"Content-Type"];
    //4 设置request的head的Content-Length。
    [self.request setValue:[NSString stringWithFormat:@"%llu", [self.bodyStream contentLength]] forHTTPHeaderField:@"Content-Length"];

    return self.request;
}

```


## AFURLResponseSerialization


### AFURLResponseSerialization 协议


```
1 AFURLResponseSerialization 也遵守NSSecureCoding,NSCopying协议。

2 AFHTTPResponseSerializer以及它的子类AFJSONResponseSerializer，AFXMLParserResponseSerializer，AFXMLDocumentResponseSerializer，AFPropertyListResponseSerializer，AFImageResponseSerializer，AFCompoundResponseSerializer遵守该协议，并实现该协议的方法responseObjectForResponse:data:error:。同时也遵守NSSecureCoding,NSCopying的协议，并实现对应的协议方法.

3 responseObjectForResponse:data:error: 根据网络请求返回的NSURLResponse和NSData来处理NSData，不同的子类，返回不同数据格式的responseObject。


```

### AFHTTPResponseSerializer

```
stringEncoding:编码类型
acceptableStatusCodes:能够处理data的状态码范围(200~299)
acceptableContentTypes:可以接收的内容类型。


serializer:类方法
validateResponse:data:error: 验证Response是否有效


- (BOOL)validateResponse:(NSHTTPURLResponse *)response
                    data:(NSData *)data
                   error:(NSError * __autoreleasing *)error
{
    BOOL responseIsValid = YES;
    NSError *validationError = nil;
    //1 验证response本身，是否是可以接收的内容类型
    if (response && [response isKindOfClass:[NSHTTPURLResponse class]]) {
        if (self.acceptableContentTypes && ![self.acceptableContentTypes containsObject:[response MIMEType]] &&
            !([response MIMEType] == nil && [data length] == 0)) {

            if ([data length] > 0 && [response URL]) {
                NSMutableDictionary *mutableUserInfo = [@{
                                                          NSLocalizedDescriptionKey: [NSString stringWithFormat:NSLocalizedStringFromTable(@"Request failed: unacceptable content-type: %@", @"AFNetworking", nil), [response MIMEType]],
                                                          NSURLErrorFailingURLErrorKey:[response URL],
                                                          AFNetworkingOperationFailingURLResponseErrorKey: response,
                                                        } mutableCopy];
                if (data) {
                    mutableUserInfo[AFNetworkingOperationFailingURLResponseDataErrorKey] = data;
                }

                validationError = AFErrorWithUnderlyingError([NSError errorWithDomain:AFURLResponseSerializationErrorDomain code:NSURLErrorCannotDecodeContentData userInfo:mutableUserInfo], validationError);
            }

            responseIsValid = NO;
        }
        //2 是否是可接收的状态码
        if (self.acceptableStatusCodes && ![self.acceptableStatusCodes containsIndex:(NSUInteger)response.statusCode] && [response URL]) {
            NSMutableDictionary *mutableUserInfo = [@{
                                               NSLocalizedDescriptionKey: [NSString stringWithFormat:NSLocalizedStringFromTable(@"Request failed: %@ (%ld)", @"AFNetworking", nil), [NSHTTPURLResponse localizedStringForStatusCode:response.statusCode], (long)response.statusCode],
                                               NSURLErrorFailingURLErrorKey:[response URL],
                                               AFNetworkingOperationFailingURLResponseErrorKey: response,
                                       } mutableCopy];

            if (data) {
                mutableUserInfo[AFNetworkingOperationFailingURLResponseDataErrorKey] = data;
            }

            validationError = AFErrorWithUnderlyingError([NSError errorWithDomain:AFURLResponseSerializationErrorDomain code:NSURLErrorBadServerResponse userInfo:mutableUserInfo], validationError);

            responseIsValid = NO;
        }
    }

    if (error && !responseIsValid) {
        *error = validationError;
    }

    return responseIsValid;
}



```


### AFJSONResponseSerializer

```
readingOptions: 读json数据的类型,NSJSONReadingOptions枚举类型
removesKeysWithNullValues:若返回的json数据中的key对应的value为NSNull，是否将键值对移除。默认为NO。
acceptableContentTypes:可以接收的内容类型, @"application/json", @"text/json", @"text/javascript"
responseObjectForResponse:data:error: 根据网络请求返回的NSURLResponse和NSData来处理NSData


- (id)responseObjectForResponse:(NSURLResponse *)response
                           data:(NSData *)data
                          error:(NSError *__autoreleasing *)error
{
    //1 判断是否是能够处理response
    if (![self validateResponse:(NSHTTPURLResponse *)response data:data error:error]) {
        if (!error || AFErrorOrUnderlyingErrorHasCodeInDomain(*error, NSURLErrorCannotDecodeContentData, AFURLResponseSerializationErrorDomain)) {
            return nil;
        }
    }

    id responseObject = nil;
    NSError *serializationError = nil;
    // Workaround for behavior of Rails to return a single space for `head :ok` (a workaround for a bug in Safari), which is not interpreted as valid input by NSJSONSerialization.
    // See https://github.com/rails/rails/issues/1742
    BOOL isSpace = [data isEqualToData:[NSData dataWithBytes:" " length:1]];
    //2 使用NSJSONSerialization，将data转化成json数据
    if (data.length > 0 && !isSpace) {
        responseObject = [NSJSONSerialization JSONObjectWithData:data options:self.readingOptions error:&serializationError];
    } else {
        return nil;
    }
    //3 移除值为Null的键值对
    if (self.removesKeysWithNullValues && responseObject) {
        responseObject = AFJSONObjectByRemovingKeysWithNullValues(responseObject, self.readingOptions);
    }

    if (error) {
        *error = AFErrorWithUnderlyingError(serializationError, *error);
    }

    return responseObject;
}
```

### AFXMLParserResponseSerializer

```
acceptableContentTypes:可以接收的内容类型, @"application/xml", @"text/xml"
responseObjectForResponse:data:error: 根据网络请求返回的NSURLResponse和NSData来处理NSData

- (id)responseObjectForResponse:(NSHTTPURLResponse *)response
                           data:(NSData *)data
                          error:(NSError *__autoreleasing *)error
{   
    //1 判断是否是能够处理response
    if (![self validateResponse:(NSHTTPURLResponse *)response data:data error:error]) {
        if (!error || AFErrorOrUnderlyingErrorHasCodeInDomain(*error, NSURLErrorCannotDecodeContentData, AFURLResponseSerializationErrorDomain)) {
            return nil;
        }
    }
    //2 将data转化成XML格式的数据
    return [[NSXMLParser alloc] initWithData:data];
}

```
### AFXMLDocumentResponseSerializer

```
acceptableContentTypes:可以接收的内容类型, @"application/xml", @"text/xml"
responseObjectForResponse:data:error: 根据网络请求返回的NSURLResponse和NSData来处理NSData

- (id)responseObjectForResponse:(NSURLResponse *)response
                           data:(NSData *)data
                          error:(NSError *__autoreleasing *)error
{
    //1 判断是否是能够处理response
    if (![self validateResponse:(NSHTTPURLResponse *)response data:data error:error]) {
        if (!error || AFErrorOrUnderlyingErrorHasCodeInDomain(*error, NSURLErrorCannotDecodeContentData, AFURLResponseSerializationErrorDomain)) {
            return nil;
        }
    }

    //2 将data转化成XML的数据
    NSError *serializationError = nil;
    NSXMLDocument *document = [[NSXMLDocument alloc] initWithData:data options:self.options error:&serializationError];

    if (error) {
        *error = AFErrorWithUnderlyingError(serializationError, *error);
    }

    return document;
}


```
### AFPropertyListResponseSerializer

```
acceptableContentTypes:可以接收的内容类型, @"application/x-plist"
responseObjectForResponse:data:error: 根据网络请求返回的NSURLResponse和NSData来处理NSData

- (id)responseObjectForResponse:(NSURLResponse *)response
                           data:(NSData *)data
                          error:(NSError *__autoreleasing *)error
{
    //1 判断是否是能够处理response
    if (![self validateResponse:(NSHTTPURLResponse *)response data:data error:error]) {
        if (!error || AFErrorOrUnderlyingErrorHasCodeInDomain(*error, NSURLErrorCannotDecodeContentData, AFURLResponseSerializationErrorDomain)) {
            return nil;
        }
    }

    id responseObject;
    NSError *serializationError = nil;
    //2 将data转化成PropertyList数据
    if (data) {
        responseObject = [NSPropertyListSerialization propertyListWithData:data options:self.readOptions format:NULL error:&serializationError];
    }

    if (error) {
        *error = AFErrorWithUnderlyingError(serializationError, *error);
    }

    return responseObject;
}


```

### AFImageResponseSerializer

```
acceptableContentTypes:可以接收的内容类型,@"image/tiff", @"image/jpeg", @"image/gif", @"image/png", @"image/ico", @"image/x-icon", @"image/bmp", @"image/x-bmp", @"image/x-xbitmap", @"image/x-win-bitmap"
imageScale:图片的比例
automaticallyInflatesResponseImage:是否自动压缩图片数据，默认为YES

responseObjectForResponse:data:error: 根据网络请求返回的NSURLResponse和NSData来处理NSData

- (id)responseObjectForResponse:(NSURLResponse *)response
                           data:(NSData *)data
                          error:(NSError *__autoreleasing *)error
{
    //1 判断是否是能够处理response
    if (![self validateResponse:(NSHTTPURLResponse *)response data:data error:error]) {
        if (!error || AFErrorOrUnderlyingErrorHasCodeInDomain(*error, NSURLErrorCannotDecodeContentData, AFURLResponseSerializationErrorDomain)) {
            return nil;
        }
    }

#if TARGET_OS_IOS || TARGET_OS_TV || TARGET_OS_WATCH
    //2 返回图片
    if (self.automaticallyInflatesResponseImage) {
        //2.1 返回压缩后的图片
        return AFInflatedImageFromResponseWithDataAtScale((NSHTTPURLResponse *)response, data, self.imageScale);
    } else {
        //2.2 返回正常图片
        return AFImageWithDataAtScale(data, self.imageScale);
    }
#else
    // Ensure that the image is set to it's correct pixel width and height
    NSBitmapImageRep *bitimage = [[NSBitmapImageRep alloc] initWithData:data];
    NSImage *image = [[NSImage alloc] initWithSize:NSMakeSize([bitimage pixelsWide], [bitimage pixelsHigh])];
    [image addRepresentation:bitimage];

    return image;
#endif

    return nil;
}


```



     
  
  
 
  
  