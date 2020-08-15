import json
import random
import time

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, AnonymousUser

from .models import UserInfo, FileInformation, FileReview, RecentBrowse, TeamInfo, GeneralAuthority, SpecificAuthority, \
    Favorites, TeamUser, TeamFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
def sayHello(request):
    return HttpResponse("hello world")

#用于获取用户信息
#myInfo:true
def getInfo(request):
    if request.method == "POST":
        data = json.loads(request.body)
        show_myInfo = data.get("myInfo")

        if show_myInfo is not None and show_myInfo == "true":
            userInfo = UserInfo.objects.get(user = request.user)
            return JsonResponse({
                "status" : 0,
                "nickname" : userInfo.user_nickname,
                "password" : userInfo.user.password,
                "email" : userInfo.user.email
            })
        else :
            #
            return JsonResponse({
                "status" : 1,
                "message": "请求错误"
            })

class FileMethod:


    # #Headers key:content-type value:multipart/form-data
    # #body key:前端的变量名 value:参数值
    # @staticmethod
    # def getFile(request):
    #     if request.method == "POST":
    #         #获取前端传来的word文件 前端字段是word
    #         file_doc = request.FILES.get("word")
    #         file_name = request.POST.get("file_name")
    #         tmpUser = UserInfo.objects.get(user = request.user)
    #         fileInfo = FileInformation(file_founder = tmpUser, file_doc = file_doc,file_name = file_name, file_id = random.randint(10,20))
    #         fileInfo.save()
    #         return JsonResponse({
    #             "status":"0",
    #             "message":"文件上传成功"
    #         })
    #     else:
    #         return JsonResponse({
    #             "status":"1",
    #             "message":"文件上传失败"
    #         })

    #获取文件内容函数 后端会返回一个文件的全部信息 具体返回的参数如下，前端根据需要提取即可:
    # "file_text": retFile.file_text,
    # "file_name": retFile.file_name,
    # "file_founder": retFile.file_founder.user.email,
    # "file_is_delete": retFile.file_is_delete,
    # "file_is_free": retFile.file_is_free,
    # "file_found_time": retFile.file_foundTime,
    # "file_lastModifiedTime": retFile.file_lastModifiedTime

    #需要前端传递的参数
    #getFile:getFile 值不是这个的话不会返回文件相关信息
    #file_id:要获取的文档的id
    @staticmethod
    def getFile(request):
        if request.method == "POST":
            data = json.loads(request.body)
            getFile = data.get("getFile")
            if getFile is not None and getFile == "getFile":
                file_id = data.get("file_id")
                retFile = FileInformation.objects.filter(file_id = file_id).first()
                if retFile:
                    retFile.file_is_free = 0
                    return JsonResponse({
                        "status":0,
                        "file_id":file_id,
                        "file_text":retFile.file_text,
                        "file_name":retFile.file_name,
                        "file_founder":retFile.file_founder.user.email,
                        "file_is_delete":retFile.file_is_delete,
                        "file_is_free":retFile.file_is_free,
                        "file_found_time":retFile.file_foundTime,
                        "file_lastModifiedTime":retFile.file_lastModifiedTime
                    })
                else:
                    return JsonResponse({
                        "status":1,
                        "message":"该文档不存在"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 3,
                "message": "请求错误"
            })

    #用于分享文档 会返回文档id
    #shareFile:shareFile
    #file_id:文档id
    @staticmethod
    def shareFile(request):
        if request.method == "POST":
            data = json.loads(request.body)
            shareFile = data.get("shareFile")
            if shareFile is not None and shareFile == "shareFile":
                file_id = data.get("file_id")
                retFile = FileInformation.objects.filter(file_id = file_id).first()
                if retFile and retFile.file_is_delete == 0:
                    return JsonResponse({
                        "status" : 0,
                        "file_id" : file_id
                    })
                else :
                    return JsonResponse({
                        "status": 1,
                        "message": "要的分享文档不存在"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 3,
                "message": "请求错误"
            })

    @staticmethod
    def myFile(request):
        if request.method == "POST":
            data = json.loads(request.body)
            myfile = data.get("myfile")
            if myfile is not None and myfile == "myfile":
                tmpUser = request.user
                userInfo = UserInfo.objects.filter(user = tmpUser).first()
                fileSet = FileInformation.objects.filter(file_founder = userInfo)
                fileNameSet = []
                fileIdSet = []
                cnt = 0
                for i in fileSet:
                    if i.file_is_delete == 0:
                        fileNameSet.append(i.file_name)
                        fileIdSet.append(i.file_id)
                        cnt += 1
                return JsonResponse({
                    "status": 0,
                    "fileNameSet":fileNameSet,
                    "fileIdSet":fileIdSet
                })
            else:
                return JsonResponse({
                    "status": 1,
                    "message" : "参数错误"
                })
        else:
            return JsonResponse({
                "status": 2,
                "message":"请求错误"
            })
    #用于申请编辑文档 如果当前没人占用此文档 就会返回该文档的全部信息（数据库里存储的有关本文档的全部内容）
    #editFile:editFile
    #file_id:file_id
    @staticmethod
    def applyEditFile(request):
        if request.method == "POST":
            data = json.loads(request.body)
            editFile = data.get("editFile")
            if editFile is not None and editFile == "editFile":
                file_id = data.get("file_id")
                retFile = FileInformation.objects.filter(file_id=file_id).first()
                print(retFile.file_is_free)
                if retFile:
                    if retFile.file_is_free == 1 and retFile.file_is_delete == 0:
                        retFile.file_is_free = 0
                        retFile.save()
                        return JsonResponse({
                            "status": 0,
                            "file_text": retFile.file_text,
                            "file_name": retFile.file_name,
                            "file_founder": retFile.file_founder.user.email,
                            "file_is_delete": retFile.file_is_delete,
                            "file_is_free": retFile.file_is_free,
                            "file_found_time": retFile.file_foundTime,
                            "file_lastModifiedTime": retFile.file_lastModifiedTime
                        })
                    else:
                        return JsonResponse({
                            "status" : 1,
                            "message" : "请求的文档正在被他人编辑或已被删除"
                        })
                else:
                    return JsonResponse({
                        "status": 2,
                        "message": "文档不存在"
                    })
            else:
                return JsonResponse({
                    "status": 3,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 4,
                "message": "请求错误"
            })


    #用于上传更新过的富文本 如果是修改富文本内容一定要调用这个函数！！！！！！！！！！
    #postFile:postFile
    #file_id:file_id
    #newContent:更新后的富文本内容
    #newName:更新后的文档名字 即使没改名字也要给后端
    @staticmethod
    def postModifiedFile(request):
        if request.method == "POST":
            data = json.loads(request.body)
            postFile = data.get("postFile")
            if postFile is not None and postFile == "postFile":
                file_id = data.get("file_id")
                fileInfo = FileInformation.objects.filter(file_id = file_id).first()
                if fileInfo:
                    newContent = data.get("newContent")
                    newName = data.get("newName")
                    fileInfo.file_text = newContent
                    fileInfo.file_name = newName
                    fileInfo.file_is_free = 1
                    fileInfo.save()
                    return JsonResponse({
                        "status" : 0,
                        "message" : "更新文档成功"
                    })
                else:
                    return JsonResponse({
                        "status": 1,
                        "message": "要更改的文档不存在"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 3,
                "message": "请求错误"
            })


    #最近浏览
    #recent:recent
    @staticmethod
    def recentBrowse(request):
        if request.method == "POST":
            data = json.loads(request.body)
            recent = data.get("recent")
            if recent is not None and recent == "recent":
                tmpUser = request.user
                userInfo = UserInfo.objects.get(user = tmpUser)
                recentFiles = RecentBrowse.objects.filter(user_id = userInfo).order_by("browse_time")
                recentFilesList = list(recentFiles)
                retNameList = []
                retTimeList = []
                retFileIdList = []
                cnt = 0
                for i in recentFilesList:
                    if i.file_id.file_is_delete != 1:
                        retNameList.append(i.file_id.file_name)
                        retTimeList.append(i.browse_time)
                        retFileIdList.append(i.file_id.file_id)
                        cnt += 1
                return JsonResponse({
                    "status":1,
                    # "list":recentFilesList
                    "namelist":retNameList,
                    "timelist":retTimeList,
                    "fileIdList":retFileIdList,
                    "message":"已经返回最近浏览的文件名字列表"
                })
            else:
                return JsonResponse({
                    "status":2,
                    "message":"请求参数错误"
                })
        return JsonResponse({
            "status": 3,
            "message": "请求方法错误"
        })


    #用于上传全新的富文本
    @staticmethod
    def uploadFileText(request):
        #需要的前端参数
        #upload:是否上传 如果参数值是upload就表明请求上传
        #content：富文本信息
        #file_name:文件名字
        print("1111111")
        if request.method == "POST":
            print("文本函数")
            data = json.loads(request.body)
            upload = data.get("upload")
            if upload == "upload":
                print("这个是upload")
                content = data.get("content")
                if content is not None:
                    print("content不是空值")
                    tmpUser = request.user
                    file_name = data.get("file_name")
                    userInfo = UserInfo.objects.get(user = tmpUser)
                    fileInfo = FileInformation(file_text = content, file_founder = userInfo, file_is_free = 1, file_is_delete = 0,
                                               file_name = file_name, file_id = int(str(time.time()).split('.')[0]))
                    fileInfo.save()
                    genAuthority = GeneralAuthority(file_info = fileInfo, read_file = 0, write_file = 0, share_file = 0, review_file = 0)
                    genAuthority.save()
                    speAuthority = SpecificAuthority(user_info = userInfo, file_info = fileInfo,
                                                     read_file = 1, write_file = 1, share_file = 1, review_file = 1)
                    speAuthority.save()
                    return JsonResponse({
                        "status":0,
                        "message":"富文本上传成功"
                    })
                else:
                    return JsonResponse({
                        "status": 1,
                        "message": "富文本无内容"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "非上传请求"
                })
        else :
            return JsonResponse({
                "status": 3,
                "message": "请求方式错误"
            })


    @staticmethod
    def checkGeneralAuthority(request):
        if request.method == "POST":
            data = json.loads(request.body)
            checkGerneralAuthority = data.get("checkGerneralAuthority")
            if checkGerneralAuthority is not None and checkGerneralAuthority == "checkGerneralAuthority":
                file_id = data.get("file_id")
                fileInfo = FileInformation.objects.filter(file_id=file_id).first()
                if fileInfo:
                    genAuthority = GeneralAuthority.objects.filter(file_info=fileInfo).first()
                    if genAuthority:
                        return JsonResponse({
                            "status": 0,
                            "file_id":file_id,
                            "read": genAuthority.read_file,
                            "write": genAuthority.write_file,
                            "share": genAuthority.share_file,
                            "review": genAuthority.review_file,
                        })
                    else:
                        return JsonResponse({
                            "status": 1,
                            "message": "文档不存在"
                        })
                else:
                    return JsonResponse({
                        "status": 1,
                        "message": "文档不存在"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 3,
                "message": "请求错误"
            })

    @staticmethod
    def setGeneralAuthority(request):
        if request.method == "POST":
            data = json.loads(request.body)
            setGenAuthor = data.get("setGenAuthor")
            if setGenAuthor is not None and setGenAuthor == "setGenAuthor":
                file_id = data.get("file_id")
                fileInfo = FileInformation.objects.filter(file_id = file_id).first()
                if fileInfo:
                    genAuthor = GeneralAuthority.objects.filter(file_info = fileInfo).first()
                    if genAuthor:
                        genAuthor.read_file = data.get("read_file")
                        genAuthor.write_file = data.get("write_file")
                        genAuthor.share_file = data.get("share_file")
                        genAuthor.review_file = data.get("review_file")
                        genAuthor.save()
                        return JsonResponse({
                            "status" : 0,
                            "file_id":file_id,
                            "message" : "修改通用权限成功",
                            "read_file": genAuthor.read_file,
                            "write_file": genAuthor.write_file,
                            "share_file": genAuthor.share_file,
                            "review_file": genAuthor.review_file,
                        })
                    else:
                        return JsonResponse({
                            "status": 1,
                            "message": "修改通用权限失败"
                        })
                else:
                    return JsonResponse({
                        "status": 2,
                        "message": "文档不存在"
                    })
            else:
                return JsonResponse({
                    "status":3,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 4,
                "message": "请求错误"
            })




    @staticmethod
    def checkSpecificAuthority(request):
        if request.method == "POST":
            data = json.loads(request.body)
            checkSpecificAuthority = data.get("checkSpecificAuthority")
            if checkSpecificAuthority is not None and checkSpecificAuthority == "checkSpecificAuthority":
                tmpUser = request.user
                userInfo = UserInfo.objects.filter(user = tmpUser).first()
                if userInfo is not AnonymousUser:
                    file_id = data.get("file_id")
                    fileInfo = FileInformation.objects.filter(file_id = file_id).first()
                    if fileInfo:
                        speAuthority = SpecificAuthority.objects.filter(file_info = fileInfo, user_info = userInfo).first()
                        if speAuthority:
                            return JsonResponse({
                                "status" : 0,
                                "file_id":file_id,
                                "read" : speAuthority.read_file,
                                "write": speAuthority.write_file,
                                "share": speAuthority.share_file,
                                "review": speAuthority.review_file,
                            })
                        else:

                                return JsonResponse({
                                    "status": 1,
                                    "message":"该用户不存在该文件的特定权限"
                                })
                    else:
                        return JsonResponse({
                            "status": 1,
                            "message" : "文档不存在"
                        })
                else:
                    return JsonResponse({
                        "status": 2,
                        "message": "用户不存在或未登陆"
                    })
            else:
                return JsonResponse({
                    "status": 3,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 4,
                "message": "请求错误"
            })

    @staticmethod
    def setSpecificAuthority(request):
        if request.method == "POST":
            data = json.loads(request.body)
            setSpeAuthor = data.get("setSpeAuthor")
            if setSpeAuthor is not None and setSpeAuthor == "setSpeAuthor":
                file_id = data.get("file_id")
                fileInfo = FileInformation.objects.filter(file_id = file_id).first()
                userInfo = UserInfo.objects.filter(user = request.user).first()
                if fileInfo:
                    SpeAuthor = SpecificAuthority.objects.filter(file_info = fileInfo, user_info = userInfo).first()
                    if SpeAuthor:
                        SpeAuthor.read_file = data.get("read_file")
                        SpeAuthor.write_file = data.get("write_file")
                        SpeAuthor.share_file = data.get("share_file")
                        SpeAuthor.review_file = data.get("review_file")
                        SpeAuthor.save()
                        return JsonResponse({
                            "status" : 0,
                            "message" : "修改特定权限成功",
                            "file_id":file_id,
                            "read_file": SpeAuthor.read_file,
                            "write_file": SpeAuthor.write_file,
                            "share_file": SpeAuthor.share_file,
                            "review_file": SpeAuthor.review_file,
                        })
                    else:
                        return JsonResponse({
                            "status": 1,
                            "message": "修改特定权限失败，文档不存在或无该用户的特定权限记录"
                        })
                else:
                    return JsonResponse({
                        "status": 2,
                        "message": "文档不存在"
                    })
            else:
                return JsonResponse({
                    "status":3,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 4,
                "message": "请求错误"
            })
    #用于判断文档是否处于可编辑状态
    @staticmethod
    def getFileEditStatus(request):
        #需要前端传递的参数:
        #freeFile:这个参数的值是freeOrNot时 会认为是在请求查看文档是否处于free状态
        #file_id:文档id

        if request.method == "POST":
            data = json.loads(request.body)
            freeFile = data.get("freeFile")
            if freeFile is not None and freeFile == "freeOrNot":
                file_id = data.get("file_id")
                tmpFile = FileInformation.objects.filter(file_id = file_id).first()
                if tmpFile:
                    if tmpFile.file_is_free == 1:
                        return JsonResponse({
                            "status":0,
                            "file_id":file_id,
                            "message":"可以编辑"
                        })
                    else:
                        return JsonResponse({
                            "status":1,
                            "file_id": file_id,
                            "message":"不可编辑"
                        })
                else:
                    return JsonResponse({
                        "status": 2,
                        "message": "文件不存在"
                    })
            else:
                return JsonResponse({
                    "status": 3,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 4,
                "message": "请求方法错误"
            })

    @staticmethod
    # 将文件移动到回收站
    #delete_file:delete_file
    #file_id:需要回复的文档id
    def moveto_recyclebin(request):
        if request.method == "POST":
            data = json.loads(request.body)
            delete_file = data.get("delete_file")
            if delete_file is not None and delete_file == "delete_file":
                fileInfo = FileInformation.objects.filter(file_id=data.get("file_id")).first()
                if fileInfo and fileInfo.file_is_delete == 0:
                    fileInfo.file_is_delete = 1
                    fileInfo.save()
                    return JsonResponse({
                        "status": 0,
                        "file_id": data.get("file_id"),
                        "data": "删除成功"

                    })
                else:
                    return JsonResponse({
                        "status": 1,
                        "message": "该文件不存在或已经被删除"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 3,
                "message": "请求错误"
            })

    @staticmethod
    # 从回收站回复
    #recover_file:recover_file
    #file_id:需要回复的文档id
    def recoverfrom_recyclebin(request):
        if request.method == "POST":
            data = json.loads(request.body)
            recover_file = data.get("recover_file")
            if recover_file is not None and recover_file == "recover_file":
                fileInfo = FileInformation.objects.filter(file_id=data.get("file_id")).first()
                if fileInfo and fileInfo.file_is_delete == 1:
                    fileInfo.file_is_delete = 0
                    fileInfo.save()
                    return JsonResponse({
                        "status": 0,
                        "file_id":data.get("file_id"),
                        "data": "恢复成功"
                    })
                else:
                    return JsonResponse({
                        "status": 1,
                        "message": "该文件不存在或已经被恢复"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 3,
                "message": "请求错误"
            })

    @staticmethod
    def addFileToTeam(request):
        if request.method == "POST":
            data = json.loads(request.body)
            addFileToTeam = data.get("addFileToTeam")
            if addFileToTeam is not None and addFileToTeam == "addFileToTeam":
                file_id = data.get("file_id")
                team_id = data.get("team_id")
                fileInfo = FileInformation.objects.filter(file_id = file_id).first()
                teamInfo = TeamInfo.objects.filter(team_id = team_id).first()
                if teamInfo and fileInfo:
                    fileExistence = TeamFile.objects.filter(file_info = fileInfo)
                    if fileExistence:
                        return JsonResponse({
                            "status":1,
                            "message":"团队中已经包含该文档"
                        })
                    else:
                        teamFile = TeamFile(file_info = fileInfo, team_info = teamInfo)
                        teamFile.save()
                        return JsonResponse({
                            "status":0,
                            "file_id":file_id,
                            "team_id":team_id
                        })
                else:
                    return JsonResponse({
                        "status":1,
                        "message":"团队或文档不存在"
                    })
            else :
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 3,
                "message": "请求错误"
            })

    @staticmethod
    def deleteFileFromTeam(request):
        if request.method == "POST":
            data = json.loads(request.body)
            deleteFileFromTeam = data.get("deleteFileFromTeam")
            if deleteFileFromTeam is not None and deleteFileFromTeam == "deleteFileFromTeam":
                file_id = data.get("file_id")
                team_id = data.get("team_id")
                fileInfo = FileInformation.objects.filter(file_id=file_id).first()
                teamInfo = TeamInfo.objects.filter(team_id=team_id).first()
                if teamInfo and fileInfo:
                    teamFile = TeamFile.objects.filter(file_info = fileInfo, team_info = teamInfo)
                    teamFile.delete()
                    return JsonResponse({
                        "status": 0,
                        "message":"删除成功"
                    })
                else:
                    return JsonResponse({
                        "status": 1,
                        "message": "团队或文档不存在"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 3,
                "message": "请求错误"
            })

    @staticmethod
    def showTeamFile(request):
        if request.method == "POST":
            data = json.loads(request.body)
            showteamfile = data.get("showteamfile")
            if showteamfile is not None and showteamfile == "showteamfile":
                team_id = data.get("team_id")
                teamInfo = TeamInfo.objects.filter(team_id = team_id).first()
                if teamInfo:
                    teamfilelist = TeamFile.objects.filter(team_info = teamInfo)
                    retFileIdList = []
                    retFileNameList = []
                    for i in teamfilelist:
                        retFileIdList.append(i.file_info.file_id)
                        retFileNameList.append(i.file_info.file_name)
                    return JsonResponse({
                        "status":0,
                        "retFileIdList":retFileIdList,
                        "retFileNameList":retFileNameList
                    })
                else:
                    return JsonResponse({
                        "status": 1,
                        "message":"团队不存在"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        else:
            return JsonResponse({
                "status": 3,
                "message": "请求错误"
            })




class UserMethod:

    @staticmethod
    def hello(request):
        email = "nihao@qq.com"
        userSet = UserInfo.objects.all()
        for i in userSet:
            if i.user.email == email:
                tmpUser = i
                break
        print(tmpUser.user_nickname)
        return JsonResponse({
            "nickname":tmpUser.user_nickname
        })

    @staticmethod
    def get_status(request):
        if request.user.is_authenticated:
            return JsonResponse({
                "status": 0,
                "username": str(request.user),
                "email": str(request.user.email),
            })
        else:
            return JsonResponse({
                "status": 1
            })

    @staticmethod
    def login_user(request):
        if request.method == "POST":
            print("JPYJPY")
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")
            print("登陆")
            print(email)
            print(password)
            if email is not None and password is not None:
                islogin = authenticate(request, username=email, password=password)
                if islogin:
                    login(request, islogin)
                    return JsonResponse({
                        "status": 0,
                        "message": "Login Success",
                        "email": email
                    })
                else:
                    return JsonResponse({
                        "status": 1,
                        "message": "登录失败, 请检查用户名或者密码是否输入正确."
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "参数错误"
                })
        return JsonResponse({
            "status": 3,
            "message": "请求错误"
        })


    # 注销
    @staticmethod
    def logout_user(request):
        logout(request)
        return JsonResponse({
            "status": 0
        })


    @staticmethod
    def register(request):
        if request.method == "POST":
            data = json.loads(request.body)

            if request.GET.get("select") is not None:
                print("select 是" + request.GET.get("select"))
                select_username = data.get("select_username")
                print(select_username)
                try:
                    User.objects.get(username=select_username)
                    return JsonResponse({
                        "status": 0,
                        "is_indb": 1
                    })
                except:
                    print("except")
                    return JsonResponse({
                        'status': 0,
                        "is_indb": 0
                    })
            print("1111111")
            username = data.get("email")
            password = data.get("password")
            email = data.get("email")
            nickname = data.get("nickname")
            print(username)
            print(password)
            print(email)
            if username is not None and password is not None and email is not None:
                try:
                    user = User.objects.create_user(username=email, password=password, email=email)
                    user.save()
                    userInfo = UserInfo(user = user)
                    userInfo.user_nickname = nickname
                    userInfo.save()
                    login_user = authenticate(request, username=username, password=password)
                    if login_user:
                        login(request, login_user)
                        print("注册成功!!!!")
                        return JsonResponse({
                            "status": 0,

                            "message": "Register and Login Success"
                        })

                except:
                    return JsonResponse({
                        "status": 2,
                        "message": "注册失败, 该用户名已经存在."
                    })

        else:
            return JsonResponse({
                "status": 1,
                "message": "error method"
            })

    @staticmethod
    def modify_nickname(request):
        if request.method == "POST":
            data = json.loads(request.body)
            new_nickname = data.get("nickname")

            if len(new_nickname) == 0:
                #昵称为空返回status和message
                return JsonResponse({
                    "status" : 0,
                    "message" : "新昵称不可为空"
                })
            elif len(new_nickname) > 16 :
                #昵称长度大于16返回status和message
                return JsonResponse({
                    "status": 0,
                    "message": "新昵称过长"
                })
            else :
                userInfo = UserInfo.objects.get(user = request.user)
                userInfo.user_nickname = new_nickname
                userInfo.save()
                print(userInfo.user.email)
                print(userInfo.user_nickname)
                #修改成功返回status、message、以及修改后的新昵称new_nickname
                return JsonResponse({
                    "status" : 1,
                    "message" : "昵称修改成功",
                    "new_nickname" : new_nickname
                })




#用于给文档添加评论
#add_review:add_review
#review_text:评论内容
#file_id:文档id
def add_review(request):
    if request.method == "POST":
        data = json.loads(request.body)
        add_review = data.get("add_review")
        # 添加评论
        if add_review is not None and add_review == "add_review":
            # 将json转换为python dict格式
            if data.get("review_text") is not None:
                # try:
                fileInfo = FileInformation.objects.filter(file_id=data.get("file_id")).first()
                userInfo = UserInfo.objects.get(user = request.user)
                db = FileReview(review_text=data.get("review_text"), user_id=userInfo,file_id=fileInfo)
                db.save()
                return JsonResponse({
                    "status_code": 0,
                    "data": "success",
                    "file_id": data.get("file_id")
                })
            else:
                return JsonResponse({
                    "status_code": 1,
                    "error": "text is none"
                })
        else:
            return JsonResponse({
                "status": 2,
                "message": "add_review is none"
            })
    else:
        return JsonResponse({
            "status": 3,
            "message": "error method"
        })




#创建团队
def create_team(request):
    if request.method == "POST":
        data = json.loads(request.body)
        create = data.get("create")
        if create is not None and create=="create":
            # 将json转换为python dict格式
            # try:
            tmpUser = request.user
            userInfo = UserInfo.objects.filter(user = tmpUser).first()
            team_description = data.get("team_description")
            team_name = data.get("team_name")
            db = TeamInfo(team_name=team_name, team_manager=userInfo,
                          team_description=team_description, team_id = int(str(time.time()).split('.')[0]))
            db.save()
            return JsonResponse({
                "status_code": 0,
                "data": "create success"
            })
        else:
            return JsonResponse({
                "status": 1,
                "message": "create is none"
            })
    else:
        return JsonResponse({
            "status": 2,
            "message": "error method"
        })



def add_favorite(request):
    if request.method == "POST":
        data = json.loads(request.body)
        add_favorite = data.get("add_favorite")
        if add_favorite is not None and add_favorite=="add_favorite":
            tmpUser = request.user
            userInfo = UserInfo.objects.filter(user = tmpUser).first()
            fileInfo = FileInformation.objects.filter(file_id=data.get("file_id")).first()
            #该文件未被删除
            if fileInfo and fileInfo.file_is_delete==0:
                #该文件未被该用户收藏
                if Favorites.objects.filter(user_info=userInfo,file_info=fileInfo).first():
                    return JsonResponse({
                        "status": 0,
                        "data": "您已收藏该文件！"
                    })
                else:
                    db = Favorites(user_info=userInfo, file_info=fileInfo,
                               favorite_id = int(str(time.time()).split('.')[0]))
                    db.save()
                    return JsonResponse({
                        "status": 1,
                        "data": "收藏成功！",
                        "file_id": data.get("file_id")
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "该文件不存在或已被用户删除！"
                })
    else:
        return JsonResponse({
            "status": 3,
            "message": "error method"
        })


# 删除收藏
def delete_favorite(request):
    if request.method == "POST":
        data = json.loads(request.body)
        delete_favorite = data.get("delete_favorite")
        if delete_favorite is not None and delete_favorite == "delete_favorite":
            tmpUser = request.user
            userInfo = UserInfo.objects.filter(user=tmpUser).first()
            tmpfavorite = Favorites.objects.filter(favorite_id=data.get("favorite_id")).first()
            # 该文件位于用户收藏夹中
            if tmpfavorite and userInfo:
                tmpfavorite.delete()
                return JsonResponse({
                    "status_code": 0,
                    "data": "删除收藏成功！",
                    "file_id":data.get("file_id")
                })
            else:
                return JsonResponse({
                    "status": 1,
                    "message": "该文件不存在或已被用户删除或不在该用户收藏夹中！"
                })
    else:
        return JsonResponse({
            "status": 2,
            "message": "error method"
        })


#用户收藏
def my_favorite(request):
    if request.method == "POST":
        data = json.loads(request.body)
        my_favorite = data.get("my_favorite")
        if my_favorite is not None and my_favorite == "my_favorite":
            tmpUser = request.user
            userInfo = UserInfo.objects.get(user=tmpUser)
            myFavoriteFiles = Favorites.objects.filter(user_info=userInfo).order_by("favorite_id")
            myFavoriteList = list(myFavoriteFiles)
            retNameList = []
            retFavoriteIdList = []
            retFileIdList = []
            cnt = 0
            for i in myFavoriteList:
                if i.file_info.file_is_delete != 1:
                    retFavoriteIdList.append(i.favorite_id)
                    retNameList.append(i.file_info.file_name)
                    retFileIdList.append(i.file_info.file_id)
                    cnt += 1
            return JsonResponse({
                "status": 1,
                "favoriteIdlist": retFavoriteIdList,
                "namelist": retNameList,
                "message": "已经返回用户收藏夹的文件名字列表"
            })
        else:
            return JsonResponse({
                "status": 2,
                "message": "请求参数错误"
            })
    return JsonResponse({
        "status": 3,
        "message": "请求方法错误"
    })


def add_teammate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        add_teammate = data.get("add_teammate")
        if add_teammate is not None and add_teammate=="add_teammate":
            #团队管理员
            teamManageUser = request.user
            teamManageuserInfo = UserInfo.objects.filter(user = teamManageUser).first()
            #团队
            teamInfo = TeamInfo.objects.filter(team_id=data.get("team_id")).first()
            #用户
            user_email = data.get("user_email")
            tmpUser = UserInfo()
            userSet = UserInfo.objects.all()
            flag = 0
            for i in userSet:
                if i.user.email == user_email:
                    tmpUser = i
                    flag += 1
                    break
            #团队与管理员对应
            teamMatch=TeamInfo.objects.filter(team_manager=teamManageuserInfo,team_id=data.get("team_id")).first()
            if teamInfo and flag == 1 and teamManageuserInfo and teamMatch:
                #该用户在该团队内
                if TeamUser.objects.filter(user_info=tmpUser,team_info=teamInfo).first():
                    return JsonResponse({
                        "status": 0,
                        "data": "该用户已在该团队内！"
                    })
                else:
                    db = TeamUser(user_info=tmpUser, team_info=teamInfo)
                    db.save()
                    return JsonResponse({
                        "status": 1,
                        "data": "用户添加成功！"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "团队、用户、团队所属人不存在或团队与所属人不匹配！"
                })
    else:
        return JsonResponse({
            "status": 3,
            "message": "error method"
        })

def delete_teammate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        delete_teammate = data.get("delete_teammate")
        if delete_teammate is not None and delete_teammate=="delete_teammate":
            #团队管理员
            teamManageUser = request.user
            teamManageuserInfo = UserInfo.objects.filter(user = teamManageUser).first()
            #团队
            teamInfo = TeamInfo.objects.filter(team_id=data.get("team_id")).first()
            #用户
            user_email = data.get("user_email")
            tmpUser = UserInfo()
            userSet = UserInfo.objects.all()
            flag = 0
            for i in userSet:
                if i.user.email == user_email:
                    tmpUser = i
                    flag += 1
                    break
            #团队与管理员对应
            teamMatch=TeamInfo.objects.filter(team_manager=teamManageuserInfo,team_id=data.get("team_id")).first()
            if teamInfo and flag == 1 and teamManageuserInfo and teamMatch:
                #该用户在该团队内
                teamUser = TeamUser.objects.filter(user_info=tmpUser, team_info=teamInfo).first()
                if teamUser:
                    teamUser.delete()
                    return JsonResponse({
                        "status": 0,
                        "data": "已删除"
                    })
                else:
                    return JsonResponse({
                        "status": 1,
                        "data": "为查询到相关团队信息"
                    })
            else:
                return JsonResponse({
                    "status": 2,
                    "message": "团队、用户、团队所属人不存在或团队与所属人不匹配！"
                })
    else:
        return JsonResponse({
            "status": 3,
            "message": "error method"
        })

def myTeam(request):
    if request.method == "POST":
        data = json.loads(request.body)
        myteam = data.get("myteam")
        if myteam is not None and myteam == "myteam":
            tmpUser = request.user
            userInfo = UserInfo.objects.filter(user = tmpUser).first()
            managerSet = TeamInfo.objects.filter(team_manager = userInfo)
            memberSet = TeamUser.objects.filter(user_info = userInfo)
            retTeamIdlist = []
            retTeamNamelist = []
            for i in managerSet:
                retTeamIdlist.append(i.team_id)
                retTeamNamelist.append(i.team_name)
            for j in memberSet:
                retTeamIdlist.append(j.team_info.team_id)
                retTeamNamelist.append(j.team_info.team_name)
            return JsonResponse({
                "status":0,
                "retTeamIdlist":retTeamIdlist,
                "retTeamNamelist":retTeamNamelist
            })
        else:
            return JsonResponse({
                "status": 1,
                "message" : "参数错误"
            })
    else:
        return JsonResponse({
            "status": 2,
            "message": "请求错误"
        })


def test(request):
    if request.method == "POST":
        print("JPY请求成功！！！！！！")
    return JsonResponse({
        "status":0
    })
