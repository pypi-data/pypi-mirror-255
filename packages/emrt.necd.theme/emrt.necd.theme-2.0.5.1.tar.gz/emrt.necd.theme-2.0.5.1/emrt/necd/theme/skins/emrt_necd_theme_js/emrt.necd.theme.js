function hightlight_restructured(){
    if ($("body").hasClass("template-emrt-necd-content-observation") ||
        $("body").hasClass("template-emrt-necd-content-conclusion") ||
        $("body").hasClass("template-edit-highlights") ||
        $("body").hasClass("template-edit portaltype-conclusion") ||
        $("body").hasClass("template-emrt-necd-content-conclusion") ||
        $("body").hasClass("template-emrt-necd-content-conclusionsphase2") ||
        $("body").hasClass("template-edit portaltype-conclusionsphase2") ||
        $("body").hasClass("template-view portaltype-observation")){
            $("<br/><br/><span style='font-weight:bold'>Draft/final conclusion flags</span><br/>").insertBefore($("input[value='psi']").parent())
    }
}

function init_emrt_necd_collapsible(context) {
  var context = context || document;
    $(".collapsiblePanelTitle", context).off("click.emrtNECD").on("click.emrtNECD", function(e){
        var panel = $(this).data("panel");
        if ($(this).hasClass("collapsed")){
            $("."+panel).show();
            if (panel == "observation-workflow"){
                $("#workflowTable").parent().scrollLeft($("#workflowTable").outerWidth())
            }
        }else{
            $("."+panel).hide();
        }
        $(this).toggleClass("collapsed");
    });
    $(".collapsibleListTitle", context).off("click.emrtNECD").on("click.emrtNECD", function(e){
        var list = $(this).data("list");
        if ($(this).hasClass("collapsed")){
            $("."+list).show();
        }else{
            $("."+list).hide();
        }
        $(this).toggleClass("collapsed");
    });
}

$(document).ready(function(){

  init_emrt_necd_collapsible();

	$(".clickableRow").off("click.emrtNECD").on("click.emrtNECD", function(evt) {
        window.open($(this).data("href"), "_blank");
	});
	$(".datetimeWF").each(function(){
		var time = $.trim($(this).text());
        var timeAgo = moment(time, "YYYY/MM/DD HH:mm:ss").format("YYYY/MM/DD HH:mm:ss")
        var timeZone = time.substr(time.indexOf("+", time.length))
        timeAgo += " +0" + timeZone + ":00"
		$(this).text(moment(timeAgo, "YYYY/MM/DD HH:mm:ss Z").fromNow())
	});
    hightlight_restructured();
    $('a.standardButton[title][title!=""]').addClass("tooltipIcon");
});
