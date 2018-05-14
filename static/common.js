$(function(){
    //toastr初始化
    toastr.options = {
        "closeButton": false,
        "debug": false,
        "positionClass": "toast-bottom-center",
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "8000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    }
})

/** 
 * 封装layer打开窗口的方法, 前台调用
 * @param string url 跳转弹窗 标题页面路径
 * @param string title 弹窗 标题
 * @param Array params layer需要的其他参数，一般传递null即可
 * @return null 没有返回值
 * 特殊情况需要传递params时，请参考layer的参数设置传递下面的各个参数
 * by zhaojpiing QQ: 17620286
*/
function openLayerPopup(url, title, params){
    layParams = new Array();
    layParams['type']          = 2;
    layParams['shadeClose']    = true;
    layParams['shade']         = 0.8;
    layParams['width']         = '800px';
    layParams['height']        = '500px';
    layParams['titleColor']    = '#fff';
    layParams['titleBackground']    = '#aaa';
    if (typeof(params) != 'undefined' && params != '' && params != null) {
        layParams['type']          = params['type']         || layParams['type'];
        //单独处理一下shadeClose的数据
        if (params['shadeClose'] != null && params['shadeClose'] != undefined) {
            layParams['shadeClose'] = params['shadeClose'];
        }
        layParams['shade']         = params['shade']        || layParams['shade'];
        layParams['width']         = params['width']        || layParams['width'];
        layParams['height']        = params['height']       || layParams['height'];
        layParams['titleColor']    = params['titleColor']   || layParams['titleColor'];
        layParams['titleBackground'] = params['titleBackground'] || layParams['titleBackground'];
    }
    
    // console.log(layParams);
    parent.layer.open({
        type: layParams['type'], 
        shadeClose: layParams['shadeClose'],
        shade: layParams['shade'],
        area: [layParams['width'], layParams['height']],
        title:  [title, 'color: '+ layParams['titleColor'] +'; background:'+ layParams['titleBackground'] +';'],
        content: url
    });
}

//表单ajax提交  by zhaojiping  liniukeji.com
var _IS_SUBMIT_SUCCESS = false;
var time = 0;
function enbaleSubmitButton(){
    $("button:submit").attr("disabled", false);
}
$(document)
    .ajaxStart(function(){
        $("button:submit").attr("disabled", true);
    })
    .ajaxStop(function(){
        if (time > 0) {
            setTimeout("enbaleSubmitButton();", 5000);//延时5s执行
        } else {
            $("button:submit").attr("disabled", false);
            time = 1;
        }
        
    });

$(".ajaxForm").submit(function(){
    var self = $(this);

    // 验证函数
    if (typeof(validate) != 'undefined' && $.isFunction(validate)) {
        if ( eval(validate)() == false ) {
            return false;
        }
    }

    $.ajax({
        type : "POST",
        cache: false,
        url  : self.attr("action"),
        data : self.serialize(),
        datatype : "json",
        success : success,
        error: function(){
            alert("程序错误!")
        }
    });
    return false;

    function success(data){
        // console.log(data);
        data = eval('(' + data + ')');
        //当有自定义回调函数时, 执行并执行回调函数
        if (typeof(callback) != 'undefined' && $.isFunction(callback)) {
            eval(callback)(data);
            
            return true;
        }

        //如果没有回调函数, 默认执行
        if(data.status == 1){
        	_IS_SUBMIT_SUCCESS = true;

            if (data.info != '' && typeof(data.info) != 'undefined')  toastr.success(data.info);;
            //跳转页面
            if ( typeof(_TARGET_URL) != 'undefined' && _TARGET_URL != '') {
                window.location.href = _TARGET_URL;
            }
            //刷新页面
            if ( typeof(_NEED_REFRESH) != 'undefined' && _NEED_REFRESH == true) {
                location.reload();
            }
        } else {
            if (data.info != '' && typeof(data.info) != 'undefined') toastr.error(data.info);
            else  toastr.error('未定义错误!');
        }
    }
});
// 表单ajax提交End

// 返回按钮事件
function goback(){
	if (_IS_SUBMIT_SUCCESS) {
		self.location=document.referrer;
	} else {
		history.back();
	}
}

// 改变数据的可用状态 
function change_disabled(id, value){
	var url = CHANGE_STAUTS_URL + "/id/" + id + "/disabled/" + value;
    // console.log(url);// return false;
    $.get(url, function(data){
        if(data.status == '1'){
            window.location.reload();
            toastr.success(data.info);
        }else{
        	if (typeof(data.info) != 'undefined') toastr.error(data.info);
			else console.log(data);
        }
    });
}

/**
 * 按主键的值进行删除数据表中的记录
 * id:主键的值. 当值为checkbox时, 由checkbox生成
 * message:弹出确认对话框的信息;
 * isDelete: 是否为物理删除
 * RECYCLE_URL: 全局变量, 删除的处理URL
 */
function recycle(id, message, isDelete){
    if(id == 'chkbId'){
        id = checkedIds('chkbId');
        //console.log(id);return;
        if(id == false)  return false;
    }
    var url = '';
    if (isDelete === true) url = DELETE_URL + "?id=" + id;
    else url = RECYCLE_URL + "?id=" + id;

    // console.log(url);// return false;
    if(confirm(message)){
         $.get(url, function(data){
            data = eval('(' + data + ')');
            // alert(data.status)
            if(data.status == '1'){
                window.location.reload();
                toastr.success(data.info);
            }else{
            	if (typeof(data.info) != 'undefined') {
            		toastr.error(data.info);
            	} else {
            		console.log(data);
            	}
            }
        });
    }
}