CELLINPUT_HTML = '\
<div class="container-fluid cellfield" >\
  <div class="cellinputmeta">\
    <table><tr>\
      <td><button class="cellinputtype">Aa</button></td>\
      <td style="width: 100%; padding-left:5px">\
        <input type=text class="newfield cellinputname">\
      </td>\
      <td>\
        <input type=text class="newfield cellinputlang">\
      </td>\
    </tr></table>\
  </div>\
  <div class="cic_container">\
      <div class = ace></div>\
  </div>\
</div>';
// using jQuery

TEXTAREA_HTML = '<textarea rows=2 class="newfield cellinputcontent"></textarea>';

var CELL_NAME = "cell name";
var CELL_CONTENT = "cell content";
var TAGS = "tag1 tag2 ...";
var POST_TITLE = "post title";
var LANG = "language"

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
  setup_inputs(0);
  setup_ace(0);
  setup_placeholder("#titlefield", POST_TITLE);
  setup_placeholder("#tagfield", TAGS);

  $('#addcell').click(function (){
    var cellinputs = $("#cellinputs");
    cellinputs.append(CELLINPUT_HTML);
    //cellfields = $(".cellfield");
    //$(cellfields[cellfields.length-1]).css("margin-bottom", "0");
    //$(cellfields[cellfields.length-2]).css("margin-bottom", "10px");
    var i = $('.cellfield').length-1;
    setup_ace(i);
    setup_inputs(i);
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
    var cellinputtypes = $('.cellinputtype');
    var cellinputlangs = $('.cellinputlang');
    for (var i = 0; i < cellfields.length; i++){
      cell = {}
      cellfield = cellfields[i]
      cell.title = cellinputnames[i].value;
      if (cell.title == CELL_NAME) cell.title = "";
      var editor = ace.edit("ace_editor" + i.toString());
      cell.content = editor.getValue();
      if (cell.content == CELL_CONTENT) cell.content = "";
      cell.lang = cellinputlangs[i]
      if (cell.lang == LANG) cell.lang = "";
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
function setup_ace(i){
  var editor_id = "ace_editor" + i.toString();
  $('.ace')[i].id = editor_id;
  var editor = ace.edit(editor_id);
  editor.setTheme("ace/theme/github");
  editor.setOptions({
    minLines: 5,
    maxLines: 50
  });
  editor.getSession().setMode("ace/mode/text");
  editor.getSession().setUseSoftTabs(true);

  editor.getSession().on("changeMode", function(){
    console.log('changed mode');
    $($(".cellinputlang")[i]).css("border-color", "#409060");
    $(".cellinputlang")[i].last_correct_mode = $(".cellinputlang")[i].value.toLowerCase();
  });
}
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

    $(selector).val(plchldr);
    $(selector).css("color", "#909090");
}
function setup_inputs(i){
  //$('.newfield').prop('contenteditable',true);
  $($('.cellinputtype')[i]).click(function(){
    var i = $('.cellinputtype').index(this)
    if (this.innerHTML == 'Aa'){
      this.innerHTML = 'MD';
      $($('.cellinputlang')[i]).val("markdown").attr("disabled", true);
    } else if (this.innerHTML == 'MD'){
      this.innerHTML = '{}';
      this.style.paddingTop = 0;
      this.style.fontFamily = "Consolas,monospace";
      $($('.cellinputlang')[i]).val("language").attr("disabled", false).css('color', '#909090');

    } else {
      this.style.paddingTop = 2;
      this.innerHTML = 'Aa';
      $($('.cellinputlang')[i]).val("text").css("color", "inherit").attr("disabled", true);
      //$('.cellinputcontent')[i].style.fontFamily = "inherit";
      this.style.fontFamily = "inherit";
    }
    $($('.cellinputlang')[i]).change();
  });

  $('textarea').each(function () { //from Obsidian on StackOverflow
      this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
  }).on('input', function () {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
  });
  setup_placeholder($('.cellinputname')[i], CELL_NAME);
  setup_placeholder($('.cellinputlang')[i], LANG);
  $($('.cellinputlang')[i]).change(function(){
    mode = this.value.toLowerCase()
      if (mode == this.last_correct_mode) {
        this.style.borderColor = "#409060";
        return;
      }
      this.style.borderColor = "#c06060";
      console.log('cellinputlang change');
      var editor = ace.edit("ace_editor" + i.toString());
      if (this.value == LANG || this.value == ""){
        this.style.borderColor = "#d8d8d8";
        return;
      }
      if (mode == "c" || mode == "c++" || mode == "cpp"){
        editor.getSession().setMode("ace/mode/c_cpp");
        return;
      }
      console.log("asking for mode change", editor);
      editor.getSession().setMode("ace/mode/" + mode);
  }).val("text").css("color", "inherit").css("border-color", "#409060").attr("disabled", true);
  //setup_placeholder(".cellinputcontent", CELL_CONTENT);
}
