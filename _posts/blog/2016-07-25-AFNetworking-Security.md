---
layout: post
title: AFNetworking原理:Security(三)
date: 2016-07-23
categories: IOS

---


## AFSecurityPolicy

### 简介

`AFSecurityPolicy`用来在安全连接时以X.509证书和公共密钥(public keys)来评估服务器信任。在你的应用中添加SSL证书，有助于防止中间人袭击和其他安全漏洞。应用处理敏感的客户数据和财富信息时强烈建议所有的交流在https下进行。

### 主要的属性和方法

#### 属性

* `SSLPinningMode`:服务器信任(server trust)应该对固定的(pinned)SSL证书评估的标准。默认是AFSSLPinningModeNone类型。该属性是个枚举类(AFSSLPinningMode)。


```
typedef NS_ENUM(NSUInteger, AFSSLPinningMode) {
    AFSSLPinningModeNone,
    AFSSLPinningModePublicKey,
    AFSSLPinningModeCertificate,
};
AFSSLPinningModeNone:不使用固定的证书去评估服务器
AFSSLPinningModePublicKey:用固定证书的公钥去验证host证书
AFSSLPinningModeCertificate:用固定证书去验证host证书
```



* `pinnedCertificates`:是一个用于评估服务器信任的证书的集合(NSSet),里面每个元素都是一个证书数据(NSData)
* `allowInvalidCertificates`:是否允许使用一个无效的或者过期的SSL证书信任服务器。默认是NO。
* `validatesDomainName`:是否在证书的CN字段中验证host。


#### 方法

* +(NSSet <NSData * > *)certificatesInBundle:(NSBundle * )bundle; 

  ```
  返回bundle中所有的证书集合
  ```
* +(instancetype)defaultPolicy;

  ```
  默认的安全策略:1 不允许无效的证书 2 验证域名 3 不使用固有的证书和公钥进行验证。(AFSSLPinningModeNone)
  ```
* +(instancetype)policyWithPinningMode:(AFSSLPinningMode)pinningMode;

  ```
  用指定的模式，创建并返回安全策略
  ```

* +(instancetype)policyWithPinningMode:(AFSSLPinningMode)pinningMode withPinnedCertificates:(NSSet <NSData * > * )pinnedCertificates;
  
  ```
  用指定的模式以及固有的证书集合，创建并返回安全策略
  ```

* -(BOOL)evaluateServerTrust:(SecTrustRef)serverTrust
                  forDomain:(nullable NSString * )domain;
                  
  ```
  这个方法应该在客户端收到来自服务器的认证挑战(authentication challenge)时被使用。来判断在当前安全策略的下，服务器信任是否被接受。
  ```

* static id AFPublicKeyForCertificate(NSData *certificate)
   
   ```
   根据证书数据来获取公钥
   ```
* static BOOL AFServerTrustIsValid(SecTrustRef serverTrust)
 
   ```
   SecTrustRef: 用于进行X.509证书的信任评估。
   判断该serverTrust是否有效
   ```
     
* static NSArray * AFCertificateTrustChainForServerTrust(SecTrustRef serverTrust) 
  
   ```
   根据SecTrustRef，返回信任的证书链。
   ```

* static NSArray * AFPublicKeyTrustChainForServerTrust(SecTrustRef serverTrust)
  
   ```
   根据SecTrustRef，返回信任的公钥链。
   ```

### 核心代码

#### 1 static id AFPublicKeyForCertificate(NSData *certificate)

```
根据证书数据来获取公钥

static id AFPublicKeyForCertificate(NSData *certificate) {
    id allowedPublicKey = nil;
    SecCertificateRef allowedCertificate;
    SecCertificateRef allowedCertificates[1];
    CFArrayRef tempCertificates = nil;
    SecPolicyRef policy = nil;
    SecTrustRef allowedTrust = nil;
    SecTrustResultType result;
     //1 通过证书的数据，创建一个证书。
    allowedCertificate = SecCertificateCreateWithData(NULL, (__bridge CFDataRef)certificate);
    __Require_Quiet(allowedCertificate != NULL, _out);
    
    allowedCertificates[0] = allowedCertificate;
    tempCertificates = CFArrayCreate(NULL, (const void **)allowedCertificates, 1, NULL);
    //2 返回X.509证书默认的策略
    policy = SecPolicyCreateBasicX509();
    //3 根据传入的证书(certificates)和策略(policies),来创建一个信任评估对象(SecTrustRef).
    __Require_noErr_Quiet(SecTrustCreateWithCertificates(tempCertificates, policy, &allowedTrust), _out);
    //4 评估该对象,并生成评估结果（SecTrustResultType）
    __Require_noErr_Quiet(SecTrustEvaluate(allowedTrust, &result), _out);
    //5 返回已经被评估的证书的公钥
    allowedPublicKey = (__bridge_transfer id)SecTrustCopyPublicKey(allowedTrust);

_out:
    if (allowedTrust) {
        CFRelease(allowedTrust);
    }

    if (policy) {
        CFRelease(policy);
    }

    if (tempCertificates) {
        CFRelease(tempCertificates);
    }

    if (allowedCertificate) {
        CFRelease(allowedCertificate);
    }

    return allowedPublicKey;
}

```

* SecCertificateRef:代表一个X.509证书
* SecPolicyRef:代表一个X.509证书的信任策略
* SecTrustRef: 用于进行X.509证书进行信任评估。
* SecTrustResultType:信任评估的结果类型。

-------

1. 通过证书的数据，创建一个证书。
SecCertificateRef SecCertificateCreateWithData(CFAllocatorRef __nullable allocator,
    CFDataRef data) 
    
2. 返回X.509证书默认的策略
SecPolicyRef SecPolicyCreateBasicX509(void)

3. 根据传入的证书(certificates)和策略(policies),来创建一个信任评估对象(SecTrustRef).
OSStatus SecTrustCreateWithCertificates(CFTypeRef certificates,
    CFTypeRef __nullable policies, SecTrustRef * __nonnull CF_RETURNS_RETAINED trust)

4. 评估该trust对象,并生成评估结果（SecTrustResultType）
OSStatus SecTrustEvaluate(SecTrustRef trust, SecTrustResultType * __nullable result)

5. 返回已经被评估的证书的公钥
SecKeyRef SecTrustCopyPublicKey(SecTrustRef trust)

-----

#### 2 static BOOL AFServerTrustIsValid(SecTrustRef serverTrust)

```
判断该serverTrust是否有效

static BOOL AFServerTrustIsValid(SecTrustRef serverTrust) {
    BOOL isValid = NO;
    SecTrustResultType result;
    //1 评估serverTrust对象，并生成评估结果。
    __Require_noErr_Quiet(SecTrustEvaluate(serverTrust, &result), _out);
    //2 判断该serverTrust是否有效
    isValid = (result == kSecTrustResultUnspecified || result == kSecTrustResultProceed);

_out:
    return isValid;
}


```

#### 3 static NSArray * AFCertificateTrustChainForServerTrust(SecTrustRef serverTrust)

```
根据SecTrustRef，返回信任的证书链。

static NSArray * AFCertificateTrustChainForServerTrust(SecTrustRef serverTrust) {
    //1 返回一个被评估的证书链中证书的个数
    CFIndex certificateCount = SecTrustGetCertificateCount(serverTrust);
    NSMutableArray *trustChain = [NSMutableArray arrayWithCapacity:(NSUInteger)certificateCount];

    for (CFIndex i = 0; i < certificateCount; i++) {
    //2 从证书链中返回一个证书
        SecCertificateRef certificate = SecTrustGetCertificateAtIndex(serverTrust, i);
        [trustChain addObject:(__bridge_transfer NSData *)SecCertificateCopyData(certificate)];
    }

    return [NSArray arrayWithArray:trustChain];
}

```

* CFIndex SecTrustGetCertificateCount(SecTrustRef trust):返回一个被评估的证书链中证书的个数
* SecCertificateRef SecTrustGetCertificateAtIndex(SecTrustRef trust, CFIndex ix): 从证书链中返回一个证书

#### 4 static NSArray * AFPublicKeyTrustChainForServerTrust(SecTrustRef serverTrust)

```
根据SecTrustRef，返回信任的公钥链。

    //1 返回X.509证书默认的策略
    SecPolicyRef policy = SecPolicyCreateBasicX509();
    //2 返回一个被评估的证书链中证书的个数
    CFIndex certificateCount = SecTrustGetCertificateCount(serverTrust);
    NSMutableArray *trustChain = [NSMutableArray arrayWithCapacity:(NSUInteger)certificateCount];
    for (CFIndex i = 0; i < certificateCount; i++) {
        //3 从证书链中返回一个证书
        SecCertificateRef certificate = SecTrustGetCertificateAtIndex(serverTrust, i);

        SecCertificateRef someCertificates[] = {certificate};
        CFArrayRef certificates = CFArrayCreate(NULL, (const void **)someCertificates, 1, NULL);
        //4 根据传入的证书(certificates)和策略(policies),来创建一个信任评估对象(SecTrustRef). 
        SecTrustRef trust;
        __Require_noErr_Quiet(SecTrustCreateWithCertificates(certificates, policy, &trust), _out);
     
        SecTrustResultType result;
        //5 评估该trust对象,并生成评估结果（SecTrustResultType）
        __Require_noErr_Quiet(SecTrustEvaluate(trust, &result), _out);
        //6 返回已经被评估的证书的公钥
        [trustChain addObject:(__bridge_transfer id)SecTrustCopyPublicKey(trust)];

    _out:
        if (trust) {
            CFRelease(trust);
        }

        if (certificates) {
            CFRelease(certificates);
        }

        continue;
    }
    CFRelease(policy);
     //7 返回公钥数组
    return [NSArray arrayWithArray:trustChain];
}

``` 

1. 返回X.509证书默认的策略: SecPolicyCreateBasicX509()
2. 返回一个被评估的证书链中证书的个数:CFIndex SecTrustGetCertificateCount(SecTrustRef trust)
3. 从证书链中返回一个证书:SecCertificateRef SecTrustGetCertificateAtIndex(SecTrustRef trust, CFIndex ix)
4. 根据传入的证书(certificates)和策略(policies),来创建一个信任评估对象(SecTrustRef):OSStatus SecTrustCreateWithCertificates(CFTypeRef certificates,
    CFTypeRef __nullable policies, SecTrustRef * __nonnull CF_RETURNS_RETAINED trust)
    
5. 评估该trust对象,并生成评估结果（SecTrustResultType）:OSStatus SecTrustEvaluate(SecTrustRef trust, SecTrustResultType * __nullable result)
6. 返回已经被评估的证书的公钥: SecKeyRef SecTrustCopyPublicKey(SecTrustRef trust)
7. 返回公钥数组



#### 5 - (BOOL)evaluateServerTrust:(SecTrustRef)serverTrust  forDomain:(NSString *)domain

```
这个方法应该在客户端收到来自服务器的认证挑战(authentication challenge)时被使用。来判断在当前安全策略的下，服务器信任是否被接受。
 
- (BOOL)evaluateServerTrust:(SecTrustRef)serverTrust
                  forDomain:(NSString *)domain
{
    if (domain && self.allowInvalidCertificates && self.validatesDomainName && (self.SSLPinningMode == AFSSLPinningModeNone || [self.pinnedCertificates count] == 0)) {
     
        //1 为了用自签名的证书验证域名，你必须使用固定的证书。
        NSLog(@"In order to validate a domain name for self signed certificates, you MUST use pinning.");
        return NO;
    }

    NSMutableArray *policies = [NSMutableArray array];
    //2 创建策略
    if (self.validatesDomainName) {
        //2.1 如果验证域名，那么创建SSL策略
        [policies addObject:(__bridge_transfer id)SecPolicyCreateSSL(true, (__bridge CFStringRef)domain)];
    } else {
        //2.2 否则，X.509证书默认的策略
        [policies addObject:(__bridge_transfer id)SecPolicyCreateBasicX509()];
    }
    
    //3 给由服务器传入的serverTrust对象，设置策略
    SecTrustSetPolicies(serverTrust, (__bridge CFArrayRef)policies);

    //4 若不使用固定的证书去评估服务器
    if (self.SSLPinningMode == AFSSLPinningModeNone) {
        return self.allowInvalidCertificates || AFServerTrustIsValid(serverTrust);
    } else if (!AFServerTrustIsValid(serverTrust) && !self.allowInvalidCertificates) {
        return NO;
    }

    switch (self.SSLPinningMode) {
        case AFSSLPinningModeNone:
        default:
            return NO;
         //5 用固定证书去验证主机证书
        case AFSSLPinningModeCertificate: {
           //5.1 创建本地固有的证书数组
            NSMutableArray *pinnedCertificates = [NSMutableArray array];
            for (NSData *certificateData in self.pinnedCertificates) {
                [pinnedCertificates addObject:(__bridge_transfer id)SecCertificateCreateWithData(NULL, (__bridge CFDataRef)certificateData)];
            }
            
            //5.2 给这个信任评估对象设置一组锚证书
            SecTrustSetAnchorCertificates(serverTrust, (__bridge CFArrayRef)pinnedCertificates);

            if (!AFServerTrustIsValid(serverTrust)) {
                return NO;
            }

            //5.3 从该信任评估对象对象中取出服务器信任的证书列表
            NSArray *serverCertificates = AFCertificateTrustChainForServerTrust(serverTrust);
            //5.4 遍历serverCertificates，看本地固有的证书(self.pinnedCertificates)中,是否包含服务器信任的证书
            for (NSData *trustChainCertificate in [serverCertificates reverseObjectEnmerator]) {
           
                if ([self.pinnedCertificates containsObject:trustChainCertificate]) {
                    return YES;
                }
            }
            
            return NO;
        }
        //6 用固定证书的公钥去验证主机证书
        case AFSSLPinningModePublicKey: {
            NSUInteger trustedPublicKeyCount = 0;
            //6.1 获取服务器信任的公钥列表
            NSArray *publicKeys = AFPublicKeyTrustChainForServerTrust(serverTrust);
            //6.2 遍历服务器信任的公钥列表（publicKeys），看本地固有的证书的公钥列表(self.pinnedPublicKeys)是否包含服务器信任的某个公钥
            for (id trustChainPublicKey in publicKeys) {
                for (id pinnedPublicKey in self.pinnedPublicKeys) {
                    if (AFSecKeyIsEqualToKey((__bridge SecKeyRef)trustChainPublicKey, (__bridge SecKeyRef)pinnedPublicKey)) {
                        trustedPublicKeyCount += 1;
                    }
                }
            }
            return trustedPublicKeyCount > 0;
        }
    }
    
    return NO;
}

```

* 1 为了用自签名的证书验证域名，你必须使用固定的证书。

* 2 创建评估策略

  ```
   2.1 如果验证域名，那么创建SSL策略
   2.2 否则，X.509证书默认的策略
  ```
  
* 3  给由服务器传入的serverTrust对象，设置策略:OSStatus SecTrustSetPolicies(SecTrustRef trust, CFTypeRef policies)

* 4 若不使用固定的证书去评估服务器

* 5 若用固定证书去验证主机证书

   ```
   5.1 创建本地固有的证书数组
   5.2 给这个信任评估对象设置一组锚证书
   5.3 从该信任评估对象对象中取出服务器信任的证书列表
   5.4 遍历serverCertificates，看本地固有的证书(self.pinnedCertificates)中,是否包含服务器信任的证书
   ```
* 6 用固定证书的公钥去验证主机证书
   
   ```
   6.1 获取服务器信任的公钥列表
   6.2 遍历服务器信任的公钥列表（publicKeys），看本地固有的证书的公钥列表
   ``` 
   
   
   
   
   
###  在框架中的应用