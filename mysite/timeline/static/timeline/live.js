var next_page = 1;
var base_url = '/';
var post_template;
var $content;
var _throttleTimer;
var loading_page = false;
var rehighlight_timer = null;
var rehighlighting = false;
var more_pages = true;

function rehighlight(){
    console.log("rehighlighting");
    if(!$("pre code.unhighlighted").length && rehighlighting){
        console.log("clearing interval");
        clearInterval(rehighlight_timer);
        rehighlighting = false;
        return;
    }
    $("pre code.unhighlighted").each(function(i, block) {
        //console.log(block)
        //try {
            var worker = newWorker(hljs_worker);
            worker.onmessage = function(event){
                block.innerHTML = event.data;
                $(block).removeClass("unhighlighted");
            };
            worker.postMessage({
                code: block.textContent,
                lang: block.getAttribute("class").replace(/^unhighlighted hljs ?/, ''),
                url: document.location.protocol + '//' + document.location.host + '/'
            });
        //}
        //finally {}
    });
}

function hljs_worker(){
    onmessage = function(event) {
        importScripts(event.data.url + 'static/js/highlight.min.js');
        if(event.data.lang){
            var result = self.hljs.highlight(event.data.lang, event.data.code);
        }
        else {
            var result = self.hljs.highlightAuto(event.data.code);
        }
        postMessage(result.value);
    }
}
//from uberschmekel on StackOverflow
var newWorker = function (funcObj) {
    // Build a worker from an anonymous function body
    var blobURL = URL.createObjectURL(new Blob(
        ['(', funcObj.toString(), ')()'],
        {type: 'application/javascript'}
     ));
    var worker = new Worker(blobURL);
    // Won't be needing this anymore
    URL.revokeObjectURL(blobURL);
    return worker;
}

function extend_page(){
    loading_page_start();
    $.ajax({
        method: "GET",
        url: base_url,
        data: {"format": "json", "page": next_page},
        contentType: 'application/json',
        success: function(data, status, jqXHR) {
            //console.log(data);
            for (var i = 0; i < data.data.length; i++){
                //console.log(data.data[i]);
                $('#posts').append(post_template(data.data[i].fields));
                if (!rehighlighting){
                    rehighlight()
                    rehighlight_timer = setInterval(rehighlight, 1500);
                    rehighlighting = true;
                }
            }
            //$('#posts').append('<br><br>');
            next_page++;
            loading_page_end();
        },
        error: function(jqXHR, status, error){
            if (error == "Not Found"){
                no_more_pages();
            }
        }
    })
}
function loading_page_start(){
    loading_page = true;
    $('#page_extender').html("loading...").off("click.live");
}
function loading_page_end(){
    loading_page = false;
    $('#page_extender').html("<a href='#'>load more</a>").on("click.live", extend_page);
}
function no_more_pages(){
    more_pages = false;
    $('#page_extender').html("no more posts").off("click.live");
}

function ScrollHandler(e) { //from geo1701 on StackOverflow
    clearTimeout(_throttleTimer);
    _throttleTimer = setTimeout(function () {
        if ($content.scrollTop() + $(window).height() > $content_row.height() - 100) {
            if (!loading_page && more_pages){
                extend_page();
            }
        }
    }, 100);
}

$(function(){
    $content = $("#content_col");
    $content_row = $("#content_row");
    $content.off("scroll", ScrollHandler).on("scroll", ScrollHandler);
    Handlebars.registerHelper('easydate', function(options){
        return options.fn(this).substring(0,10); 
    }) //this might be the HACKiest thing I've ever written
    post_template = Handlebars.compile($('#post_template').html());

    //console.log(post_template);
    extend_page()
})
