# MeizituSpider
异步IO爬取妹子

使用：

  切换下载的类型请在实例化类的时候，传递类型,legs为网页中的类型名称
  download = MeiZiTuDownload(genre='legs')

  如果需要下载很多页，请修改起始页面和终止页面，修改range中的起始页面(1)以及终止页面(3)
  to_do = [download(num) for num in range(1, 3)]


效果图见文件内~
