cellinput_html = '\
<div class="container-fluid cellfield" >\
  <div class="cellinputmeta">\
    <table><tr>\
      <td><button class="cellinputtype" style="width: 35px;">Aa</button></td>\
      <td style="width: 100%; padding-left:5px">\
        <input type=text class="newfield cellinputname">\
      </td>\
    </tr></table>\
  </div>\
  <textarea rows=2 class="newfield cellinputcontent"></textarea>\
</div>\
'
// using jQuery

var CELL_NAME = "cell name";
var CELL_CONTENT = "cell content";
var TAGS = "tag1 tag2 ...";
var POST_TITLE = "post title";

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function statusclear(){
  $('#status').html("");
}
function statuserror(error){
  $('#status').append("<p style='color:#c06060;'>"+error+"</p>");
}
function statusupdate(update){
  $('#status').append("<p>"+update+"</p>");
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(function(){
  console.log('ready');
  $('.newfield').css('color', '#909090');
  setup_inputs()

  $('#addcell').click(function (){
    var cellinputs = $("#cellinputs");
    cellinputs.append(cellinput_html);
    //cellfields = $(".cellfield");
    //$(cellfields[cellfields.length-1]).css("margin-bottom", "0");
    //$(cellfields[cellfields.length-2]).css("margin-bottom", "10px");
    setup_inputs()
  });

  $('#submit').click(function(){
    statusclear();
    statusupdate("submitting");
    post = {};
    post.title = $('#titlefield')[0].value;
    if (post.title == POST_TITLE) post.title = "";
    post.tagstring = $('#tagfield')[0].value;
    if (post.tagstring == TAGS) post.tagstring = "untagged";
    post.author = 'murtaza64' //TODO fix, uh, this whole thing
    post.cells = [];
    var cellfields = $('.cellfield');
    var cellinputnames = $('.cellinputname');
    var cellinputcontents = $('.cellinputcontent');
    var cellinputtypes = $('.cellinputtype');
    for (var i = 0; i < cellfields.length; i++){
      cell = {}
      cellfield = cellfields[i]
      cell.title = cellinputnames[i].value;
      if (cell.title == CELL_NAME) cell.title = "";
      cell.content = cellinputcontents[i].value;
      if (cell.content == CELL_CONTENT) cell.content = "";
      type_btn = cellinputtypes[i]
      if (type_btn.innerHTML == 'Aa'){
        cell.type = 0;
      } else if (type_btn.innerHTML == 'MD'){
        cell.type = 1;
      } else {
        cell.type = 2;
      }
      cell.lang = null
      if (cell.title != "" || cell.content != ""){
        post.cells.push(cell)
      }
    }
    console.log(post)
    $.ajax({
      method : "POST",
      data: JSON.stringify(post),

        //{post: post,
        //csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()},

      contentType: 'application/json',
      processData: false,
      success: function(data, status, jqXHR){
        statusclear();
        console.log("ajax success");
        console.log(data);
        if (!data.success){
          if (data.error == "empty post"){
            statuserror("error: empty post");
          }
        }
        else{
          statusupdate("post created");
          statusupdate("<a href='"+data.link+"'>"+data.link+"</a>");
        }
      },
      error: function(){
        statusclear()
        console.log("ajax failure");
        statuserror("ajax error");
      }
    });
  });
});

function setup_inputs(){
  //$('.newfield').prop('contenteditable',true);
  $('.cellinputtype').click(function(){
    var i = $('.cellinputtype').index(this)
    if (this.innerHTML == 'Aa'){
      this.innerHTML = 'MD';
    } else if (this.innerHTML == 'MD'){
      this.innerHTML = '{}';
      this.style.paddingTop = 0;
      $('.cellinputcontent')[i].style.fontFamily = "Consolas,monospace";
      this.style.fontFamily = "Consolas,monospace";
    } else {
      this.style.paddingTop = 2;
      this.innerHTML = 'Aa';
      $('.cellinputcontent')[i].style.fontFamily = "inherit";
      this.style.fontFamily = "inherit";
    }
  });

  $('textarea').each(function () { //from Obsidian on StackOverflow
      this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
  }).on('input', function () {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
  });


  function setup_placeholder(selector, plchldr){
    $(selector).focus(function(){
      if (this.value == plchldr){
        this.value = "";
      }
      $(this).css('color', 'inherit');
    }).focusout(function(){
      if (this.value == ""){
        $(this).css('color', '#909090');
        this.value = plchldr;
      }
    })
    sel = $(selector);
    for (var i=0; i<sel.length; i++){
      //console.log(sel[i], sel[i].value);
      if (sel[i].value == ""){
        sel[i].value = plchldr;
        //console.log(sel[i], sel[i].value);
      }
      if (sel[i].value == plchldr){
        sel[i].style.color = '#909090';
      }
    }
  }

  setup_placeholder("#titlefield", POST_TITLE);
  setup_placeholder("#tagfield", TAGS);
  setup_placeholder(".cellinputname", CELL_NAME);
  setup_placeholder(".cellinputcontent", CELL_CONTENT);
}
