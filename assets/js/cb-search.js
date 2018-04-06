$(document).ready(function () {
    var time1 = 0;
    var show = false;
    var names = new Array(); //文章名字等
    var urls = new Array(); //文章地址
    $(document).keyup(function (e) {
        var time2 = new Date().getTime();
        if (e.keyCode == 17) {
            var gap = time2 - time1;
            time1 = time2;
            if (gap < 500) {
                if (show) {
                    $(".cb-search-tool").css("display", "none");
                    show = false;
                } else {
                    $(".cb-search-tool").css("display", "block");
                    show = true;
                    $("#cb-search-content").val("");
                    $("#cb-search-content").focus();
                }
                time1 = 0;
            }
        } else if (e.keyCode == 27) {
            $(".cb-search-tool").css("display", "none");
            show = false;
            time1 = 0;
        }
    });

    $("#cb-search-content").keyup(function (e) {
        var time2 = new Date().getTime();
        if (e.keyCode == 17) {
            var gap = time2 - time1;
            time1 = time2;
            if (gap < 500) {
                if (show) {
                    $(".cb-search-tool").css("display", "none");
                    show = false;
                } else {
                    $(".cb-search-tool").css("display", "block");
                    show = true;
                    $("#cb-search-content").val("");
                    $("#cb-search-content").focus();
                }
                time1 = 0;
            }
        }
    });

    $("#cb-close-btn").click(function () {
        $(".cb-search-tool").css("display", "none");
        show = false;
        time1 = 0;
    });

    $("#cb-search-btn").click(function () {
        $(".cb-search-tool").css("display", "block");
        show = true;
        $("#cb-search-content").val("");
        $("#cb-search-content").focus();
        time1 = 0;
    });

    $.getJSON("/assets/cb-search.json", function (data) {
        if (data.code == 0) {
            console.log(data)
            for (var index in data.data) {
                var item = data.data[index];
                names.push(item.title);
                urls.push(item.url);
            }
            
            $.typeahead({
                input: '.js-typeahead-search',
                order: "desc",
                source: {
                    data: names
                },
                callback: {
                    onInit: function (node) {
                        console.log('Typeahead Initiated on ' + node.selector);
                    },
                    onClickAfter: function (node, a, item, event) {
 
                        event.preventDefault;
                        $(".cb-search-tool").css("display", "none");
                        show = false;
                        let name = item.display;
                        console.log(name);
                        console.log(names.indexOf(name));
                        console.log(urls[names.indexOf(name)]);
                        window.location.href = (urls[names.indexOf(name)]);
                        // href key gets added inside item from options.href configuration
                        // alert(item.href);
             
                    }
                }
            });

        }
    });

});