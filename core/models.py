from django.db import models

class CoreUser(models.Model): # core_user
    username     = models.CharField(max_length=128)
    exportId     = models.IntegerField(default=-1) # Arbitrary value
    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)
    
class BlogPost(models.Model): # blog_post
    user      = models.ForeignKey(CoreUser)
    title     = models.CharField(max_length=255)
    seoTitle  = models.CharField(max_length=255)
    excerpt   = models.TextField(blank=True)
    exportId  = models.IntegerField(default=-1) # Arbitrary value
    created   = models.CharField(max_length=30) # Arbitrary value
    published = models.CharField(max_length=30) # Arbitrary value

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class CoreComment(models.Model): # core_comments
    post = models.ForeignKey(BlogPost)
    body = models.TextField()
    name = models.CharField(max_length=100)
    user = models.ForeignKey(CoreUser)
    email = models.CharField(max_length=100)
    
    created      = models.CharField(max_length=30) # Arbitrary value
    published    = models.CharField(max_length=30) # Arbitrary value
    exportId     = models.IntegerField(default=-1) # Arbitrary value
    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class Forum(models.Model): # forum_forum
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    
    exportId = models.IntegerField(default=-1) # Arbitrary value
    created = models.CharField(max_length=30) # Arbitrary value
    modified = models.CharField(max_length=30) # Arbitrary value
    published = models.CharField(max_length=30) # Arbitrary value
    locked = models.IntegerField(default=0)
    status = models.IntegerField(default=1)

    dateCreated = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class ForumPost(models.Model): # forum_posts
    user = models.ForeignKey(CoreUser)
    forum = models.ForeignKey(Forum)
    parent = models.ForeignKey('ForumPost', blank=True, default=None)

    body = models.TextField(blank=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    
    special = models.CharField(max_length=100)
    exportId = models.IntegerField(default=-1) # Arbitrary value
    created = models.CharField(max_length=100) # From older datetime as str
    modified = models.CharField(max_length=100) # From older datetime as str

    dateCreated = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class Group(models.Model): # acl_roles
    exportId = models.IntegerField(default=-1) # Arbitrary value
    title    = models.CharField(max_length=100)
    status   = models.IntegerField(default=1)
    locked   = models.IntegerField(default=0)
    created  = models.CharField(max_length=100) # From older datetime as str
    parentId = models.ForeignKey('Group', null=True)
    modified = models.CharField(max_length=100) # From older datetime as str

    dateCreated = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class Video(models.Model): # core_videos
    exportId     = models.IntegerField(default=-1) # Arbitrary value
    accessKey    = models.CharField(max_length=32)
    title        = models.CharField(max_length=256)
    description  = models.TextField(blank=True)
    created      = models.CharField(max_length=100) # From older datetime as str
    publishDate  = models.CharField(max_length=100) # From older datetime as str
    uploadedBy   = models.ForeignKey(CoreUser)
    download     = models.IntegerField(default=2)
    embed        = models.IntegerField(default=2)
    published    = models.IntegerField(default=0)

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class Category(models.Model): # core_categories
    name         = models.CharField(max_length=64)
    seoName      = models.CharField(max_length=64)
    description  = models.TextField(blank=True)
    userId       = models.ForeignKey(CoreUser)
    status       = models.IntegerField(default=0)
    created      = models.CharField(max_length=100) # From older datetime as str
    parentId     = models.ForeignKey('Category', null=True)
    exportId     = models.IntegerField(default=-1) # Arbitrary value

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class VideoCategory(models.Model): # core_videos_categories
    videoId     = models.ForeignKey(Video)
    categoryId  = models.ForeignKey(Category)
    exportId    = models.IntegerField(default=-1) # Arbitrary value

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class Playlist(models.Model): # necessitated by core_video_playlist_videos
    exportId     = models.IntegerField(default=-1) # Arbitrary value

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class VideoPlaylist(models.Model): # core_video_playlist_videos
    playlist = models.ForeignKey(Playlist)
    video    = models.ForeignKey(Video)

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)

class Mail(models.Model): # core_mail
    messageClass = models.CharField(max_length=31)
    messageData  = models.TextField(blank=True)
    sendOn       = models.CharField(max_length=100) # From older datetime as str
    sentOn       = models.CharField(max_length=100) # From older datetime as str
    priority     = models.IntegerField(default=-1)
    created      = models.CharField(max_length=100) # From older datetime as str
    modified     = models.CharField(max_length=100) # From older datetime as str

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)
