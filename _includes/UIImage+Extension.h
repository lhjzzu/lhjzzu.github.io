//
//  UIImage+extension.h
//
//  Created by chiyou on 16/12/20.
//  Copyright © 2016年 chiyou. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface UIImage (extension)


/**
 根据颜色和大小生成矩形图片

 @param color 图片颜色
 @param size  图片大小

 @return 生成的图片
 */
+ (UIImage*)imageWithColor:(UIColor*)color andSize:(CGSize)size;


/**
 根据颜色,大小,圆弧半径生成圆角矩形图片

 @param color        图片颜色
 @param size         图片大小
 @param cornerRadius 圆弧半径

 @return 生成的圆角矩形图片
 */

+ (UIImage*)imageWithColor:(UIColor*)color andSize:(CGSize)size cornerRadius:(CGFloat)cornerRadius;


/**
 根据原来的图片生成新的图片(圆角+边界)

 @param originalImage 原图
 @param borderWidth   border的宽度
 @param borderColor   border的颜色
 @param cornerRadius  圆弧半径

 @return 新的圆角矩形图片(圆角+边界)
 */
+ (UIImage*)roundedWithOriginalImage:(UIImage *)originalImage withBorderWidth:(CGFloat)borderWidth borderColor:(UIColor*)borderColor cornerRadius:(CGFloat)cornerRadius;

/**
 根据视图的尺寸来压缩/放大原图，压缩/放大后得到的图片的比例仍是原图的比例(图片不变形)。
 
 原图的宽与视图宽的比率 > 原图的高与视图高的比率 。那么按照视图的高来压缩/放大。
 原图的宽与视图宽的比率 < 原图的高与视图高的比率 。那么按照视图的宽来压缩/放大。

 @param originalImage  原图
 @param viewSize       视图的尺寸

 @return 返回压缩/放大后的图片
 */
+ (UIImage *)compressOriginalImage:(UIImage *)originalImage viewSize:(CGSize)viewSize;


/**
 根据剪切区域剪切图片

 @param originalImage 要被剪切的图片
 @param clipRect      剪切的区域

 @return 剪切后的图片
 */
+ (UIImage *)clipWithOriginalImage:(UIImage *)originalImage withClipRect:(CGRect)clipRect;


/**
 根据原图生成对应的灰色图片

 @param originalImage 原图

 @return 对应的灰色图片
 */
+ (UIImage *)grayImageWithOriginalImage:(UIImage *)originalImage;


+ (UIImage *)loadingImageWithSize:(CGSize)size withColor:(UIColor *)color;
@end
