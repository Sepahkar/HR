from datetime import datetime
from django.db.models import F, ExpressionWrapper, fields
from HR import models as HRMODEL
from django.shortcuts import render
from django.http import HttpResponse
import json
from django.conf import settings
import os
# from datetime import datetime
import json
from django.core.paginator import Paginator
from HR.utils import call_api_post
from HR.jwt import init_tokens
# from django.db.models import F, ExpressionWrapper, fields
# from HR import models as HRMODEL
from django.http.response import JsonResponse
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
import jdatetime
from django.db.models import Q
# def get_user_teamrole(request,teamcode,roleid,levelid,superior):
#     userTeamRole = HRMODEL.UserTeamRole.objects.filter(RoleId__RoleId=roleid,TeamCode__TeamCode=teamcode,LevelId=levelid
#                                                   ,Superior=superior).values('UserName__UserName','UserName__FirstName','UserName__LastName','UserName__FieldOfStudy','UserName__BirthDate')
#
#     duration = ExpressionWrapper(datetime.now().date() - F('UserName__BirthDate'), output_field=fields.DurationField())
#
#     data = HRMODEL.UserTeamRole.objects.filter(RoleId__RoleId=roleid, TeamCode__TeamCode=teamcode, LevelId=levelid
#                                    , Superior=superior).annotate(duration=duration)
#     print(data)
#     return "a"


def UserPageList(request):
    page_name = 'user_list'
    obj_list = list(HRMODEL.Users.objects.all())
    obj_info = HRMODEL.UserTeamRole.objects.all()
    # page = request.GET.get('page', 1)
    # paginator = Paginator(obj_info, 10)
    # try:
    #     obj_info = paginator.page(page)
    # except PageNotAnInteger:
    #     obj_info = paginator.page(1)
    # except EmptyPage:
    #     obj_info = paginator.page(paginator.num_pages)
    content = {
        "obj_list": obj_list,
        'obj_info': obj_info,
        'page_name': page_name,
    }
    return render(request, 'HR/userlist.html', content)


def GeneralInfo(username, page_name, request):
    current_user = request.user.username
    # read user info
    user_info = HRMODEL.Users.objects.filter(UserName=username).first()
    # check if this user exists
    if user_info is None:
        context = {"valid_person": False, "message": "شخص مورد نظر پیدا نشد"}
        return context
    edit_permission = False
    page = HRMODEL.PageInformation.objects.filter(EnglishName=page_name).first()

    # if send user is not current user, we must check his access
    if current_user != username:
        # check if this user access this page
        page_access_control = HRMODEL.V_PagePermission.objects.filter(UserName=current_user, Page__EnglishName=page_name).first()
        if page_access_control is None:
            context = {"valid_person": False, "permission": False, "message":"دسترسی برای این کاربر مجاز نمی باشد"}
            return context
        # check if this user has edit access to this page
        edit_permission = page_access_control.Editable

    # get all user access for bookmark
    page_access = HRMODEL.V_PagePermission.objects.filter(UserName=current_user).exclude(Page__EnglishName='first-page')
    # page_access = HRMODEL.V_PagePermission.objects.filter(UserName=current_user).filter(~Q(Page__PageName='first-page'))

    fullname = user_info.FirstName + ' ' + user_info.LastName
    # remove @eit from user name: m.sepahkar@eit.com -> m.sepahkar
    user_name = username.split('@')[0]
    user = {"username": user_name, "fullname": fullname, "full_username": username}

    # get this user roles
    roles = []
    user_role = HRMODEL.UserTeamRole.objects.filter(UserName=username)
    for r in user_role:
        role_title = r.RoleId.RoleName
        if r.Superior:
            role_title += ' ارشد '
        if r.LevelId:
            role_title += ' ' + r.LevelId.LevelName
        role_title += ' (تيم ' + r.TeamCode.TeamName + ')'
        roles.append({"title": role_title, "role": r.RoleId.RoleName, "team": r.TeamCode.TeamName,
                      "level": r.LevelId, "from_date": r.StartDate, "superior": r.Superior})

    # if this page has detail
    show_detail = page.ShowDetail

    context = {
        "page": page,
        "username": username,
        "user": user,
        "valid_person": True,
        "roles": roles,
        "edit_permission": edit_permission,
        'show_detail': show_detail,
        "current_user":current_user,
        "full_permission":False,
        "page_access": page_access,
    }
    return context


def FirstPage(request, username=''):
    context = GeneralInfo(username, 'first-page', request)
    return render(request, 'HR/layout.html', context)


def ContactInfoPage(request, username=''):
    context = GeneralInfo(username, 'contact', request)

    if context["valid_person"]:
        addresses = list(HRMODEL.PostalAddress.objects.filter(Person_id=username))
        phones = list(HRMODEL.PhoneNumber.objects.filter(Person_id=username))
        tel_type = HRMODEL.ConstValue.objects.filter(Parent__Code='TelType')
        emails = list(HRMODEL.EmailAddress.objects.filter(Person_id=username))
        city = HRMODEL.City.objects.all()
        province = HRMODEL.Province.objects.all()
        city_district = HRMODEL.CityDistrict.objects.all()
        context.update(
            {
                "addresses": addresses,
                "phones": phones,
                "emails": emails,
                "city": city,
                "province": province,
                "tel_type": tel_type,
                "city_district": city_district,
            })
    return render(request, 'HR/contact-info.html', context)


def EducationHistory(request, username=''):
    context = GeneralInfo(username, 'education', request)

    if context["valid_person"]:
        education_history = list(HRMODEL.EducationHistory.objects.filter(Person_id=username))
        university_type = HRMODEL.ConstValue.objects.filter(Parent__Code='UniversityType')
        degree_Type = HRMODEL.ConstValue.objects.filter(Parent__Code='DegreeType')
        city = HRMODEL.City.objects.all()
        province = HRMODEL.Province.objects.all()
        university = HRMODEL.University.objects.all()
        tendency = HRMODEL.Tendency.objects.all()
        field_of_study = HRMODEL.FieldOfStudy.objects.all()
        context.update(
            {
                "education_history": education_history,
                "city": city,
                "province": province,
                "university": university,
                "tendency": tendency,
                "field_of_study": field_of_study,
                "degree_Type": degree_Type,
                "university_type": university_type,
            })
    return render(request, 'HR/education-info.html', context)


# def UserView(request, username=''):
#     context = {}
#     obj_edit = {}
#     obj_uni = {}
#     obj_address = {}
#     obj_Phone = {}
#     obj_Email = {}
#     obj_History = {}
#     CurrentYear = 1400
#     obj_History_name = {}
#     if username != '':
#         ValidPerson = True
#         obj_edit = HRMODEL.Users.objects.filter(UserName=username).first()
#         obj_uni = list(HRMODEL.EducationHistory.objects.filter(Person_id=username))
#         obj_address = list(HRMODEL.PostalAddress.objects.filter(Person_id=username))
#         obj_Phone = list(HRMODEL.PhoneNumber.objects.filter(Person_id=username))
#         obj_Email = list(HRMODEL.EmailAddress.objects.filter(Person_id=username))
#         obj_History = HRMODEL.UserTeamRole.objects.filter(UserName=username)
#         obj_History_name = HRMODEL.UserTeamRole.objects.filter(UserName=username).first()
#     else:
#         ValidPerson = False
#
#     City = HRMODEL.City.objects.all()
#     Province = HRMODEL.Province.objects.all()
#     University = HRMODEL.University.objects.all()
#     Tendency = HRMODEL.Tendency.objects.all()
#     FieldOfStudy = HRMODEL.FieldOfStudy.objects.all()
#     UniversityTypeChoice = HRMODEL.ConstValue.objects.filter(Parent__Code='UniversityType')
#     MarriageStatusList = HRMODEL.ConstValue.objects.filter(Parent__Code='MarriageStatus')
#     DegreeType = HRMODEL.ConstValue.objects.filter(Parent__Code='DegreeType')
#     MilitaryServiceList = HRMODEL.ConstValue.objects.filter(Parent__Code='MilitaryService')
#     TelTypeChoices = HRMODEL.ConstValue.objects.filter(Parent__Code='TelType')
#     CityDistrict = HRMODEL.CityDistrict.objects.all()
#     Team = HRMODEL.Team.objects.all()
#     Role = HRMODEL.Role.objects.all()
#     Level = HRMODEL.RoleLevel.objects.all()
#
#     context = {
#         "CurrentYear": CurrentYear,
#         "CityList": City,
#         "ProvinceList": Province,
#         "UniversityTypeChoice": UniversityTypeChoice,
#         "ValidPerson": ValidPerson,
#         "DegreeType": DegreeType,
#         "MarriageStatusList": MarriageStatusList,
#         "MilitaryServiceList": MilitaryServiceList,
#         "University": University,
#         "TelTypeChoices": TelTypeChoices,
#         "Tendency": Tendency,
#         "FieldOfStudy": FieldOfStudy,
#         "CityDistrict": CityDistrict,
#         "obj_History": obj_History,
#         "Team": Team,
#         "Role": Role,
#         "Level": Level,
#         "username": username,
#         'obj_History_name': obj_History_name,
#
#     }
#
#     if obj_edit is None:
#         context.update({'Message': 'شخص مورد نظر پیدا نشد'})
#     context.update({'obj_edit': obj_edit, 'ValidPerson': ValidPerson, 'obj_uni': obj_uni, 'obj_address': obj_address,
#                     'obj_Phone': obj_Phone, 'obj_Email': obj_Email})
#
#     # return render(request, 'HR/useredit.html', context)
#     return render(request, 'HR/layout1.html', context)


# def UserView(request,username=''):

def is_not_empty(variable):
    if variable is None or variable == '' or \
            ((type(variable) == int or type(variable) == float) and variable == 0):
        return False
    return True


def get_numeric_value(value, value_type="int"):
    if not is_not_empty(value):
        return 0
    else:
        if type(value) == str and value.strip().isnumeric():
            if value_type == "float":
                return float(value)
            else:
                return int(value)


def get_checkbox_value(value):
    if value == "on":
        return True
    else:
        return False


def UserSave(request, action_type=''):
    if request.method == 'POST':
        # ابتدا اطلاعات باید دریافت شوند
        username = request.POST.get('user_name')
        if is_not_empty(username):
            username += '@eit'
        lastname = request.POST.get('last_name')
        firstname = request.POST.get('first_name')
        lastname_english = request.POST.get('last_name_english')
        firstname_english = request.POST.get('first_name_english')
        father_name = request.POST.get('father_name')
        national_code = request.POST.get('national_code')
        number_of_children = get_numeric_value(request.POST.get('number-of-children'))
        about = request.POST.get('about')
        military_status = get_numeric_value(request.POST.get('military'))
        marriage_status = get_numeric_value(request.POST.get('marriage'))
        degree_type = get_numeric_value(request.POST.get('Degree'))
        birth_city = get_numeric_value(request.POST.get('birth_city'))
        gender = get_numeric_value(request.POST.get('gender'))
        birth_date = request.POST.get('birthday')
        religion = get_numeric_value(request.POST.get('religion'))
        identity_number = get_numeric_value(request.POST.get('identity_number'))
        identity_serial_number = get_numeric_value(request.POST.get('identity_serial_number'))
        insurance_number = get_numeric_value(request.POST.get('insurance_number'))
        role = get_numeric_value(request.POST.get('role'))
        team = request.POST.get('team')
        level = get_numeric_value(request.POST.get('level'))
        contract_date = request.POST.get('contract-date')


        arr_date = contract_date.split('/')
        contract_gdate = jdatetime.JalaliToGregorian(int(arr_date[0]),int(arr_date[1]),int(arr_date[2]))
        contract_gdate = str(contract_gdate.gyear) + "-" +  str(contract_gdate.gmonth) +  "-" + str(contract_gdate.gday)



        arr_date = birth_date.split('/')
        birth_gdate = jdatetime.JalaliToGregorian(int(arr_date[0]),int(arr_date[1]),int(arr_date[2]))
        birth_gdate = str(birth_gdate.gyear) + "-" +  str(birth_gdate.gmonth) +  "-" + str(birth_gdate.gday)


        # cv_file = request.get('CVFile')


        # لیست ها باید کنترل شود و در صورت وجود ذخیره شوند
        # اگر وضعیت نظام وظیفه معتبر نباشد
        exist = HRMODEL.ConstValue.objects.filter(id=military_status, Parent__Code='MilitaryService').exists()
        if not exist: military_status = None
        # اگر وضعیت تاهل معتبر نباشد
        exist = HRMODEL.ConstValue.objects.filter(id=marriage_status, Parent__Code='MarriageStatus').exists()
        if not exist: marriage_status = None

        # اگر اخرین مدرک معتبر نباشد
        exist = HRMODEL.ConstValue.objects.filter(id=degree_type, Parent__Code='DegreeType').exists()
        if not exist: degree_type = None

        # اگر شهر محل تولد معتبر نباشد
        exist = HRMODEL.City.objects.filter(id=birth_city).exists()
        if not exist: birth_city = None


        # ابتدا چک می کنیم که فیلدهای اجباری مقدار داشته باشند
        if is_not_empty(firstname) and is_not_empty(lastname) and is_not_empty(username):
            # check if there is a user with same national code
            obj = HRMODEL.Users.objects.filter(NationalCode=national_code).first()
            msg = ""
            # if it is insert mode, repeated national code is not allow
            # or if it is in update mode and this national code is for another username
            if obj and ((action_type == 'i') or (obj.UserName != username and action_type == 'u')):
                msg = "این کد ملی قبلا برای " + "<a href='/HR/" + obj.UserName + "/'>" + obj.FirstName + " " + obj.LastName + "</a>" + " ثبت شده است."

            # بررسی می کنیم که این کاربر وجود دارد یا خیر
            user = HRMODEL.Users.objects.filter(UserName=username)



            # if user is exists
            if user:
                user = user[0]
                # we are in insert mode and there is a user with same username
                if action_type == 'i':
                    msg = "این نام کاربری قبلا برای " + "<a href='/HR/" + user.UserName + "/'>" + user.FirstName + " " + user.LastName + "</a>" + " ثبت شده است."
            # if user is not exists
            else:
                # if we are in edit mode but user is not exists
                if action_type == 'u':
                    msg = "متاسفانه اطلاعات این کاربر وجود ندارد. در صورت نیاز به تعریف کاربر جدید" + "<a href='/HR/'>اینجا</a>" + "را کلیک کنید"
                # if user not exists and we are in insert mode
                else:
                    user = HRMODEL.Users()

            if msg != "":
                return HttpResponse(
                    json.dumps({"success": False, "Message": msg}),
                    content_type="application/json")

            # اکنون فیلدها را مقداردهی می کنیم
            user.UserName = username
            user.LastName = lastname
            user.FirstName = firstname
            user.LastNameEnglish = lastname_english
            user.FirstNameEnglish = firstname_english
            if is_not_empty(national_code): user.NationalCode = national_code
            user.NumberOfChildren = number_of_children
            user.ContractDate = contract_gdate
            user.About = about
            if is_not_empty(birth_city): user.BirthCity_id = birth_city
            if is_not_empty(military_status): user.Military_Status_id = military_status
            if is_not_empty(birth_date): user.BirthDate = birth_gdate
            if is_not_empty(marriage_status): user.Marriage_Status_id = marriage_status
            if is_not_empty(degree_type): user.Degree_Type_id = degree_type
            user.FatherName = father_name
            if is_not_empty(religion): user.Religion_id = religion
            if is_not_empty(identity_number): user.IdentityNumber = identity_number
            if is_not_empty(identity_serial_number): user.IdentitySerialNumber = identity_serial_number
            if is_not_empty(insurance_number): user.InsuranceNumber = insurance_number
            user.Gender = True if gender else False

            user.save()
            if level == 0:
                level = None

            exist = HRMODEL.UserTeamRole.objects.filter(UserName=username).exists()

            manager_username = HRMODEL.V_RoleTeam.objects.filter(RoleID=role,TeamCode=team).only('ManagerUserName')
            if manager_username.exists():
                manager_username = manager_username.first().ManagerUserName.UserName
            if not exist:
                user_team_role = HRMODEL.UserTeamRole(
                    UserName=user,
                    RoleId_id=role,
                    LevelId_id=level,
                    TeamCode_id=team,
                    Superior=0,
                    StartDate=contract_date,
                    ManagerUserName_id=manager_username,
                )

                user_team_role.save()


            if 'Avatar' in request.FILES:
                myfile = request.FILES['Avatar']
                fs = FileSystemStorage()
                ext = myfile.name.split(".")[1]
                new_name = username.replace("@eit", "") + "." + ext
                file_uri = os.path.join(settings.MEDIA_ROOT, new_name)
                if os.path.exists(file_uri):
                    os.remove(file_uri)
                filename = fs.save(file_uri, myfile)
                uploaded_file_url = fs.url(filename)

            context = GeneralInfo(username, 'person', request)


            # append this line for fix
            if 'page' in context:
                new_page = context.get('page').__dict__
                new_page.pop("_state")
                context.update({'page':new_page})

            if 'roles' in context:
                tmp_roles = []
                for item in context.get('roles'):
                    tmp_item = item
                    if tmp_item.get('level'):
                        level = tmp_item.get('level').__dict__
                        level.pop('_state')
                        tmp_item.update({'level':level})
                    tmp_roles.append(tmp_item)
                context.update({'roles':tmp_roles})

            if 'page_access' in context:
                context.update({'page_access':list(context.get('page_access').values())})
            #print("typeeeeeeeeeeeee",context)




            context.update({'Message': 'با موفیقت ذخیره شد', 'ValidPerson': True, "success": True, "action_type":action_type})
            return HttpResponse(
                json.dumps(context),
                content_type="application/json"
            )

        else:
            return HttpResponse(
                json.dumps({"success": False, "Message": "به دلیل مشکل داده ها ورودی، امکان ذخیره اطلاعات وجود ندارد"}),
                content_type="application/json")

    return render(request, 'HR/layout.html', {"success": False, "Message": "به دلیل مشکل نوع ارسال داده ها، امکان ذخیره اطلاعات وجود ندارد"})


def DetailSave_Education(request, data, username):
    education_history_id = get_numeric_value(request.POST.get("EducationHistoryId"))
    university = get_numeric_value(request.POST.get("Uni"))
    degree_type = get_numeric_value(request.POST.get("Degree"))
    tendency = get_numeric_value(request.POST.get("Tendency"))
    GPA = get_numeric_value(request.POST.get("GPA"), "float")
    start_year = get_numeric_value(request.POST.get("StartYear"))
    end_year = get_numeric_value(request.POST.get("EndYear"))
    is_student = get_checkbox_value(request.POST.get("IsStudent"))

    # بررسی می کنیم که کلیدهای خارجی وجود داشته باشند
    # شناسه سابقه تحصیلی
    exist = HRMODEL.EducationHistory.objects.filter(id=education_history_id).exists()
    if not exist:
        education_history_id = None
    # شناسه دانشگاه
    exist = HRMODEL.University.objects.filter(id=university).exists()
    if not exist:
        university = None
    # شناسه مقطع تحصیلی
    exist = HRMODEL.ConstValue.objects.filter(id=degree_type, Parent__Code="DegreeType").exists()
    if not exist:
        degree_type = None
    # شناسه رشته تحصیلی
    exist = HRMODEL.Tendency.objects.filter(id=tendency).exists()
    if not exist:
        tendency = None
    # در صورتی که فیلدهای اجباری تکمیل شده باشد
    if degree_type is not None:
        # اگر شناسه را داشته باشیم، به روزرسانی است، در غیر این صورت درج است
        if education_history_id is not None:
            obj = HRMODEL.EducationHistory.objects.get(id=education_history_id)
        else:
            obj = HRMODEL.EducationHistory()
        # اطلاعات را به روز می کنیم
        obj.Person_id = username
        obj.University_id = university
        obj.Degree_Type_id = degree_type
        obj.EducationTendency_id = tendency
        obj.GPA = GPA
        obj.StartYear = start_year
        obj.EndYear = end_year
        obj.IsStudent = is_student
        # اطلاعات را ذخیره می کنیم
        obj.save()

        # now add data for detail table
        data["Message"] = "اطلاعات سوابق تحصیلی با موفقیت اضافه شد"
        data["id"] = obj.id

        data["UniversityName"] = obj.University.__str__()
        data["DegreeTitle"] = obj.Degree_Type.Caption
        data["EducationTendency"] = obj.EducationTendency.__str__()
    return


def DetailSave_Phone(request, data, username):
    phone_number_id = get_numeric_value(request.POST.get("PhoneNumberId"))
    tel_city = get_numeric_value(request.POST.get("TelCity"))
    phone_title = request.POST.get("PhoneTitle")
    tel_number = get_numeric_value(request.POST.get("TelNumber"))
    tel_type = get_numeric_value(request.POST.get("TelType"))
    tel_province = get_numeric_value(request.POST.get("TelProvince"))

    # بررسی می کنیم که کلیدهای خارجی وجود داشته باشند
    # شناسه شماره تماس
    exist = HRMODEL.PhoneNumber.objects.filter(id=phone_number_id).exists()
    if not exist:
        phone_number_id = None

    # شناسه شهر
    exist = HRMODEL.Province.objects.filter(id=tel_province).exists()
    if not exist:
        tel_province = None

    # شناسه نوع تلفن
    exist = HRMODEL.ConstValue.objects.filter(id=tel_type, Parent__Code="TelType").exists()
    if not exist:
        tel_type = None

    # در صورتی که فیلدهای اجباری تکمیل شده باشد
    if tel_number is not None:
        # اگر شناسه را داشته باشیم، به روزرسانی است، در غیر این صورت درج است
        if phone_number_id is not None:
            obj = HRMODEL.PhoneNumber.objects.get(id=phone_number_id)
        else:
            obj = HRMODEL.PhoneNumber()
        # اطلاعات را به روز می کنیم
        obj.Person_id = username
        # obj.City_id = tel_city
        obj.Title = phone_title
        obj.TelType_id = tel_type
        obj.TelNumber = tel_number
        obj.Province_id = tel_province
        # اطلاعات را ذخیره می کنیم
        obj.save()

        data["Message"] = "اطلاعات شماره تماس با موفقیت اضافه شد"
        data["id"] = obj.id
        data["AddressTitle"] = obj.Title
        data["PostalCode"] = obj.TelNumber


    return


def DetailSave_Address(request, data, username):
    postal_address_id = get_numeric_value(request.POST.get("PostalAddressId"))
    address_city = get_numeric_value(request.POST.get("AddressCity"))
    city_district = get_numeric_value(request.POST.get("CityDistrict"))
    address_title = request.POST.get("AddressTitle")
    number = get_numeric_value(request.POST.get("No"))
    postal_code = get_numeric_value(request.POST.get("PostalCode"))
    unit_number = get_numeric_value(request.POST.get("UnitNo"))
    address_text = request.POST.get("AddressText")

    # بررسی می کنیم که کلیدهای خارجی وجود داشته باشند
    # شناسه آدرس
    exist = HRMODEL.EducationHistory.objects.filter(id=postal_address_id).exists()
    if not exist:
        postal_address_id = None
    # شناسه شهر
    exist = HRMODEL.City.objects.filter(id=address_city).exists()
    if not exist:
        address_city = None
    # شناسه منطقه شهری
    exist = HRMODEL.CityDistrict.objects.filter(id=city_district).exists()
    if not exist:
        city_district = None

    # در صورتی که فیلدهای اجباری تکمیل شده باشد
    if address_city is not None and address_text is not None:
        # اگر شناسه را داشته باشیم، به روزرسانی است، در غیر این صورت درج است
        if postal_address_id is not None:
            obj = HRMODEL.PostalAddress.objects.get(id=postal_address_id)
        else:
            obj = HRMODEL.PostalAddress()
        # اطلاعات را به روز می کنیم
        obj.Person_id = username
        obj.City_id = address_city
        obj.CityDistrict_id = city_district
        obj.Title = address_title
        obj.No = number
        obj.UnitNo = unit_number
        obj.PostalCode = postal_code
        obj.AddressText = address_text
        # اطلاعات را ذخیره می کنیم
        obj.save()

        data["Message"] = "اطلاعات آدرس با موفقیت اضافه شد"
        data["id"] = obj.id
        data["AddressCityText"] = obj.City.CityTitle.__str__()
    return


def DetailSave_Email(request, data, username):
    email_id = get_numeric_value(request.POST.get("EmailAddressId"))
    email_title = request.POST.get("EmailTitle")
    email_address = request.POST.get("Email")

    # بررسی می کنیم که کلیدهای خارجی وجود داشته باشند
    # شناسه ایمیل
    exist = HRMODEL.EmailAddress.objects.filter(id=email_id).exists()
    if not exist:
        email_id = None

    # در صورتی که فیلدهای اجباری تکمیل شده باشد
    if email_address is not None:
        # اگر شناسه را داشته باشیم، به روزرسانی است، در غیر این صورت درج است
        if email_id is not None:
            obj = HRMODEL.EmailAddress.objects.get(id=email_id)

        else:
            obj = HRMODEL.EmailAddress()

        # اطلاعات را به روز می کنیم
        obj.Person_id = username
        obj.Email = email_address
        obj.Title = email_title
        # اطلاعات را ذخیره می کنیم
        obj.save()

        data["Message"] = "اطلاعات ایمیل با موفقیت اضافه شد"
        data["id"] = obj.id
        data["EmailTitle"] = obj.Title
    return


def UserDetailSave(request):
    # we must return request data to client
    data = dict(request.POST)

    if request.method == "POST":
        # ابتدا باید چک کنیم کدام جزییات را می خواهیم ذخیره کنیم
        detail_type = request.POST.get("detail_type")
        username = request.POST.get("UserName")
        data["DetailType"] = detail_type
        # چک می کنیم که چنین کاربری وجود داشته باشد
        exist = HRMODEL.Users.objects.filter(UserName=username).exists()
        if not exist:
            return HttpResponse(
                json.dumps({"success": False, "Message": "کاربر معتبر نمی باشد"}),
                content_type="application/json")

        # اطلاعات تحصیلی
        if detail_type == "EducationHistory":
            DetailSave_Education(request, data, username)

        # اطلاعات ایمیل ها
        elif detail_type == "EmailAddress":
            DetailSave_Email(request, data, username)

        # اطلاعات آدرس ها
        elif detail_type == "PostalAddress":
            DetailSave_Address(request, data, username)

        # اطلاعات شماره های تماس
        elif detail_type == "PhoneNumber":
            DetailSave_Phone(request, data, username)
        else:
            return HttpResponse(
                json.dumps(
                    {"success": False, "Message": "مشخص نیست که کدام بخش از جزییات در حال به روزرسانی می باشند"}),
                content_type="application/json")

        if is_not_empty(data["id"]):
            data["success"] = True
            return HttpResponse(
                json.dumps(data),
                content_type="application/json"
            )
        else:
            data["success"] = False
            return HttpResponse(
                json.dumps(data),
                content_type="application/json"
            )

    else:
        return HttpResponse(
            json.dumps({"success": False, "Message": "خطا در نحوه ارسال اطلاعات"}),
            content_type="application/json")


def UserDetailDelete(request):
    data = dict(request.POST)
    if request.method == "POST":
        detail_id = request.POST.get('id')
        detail_type = request.POST.get('detail_type')
        if detail_id is not None:
            #  if this detail is about education history
            if detail_type == "EducationHistory":
                HRMODEL.EducationHistory.objects.filter(id=detail_id).delete()
            elif detail_type == "EmailAddress":
                HRMODEL.EmailAddress.objects.filter(id=detail_id).delete()
            elif detail_type == "PhoneNumber":
                HRMODEL.PhoneNumber.objects.filter(id=detail_id).delete()
            elif detail_type == "PostalAddress":
                HRMODEL.PostalAddress.objects.filter(id=detail_id).delete()

        data["success"] = True
        data["DetailId"] = detail_id
        return HttpResponse(
            json.dumps(data),
            content_type="application/json"
        )
    else:
        data["success"] = False
        return HttpResponse(
            json.dumps(data),
            content_type="application/json"
        )


@login_required
def get_internal_token(request):
    if request.user.is_superuser:
        token = init_tokens(request.user.UserName)
        return JsonResponse({'state': 'ok', 'token': token}, status=200)
    return JsonResponse({'state': 'error'}, status=400)


# def NewUser(request):
#     team_list = HRMODEL.Team.objects.all()
#     role_list = HRMODEL.Role.objects.all()
#     level_list = HRMODEL.RoleLevel.objects.all()
#     context = {
#         "role_list": role_list,
#         "level_list": level_list,
#         "team_list": team_list,
#     }
#     return render(request, 'HR/new_user.html', context)


def PersonInfoPage(request, username=''):
    context = GeneralInfo(username, 'person', request)

    city = HRMODEL.City.objects.all()
    province = HRMODEL.Province.objects.all()
    marriage_status = HRMODEL.ConstValue.objects.filter(Parent__Code='MarriageStatus')
    degree_type = HRMODEL.ConstValue.objects.filter(Parent__Code='DegreeType')
    religion_type = HRMODEL.ConstValue.objects.filter(Parent__Code='Religion')
    military_service = HRMODEL.ConstValue.objects.filter(Parent__Code='MilitaryService')
    context.update({
        "city": city,
        "province": province,
        "name": "user",
        "title": 'اطلاعات  شخصی',
        "marriage_status": marriage_status,
        "degree_type": degree_type,
        "military_service": military_service,
        'religion_type': religion_type,
    })

    # if we are in update mode
    if context["valid_person"]:
        obj_person = HRMODEL.Users.objects.filter(UserName=username).first()
        context.update(
            {
                "obj_person": obj_person,
            })
    # if we are in insert mode
    else:
        team_list = HRMODEL.Team.objects.all()
        role_list = HRMODEL.Role.objects.all().order_by('RoleName')
        level_list = HRMODEL.RoleLevel.objects.all()
        # we want to know each team has which roles?
        # so find roles which are defined in each team
        # reading from UserTeamRole is not right, but we must do it,
        # because we have not any table that contain chart positions
        # team_role_list = HRMODEL.UserTeamRole.objects.values('TeamCode', 'RoleId').distinct('TeamCode','RoleId')
        team_role_list = HRMODEL.UserTeamRole.objects.values('TeamCode', 'RoleId')
        # this dict is something like this: {'CAR':[2,4,5,6], 'OFF':[3,4,7] , ....}
        # which array elements are role id that define in each team
        team_role_dict = {}
        # now select new dict with team code as key
        for team_role in team_role_list:
            roles = []
            team_code = team_role['TeamCode']
            role_id = team_role['RoleId']
            # check if we have an element for this team
            if team_code in team_role_dict.keys():
                # get roles of this team
                roles = team_role_dict[team_code]
            # now add new role
            # to distinct role id
            if role_id not in roles:
                roles.append(role_id)
            team_role_dict[team_code] = roles

        context.update({
            "valid_person": False,
            "role_list": role_list,
            "level_list": level_list,
            "team_list": team_list,
            "team_role_list": team_role_dict

        })
    return render(request, 'HR/person-info.html', context)


def JobInfoPage(request, username=''):
    context = GeneralInfo(username, 'job', request)
    if context["valid_person"]:
        emails = list(HRMODEL.EmailAddress.objects.filter(Person_id=username))
        city = HRMODEL.City.objects.all()
        province = HRMODEL.Province.objects.all()
        obj_edit = HRMODEL.Users.objects.filter(UserName=username).first()
        obj_History = HRMODEL.UserTeamRole.objects.filter(UserName=username)
        obj_History_name = HRMODEL.UserTeamRole.objects.filter(UserName=username).first()
        valid_person = True
        context.update(
            {
                "emails": emails,
                "city": city,
                "province": province,
                "valid_person": valid_person,
                "obj_edit": obj_edit,
                "obj_History": obj_History,
                "obj_History_name": obj_History_name,
            })
    return render(request, 'HR/job-info.html', context)


def PaymentInfoPage(request, username=''):
    context = GeneralInfo(username, 'payment',  request)
    if context["valid_person"]:
        obj_payment = HRMODEL.Payment.objects.filter(UserName=username).order_by('-YearNumber', '-MonthNo')
        valid_person = True
        page = request.GET.get('page', 1)
        paginator = Paginator(obj_payment, 10)
        try:
            obj_payment = paginator.page(page)
        except PageNotAnInteger:
            obj_payment = paginator.page(1)
        except EmptyPage:
            obj_payment = paginator.page(paginator.num_pages)
        context.update(
            {
                "obj_payment": obj_payment,

            })
    return render(request, 'HR/payment-info.html', context)


def WorkTimeInfoPage(request, username=''):
    context = GeneralInfo(username, 'worktime', request)
    if context["valid_person"]:
        # obj_work_time = HRMODEL.V_WorkTime.objects.filter(UserName=username).order_by('-YearNo')
        obj_work_time_detail = HRMODEL.WorkTime.objects.filter(UserName=username).order_by('-YearNo', '-MonthNo')
        valid_person = True
        page = request.GET.get('page', 1)
        paginator = Paginator(obj_work_time_detail, 10)

        try:
            obj_work_time_detail = paginator.page(page)
        except PageNotAnInteger:
            obj_work_time_detail = paginator.page(1)
        except EmptyPage:
            obj_work_time_detail = paginator.page(paginator.num_pages)


        context.update(
            {
                # "obj_work_time":obj_work_time,
                'obj_work_time_detail': obj_work_time_detail,

            })
    return render(request, 'HR/worktime-info.html', context)
