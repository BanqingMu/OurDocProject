import django.utils.timezone as timezone
import time
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userinfo')
    user_nickname = models.CharField(max_length = 16, null = True)
    user_icon = models.URLField(null = True)

class FileInformation(models.Model):
    file_id = models.IntegerField(default = 0)
    file_name = models.CharField(max_length = 64)
    file_founder = models.ForeignKey(UserInfo, on_delete = models.CASCADE)
    file_foundTime = models.DateTimeField(auto_now_add = True)
    # file_lastBrowseTime = models.DateTimeField(default=timezone.now)
    file_lastModifiedTime = models.DateTimeField(auto_now = True)
    # file_doc = models.FileField(upload_to = 'word/')
    # file_size = models.IntegerField(default=0)
    file_text = models.TextField(default="")
    file_is_delete = models.SmallIntegerField(default=0)
    file_is_free = models.SmallIntegerField(default = 1)
    # file_teamBelong = models.ForeignKey(TeamInfo, on_delete = models.CASCADE)
    class Meta:
        unique_together = (("file_id"),)

class FileReview(models.Model):
    file_id = models.ForeignKey(FileInformation, on_delete = models.CASCADE)
    user_id = models.ForeignKey(UserInfo, on_delete = models.CASCADE)
    review_text = models.CharField(max_length = 512)
    class Meta:
        unique_together = (("file_id"),)

class RecentBrowse(models.Model):
    file_id = models.ForeignKey(FileInformation, on_delete=models.CASCADE)
    user_id = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    browse_time = models.DateTimeField(auto_now = True)
    class Meta:
        unique_together = (("user_id", "file_id"),)


class TeamInfo(models.Model):
    team_id = models.IntegerField(default = int(str(time.time()).split('.')[0]))
    team_manager = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    team_name = models.CharField(max_length = 16)
    team_description = models.CharField(max_length = 256)
    class Meta:
        unique_together = (("team_id"),)
#
# class TeamUser(models.Model):
#     team_id = models.ForeignKey(TeamInfo, on_delete= models.CASCADE)
#     user_id = models.ForeignKey(UserInfo, on_delete= models.CASCADE)
#     class Meta:
#         unique_together = (("team_id", "user_id"),)
#
#

#
# class AdminInfo(models.Model):
#     admin_id = models.IntegerField(primary_key = True)
#     admin_account = models.CharField(max_length = 16)
#     admin_password = models.CharField(max_length = 16)
#     admin_nickname = models.CharField(max_length = 16)
#     admin_icon = models.URLField()



# class Favorites(models.Model):
#     favorite_id = models.IntegerField(primary_key = True)
#     user_id = models.ForeignKey(UserInfo, on_delete = models.CASCADE)
#     file_num = models.IntegerField()
#     class Meta:
#         unique_together = (("user_id"),)
#
# class FavoritesFile(models.Model):
#     favorite_id = models.ForeignKey(Favorites, on_delete = models.CASCADE)
#     file_id = models.ForeignKey(FileInfo, on_delete = models.CASCADE)
#     class Meta:
#         unique_together = (("favorite_id", "file_id"),)
#

#

#
# class GeneralAuthority(models.Model):
#     file_id = models.ForeignKey(FileInfo, on_delete=models.CASCADE)
#     read_file = models.SmallIntegerField()
#     write_file = models.SmallIntegerField()
#     share_file = models.SmallIntegerField()
#     review_file = models.SmallIntegerField()
#     class Meta:
#         unique_together = (("file_id"),)
#
# class SpecificAuthority(models.Model):
#     file_id = models.ForeignKey(FileInfo, on_delete=models.CASCADE)
#     user_id = models.ForeignKey(UserInfo, on_delete = models.CASCADE)
#     read_file = models.SmallIntegerField()
#     write_file = models.SmallIntegerField()
#     share_file = models.SmallIntegerField()
#     review_file = models.SmallIntegerField()
#     class Meta:
#         unique_together = (("user_id", "file_id"),)

