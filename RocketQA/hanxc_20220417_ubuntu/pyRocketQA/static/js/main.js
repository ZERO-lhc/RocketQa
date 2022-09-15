function jump(url, value) {
    /*在当前页面打开
    window.location.href='https://baidu.com/s?wd='+document.getElementById('textbox').value
    */

    let fullUrl = url;
    if(value) {
        fullUrl = url + '?search=' + encodeURIComponent(value);
    }
    console.log("urlSearch", value);
    window.open(fullUrl, "_self");
}

/**
 * 获取URL参数
 */
function getRequestParam() {
    const urlSearch = new URLSearchParams(location.search);
    return Object.fromEntries(urlSearch.entries());
}

function requestSearch(props) {
    if (!props.searchText) {
        alert("请输入关键字！")
        return;
    }
    props.isLoading = true;
    // 显示加载动画
    // footer.appendChild(loadingImg);
    //TO DO 此处修改results的值可改变加载内容，改变noMoreResults的值触发结尾
    //setTimeout('vm.add("list",results);footer.removeChild(footer.lastChild);',2500);


    // 获取检索结果
    $.ajax({
        url: 'pyQA/questionQuery',
        type: 'get',
        async: true,//使用同步的方式,true为异步方式
        data: {'sentence': props.searchText, 'page': props.page},//这里使用json对象
        success: (data) => {
            console.log('search data: ', data);
            if (data) {
                const parsedData = JSON.parse(data);

                if (parsedData.data?.answer.length == 0){
                    alert("未搜索到匹配信息！");
                }
                else {
                    props.page++;
                    // vueApp.add("itemExtend", parseddata.data.answer);
                    props.items.push(...parsedData.data?.answer || [])
                }

            }
            props.isLoading = false;
        },
        fail: () => {
            alert("connection failed");
            props.isLoading = false;
        },
        error: () => {
            props.isLoading = false;
            alert("数据文件做成中……请稍后重试！");
        }
    });
}


// 发送点赞/踩请求
function requestVote(upNum, downNum, questionId, callback) {
    $.ajax({
        url: 'pyQA/vote',
        type: 'get',
        async: true,//使用同步的方式,true为异步方式
        data: {
            'questionId': questionId,
            'numUpvote': upNum,
            'numDownvote': downNum
        },//这里使用json对象
        success: () => {
            callback();
        },
        fail: () => {
            alert('点赞/踩失败！');
        }
    });
}

// function keepConnection() {
//     $.ajax({
//         url: 'pyQA/keepConnection',
//         type: 'get',
//         async: true,//使用同步的方式,true为异步方式
//         data: '',
//         success: () => {
//             console.log('-------------- ');
//         },
//         fail: () => {
//             console.log('+++++++++++++ ');
//         }
//     });
//     console.log('!!!!!!!!!! ');
// }

function requestUpload(props) {
    if (!props.file) {
        alert("请选择数据文件！")
        return;
    }
    props.isLoading = true;
    const formData = new FormData();
    formData.append("indexFile", props.file);
    let intervalHandle;
    // 上传文件
    $.ajax({
        url: 'pyQA/saveIndexFile',
        type: 'post',
        async: true,//使用同步的方式,true为异步方式
        data: formData,
        processData: false,
        contentType: false,
        cache: false,
        success: (data) => {
            // clearInterval(intervalHandle);
            // alert("connection success");
            console.log('upload file: ', props.file?.name);
            props.isLoading = false;
            props.file = undefined;
            props.message = "上传成功！";


        },
        fail: () => {
            // clearInterval(intervalHandle);
            // alert("connection failed");
            props.isLoading = false;
            props.message = "上传失败！";

        },
        error: () => {
            props.isLoading = false;
            props.message = "数据文件做成中……请稍后重试！";
        }
    });

    // intervalHandle = setInterval(keepConnection, 20000);


    // .fail(() => {
    //     alert("connection failed");
    //     props.isLoading = false;
    // });

}


function restartService(props) {

    props.isLoading = true;

    // 重启服务
    $.ajax({
        url: 'pyQA/restartService',
        type: 'post',
        async: true,//使用同步的方式,true为异步方式
        data: '',
        processData: false,
        contentType: false,
        cache: false,
        success:() => {
            console.log('restartService-------------- ');
            props.isLoading = false;
            props.message = "启动成功！";
        },
        fail: () => {

            props.isLoading = false;
            props.message = "启动失败！";
        },
        error: () => {
            props.isLoading = false;
            props.message = "数据文件做成中……请稍后重试！";
        }
    });

}
