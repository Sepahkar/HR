/***********************************Global Page Start*************************/
$(".YearBar span").click(
    function ()
    {
        //remove previous selected year style
        $(".YearBar span").removeClass("Selected")
        //select this year, change color and position
        year = $(this)
        //find number to move selector pointer
        d = (year.text()-1400) * 178 + 60
        $(".YearPicker img").animate({
        left: d,
      }, 500, function ()
        {
        year.addClass("Selected")
        })

    }
)


function RunAjax(url, method, data)
{
    debugger
    $.ajax(
        {
        url : url, // the endpoint
        type : method, // http method
        data : data, // data sent with the get request

        // handle a successful response
        success : function(json) {
            debugger
            // j = $.parseJSON(json)
            //     $("#PersonId").val(j.PersonId)
            if (json.success)
            {
                console.log(json)
                console.log("success"); // another sanity check
                $.alert({
                    title: 'موفقیت آمیز',
                    content: "اطلاعات به روزرسانی شد",
                    type: 'green',
                    typeAnimated: true,
                    buttons: {
                        close: {
                            text: 'بستن',
                            btnClass: 'btn-success',
                        },
                    }
                });
            }
            else
            {
            $.alert({
                title: 'خطا',
                content: "به روزرساني اطلاعات با خطا مواجه شد",
                type: 'red',
                typeAnimated: true,
                buttons: {
                    close: {
                        text: 'بستن',
                        btnClass: 'btn-success',
                    },
                }
            });
            }

        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            //debugger
            //alert(xhr.status + ' ' + xhr.responseText)
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            //extract error info
            let rt =  xhr.responseText
            let ErrorText = ""
            let ErrorPlace = ""
            $(rt).find('tr th').each(
                function(index, item)
                {
                    if ($(item).text()=='Exception Value:')
                        ErrorText = $(item).next().text()
                    if ($(item).text()=='Exception Location:')
                        ErrorPlace = $(item).next().text()
                }
            )
            let msg = ""
            msg = "متاسفانه عملیات با خطا مواجه شد"
            msg += "<br/>" +ErrorText+"<br/>"+ErrorPlace
            $.alert({
                title: 'خطا',
                content: msg,
                type: 'red',
                typeAnimated: true,
                buttons: {
                    close: {
                        text: 'بستن',
                        btnClass: 'btn-red',
                    },
                }
            });
        }
    });
}
/***********************************Global Page End*************************/

/***********************************First Page Start*************************/
function ShowIcon(IsCorp)
{
    if (IsCorp)
        table = $(".Right .IconTable")
    else
        table = $(".Left .IconTable")

    table.find("td").each(
        function (index, item) {
            setTimeout(
              function()
              {
                //get which image is shown?
                var image_no = $(item).attr("data")
                //find next image to show
                var new_image_no = parseInt(image_no) + 1
                if ((IsCorp && new_image_no > 16) || (!IsCorp && new_image_no > 10))
                    new_image_no = 1
                // console.log("image no :", image_no)
                // console.log("new image no :", new_image_no)
                //hide all image in this td
                $(item).find("img").hide()
                 //show new image
                $(item).find("img[data='"+new_image_no+"']").fadeIn(2500)
                //console.log("show image:" ,new_image_no)


                //set number of new shown image in td data
                $(item).attr("data",new_image_no)
              }, (Math.floor(Math.random()*10)+3)*2000);

        }
    )
}
function Box_Show(IsCorp, IsShow)
{

    if (IsCorp)
    {
        box = $(".Right")
        other_box = $(".Left")
    }
    else
    {
        box = $(".Left")
        other_box = $(".Right")
    }

    if (IsShow)
    {
        box.find(".IconTable").show()
        W = 500
    }
    else
    {
        W = 0
        box.find(".IconTable").hide()
    }


    box.animate(
        {
            width:W,
        },500,
        function()
        {
                ShowIcon(IsCorp)
        })

}
$(".FirstPage .Title").hover(
    function ()
    {
        Box_Show($(this).hasClass("Corp"), true)
        Box_Show(!$(this).hasClass("Corp"), false)

    }
)

/***********************************First Page End**************************/

/***********************************Person Page Start**************************/
$(".PersonPage .Refresh").click(function ()
{
    var counterTmpAnimnNew = 0;
    var element = $(this);
    counterTmpAnimnNew = counterTmpAnimnNew + 360;

    $({degrees: counterTmpAnimnNew - 360}).animate({degrees: counterTmpAnimnNew}, {
        duration: 1000,
        step: function(now) {
            element.css({
                transform: 'rotate(' + now + 'deg)'
            });
        }
    });
    let url = window.location.href
    Form = $("form[name='frmPersonInfo']")
    data = Form.serializeArray()
    $(".SubmitForm").click()
    //RunAjax(url, "POST", data)
})
function ActiveRoleIcon(Icon, Active)
{
    src = Icon.attr('src')
    l = src.length
    if (Active)
    {
        s = src.substring(0, l-4)+'active.png'
        Icon.addClass('Active')
        if (Icon.hasClass("Superior"))
            $("input[name='IsSuperior']").val(1)
        else
            $("input[name='Level']").val(Icon.attr("data"))
    }
    else
    {
        s = src.substring(0, l-10)+'.png'
        Icon.removeClass('Active')
        if (Icon.hasClass("Superior"))
            $("input[name='IsSuperior']").val(0)

    }
    Icon.attr('src', s)
}
$(".Level").click(
    function ()
    {
        //at first remove active from active image
        //we have to active icon, one for role and another one for Superior
        //we must sepreate them, if we active role, must not deactive Superior
        // debugger
        //if it is superior icon, we must not deactive any thing
        if (!($(this).hasClass("Superior")))
        {
            ActiveRoleIcon($(".Active").not(".Superior"), false)
            ActiveRoleIcon($(this), true)
        }
        else
        {
            if ($(this).hasClass("Active"))
                ActiveRoleIcon($(this), false)
            else
                ActiveRoleIcon($(this), true)
        }



    }
)

$(".PersonnelIcon").hover(
    function () {
        var info = $(this).parents('.PersonnelPlace').find('.MainInfo')
        info.fadeIn(1000, "linear")
    }
)
$(".PersonnelPlace").mouseleave(
    function () {
        var info = $(this).find('.MainInfo')
        info.fadeOut(1000, "swing")
    }
)
/***********************************Person Page End**************************/
