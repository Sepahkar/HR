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

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg


@csrf_exempt
def UserPageList(request):
    page_name = 'user_list'
    obj_list = list(HRMODEL.Users.objects.all())
    obj_info_new = list(HRMODEL.UserTeamRole.objects.all())
    obj_info_old = list(HRMODEL.PreviousUserTeamRole.objects.all())
    obj_info = obj_info_new + obj_info_old
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
        page_access_control = HRMODEL.V_PagePermission.objects.filter(UserName=current_user,
                                                                      Page__EnglishName=page_name).first()
        if page_access_control is None:
            context = {"valid_person": False, "permission": False, "message": "دسترسی برای این کاربر مجاز نمی باشد"}
            return context
        # check if this user has edit access to this page
        edit_permission = page_access_control.Editable

    # get all user access for bookmark
    bookmark_access_qs = list(
        HRMODEL.V_PagePermission.objects.filter(UserName=current_user).exclude(Page__EnglishName='first-page').order_by(
            'OrderNumber'))
    # page_access = HRMODEL.V_PagePermission.objects.filter(UserName=current_user).filter(~Q(Page__PageName='first-page'))
    bookmark_access = []
    for bookmark in bookmark_access_qs:
        bookmark_item = {'PageEnglishName': bookmark.Page.EnglishName, 'PageColorSet': bookmark.Page.ColorSet,
                         'PageName': bookmark.Page.PageName, 'PageIconName': bookmark.Page.IconName}
        bookmark_access.append(bookmark_item)
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
        "current_user": current_user,
        "full_permission": False,
        "bookmark_access": bookmark_access,
    }
    return context


def FirstPage(request, username=''):
    context = GeneralInfo(username, 'first-page', request)
    return render(request, 'HR/layout.html', context)


def FacilitiesPage(request, username=''):
    context = GeneralInfo(username, 'contact', request)
    return render(request, 'HR/facilities-info.html', context)


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


def PersonInfoPage(request, username=''):
    context = GeneralInfo(username, 'person', request)

    city = HRMODEL.City.objects.all()
    province = HRMODEL.Province.objects.all()
    marriage_status = HRMODEL.ConstValue.objects.filter(Parent__Code='MarriageStatus')
    degree_type = HRMODEL.ConstValue.objects.filter(Parent__Code='DegreeType')
    religion_type = HRMODEL.ConstValue.objects.filter(Parent__Code='Religion')
    military_service = HRMODEL.ConstValue.objects.filter(Parent__Code='MilitaryService')
    contract_type = HRMODEL.ConstValue.objects.filter(Parent__Code='ContractType')
    user_status = HRMODEL.ConstValue.objects.filter(Parent__Code='UserStatus')

    context.update({
        "city": city,
        "province": province,
        "name": "user",
        "title": 'اطلاعات  شخصی',
        "marriage_status": marriage_status,
        "degree_type": degree_type,
        "military_service": military_service,
        'religion_type': religion_type,
        'contract_type': contract_type,
        'user_status':user_status,
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
        obj_History_new = list(HRMODEL.UserTeamRole.objects.filter(UserName=username))
        obj_History_old = list(HRMODEL.PreviousUserTeamRole.objects.filter(UserName=username))
        obj_History = obj_History_new + obj_History_old
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


def payment_info(payment_list, month_name_all):
    month_name = []
    payment = []  # خالص دریافتی
    total_payment = []  # حقوق ناخالص
    other_payment = []  # سایر هزینه ها
    over_time_payment = []  # اضافه کار
    reward = []  # اضافه کار
    base_payment = []  # حکم کارگزینی

    for pay in payment_list:
        payment.append(pay.Payment / 10)
        total_payment.append(pay.TotalPayment / 10)
        other_payment.append(pay.OtherPayment / 10)
        over_time_payment.append(pay.OverTimePayment / 10)
        reward.append(pay.Reward / 10)
        base_payment.append(pay.BasePayment / 10)
        if len(month_name_all) == 12:
            month_name.append(month_name_all[pay.MonthNumber - 1])

    payment_dict = {
        'payment': payment,
        'total_payment': total_payment,
        'other_payment': other_payment,
        'over_time_payment': over_time_payment,
        'reward': reward,
        'base_payment': base_payment,
        'month_name': month_name,
    }
    return payment_dict

def get_initial_information(request, username, default_chart):
    # سالهایی که این کاربر در فناوران مشغول بوده است را به دست می آوریم
    year_list = HRMODEL.Payment.objects.filter(Username=username).order_by('YearNumber').values_list(
        'YearNumber').distinct()
    # آخرین سال را به عنوان سال پیش فرض می گیریم
    year_number = year_list.last()[0]
    if 'year_number' in request.POST:
        year_number = int(request.POST.get('year_number'))
    has_more_than_one_year = True
    if len(year_list) == 1:
        has_more_than_one_year = False

    # همه سمت های فعلی این کاربر را به دست می آوریم
    role_list = HRMODEL.UserTeamRole.objects.filter(UserName=username).order_by('StartDate').values_list('RoleId',
                                                                                                         'RoleId__RoleName',
                                                                                                         'LevelId',
                                                                                                         'LevelId__LevelName').distinct()
    # نخستین سمت فرد را به دست می آوریم
    role_id = role_list.first()[0]
    role_title = role_list.first()[1]
    if 'role_id' in request.POST:
        role_id = int(request.POST.get('role_id'))
        role_title = request.POST.get('role_title').strip()
    has_more_than_one_role = False
    if len(role_list) > 1:
        has_more_than_one_role = True

    # سطح فرد را به دست می آوریم
    l = HRMODEL.UserTeamRole.objects.filter(UserName=username, RoleId_id=role_id).first()
    level_id = l.LevelId_id
    level_title = l.LevelId
    if 'level_id' in request.POST:
        l = request.POST.get('level_id')
        if l != '' and l != 'None':
            level_id = int(l)
            level_title = request.POST.get('level_title')

    month_name_all = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن',
                          'اسفند']

    # برای اینکه بدانیم کدام چارت باید فعال باشد
    current_chart = default_chart
    if 'current_chart' in request.POST:
        current_chart = request.POST.get('current_chart')

    context = {
        'year_number': year_number,
        'year_list': year_list,
        'role_id': role_id,
        'role_title': role_title,
        'role_list': role_list,
        'level_id': level_id,
        'level_title': level_title,
        'month_name_all':month_name_all,
        'has_more_than_one_year': has_more_than_one_year,
        'has_more_than_one_role': has_more_than_one_role,
        'current_chart':current_chart,

    }
    return context

def PaymentInfoPage(request, username=''):
    context = GeneralInfo(username, 'payment', request)
    if context["valid_person"]:

        context.update( get_initial_information(request, username, 'payment-count-chart'))

        # برای نمودار اول باید تعداد کل کسانی که بیشتر و یا کمتر از این فرد دریافت می کنند را به دست بیاوریم
        # میانگین دریافتی سالانه این فرد
        average_payment = HRMODEL.PaymentYearly.objects.filter(YearNumber=context['year_number'],
                                                               Username=username).first().Payment
        # تعداد کسانی که کمتر از این فرد دریافتی داشته اند
        more_payment_count = len(HRMODEL.PaymentYearly.objects.filter(YearNumber=context['year_number'],
                                                                         Payment__gt=average_payment))
        # تعداد کسانی که بیشتر از این فرد دریافتی داشته اند
        less_payment_count = len(HRMODEL.PaymentYearly.objects.filter(YearNumber=context['year_number'],
                                                                         Payment__lt=average_payment))
        # تعداد افرادی با همین سمت کمتر از این فرد دریافتی داشته اند
        more_role_payment_count = len(HRMODEL.PaymentRoleAverage.objects.filter(YearNumber=context['year_number'],
                                                                                  Payment__gt=average_payment,
                                                                                  RoleId=context['role_id'],
                                                                                  LevelId=context['level_id']))
        # تعداد افرادی که با همین سمت بیشتر از این فرد دریافتی داشته اند
        less_role_payment_count = len(HRMODEL.PaymentRoleAverage.objects.filter(YearNumber=context['year_number'],
                                                                                  Payment__lt=average_payment,
                                                                                  RoleId=context['role_id'],
                                                                                  LevelId=context['level_id']))

        person_payment_list = HRMODEL.Payment.objects.filter(Username=username, YearNumber=context['year_number']).order_by(
            'MonthNumber')
        person_payment = payment_info(person_payment_list, context['month_name_all'])
        # از آنجا که ممکن است فرد در میانه سال آمده باشد (مثلا خرداد ماه) نباید ماه هایی که نبوده است را در نظر بگیریم
        first_month = person_payment_list.first().MonthNumber
        # از آنجا که ممکن است فرد در میانه سال رفته باشد (مثلا آبان ماه) نباید ماه هایی که نبوده است را در نظر بگیریم
        last_month = person_payment_list.last().MonthNumber
        month_name = person_payment['month_name']

        payment_average_list = HRMODEL.PaymentAverage.objects.filter(YearNumber=context['year_number'],
                                                                     MonthNumber__gte=first_month,
                                                                     MonthNumber__lte=last_month
                                                                     ).order_by('MonthNumber')
        payment_average = payment_info(payment_average_list, context['month_name_all'])

        role_payment_average_list = HRMODEL.PaymentRoleAverage.objects.filter(YearNumber=context['year_number'],
                                                                              MonthNumber__gte=first_month,
                                                                              MonthNumber__lte=last_month,
                                                                              RoleId__RoleId=context['role_id'],
                                                                              LevelId=context['level_id']).order_by('MonthNumber')
        role_payment_average = payment_info(role_payment_average_list, context['month_name_all'])


        # اگر این فرد چند سال باشد که در شرکت حضور دارد
        # نمودار مقایسه سالانه را برای تمام سالها نیز باید ترسیم کنیم
        all_year_payment = ''
        all_year_average_payment = ''
        all_year_average_role_payment = ''
        if context['has_more_than_one_year']:
            person_payment_yearly_list = HRMODEL.PaymentYearly.objects.filter(Username=username).order_by('YearNumber')
            all_year_payment = payment_info(person_payment_yearly_list, '')

            # ممکن است یک نفر مثلا دو سال باشد در صورتی که ما اطلاعات 5 سال را داریم
            # ما باید در نمودار اطلاعات 2 سال را نشان دهیم
            # پس سال اول و آخر را به دست می آوریم
            start_year = context['year_list'].first()[0]
            end_year = context['year_list'].last()[0]

            payment_average_yearly_list = HRMODEL.PaymentAverageYearly.objects.filter(YearNumber__lte=end_year,
                                                                                      YearNumber__gte=start_year
                                                                                      ).order_by('YearNumber')
            all_year_average_payment = payment_info(payment_average_yearly_list, '')

            role_payment_average_yearly_list = HRMODEL.PaymentRoleAverageYearly.objects.filter(
                YearNumber__gte=start_year,
                YearNumber__lte=end_year,
                RoleId__RoleId=context['role_id'],
                LevelId=context['level_id']).order_by(
                'YearNumber')
            all_year_average_role_payment = payment_info(role_payment_average_yearly_list, '')

        context.update(
            {'payment_average': payment_average,
             'role_payment_average': role_payment_average,
             'person_payment': person_payment,
             'all_year_payment': all_year_payment,
             'all_year_average_payment': all_year_average_payment,
             'all_year_average_role_payment': all_year_average_role_payment,
             'more_payment_count': more_payment_count,
             'less_payment_count': less_payment_count,
             'more_role_payment_count': more_role_payment_count,
             'less_role_payment_count': less_role_payment_count,
            'month_name': month_name,
             })
    return render(request, 'HR/payment-info.html', context)

def get_EIT_user_item_value(list, code_EIT, code_user, month_name_all):
    list_EIT = []
    list_EIT_month = []
    list_user_draft = []
    list_user_month = []
    month_name = []

    for item in list:
        if item.Code == code_EIT:
            list_EIT.append(item.ItemValue)
            list_EIT_month.append(item.MonthNumber)
        elif item.Code == code_user:
            list_user_draft.append(item.ItemValue)
            list_user_month.append(item.MonthNumber)

    # ممکن است هزینه  مربوطه در برخی از ماه ها برای کاربر وجود نداشته باشد
    # باید هزینه را در آن ماه ها برای کاربر صفر در نظر بگیریم
    list_user = [0]*len(list_EIT_month)
    for month in list_EIT_month:
        if month in list_user_month:
            list_user[list_EIT_month.index(month)] = list_user_draft[list_user_month.index(month)]
        month_name.append(month_name_all[month-1])
    return list_EIT, list_user, month_name

def FacilitiesInfoPage(request, username=''):
    context = GeneralInfo(username, 'facilities', request)
    if context["valid_person"]:

        context.update( get_initial_information(request,username, 'nahar-time-chart'))

        # هزینه ناهارتایم برای این کاربر در این سال
        nahar_time = HRMODEL.UserSlip.objects.filter(Username=username, YearNumber=context['year_number']
                                        ,Code__in=('NaharTimeCostEIT','NaharTimeCost')).order_by('MonthNumber')

        # اگر برای این کاربر در این سال اطلاعات وجود نداشته باشد
        if len(nahar_time)==0 and context['current_chart'] == 'nahar-time-chart':
            context['message'] = 'متاسفانه اطلاعاتی برای این سال وجود ندارد'
        else:

            nahar_time_EIT, nahar_time_user, month_name_nahar_time = \
                get_EIT_user_item_value(nahar_time, 'NaharTimeCostEIT','NaharTimeCost',context['month_name_all'])

            # متوسط هزینه ناهار تایم برای پرسنل شرکت
            nahar_time_average = HRMODEL.UserSlipAverage.objects.filter(YearNumber=context['year_number']
                                            ,Code__in=('NaharTimeCostEIT','NaharTimeCost')).order_by('MonthNumber')

            nahar_time_average_EIT, nahar_time_average_user,month_name_nahar_time_average = \
                get_EIT_user_item_value(nahar_time_average, 'NaharTimeCostEIT','NaharTimeCost',context['month_name_all'])

            # هزینه بیمه تکمیلی برای این کاربر در این سال
            insurance_cost = HRMODEL.UserSlip.objects.filter(Username=username, YearNumber=context['year_number']
                                                         , Code__in=('HealthcareInsuranceEIT', 'HealthcareInsurance')).order_by('MonthNumber')
            # اگر برای این کاربر در این سال اطلاعات وجود نداشته باشد
            if len(insurance_cost) == 0 and context['current_chart'] == 'insurance_cost-chart':
                context['message'] = 'متاسفانه اطلاعاتی برای این سال وجود ندارد'
            else:
                insurance_cost_EIT, insurance_cost_user, month_name_insurance_cost = \
                    get_EIT_user_item_value(insurance_cost, 'HealthcareInsuranceEIT','HealthcareInsurance',context['month_name_all'])


                # متوسط هزینه بیمه تکمیلی برای پرسنل شرکت
                insurance_cost_average = HRMODEL.UserSlipAverage.objects.filter(YearNumber=context['year_number']
                                                                            , Code__in=('HealthcareInsuranceEIT', 'HealthcareInsurance')).order_by('MonthNumber')
                insurance_cost_average_EIT, insurance_cost_average_user, month_name_insurance_average_cost = \
                    get_EIT_user_item_value(insurance_cost_average, 'HealthcareInsuranceEIT','HealthcareInsurance',context['month_name_all'])

                context.update(
                    {
                        'nahar_time_EIT':nahar_time_EIT,
                        'nahar_time_user':nahar_time_user,
                        'month_name_nahar_time':month_name_nahar_time,
                        'nahar_time_average_EIT':nahar_time_average_EIT,
                        'nahar_time_average_user':nahar_time_average_user,
                        'month_name_nahar_time_average':month_name_nahar_time_average,
                        'insurance_cost_EIT':insurance_cost_EIT,
                        'insurance_cost_user':insurance_cost_user,
                        'month_name_insurance_cost':month_name_insurance_cost,
                        'insurance_cost_average_EIT':insurance_cost_average_EIT,
                        'insurance_cost_average_user':insurance_cost_average_user,
                        'month_name_insurance_average_cost':month_name_insurance_average_cost,
                        'message':'',
                     })

    return render(request, 'HR/facilities-info.html', context)

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
        contract_type = get_numeric_value(request.POST.get('ContractType'))
        is_active = get_numeric_value(request.POST.get('IsActive'))
        user_status = get_numeric_value(request.POST.get('UserStatus'))

        arr_date = contract_date.split('/')
        contract_gdate = jdatetime.JalaliToGregorian(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]))
        # we added line bellow for fixing the ????/??/?? StartDate column in UserTeamRole
        # table
        contract_date = str(contract_gdate.jyear) + "/" + str(contract_gdate.jmonth).zfill(2) + "/" + str(
            contract_gdate.jday).zfill(2)
        contract_gdate = str(contract_gdate.gyear) + "-" + str(contract_gdate.gmonth) + "-" + str(contract_gdate.gday)

        arr_date = birth_date.split('/')
        birth_gdate = jdatetime.JalaliToGregorian(int(arr_date[0]), int(arr_date[1]), int(arr_date[2]))
        birth_gdate = str(birth_gdate.gyear) + "-" + str(birth_gdate.gmonth) + "-" + str(birth_gdate.gday)

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
            if is_not_empty(military_status): user.MilitaryStatus_id = military_status
            if is_not_empty(birth_date): user.BirthDate = birth_gdate
            if is_not_empty(marriage_status): user.MarriageStatus_id = marriage_status
            if is_not_empty(degree_type): user.DegreeType_id = degree_type
            user.FatherName = father_name
            if is_not_empty(religion): user.Religion_id = religion
            if is_not_empty(identity_number): user.IdentityNumber = identity_number
            if is_not_empty(identity_serial_number): user.IdentitySerialNumber = identity_serial_number
            if is_not_empty(insurance_number): user.InsuranceNumber = insurance_number
            if is_not_empty(contract_type): user.ContractType_id = contract_type
            if is_not_empty(user_status): user.UserStatus_id = user_status
            if is_active == 1:
                user.IsActive = True
            else:
                user.IsActive = False

            user.Gender = True if gender else False

            user.save()
            if level == 0:
                level = None

            exist = HRMODEL.UserTeamRole.objects.filter(UserName=username).exists()

            manager_username = HRMODEL.V_RoleTeam.objects.filter(RoleID=role, TeamCode=team).only('ManagerUserName')
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

            if 'avatar-file' in request.FILES:
                myfile = request.FILES['avatar-file']
                fs = FileSystemStorage()
                ext = 'jpg'
                new_name = username.replace("@eit", "") + "." + ext
                file_uri = os.path.join(settings.BASE_DIR, 'media', 'HR', 'PersonalPhoto', new_name)
                if os.path.exists(file_uri):
                    os.remove(file_uri)
                filename = fs.save(file_uri, myfile)
                uploaded_file_url = fs.url(filename)

            if 'cv-file' in request.FILES:
                myfile = request.FILES['cv-file']
                fs = FileSystemStorage()
                ext = myfile.name.split('.')[1]
                new_name = username.replace("@eit", "") + "." + ext
                file_uri = os.path.join(settings.BASE_DIR, 'media', 'HR', 'Resume', new_name)
                if os.path.exists(file_uri):
                    os.remove(file_uri)
                filename = fs.save(file_uri, myfile)
                user.CVFile = new_name
                user.save()

            context = GeneralInfo(username, 'person', request)

            # append this line for fix
            if 'page' in context:
                new_page = context.get('page').__dict__
                new_page.pop("_state")
                context.update({'page': new_page})

            if 'roles' in context:
                tmp_roles = []
                for item in context.get('roles'):
                    tmp_item = item
                    if tmp_item.get('level'):
                        level = tmp_item.get('level').__dict__
                        level.pop('_state')
                        tmp_item.update({'level': level})
                    tmp_roles.append(tmp_item)
                context.update({'roles': tmp_roles})

            if 'page_access' in context:
                context.update({'page_access': list(context.get('page_access').values())})
            # print("typeeeeeeeeeeeee",context)

            context.update(
                {'Message': 'با موفیقت ذخیره شد', 'ValidPerson': True, "success": True, "action_type": action_type})
            return HttpResponse(
                json.dumps(context),
                content_type="application/json"
            )

        else:
            return HttpResponse(
                json.dumps({"success": False, "Message": "به دلیل مشکل داده ها ورودی، امکان ذخیره اطلاعات وجود ندارد"}),
                content_type="application/json")

    return render(request, 'HR/layout.html',
                  {"success": False, "Message": "به دلیل مشکل نوع ارسال داده ها، امکان ذخیره اطلاعات وجود ندارد"})


def DetailSave_Education(request, data, username):
    education_history_id = get_numeric_value(request.POST.get("educationId"))
    university = get_numeric_value(request.POST.get("Uni"))
    degree_type = get_numeric_value(request.POST.get("DegreeType"))
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
    if degree_type is not None and tendency is not None:
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
        if is_not_empty(GPA): obj.GPA = GPA
        if is_not_empty(start_year): obj.StartYear = start_year
        if is_not_empty(end_year): obj.EndYear = end_year
        obj.IsStudent = is_student
        # اطلاعات را ذخیره می کنیم
        obj.save()

        # now add data for detail table
        data["Message"] = "اطلاعات سوابق تحصیلی با موفقیت اضافه شد"
        data["id"] = obj.id

        data["UniversityName"] = obj.University.__str__()
        data["DegreeTitle"] = obj.Degree_Type.Caption
        data["EducationTendency"] = obj.EducationTendency.__str__()
    else:
        # اگر فیلدهای اجباری تکمیل نشده باشد
        return -1
    return 1


def DetailSave_Phone(request, data, username):
    phone_number_id = get_numeric_value(request.POST.get("PhoneNumberId"))
    tel_city = get_numeric_value(request.POST.get("TelCity"))
    phone_title = request.POST.get("PhoneTitle")
    tel_number = get_numeric_value(request.POST.get("TelNumber"))
    tel_type = get_numeric_value(request.POST.get("TelType"))
    tel_province = get_numeric_value(request.POST.get("TelProvince"))
    is_default = get_checkbox_value(request.POST.get("IsDefault"))

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
        obj.IsDefault = is_default
        # اطلاعات را ذخیره می کنیم
        obj.save()

        data["Message"] = "اطلاعات شماره تماس با موفقیت اضافه شد"
        data["id"] = obj.id
        data["AddressTitle"] = obj.Title
        data["PostalCode"] = obj.TelNumber
        if obj.IsDefault:
            data["IsDefault"] = 'بله'
        else:
            data["IsDefault"] = 'خیر'
    else:
        # اگر فیلدهای اجباری تکمیل نشده باشد
        return -1
    return 1


def DetailSave_Address(request, data, username):
    postal_address_id = get_numeric_value(request.POST.get("PostalAddressId"))
    address_city = get_numeric_value(request.POST.get("AddressCity"))
    city_district = get_numeric_value(request.POST.get("CityDistrict"))
    address_title = request.POST.get("AddressTitle")
    number = get_numeric_value(request.POST.get("No"))
    postal_code = get_numeric_value(request.POST.get("PostalCode"))
    unit_number = get_numeric_value(request.POST.get("UnitNo"))
    address_text = request.POST.get("AddressText")
    is_default = get_checkbox_value(request.POST.get("IsDefault"))

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
        obj.IsDefault = is_default
        # اطلاعات را ذخیره می کنیم
        obj.save()

        data["Message"] = "اطلاعات آدرس با موفقیت اضافه شد"
        data["id"] = obj.id
        data["AddressCityText"] = obj.City.CityTitle.__str__()
        if obj.IsDefault:
            data["IsDefault"] = 'بله'
        else:
            data["IsDefault"] = 'خیر'

    else:
        # اگر فیلدهای اجباری تکمیل نشده باشد
        return -1
    return 1


def DetailSave_Email(request, data, username):
    email_id = get_numeric_value(request.POST.get("EmailAddressId"))
    email_title = request.POST.get("EmailTitle")
    email_address = request.POST.get("Email")
    is_default = get_checkbox_value(request.POST.get("IsDefault"))

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
        obj.IsDefault = is_default
        # اطلاعات را ذخیره می کنیم
        obj.save()

        data["Message"] = "اطلاعات ایمیل با موفقیت اضافه شد"
        data["id"] = obj.id
        data["EmailTitle"] = obj.Title
        if obj.IsDefault:
            data["IsDefault"] = 'بله'
        else:
            data["IsDefault"] = 'خیر'
    else:
        # اگر فیلدهای اجباری تکمیل نشده باشد
        return -1
    return 1


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
        detail_save = 0
        # اطلاعات تحصیلی
        if detail_type == "education":
            detail_save = DetailSave_Education(request, data, username)

        # اطلاعات ایمیل ها
        elif detail_type == "EmailAddress":
            detail_save = DetailSave_Email(request, data, username)

        # اطلاعات آدرس ها
        elif detail_type == "PostalAddress":
            detail_save = DetailSave_Address(request, data, username)

        # اطلاعات شماره های تماس
        elif detail_type == "PhoneNumber":
            detail_save = DetailSave_Phone(request, data, username)
        else:
            return HttpResponse(
                json.dumps(
                    {"success": False, "Message": "مشخص نیست که کدام بخش از جزییات در حال به روزرسانی می باشند"}),
                content_type="application/json")

        if is_not_empty(data["id"]) and detail_save > 0:
            data["success"] = True
            return HttpResponse(
                json.dumps(data),
                content_type="application/json"
            )
        else:
            if detail_save < 0:
                data["Message":"امکان ذخیره اطلاعات به علت عدم تکمیل شدن فیلدهای اجباری امکان ندارد."]
            else:
                data["Message":"امکان ذخیره اطلاعات وجود ندارد."]
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
            if detail_type == "education":
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


def SaveImageUser(request):
    upload = request.FILES['avatar-file']
    fss = FileSystemStorage()
    new_name = request.POST.get('user_name').split('@eit')[0] if '@eit' in request.POST.get(
        'user_name') else request.POST.get('user_name')
    ext = upload.name.split('.')[1]
    new_name = new_name + '.' + ext
    dir = os.path.join(settings.BASE_DIR, 'media', 'HR', 'PersonalPhoto', new_name)
    file = fss.save(dir, upload)
    file_url = fss.url(file)
    return file_url
