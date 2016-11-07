---
layout: post
title: AFNetworking3源码:AFURLRequestSerialization(一)
date: 2016-07-21
categories: IOS

---

## AFURLRequestSerialization

### 主要作用
 其主要作用是为我们进行网络请求构建了一个配置好的NSMutableURLRequest。
  
### 主要的类

**一 声明了两个C语言方法**

 * `AFPercentEscapedStringFromString(NSString *string)`:去除非法字符并且对特殊字符进行编码
 * `AFQueryStringFromParameters(NSDictionary *parameters)`: 将参数字典序列化为查询字符串(query),即`key=value&key=value...`的形式
 
**二 声明了两个协议**

 1 AFURLRequestSerialization
 
 ```
AFURLRequestSerialization遵守NSSecureCoding,NSCopying协议。所以遵守该协议的类只要实现NSSecureCoding,NSCopying对应的方法，就可以进行归档和copy了。

`AFHTTPRequestSerializer`遵守该协议，同样`AFHTTPRequestSerializer`的子类`AFJSONRequestSerializer`,`AFPropertyListRequestSerializer`遵守该协议，并实现协议方法
 `requestBySerializingRequest:withParameters:error:`
 
 协议方法`requestBySerializingRequest:withParameters:error:`:处理参数字典，并设置`Content-Type`,组成网络请求`NSURLRequest`并返回.


```

2 AFMultipartFormData
  
```
AFStreamingMultipartFormData遵守该协议,并实现下列协议方法，上传文件数据。

appendPartWithFileURL:name:error:
appendPartWithFileURL:name:fileName:mimeType:error:
appendPartWithInputStream:name:fileName:length:mimeType:
appendPartWithFileData:name:fileName:mimeType:     
appendPartWithFormData:name:(NSString *)name;
appendPartWithHeaders:body:(NSData *)body;
                          
```

三 AFHTTPRequestSerializer

* 遵守AFHTTPRequestSerializer协议
* 属性 & 方法

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

* 核心方法:requestWithMethod:URLString:parameters:error:

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


* 核心方法:multipartFormRequestWithMethod:URLString:parameters:constructingBodyWithBlock:error:


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
                [formData appendPartWithFormData:data name:[pair.field description]];
            }
        }
    }
    //4 回调block
    if (block) {
        block(formData);
    }
   
   //5 调用requestByFinalizingMultipartFormData返回组成好的NSMutableURLRequest.
   return [formData requestByFinalizingMultipartFormData];
}


```











## 参考

* [WebViewJavascriptBridge源码分析](http://blog.csdn.net/mociml/article/details/47701133)



     
  
  
 
  
  