---
layout: post
title: git基本用法
date: 2016-05-08
categories: Git

---


## git简介

### git作用

git是进行版本控制的工具。

### 利用github建立一个git仓库

#### 方法1:直接克隆远程仓库（建议）

1 首先注册一个github账号

2 新建一个仓库，如下图，并且点击`creating repository`

![](http://7xqijx.com1.z0.glb.clouddn.com/git%E4%BB%93%E5%BA%93.png)

3 克隆这个仓库到桌面

   * cd到桌面
   
     `$ cd ~/desktop `
    
   * 克隆仓库
   
     `$ git clone https://github.com/lhjzzu/learngit`
     
        Cloning into 'learngit'...
        remote: Counting objects: 11, done.
        remote: Compressing objects: 100% (7/7), done.
        remote: Total 11 (delta 2), reused 7 (delta 1), pack-reused 0
        Unpacking objects: 100% (11/11), done.
        Checking connectivity... done.
    
   * 添加文件
        
        $ cd ./learngit
        $ touch test.txt (创建test.txt文件)
        $ open test.txt (输入这是一个测试)
        $ git add . (添加所有文件到版本库的暂存区)
        $ git commit -m 'first commit' （把暂存区的所有内容提交到当前分支）
        
   * 把本地的分支的修改推送到远端
     
     `$ git push`
     
        Counting objects: 3, done.
        Delta compression using up to 8 threads.
        Compressing objects: 100% (2/2), done.
        Writing objects: 100% (3/3), 283 bytes | 0 bytes/s, done.
        Total 3 (delta 1), reused 0 (delta 0)
        To https://github.com/lhjzzu/learngit
           ffc4dff..c422d8d  master -> master
     
#### 方法2:建立本地仓库，并与远程仓库关联

1 首先注册一个github账号

2 新建一个仓库，如下图，并且点击`creating repository`

![](http://7xqijx.com1.z0.glb.clouddn.com/git%E4%BB%93%E5%BA%93.png)

3 在本地建立git仓库，并与远端仓库关联到一起

   * 建立learngit文件夹并进入文件夹
   
   
        $ cd ~/desktop
        $ mkdir learngit
        $ cd ./learngit
    
   * 初始化仓库
    
       `$ git init  `  
        
        Initialized empty Git repository in /Users/chiyou/Desktop/learngit/.git/
   
   * 添加文件
   
        $ touch test.txt (创建test.txt文件)
        $ open test.txt (输入这是一个测试)
        $ git add . (添加所有文件到版本库的暂存区)
        $ git commit -m 'first commit' （把暂存区的所有内容提交到当前分支）
        
   * 与远程仓库建立连接
    
     `$ git remote add origin https://github.com/lhjzzu/learngit`
     
     
   * 由于远程仓库中的信息与本地并不一直，先进行拉取  
   
     `$ git pull`
     
        See git-pull(1) for details.
          git pull <remote> <branch>
        If you wish to set tracking information for this branch you can do so with:
          git branch --set-upstream-to=origin/<branch> master
          
   * 由上面的信息可知，我们需要设置本地仓库与远程仓库的拉取的关联(pull)
     
     `$ git branch --set-upstream-to=origin/master master `
   
        Branch master set up to track remote branch master from origin.
        
     `$ git pull`
     
        Merge made by the 'recursive' strategy.
        .gitignore | 53 +++++++++++++++++++++++++++++++++++++++++++++++++++++
        LICENSE    | 21 +++++++++++++++++++++
        README.md  |  2 ++
        3 files changed, 76 insertions(+)
        create mode 100644 .gitignore
        create mode 100644 LICENSE
        create mode 100644 README.md
      
   * 把本地的分支的修改推送到远端
   
     `$ git push`
     
        Counting objects: 5, done.
        Delta compression using up to 8 threads.
        Compressing objects: 100% (3/3), done.
        Writing objects: 100% (5/5), 512 bytes | 0 bytes/s, done.
        Total 5 (delta 1), reused 0 (delta 0)
        To https://github.com/lhjzzu/learngit
           fe6b1e2..10c8b9c  master -> master
     
   
   
   
   
## learngit结构分析

工作区:learngit文件夹就是工作区

版本库:工作区中的隐藏目录,.git就是版本库

* 查看.git目录的相关信息
  
        $ cd ~/desktop/learngit
        $ cd .git
        $ ls -F1
        
        COMMIT_EDITMSG
        HEAD
        branches/
        config
        description
        hooks/
        index
        info/
        logs/
        objects/
        packed-refs
        refs/
  
* 关于.git目录下的各项的作用请参考[这篇文章](http://www.zhihu.com/question/38983686?sort=created)

暂存区：版本库中的stage（或者index）就是暂存区，还有Git为我们自动创建的第一个分支master，以及指向master的一个指针叫HEAD。



   
## 参考
* [代码签名探析](http://objccn.io/issue-17-2/)
* [iOS证书及ipa包重签名探究](http://www.olinone.com/?p=198)
* [ReCodeSign](https://gist.github.com/0xc010d/1365444)
 



     
  
  
 
  
  