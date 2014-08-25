from django.db import models

class CoreUser(models.Model): # core_user
    username = models.CharField(max_length=128)
    exportId = models.IntegerField(default=-1) # Arbitrary value
    dateCreated = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)
    
class BlogPost(models.Model): # blog_post
    title = models.CharField(max_length=255)
    seoTitle = models.CharField(max_length=255)
    excerpt = models.TextField(blank=True)
    user = models.ForeignKey(CoreUser)
    exportId = models.IntegerField(default=-1) # Arbitrary value

    dateCreated = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)
    created = models.CharField(max_length=30) # Arbitrary value
    published = models.CharField(max_length=30) # Arbitrary value

class CoreComment(models.Model): # core_comments
    post = models.ForeignKey(BlogPost)
    body = models.TextField()
    name = models.CharField(max_length=100)
    user = models.ForeignKey(CoreUser)
    email = models.CharField(max_length=100)
    
    exportId = models.IntegerField(default=-1) # Arbitrary value
    dateCreated = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True)
    created = models.CharField(max_length=30) # Arbitrary value
    published = models.CharField(max_length=30) # Arbitrary value

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
