//
//  UIImage+extension.m
//
//  Created by chiyou on 16/12/20.
//  Copyright © 2016年 chiyou. All rights reserved.
//

#import "UIImage+extension.h"

@implementation UIImage (extension)

#pragma mark - 根据颜色、大小生成矩形图片
+ (UIImage*)imageWithColor:(UIColor*)color andSize:(CGSize)size
{
    CGRect rect =CGRectMake(0.0f,0.0f, size.width, size.height);
    UIGraphicsBeginImageContextWithOptions(rect.size,NO, [UIScreen mainScreen].scale);
    CGContextRef context =UIGraphicsGetCurrentContext();
    CGContextSetFillColorWithColor(context, [color CGColor]);
    CGContextFillRect(context, rect);
    UIImage*image =UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    return image;
}
#pragma mark - 根据颜色、大小、圆弧半径生成圆角矩形图片

+ (UIImage*)imageWithColor:(UIColor*)color andSize:(CGSize)size cornerRadius:(CGFloat)cornerRadius
{
    CGRect rect =CGRectMake(0.0f,0.0f, size.width, size.height);
    UIGraphicsBeginImageContextWithOptions(rect.size,NO, [UIScreen mainScreen].scale);
    CGContextRef context =UIGraphicsGetCurrentContext();
    CGContextSetFillColorWithColor(context, [color CGColor]);
    UIBezierPath *path = [UIBezierPath bezierPathWithRoundedRect:CGRectMake(0, 0, size.width, size.height) cornerRadius:cornerRadius];
    CGContextAddPath(context, path.CGPath);
    CGContextFillPath(context);
    UIImage*image =UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    return image;
}

#pragma mark - 根据原来的图片生成新的图片(圆角+边界)

+ (UIImage*)roundedWithOriginalImage:(UIImage *)originalImage withBorderWidth:(CGFloat)borderWidth borderColor:(UIColor *)borderColor cornerRadius:(CGFloat)cornerRadius {
    CGFloat width =originalImage.size.width;
    CGFloat height =originalImage.size.height;
    UIBezierPath *maskShape;
    maskShape = [UIBezierPath bezierPathWithRoundedRect:CGRectMake(0 ,0, width, height) cornerRadius:cornerRadius];
    UIGraphicsBeginImageContextWithOptions(originalImage.size,NO, [UIScreen mainScreen].scale);
    CGContextRef ctx =UIGraphicsGetCurrentContext();
    //保存上下文
    CGContextSaveGState(ctx);
    CGContextAddPath(ctx, maskShape.CGPath);
    CGContextClip(ctx);
    
    /** 变换坐标系
     * 1 cotext的坐标系，以视图左上角为(0,0)点。x轴水平向右 y轴水平向下
     * 2 CGContextTranslateCTM(ctx,0, height),将坐标系水平下移到视图左下角。
     * 3 CGContextScaleCTM(ctx,1.0,-1.0) x轴不变，y轴进行翻转180度。
     * 4 最终，坐标系为以视图左下角为(0,0)点，x轴水平向右 y轴水平向上
     */
    
    CGContextTranslateCTM(ctx,0, height);
    CGContextScaleCTM(ctx,1.0,-1.0);
    
    CGContextDrawImage(ctx,CGRectMake(0,0, width, height),originalImage.CGImage);
    //恢复上下文
    CGContextRestoreGState(ctx);

    if(borderWidth > 0) {
        [borderColor setStroke];

        UIBezierPath*border = [UIBezierPath bezierPathWithRoundedRect:CGRectMake(borderWidth / 2, borderWidth / 2 , originalImage.size.width - borderWidth  ,originalImage.size.height - borderWidth) cornerRadius:cornerRadius];

        //开启反锯齿功能
        CGContextSetShouldAntialias(ctx,YES);
        CGContextSetAllowsAntialiasing(ctx,YES);
        CGContextSetLineWidth(ctx, borderWidth);
        CGContextAddPath(ctx, border.CGPath);
        CGContextStrokePath(ctx);
    }
    
    UIImage*resultingImage =UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    return resultingImage;
}


#pragma mark - 根据视图的大小来压缩图片，压缩后的图片比例仍是原图的比例。

+ (UIImage *)compressOriginalImage:(UIImage *)originalImage viewSize:(CGSize)viewSize{
    UIImage * resultImage;
    
    CGFloat imageW = originalImage.size.width;
    CGFloat imageH = originalImage.size.height;
    
    CGFloat viewW = viewSize.width;
    CGFloat viewH = viewSize.height;
    
    CGFloat scaleW = viewW /imageW;
    CGFloat scaleH = viewH /imageH;
    
    CGFloat scale = scaleW > scaleH ? scaleW : scaleH;
    
    
    UIGraphicsBeginImageContextWithOptions(CGSizeMake(imageW * scale, imageH * scale), NO, [UIScreen mainScreen].scale);
    [originalImage drawInRect:CGRectMake(0, 0, imageW * scale, imageH * scale)];
    resultImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    
    return resultImage;
}

#pragma mark - 剪切图片
+ (UIImage *)clipWithOriginalImage:(UIImage *)originalImage withClipRect:(CGRect)clipRect {
    
    CGImageRef imageRef = originalImage.CGImage;
    CGFloat scale = originalImage.scale;
    CGImageRef imagePartRef = CGImageCreateWithImageInRect(imageRef,CGRectMake(clipRect.origin.x * scale , clipRect.origin.y * scale , clipRect.size.width  * scale, clipRect.size.height * scale));
    UIImage *newImage=[UIImage imageWithCGImage:imagePartRef scale:scale orientation:originalImage.imageOrientation];
    CGImageRelease(imagePartRef);
    return newImage;
}

#pragma mark - 灰色的图片
+ (UIImage *)grayImageWithOriginalImage:(UIImage *)originalImage {
    int bitmapInfo = kCGImageAlphaNone;
    int width = originalImage.size.width;
    int height = originalImage.size.height;
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceGray();
    CGContextRef context = CGBitmapContextCreate (nil,
                                                  width,
                                                  height,
                                                  8,      // bits per component
                                                  0,
                                                  colorSpace,
                                                  bitmapInfo);
    CGColorSpaceRelease(colorSpace);
    if (context == NULL) {
        return nil;
    }
    CGContextDrawImage(context,
                       CGRectMake(0, 0, width, height), originalImage.CGImage);
    UIImage *grayImage = [UIImage imageWithCGImage:CGBitmapContextCreateImage(context)];
    CGContextRelease(context);
    return grayImage;

}

#pragma mark -- loading
+ (UIImage *)loadingImageWithSize:(CGSize)size withColor:(UIColor *)color
{
    UIImage *loadingImage;
    
    UIGraphicsBeginImageContextWithOptions(size, NO, [UIScreen mainScreen].scale);
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    UIBezierPath *path = [UIBezierPath bezierPath];
    [path moveToPoint:CGPointMake(size.width / 2, 3)];
    [path addLineToPoint:CGPointMake(size.width / 2 - 3, 0)];

    [path moveToPoint:CGPointMake(size.width / 2, 3)];
    [path addLineToPoint:CGPointMake(size.width / 2 - 3, 6)];
    
    [path appendPath:[UIBezierPath bezierPathWithArcCenter:CGPointMake(size.width / 2, size.height / 2) radius:(size.height - 6) / 2 startAngle: - M_PI/2 + M_PI/24 endAngle:M_PI/2 + M_PI clockwise:YES]];
    
    [color setStroke];
    CGContextAddPath(ctx, path.CGPath);
    CGContextStrokePath(ctx);
    
    
    loadingImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    
    
    return loadingImage;
}

@end
