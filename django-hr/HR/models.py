from django.db import models, connections
from HR.validator import Validator as v, DefaultValue as d
import datetime
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django_middleware_global_request.middleware import get_request
from django.contrib.auth import get_user_model
from django.conf import settings


def ConstValueChoice(ConstType):
    ParentId = ConstValue.objects.filter(Code=ConstType)
    choice = {"IsActive": True}  # , "Parent_Id": ParentId[0].id}
    return choice


class Province(models.Model):
    class Meta:
        verbose_name = "استان"
        verbose_name_plural = "استان ها"

    ProvinceTitle = models.CharField(max_length=50, verbose_name="استان", unique=True)
    AbbreviationCode = models.CharField(max_length=2, verbose_name="کد استان", null=True, blank=True)
    PhoneCode = models.IntegerField(verbose_name="پیش شماره شهرستان", null=True, blank=True)

    def __str__(self):
        return self.ProvinceTitle


class City(models.Model):
    class Meta:
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"

    Province = models.ForeignKey("Province", verbose_name="استان", on_delete=models.SET_DEFAULT, default=8)
    CityTitle = models.CharField(max_length=100, verbose_name="شهر")

    IsCapital = models.BooleanField(verbose_name="مرکز استان است؟", default=False)
    CityCode = models.CharField(max_length=4, verbose_name="کد شهر", null=True, blank=True)

    def __str__(self):
        return self.Province.ProvinceTitle + ' ' + self.CityTitle


class CityDistrict(models.Model):
    class Meta:
        verbose_name = "ناحیه شهری"
        verbose_name_plural = "نواحی شهری"

    City = models.ForeignKey("City", verbose_name="شهر", default=d.City,
                             on_delete=models.CASCADE)
    DistrictTitle = models.CharField(max_length=50, verbose_name="عنوان")

    def __str__(self):
        if self.DistrictTitle is not None:
            return self.City.CityTitle + ' - منطقه ' + self.DistrictTitle


class MilitaryService(models.Model):
    class Meta:
        verbose_name = 'وضعیت پایان خدمت'
        verbose_name_plural = 'وضعیت های پایان خدمت'

    MilitaryService = models.CharField(max_length=300, verbose_name='وضعیت')


class VirtualUsers(models.Model):
    class Meta:
        verbose_name = "کاربر برنامه ها"
        verbose_name_plural = "کاربران برنامه ها"
        managed = False


class Users(models.Model):
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        db_table = 'Users'

    # username = None
    AuthLoginKey = models.CharField(max_length=300, null=True, blank=True)
    AuthLoginDate = models.CharField(default=None, null=True, max_length=100, blank=True)
    UserName = models.CharField(primary_key=True, max_length=100, verbose_name='نام کاربری')
    # password = models.CharField(max_length=300,null=True,blank=True)
    FirstName = models.CharField(max_length=200, verbose_name='نام')
    LastName = models.CharField(max_length=200, verbose_name='نام خانوادگی')
    BirthDate = models.DateField(null=True, blank=True, verbose_name='تاریخ تولد')
    ContractDate = models.DateField(null=True, blank=True, verbose_name='تاریخ استخدام')
    About = models.CharField(max_length=1000, verbose_name="درباره من", null=True, blank=True)
    Gender = models.BooleanField(default=False, verbose_name='جنسیت')
    FirstNameEnglish = models.CharField(max_length=80, verbose_name="نام لاتین", null=True, blank=True)
    LastNameEnglish = models.CharField(max_length=100, verbose_name="نام خانوادگی لاتین", null=True, blank=True)
    LivingAddress = models.ForeignKey("PostalAddress", verbose_name="آدرس محل سکونت", on_delete=models.SET_NULL,
                                      null=True, blank=True)
    # is_staff = models.BooleanField(default=True)
    # is_active = models.BooleanField(default=True)
    # is_superuser = models.BooleanField(default=False)

    NotEducated = 0
    ElementarySchool = 1
    PreHighSchool = 2
    Diploma = 3
    Collage = 4
    Bachelor = 5
    Master = 6
    Phd = 7
    Education_Choices = [(NotEducated, "بی سواد"), (ElementarySchool, "ابتدایی"), (PreHighSchool, "دبیرستان"),
                         (Diploma, "دیپلم"), (Collage, "کاردانی"), (Bachelor, "کارشناسی"), (Master, "کارشناسی ارشد"),
                         (Phd, "دکتری")]
    DegreeType = models.IntegerField(choices=Education_Choices, null=True, blank=True, verbose_name='آخرین مقطع تحصیلی')
    Degree_Type = models.ForeignKey('ConstValue', on_delete=models.PROTECT, null=True, blank=True,
                                    verbose_name='آخرین مقطع تحصیلی')
    CVFile = models.FileField(verbose_name="فایل رزومه", null=True, blank=True)
    Address = models.CharField(max_length=2000, null=True, blank=True, verbose_name='آدرس')
    Marriage_Single = 1
    Marriage_Married = 2
    Marriage_Divorced = 3
    Marriage_Widow = 4
    Marriage_Choices = ((Marriage_Single, "مجرد"), (Marriage_Married, "متاهل"), (Marriage_Divorced, "جدا شده"),
                        (Marriage_Widow, "فوت شده"))
    MarriageStatus = models.PositiveSmallIntegerField(choices=Marriage_Choices, verbose_name="وضعیت تاهل",
                                                      default=Marriage_Single, blank=True, null=True)
    Marriage_Status = models.ForeignKey("ConstValue", verbose_name="وضعیت تاهل", on_delete=models.PROTECT,
                                        related_name='UsersMarriageStatus', null=True, blank=True)
    NumberOfChildren = models.PositiveSmallIntegerField(verbose_name="تعداد فرزند", default=0, null=True, blank=True)
    MilitaryStatus = models.ForeignKey('MilitaryService', null=True, blank=True, on_delete=models.PROTECT,
                                       verbose_name='وضعیت خدمت')
    Military_Status = models.ForeignKey("ConstValue", verbose_name='وضعیت خدمت', on_delete=models.PROTECT,
                                        related_name='UsersMilitaryStatus', null=True, blank=True)
    NationalCode = models.CharField(max_length=10, null=True, unique=True, blank=True,
                                    validators=[v.NationalCode_Validator],
                                    verbose_name="کد ملی")
    BirthCity = models.ForeignKey("City", verbose_name="شهر", default=d.City,
                                  on_delete=models.SET_DEFAULT)
    FatherName = models.CharField(max_length=200, null=True, blank=True, verbose_name='نام پدر')
    IdentityNumber = models.IntegerField(null=True, blank=True, verbose_name='شماره شناسنامه')
    IdentitySerialNumber = models.IntegerField(null=True, blank=True, verbose_name='سریال شناسنامه')
    InsuranceNumber = models.IntegerField(null=True, blank=True, verbose_name='شماره بیمه')
    Religion = models.ForeignKey("ConstValue", verbose_name="دین", on_delete=models.PROTECT,
                                 related_name='UsersReligion', null=True, blank=True)

    # USERNAME_FIELD = 'UserName'
    # objects = CustomUserManager()
    #
    # @property
    # def groups(self):
    #     cursor = connections['default'].cursor()
    #     try:
    #         cursor.execute("select * from auth_user where username=%s ", (self.UserName,))
    #         row = cursor.fetchone()
    #         user_id = row[0]
    #         cursor.execute("select * from auth_user_groups where user_id=%s", (user_id,))
    #         row = cursor.fetchall()
    #         if row is not None:
    #             rows = [item[2] for item in row]
    #             return Group.objects.filter(id__in=rows)
    #     except:
    #         cursor.close()
    #     finally:
    #         cursor.close()
    #
    #     return Group.objects.none()

    def __str__(self):
        return self.FirstName + ' ' + self.LastName

    @property
    def username(self):
        return self.UserName

    @property
    def is_authenticated(self):
        User = get_user_model()
        user = User.objects.filter(username=self.UserName).first()
        if user:
            return user.is_authenticated
        return False
        # try:
        #     request = get_request()
        #     session_name = settings.SESSION_COOKIE_NAME
        #     session_key = request.COOKIES.get(session_name)
        #     if session_key:
        #         session = Session.objects.get(session_key=session_key)
        #         session_data = session.get_decoded()
        #         uid = session_data.get('_auth_user_id')
        #         user = get_user_model().objects.filter(id=uid).first()
        #         if user:
        #             return True
        #     return False
        # except:
        #     return False


    @property
    def all_teams_code(self):
        qs = UserTeamRole.objects.filter(UserName__UserName=self.UserName)
        teams = [item.TeamCode.TeamCode for item in qs]
        teams = list(set(teams))
        return teams

    @property
    def all_teams_name(self):
        qs = UserTeamRole.objects.filter(UserName__UserName=self.UserName)
        teams = [item.TeamCode.TeamName for item in qs]
        teams = list(set(teams))
        return teams

    @property
    def first_team_code(self):
        request = get_request()
        team = request.COOKIES.get('team', None)
        if team and team in self.all_teams_code:
            return team
        else:
            qs = UserTeamRole.objects.filter(UserName__UserName=self.UserName)
            team = qs[0].TeamCode.TeamCode
            return team

    @property
    def first_team_name(self):
        request = get_request()
        team = request.COOKIES.get('team', None)
        if team and team in self.all_teams_code:
            team_name = Team.objects.get(TeamCode=team).TeamName
            return team_name
        else:
            qs = UserTeamRole.objects.filter(UserName__UserName=self.UserName)
            team_name = qs[0].TeamCode.TeamName
            return team_name

    @property
    def user_team_roles_service(self):
        qs = V_UserTeamRole.objects.filter(UserName__UserName=self.UserName)
        team_roles = []
        if qs.exists():
            team_roles = list(qs.values())
        return team_roles

    @property
    def user_team_roles(self):
        qs = UserTeamRole.objects.filter(UserName__UserName=self.UserName)
        team_roles = []
        if qs.exists():
            team_roles = list(qs.values())
        return team_roles

    @property
    def is_active(self):
        User = get_user_model()
        user = User.objects.filter(username=self.UserName).first()
        if user:
            return user.is_active
        return False

    @property
    def is_staff(self):
        User = get_user_model()
        user = User.objects.filter(username=self.UserName).first()
        if user:
            return user.is_staff
        return False

    @property
    def is_superuser(self):
        User = get_user_model()
        user = User.objects.filter(username=self.UserName).first()
        if user:
            return user.is_superuser
        return False

    @property
    def groups(self):
        from HR.jwt import get_object_user
        user = get_object_user(None,self.UserName)
        return user.groups

    @property
    def DisplayDegreeType(self):
        return self.get_DegreeType_display()

    @property
    def FullName(self):
        return self.FirstName + " " + self.LastName

    @property
    def get_birth(self):
        if self.BirthDate:
            now = datetime.datetime.now().date()
            diff = now - self.BirthDate
            number_of_days = diff.days
            years = number_of_days // 365
            months = (number_of_days - years * 365) // 30
            days = (number_of_days - years * 365 - months * 30)
            return str(years) + " سال "
        return "25" + " سال "

    @property
    def get_contract(self):
        ret = ''
        if self.ContractDate:
            now = datetime.datetime.now().date()
            diff = now - self.ContractDate
            number_of_days = diff.days
            years = number_of_days // 365
            months = (number_of_days - years * 365) // 30
            days = (number_of_days - years * 365 - months * 30)
            if years != 0:
                ret = str(years) + " سال " + "#"
            if months != 0:
                ret += str(months) + " ماه " + "#"
            if days != 0:
                ret += str(days) + " روز "
            if ret and ret[-1] == "#":
                ret = ret[0:-1]
            ret = ret.replace("#", " و ")

        return ret

    @property
    def user_image_name(self):
        return self.UserName.replace("@eit", ".jpg")

    @property
    def get_degree(self):
        if self.Degree_Type:
            return self.Degree_Type.Caption
        return ''

    @property
    def get_study(self):
        education_history = EducationHistory.objects.filter(Person_id=self.UserName).first()
        if education_history:
            return education_history.EducationTendency.Title

        return ''

    @property
    def get_Marriage(self):
        return self.Marriage_Status.Caption if self.Marriage_Status else ''

    @property
    def GenderTitle(self):
        return 'آقا' if self.Gender else 'خانم'

    @property
    def GenderTitlePrefix(self):
        return 'جناب آقای' if self.Gender else 'سرکار خانم'

    @property
    def GenderTitlePrefixFullName(self):
        return f' جناب آقای {self.FullName}' if self.Gender else f' سرکار خانم {self.FullName}'


class PostalAddress(models.Model):
    class Meta:
        verbose_name = "آدرس پستی"
        verbose_name_plural = "آدرس های پستی"

    Title = models.CharField(max_length=100, verbose_name="عنوان", null=True, blank=True)
    City = models.ForeignKey("City", verbose_name="شهر", default=d.City,
                             on_delete=models.SET_DEFAULT)
    CityDistrict = models.ForeignKey("CityDistrict", verbose_name="منطقه", blank=True, null=True,
                                     on_delete=models.SET_NULL)
    AddressText = models.CharField(max_length=500, verbose_name="آدرس",  # validators=[jv.MinLengthValidator(20)],
                                   null=True, blank=True)
    No = models.CharField(max_length=20, verbose_name="پلاک", null=True, blank=True)
    UnitNo = models.PositiveSmallIntegerField(verbose_name="شماره واحد", null=True, blank=True)
    PostalCode = models.IntegerField(verbose_name="کد پستی", null=True, blank=True, validators=[v.PostalCode]
                                     )

    Person = models.ForeignKey("Users", verbose_name="فرد", blank=True, null=True, on_delete=models.CASCADE)

    # موقعیت جغرافیایی اضافه شود
    # اصلاح شود که در صورت نال بودن هر قسمت آورده نشود. همچنین کلمه کد پستی در خروجی نمایش داده شود

    def __str__(self):
        r = ""
        if self.Title is not None:
            r = self.Title + " : "
        if self.City.CityTitle is not None:
            r += self.City.CityTitle
        if self.AddressText is not None:
            r += ", " + self.AddressText
        if self.No is not None:
            r += ", " + self.No
        if self.UnitNo is not None:
            r += ", " + str(self.UnitNo)
        if self.PostalCode is not None:
            r += ", " + str(self.PostalCode)

        return r

    def clean(self):
        v.PersonCompanyValidator(self, 'آدرس')


class EmailAddress(models.Model):
    class Meta:
        verbose_name = "آدرس پست الکترونیکی"
        verbose_name_plural = "آدرس های پست الکترونیکی"

    Email = models.EmailField(verbose_name="ادرس ایمیل")
    Title = models.CharField(max_length=100, verbose_name="عنوان", null=True, blank=True)
    Person = models.ForeignKey("Users", verbose_name="فرد", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        val = self.Email
        if self.Title is not None:
            val = self.Title + " : " + val
        return val


class PhoneNumber(models.Model):
    class Meta:
        verbose_name = "شماره تماس"
        verbose_name_plural = "شماره های تماس"

    # City = models.ForeignKey("City", verbose_name="پیش شماره شهرستان", default=d.City,
    #                          null=True, blank=True, on_delete=models.SET_NULL)
    Province = models.ForeignKey("Province", verbose_name="پیش شماره شهرستان", default=d.City,
                                 null=True, blank=True, on_delete=models.SET_NULL)
    TelNumber = models.BigIntegerField(verbose_name="شماره تماس",
                                       help_text=" شماره ثابت بدون داخلی وارد شود. (مثلا : 87654321) شماره موبایل بدون صفر وارد شود مثلاً 9121234567",
                                       )
    TelType_Mobile = 1
    TelType_Home = 2
    TelType_Work = 3
    TelType_Emergency = 4
    TelTypeChoices = ((TelType_Mobile, "تلفن همراه"), (TelType_Home, "منزل"), (TelType_Work, "محل کار"),
                      (TelType_Emergency, "ضروری"))
    TelType2 = models.PositiveSmallIntegerField(choices=TelTypeChoices, verbose_name="نوع", null=True, blank=True)
    TelType = models.ForeignKey("ConstValue", verbose_name="نوع", on_delete=models.PROTECT)
    Title = models.CharField(max_length=50, verbose_name="توضیحات", blank=True, null=True)
    Person = models.ForeignKey("Users", verbose_name="فرد", blank=True, null=True, on_delete=models.CASCADE)

    # باید کنترل شود که اگر شماره تماس موبایل بود کد شهرستان وارد نشود
    # تعداد ارقام شماره موبایل چک شود
    # چک شود که شماره موبال با 9 شروع شود
    # تعداد ارقام شماره تلفن چک شود
    def clean(self):
        v.PersonCompanyValidator(self, 'تلفن')
        v.PhoneNumber(self)

    def __str__(self):
        Title = ""
        # if self.Company is not None:
        #     Title = self.Company.Title
        # elif self.Person is not None:
        #     Title = self.Person.LastName
        return Title + ' : ' + str(self.TelNumber)

    def TelTypeTitle(self):
        if self.TelType is not None:
            return self.TelType.Caption
        return "Not Found"


class ConstValue(models.Model):
    class Meta:
        verbose_name = "مقدار ثابت"
        verbose_name_plural = "مقادیر ثابت"
        ordering = ["Parent_id", "OrderNumber"]

    Caption = models.CharField(max_length=50, verbose_name="عنوان")
    Code = models.CharField(max_length=100, verbose_name="کد")
    Parent = models.ForeignKey("ConstValue", verbose_name="شناسه پدر", on_delete=models.CASCADE, null=True, blank=True)
    IsActive = models.BooleanField(verbose_name="فعال است؟", default=True)
    OrderNumber = models.PositiveSmallIntegerField(verbose_name="شماره ترتیب", null=True, blank=True, default=1)
    ConstValue = models.IntegerField(verbose_name="مقدار مربوطه"  # , validators=[jv.MinValueValidator(1)]
                                     , null=True,
                                     blank=True)

    def __str__(self):
        return self.Caption


class University(models.Model):
    class Meta:
        verbose_name = "دانشگاه"
        verbose_name_plural = "دانشگاه ها"

    Title = models.CharField(max_length=150, verbose_name="نام دانشگاه")
    PublicUniversity = 1
    IslamicAzadUniversity = 2
    NoneProfit = 3
    UAST = 4
    PNU = 5
    Virtual = 6
    UniversityTypeChoice = ((PublicUniversity, "دولتی"), (IslamicAzadUniversity, "دانشگاه آزاد اسلامی"),
                            (NoneProfit, "غیرانتفاعی"), (UAST, "علمی و کاربردی"), (PNU, "پیام نور"), (Virtual, "مجازی"))
    UniversityType = models.PositiveSmallIntegerField(choices=UniversityTypeChoice, verbose_name="نوع دانشگاه",
                                                      null=True, blank=True)
    University_Type = models.ForeignKey("ConstValue", verbose_name="نوع دانشگاه", on_delete=models.PROTECT,
                                        limit_choices_to=ConstValueChoice("UniversityType")
                                        , null=True, blank=True)
    UniversityCity = models.ForeignKey("City", verbose_name="شهر", default=d.City,
                                       on_delete=models.SET_DEFAULT)

    def __str__(self):
        return self.UniversityCity.CityTitle + " - " + self.Title

    @property
    def DisplayUniversityType(self):
        return self.get_UniversityType_display()


class FieldOfStudy(models.Model):
    class Meta:
        verbose_name = "رشته تحصیلی"
        verbose_name_plural = "رشته های تحصیلی"
        ordering = ("Title",)

    Title = models.CharField(max_length=150, verbose_name="رشته")

    def __str__(self):
        return self.Title


class Tendency(models.Model):
    class Meta:
        verbose_name = "گرایش تحصیلی"
        verbose_name_plural = "گرایش های تحصیلی"

    Title = models.CharField(max_length=150, verbose_name="گرایش")
    FieldOfStudy = models.ForeignKey("FieldOfStudy", verbose_name="گرایش تحصیلی", on_delete=models.CASCADE)

    def __str__(self):
        return self.FieldOfStudy.Title + " - " + self.Title


class EducationHistory(models.Model):
    class Meta:
        verbose_name = "سابقه تحصیلی"
        verbose_name_plural = "سوابق تحصیلی"

    Person = models.ForeignKey("Users", verbose_name="پرسنل", on_delete=models.CASCADE)

    PrimarySchool = 1
    HighSchool = 2
    Associate = 3
    Bachelor = 4
    Master = 5
    Doctoral = 6
    DegreeChoice = ((PrimarySchool, 'زیر دیپلم'), (HighSchool, 'دیپلم'), (Associate, 'کاردانی'), (Bachelor, 'کارشناسی')
                    , (Master, 'فوق کارشناسی')
                    , (Doctoral, 'دکترا'))
    DegreeType = models.IntegerField(choices=DegreeChoice, null=True, blank=True, verbose_name='مقطع تحصیلی')
    Degree_Type = models.ForeignKey('ConstValue', on_delete=models.PROTECT,
                                    verbose_name=' مقطع تحصیلی')
    University = models.ForeignKey("University", verbose_name="دانشگاه محل تحصیل",
                                   null=True, blank=True, on_delete=models.SET_NULL)
    StartDate = models.DateField(verbose_name="تاریخ شروع", blank=True, null=True)
    EndDate = models.DateField(verbose_name="تاریخ خاتمه", blank=True, null=True)
    StartYear = models.PositiveSmallIntegerField(verbose_name="سال ورود",
                                                 blank=True, null=True, validators=[v.YearNumber]
                                                 )
    EndYear = models.PositiveSmallIntegerField(verbose_name="سال فراغت از تحصیل",
                                               blank=True, null=True, validators=[v.YearNumber]
                                               )
    IsStudent = models.BooleanField(verbose_name="دانشجو است؟", default=False)
    EducationTendency = models.ForeignKey("Tendency", verbose_name="رشته",
                                          on_delete=models.PROTECT)
    GPA = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="معدل", null=True, blank=True)

    def __str__(self):
        r = ""
        if self.Person is not None:
            r = self.Person.LastName + " : "
        if self.University is not None:
            r += self.University.Title
        if self.EducationTendency is not None:
            r += " - " + self.EducationTendency.Title
        return r

    def DegreeTitle(self):
        if self.Degree_Type is not None:
            return self.Degree_Type.Caption

        return "Not Found"


#
# class Users(models.Model):
#     class Meta:
#         verbose_name = 'کاربر'
#         verbose_name_plural = 'کاربران'
#         db_table = 'Users'
#
#     UserName = models.CharField(primary_key=True, max_length=100, verbose_name='نام کاربری')
#     FirstName = models.CharField(max_length=200, verbose_name='نام')
#     LastName = models.CharField(max_length=200, verbose_name='نام خانوادگی')
#     BirthDate = models.DateField (null=True,blank=True ,verbose_name='تاریخ تولد')
#     ContractDate = models.DateField (null=True,blank=True, verbose_name='تاریخ استخدام')
#     FieldOfStudy = models.CharField(max_length=300, null=True, blank=True, verbose_name='رشته تحصیلی')
#     PrimarySchool = 1
#     HighSchool = 2
#     Associate = 3
#     Bachelor = 4
#     Master = 5
#     Doctoral = 6
#     DegreeChoice= ((PrimarySchool,'زیر دیپلم'),(HighSchool,'دیپلم'),(Associate,'کاردانی'),(Bachelor,'کارشناسی')
#                    ,(Master,'فوق کارشناسی')
#                    , (Doctoral ,'دکترا'))
#     DegreeType = models.IntegerField(choices=DegreeChoice, null=True, blank=True, verbose_name='مقطع تحصیلی')


class Team(models.Model):
    class Meta:
        db_table = 'Team'
        verbose_name = 'تیم'
        verbose_name_plural = 'تیم ها'

    TeamCode = models.CharField(primary_key=True, max_length=3, verbose_name='کدتیم')
    TeamName = models.CharField(max_length=100, verbose_name='نام تیم')
    ActiveInService = models.BooleanField(default=True, verbose_name=' کتاب')
    ActiveInEvaluation = models.BooleanField(default=True, verbose_name='ارزیابی')

    def __str__(self):
        return self.TeamName

    def get_pk(self):
        return self.pk

    def get_cls_name(self):
        return self.__class__.__name__


class Role(models.Model):
    class Meta:
        db_table = 'Role'
        verbose_name = 'سمت'
        verbose_name_plural = 'سمت ها'

    RoleId = models.IntegerField(primary_key=True, verbose_name='کد سمت')
    RoleName = models.CharField(max_length=100, verbose_name='نام سمت')
    HasLevel = models.BooleanField(default=False, verbose_name='دارای سطح')
    HasSuperior = models.BooleanField(default=False, verbose_name='ارشد دارد')

    def __str__(self):
        return self.RoleName


class UserTeamRole(models.Model):
    class Meta:
        db_table = 'UserTeamRole'
        verbose_name = 'اطلاعات پرسنل'
        verbose_name_plural = 'اطلاعات همه ی پرسنل'

    UserName = models.ForeignKey("Users", verbose_name='نام کاربری', related_name='UserTeamRoleUserNames',
                                 db_column='UserName', on_delete=models.CASCADE)
    TeamCode = models.ForeignKey("Team", db_column='TeamCode', on_delete=models.CASCADE, verbose_name='کدتیم')
    RoleId = models.ForeignKey("Role", db_column='RoleId', on_delete=models.CASCADE, verbose_name='کد سمت')
    LevelId = models.ForeignKey('RoleLevel', null=True, blank=True, on_delete=models.CASCADE, verbose_name='سطح')
    Superior = models.BooleanField(verbose_name='ارشد', default=False)
    ManagerUserName = models.ForeignKey("Users", null=True, blank=True, verbose_name='نام مدیر',
                                        related_name='UserTeamRoleManagerUserNames', on_delete=models.CASCADE)
    StartDate = models.CharField(max_length=10, verbose_name='تاریخ شروع')
    EndDate = models.CharField(max_length=10, null=True, blank=True, verbose_name='تاریخ پایان')

    def __str__(self):
        return '(' + self.RoleId.RoleName + ')' + '(' + self.TeamCode.TeamName + ')'

    @property
    def get_birth(self):
        if self.UserName.BirthDate:
            now = datetime.datetime.now().date()
            diff = now - self.UserName.BirthDate
            number_of_days = diff.days
            years = number_of_days // 365
            months = (number_of_days - years * 365) // 30
            days = (number_of_days - years * 365 - months * 30)
            return str(years) + " سال "
        return '25' + ' سال '

    @property
    def get_contract(self):
        ret = ''
        if self.UserName.ContractDate:
            now = datetime.datetime.now().date()
            diff = now - self.UserName.ContractDate
            number_of_days = diff.days
            years = number_of_days // 365
            months = (number_of_days - years * 365) // 30
            days = (number_of_days - years * 365 - months * 30)
            if years != 0:
                ret = str(years) + " سال " + "#"
            if months != 0:
                ret += str(months) + " ماه " + "#"
            if days != 0:
                ret += str(days) + " روز "
            if ret[-1] == "#":
                ret = ret[0:-1]
            ret = ret.replace("#", " و ")

        return ret


class RoleLevel(models.Model):
    LevelName = models.CharField(verbose_name='نام سطح', max_length=20)

    class Meta:
        db_table = 'RoleLevel'
        verbose_name = 'سطح'
        verbose_name_plural = 'سطوح'

    def __str__(self):
        return self.LevelName


class V_UserTeamRole(models.Model):
    class Meta:
        db_table = 'V_UserTeamRole'
        managed = False
        verbose_name = 'اطلاعات پرسنل'
        verbose_name_plural = 'اطلاعات همه ی پرسنل'

    UserName = models.ForeignKey("Users", verbose_name='نام کاربری', db_column='UserName', on_delete=models.CASCADE)
    TeamCode = models.ForeignKey("Team", db_column='TeamCode', on_delete=models.CASCADE, verbose_name='کدتیم')
    RoleId = models.ForeignKey("Role", db_column='RoleId', on_delete=models.CASCADE, verbose_name='کد سمت')
    LevelId = models.ForeignKey('RoleLevel', null=True, blank=True, on_delete=models.CASCADE, verbose_name='سطح')
    Superior = models.BooleanField(verbose_name='ارشد', default=False)
    StartDate = models.CharField(max_length=10, verbose_name='تاریخ شروع')
    EndDate = models.CharField(max_length=10, null=True, blank=True, verbose_name='تاریخ پایان')


class ChangeRole(models.Model):
    class Meta:
        verbose_name = 'اطلاعات تغییر سمت'
        verbose_name_plural = 'اطلاعات تغییر سمت ها'

    RoleID = models.ForeignKey('Role', related_name='ChangeRoleRoleIDs', on_delete=models.CASCADE,
                               verbose_name='سمت فعلی')
    LevelId = models.ForeignKey('RoleLevel', related_name='ChangeRoleRoleLevels', null=True, blank=True,
                                on_delete=models.CASCADE, verbose_name='سطح فعلی')
    Superior = models.BooleanField(verbose_name='وضعیت فعلی ارشد', default=False)
    RoleIdTarget = models.ForeignKey('Role', related_name='ChangeRoleRoleIdTargets', on_delete=models.CASCADE,
                                     verbose_name='سمت جدید')
    LevelIdTarget = models.ForeignKey('RoleLevel', related_name='ChangeRoleLevelIdTargets', null=True, blank=True,
                                      on_delete=models.CASCADE, verbose_name='سطح جدید')
    SuperiorTarget = models.BooleanField(verbose_name='وضعیت جدید ارشد', default=False)
    Education = models.BooleanField(default=True, verbose_name='آموزش نیاز دارد؟')
    Educator = models.CharField(max_length=100, null=True, blank=True, verbose_name='آموزش دهنده')
    Evaluation = models.BooleanField(default=True, verbose_name='ارزیابی نیاز دارد؟')
    Assessor = models.CharField(max_length=100, null=True, blank=True, verbose_name='ارزیابی کننده')
    RequestGap = models.IntegerField(null=True, blank=True, verbose_name='مدت زمان')
    Assessor2 = models.CharField(max_length=100, null=True, blank=True, verbose_name='ارزیابی کننده دوم')
    ReEvaluation = models.BooleanField(default=True, verbose_name='ارزیابی  دوم نیاز دارد؟')
    PmChange = models.BooleanField(default=True, verbose_name='تغیرات PM؟')
    ITChange = models.BooleanField(default=True, verbose_name='تغیرات IT؟')

    def __str__(self):
        return self.RoleID.RoleName + ' به ' + self.RoleIdTarget.RoleName


class RoleGroup(models.Model):
    class Meta:
        verbose_name = 'گروه سمت'
        verbose_name_plural = 'گروه های سمت ها'

    RoleID = models.ForeignKey('Role', related_name='RoleGroupRoleIDs', on_delete=models.CASCADE,
                               verbose_name='سمت فعلی')
    RoleGroup = models.CharField(max_length=50, verbose_name='گروه')
    RoleGroupName = models.CharField(max_length=100, null=True, blank=True, verbose_name=' نام گروه')

    def __str__(self):
        return self.RoleGroup


class RoleGroupTargetException(models.Model):
    class Meta:
        verbose_name = 'گروه سمت'
        verbose_name_plural = 'گروه های سمت ها'

    RoleGroup = models.CharField(max_length=100,
                                 verbose_name='گروه مبدا')
    RoleGroupTarget = models.CharField(max_length=100,
                                       verbose_name='گروه مقصد')

    def __str__(self):
        return self.RoleGroup + ' به ' + self.RoleGroupTarget


class AccessPersonnel(models.Model):
    class Meta:
        verbose_name = 'دسترسی انتخاب  سمت'
        verbose_name_plural = 'دسترسی های انتخاب همه سمت ها'

    UserName = models.ForeignKey("Users", verbose_name='نام کاربری', related_name='AccessPersonnelUserNames',
                                 on_delete=models.CASCADE)

    def __str__(self):
        return self.UserName.LastName


class OrganizationChartRole(models.Model):
    class Meta:
        verbose_name = 'سمت و سطح'
        verbose_name_plural = 'سمت ها و سطح ها'

    RoleId = models.ForeignKey('Role', related_name='OrganizationChartRoleRoleIDs', on_delete=models.CASCADE,
                               verbose_name='سمت')
    LevelId = models.ForeignKey('RoleLevel', related_name='OrganizationChartRoleRoleLevels', null=True, blank=True,
                                on_delete=models.CASCADE, verbose_name='سطح ')

    def __str__(self):
        return self.RoleId.RoleName


class OrganizationChartTeamRole(models.Model):
    class Meta:
        verbose_name = 'سمت  تیم'
        verbose_name_plural = 'سمت های تیم های عملیاتی'

    TeamCode = models.ForeignKey('Team', related_name='OrganizationChartTeamRoleTeamCodes', on_delete=models.CASCADE,
                                 verbose_name='نام تیم')
    RoleCount = models.IntegerField(verbose_name='ظرفیت سمت', null=True, blank=True)
    ManagerUserName = models.ForeignKey("Users", null=True, blank=True, verbose_name='نام مدیر',
                                        related_name='OrganizationChartTeamRoleManagerUserNames',
                                        on_delete=models.CASCADE)
    OrganizationChartRole = models.ForeignKey('OrganizationChartRole', on_delete=models.CASCADE,
                                              verbose_name='مدیر تیم و سمت')

    def __str__(self):
        return self.TeamCode


class UserHistory(models.Model):
    UserName = models.CharField(max_length=300)
    AppName = models.CharField(max_length=100, default=None, null=True)
    AuthLoginKey = models.CharField(max_length=300, null=True)
    RequestDate = models.DateTimeField(default=None)
    EnterDate = models.DateTimeField(default=None, null=True)
    RequestUrl = models.CharField(max_length=300, null=True)
    EnterUrl = models.CharField(max_length=300, null=True)
    IP = models.GenericIPAddressField(null=True)
    UserAgent = models.CharField(max_length=300, null=True)
    ChangedUserInfo = models.BooleanField(default=None, null=True)

    @property
    def GetEnterDate(self):
        if self.EnterDate is not None:
            return self.EnterDate.split(".")[0]
        return self.EnterDate

    @property
    def GetRequestDate(self):
        if self.RequestDate is not None:
            return self.RequestDate.split(".")[0]
        return self.RequestDate


class V_HR_RoleTarget(models.Model):
    class Meta:
        db_table = 'V_HR_RoleTarget'
        managed = False
        verbose_name = "تغییر جایگاه"
        verbose_name_plural = "تغییرات جایگاه"

    RoleID = models.ForeignKey('Role', db_column="RoleID", related_name='RoleTargetRoleIDs', on_delete=models.CASCADE,
                               verbose_name='سمت')
    RoleTargetID = models.ForeignKey('Role', db_column="RoleTargetID", related_name='RoleTargetRoleTargetIDs',
                                     on_delete=models.CASCADE, verbose_name='سمت')
    RoleTargetName = models.CharField(max_length=100, verbose_name='نام سمت مقصد')
    LevelID = models.ForeignKey('RoleLevel', db_column="LevelID", related_name='RoleTargetLevelIDs', null=True,
                                blank=True, on_delete=models.CASCADE, verbose_name='سطح ')
    LevelIdTargetID = models.ForeignKey('RoleLevel', db_column="LevelIdTargetID",
                                        related_name='RoleTargetLevelIdTargetID', null=True, blank=True,
                                        on_delete=models.CASCADE, verbose_name='سطح ')
    Superior = models.BooleanField(verbose_name='وضعیت فعلی ارشد', default=False)
    SuperiorTarget = models.BooleanField(verbose_name='وضعیت فعلی ارشد', default=False)
    Education = models.BooleanField(default=True, verbose_name='آموزش نیاز دارد؟')
    Educator = models.CharField(max_length=100, null=True, blank=True, verbose_name='آموزش دهنده')
    Evaluation = models.BooleanField(default=True, verbose_name='ارزیابی نیاز دارد؟')
    Assessor = models.CharField(max_length=100, null=True, blank=True, verbose_name='ارزیابی کننده')
    PmChange = models.BooleanField(default=True, verbose_name='تغیرات PM؟')
    ReEvaluation = models.BooleanField(default=True, verbose_name='ارزیابی مجدد')
    ITChange = models.BooleanField(default=True, verbose_name='تغیرات IT؟')
    RequestType = models.IntegerField(verbose_name='نوع درخواست')


class V_RoleTeam(models.Model):
    class Meta:
        db_table = 'V_RoleTeam'
        managed = False
        verbose_name = "سمت موجودر تیم"
        verbose_name_plural = "سمت های موجوددر تیم"

    Id = models.IntegerField(primary_key=True)
    RoleID = models.ForeignKey('Role', db_column="RoleID", related_name='RoleTeamRoleIDs', on_delete=models.CASCADE,
                               verbose_name='سمت')
    TeamCode = models.ForeignKey("Team", db_column='TeamCode', related_name='RoleTeamTeamCode',
                                 on_delete=models.CASCADE, verbose_name='کدتیم')
    ManagerUserName = models.ForeignKey("Users", related_name='RoleTeamManagerUserName', verbose_name='نام مدیر',
                                        db_column='ManagerUserName', on_delete=models.CASCADE)


class PreviousUserTeamRole(models.Model):
    class Meta:
        db_table = 'PreviousUserTeamRole'
        verbose_name = 'اطلاعات پرسنل'
        verbose_name_plural = 'اطلاعات همه ی پرسنل'

    UserName = models.ForeignKey("Users", verbose_name='نام کاربری', related_name='UserNames', db_column='UserName',
                                 on_delete=models.CASCADE)
    TeamCode = models.ForeignKey("Team", db_column='TeamCode', on_delete=models.CASCADE, verbose_name='کدتیم')
    RoleId = models.ForeignKey("Role", db_column='RoleId', on_delete=models.CASCADE, verbose_name='کد سمت')
    LevelId = models.ForeignKey('RoleLevel', null=True, blank=True, on_delete=models.CASCADE, verbose_name='سطح')
    Superior = models.BooleanField(verbose_name='ارشد', default=False)
    ManagerUserName = models.ForeignKey("Users", null=True, blank=True, verbose_name='نام مدیر',
                                        related_name='ManagerUserNames', on_delete=models.CASCADE)
    StartDate = models.CharField(max_length=10, verbose_name='تاریخ شروع')
    EndDate = models.CharField(max_length=10, null=True, blank=True, verbose_name='تاریخ پایان')

    def __str__(self):
        return '(' + self.RoleId.RoleName + ')' + '(' + self.TeamCode.TeamName + ')'

    @property
    def get_birth(self):
        if self.UserName.BirthDate:
            now = datetime.datetime.now().date()
            diff = now - self.UserName.BirthDate
            number_of_days = diff.days
            years = number_of_days // 365
            months = (number_of_days - years * 365) // 30
            days = (number_of_days - years * 365 - months * 30)
            return str(years) + " سال "
        return '25' + ' سال '

    @property
    def get_contract(self):
        ret = ''
        if self.UserName.ContractDate:
            now = datetime.datetime.now().date()
            diff = now - self.UserName.ContractDate
            number_of_days = diff.days
            years = number_of_days // 365
            months = (number_of_days - years * 365) // 30
            days = (number_of_days - years * 365 - months * 30)
            if years != 0:
                ret = str(years) + " سال " + "#"
            if months != 0:
                ret += str(months) + " ماه " + "#"
            if days != 0:
                ret += str(days) + " روز "
            if ret[-1] == "#":
                ret = ret[0:-1]
            ret = ret.replace("#", " و ")

        return ret


class Payment(models.Model):
    class Meta:
        verbose_name = "حقوق"
        verbose_name_plural = "حقوق های پرسنل"
        managed = False
        db_table = 'V_Payment'

    YearNumber = models.IntegerField(verbose_name='سال')
    Payment = models.BigIntegerField(null=True, blank=True, verbose_name='حقوق')
    MonthNo = models.IntegerField(verbose_name='ماه')
    PersonnelCode = models.CharField(max_length=10, verbose_name='کدملی')
    BasePayment = models.BigIntegerField(null=True, blank=True, verbose_name='پایه حقوق')
    UserName = models.ForeignKey("Users", verbose_name='نام کاربری', related_name='PaymentUserNames',
                                 db_column='UserName',
                                 on_delete=models.CASCADE)

    def __str__(self):
        return str(self.YearNumber)


class WorkTime(models.Model):
    class Meta:
        verbose_name = "اطلاعات چارگون"
        verbose_name_plural = "اطلاعات چارگون"
        managed = False
        db_table = 'WorkTime'

    UserName = models.ForeignKey("Users", verbose_name='نام کاربری', related_name='WorkTimeUserNames',
                                 db_column='UserName',
                                 on_delete=models.CASCADE)
    YearNo = models.IntegerField(verbose_name='سال')
    MonthNo = models.IntegerField(verbose_name='ماه')
    PersonnelCode = models.CharField(max_length=10, verbose_name='کدملی')
    WorkHours = models.CharField(max_length=10, verbose_name='ساعت حضوری')
    RemoteHours = models.CharField(max_length=10, verbose_name='ساعت دورکاری')
    RemoteDays = models.IntegerField(verbose_name='روز دورکاری')
    OverTime = models.CharField(max_length=10, verbose_name='اضافه کار')
    DeductionTime = models.CharField(max_length=10, verbose_name='کسر کار')
    OffTimeHourly = models.CharField(max_length=10, verbose_name='ساعت مرخصی')
    OffTimeDaily = models.IntegerField(verbose_name='روز مرخصی')
    Id = models.IntegerField(primary_key=True)


class V_WorkTime(models.Model):
    class Meta:
        verbose_name = "اطلاعات چارگون"
        verbose_name_plural = "اطلاعات چارگون"
        managed = False
        db_table = 'V_WorkTime'

    UserName = models.ForeignKey("Users", verbose_name='نام کاربری', related_name='V_WorkTimeUserNames',
                                 db_column='UserName',
                                 on_delete=models.CASCADE)
    YearNo = models.IntegerField(verbose_name='سال')
    WorkHours = models.CharField(max_length=10, verbose_name='ساعت حضوری')
    RemoteHours = models.CharField(max_length=10, verbose_name='ساعت دورکاری')
    RemoteDays = models.IntegerField(verbose_name='روز دورکاری')
    OverTime = models.CharField(max_length=10, verbose_name='اضافه کار')
    DeductionTime = models.CharField(max_length=10, verbose_name='کسر کار')
    OffTimeHourly = models.CharField(max_length=10, verbose_name='ساعت مرخصی')
    OffTimeDaily = models.IntegerField(verbose_name='روز مرخصی')
    Id = models.IntegerField(primary_key=True)


# class TeamJobPosition(models.Model):
#     class Meta:
#         verbose_name = "موقعیت شعلی در تیم"
#         verbose_name_plural = "موقعیت های شغلی در تیم ها"
#
#     TeamCode = models.ForeignKey("Team", db_column='TeamCode', on_delete=models.CASCADE, verbose_name='کد تیم')
#     RoleId = models.ForeignKey("Role", db_column='RoleId', on_delete=models.CASCADE, verbose_name='کد سمت')
#     PositionCount = models.PositiveSmallIntegerField(verbose_name="تعداد", default=1)
#
#     def __str__(self):
#         return self.TeamCode.TeamName + ' ' + self.RoleId.RoleName

class PageInformation(models.Model):
    class Meta:
        verbose_name = "اطلاعات صفحه"
        verbose_name_plural = "اطلاعات صفحات"
    PageName = models.CharField(max_length=30,verbose_name='نام صفحه')
    EnglishName = models.CharField(max_length=30, verbose_name='نام لاتین صفحه', )
    ColorSet = models.CharField(max_length=30, verbose_name='رنگ آیکون صفحه', )
    IconName = models.CharField(max_length=30, verbose_name='آیکون صفحه',)
    ShowDetail = models.BooleanField(default=False, verbose_name="جزییات نمایش داده شود؟")

    def __str__(self):
        return self.EnglishName

class PagePermission(models.Model):
    class Meta:
        verbose_name = "دسترسی صفحه"
        verbose_name_plural = "دسترسی های صفحات"

    Page = models.ForeignKey(verbose_name="نام صفحه", on_delete=models.CASCADE, to="PageInformation", null=True)
    GroupId = models.PositiveIntegerField(verbose_name='شناسه گروه')
    Editable = models.BooleanField(default=False,verbose_name='قابل ویرایش')


class V_PagePermission(models.Model):
    class Meta:
        verbose_name = "دسترسی صفحه"
        verbose_name_plural = "دسترسی های صفحات"
        managed = False
        db_table = "V_PagePermission"

    UserName = models.ForeignKey('Users',on_delete=models.CASCADE,verbose_name='نام کاربری')
    Page = models.ForeignKey(verbose_name="نام صفحه", on_delete=models.CASCADE, to="PageInformation", null=True)
    GroupId = models.PositiveIntegerField(verbose_name='شناسه گروه')
    Editable = models.BooleanField(default=False,verbose_name='قابل ویرایش')


