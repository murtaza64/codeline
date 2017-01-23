CELLINPUT_HTML = '\
<div class="container-fluid cellfield" >\
  <div class="cellinputmeta">\
    <table><tr>\
      <td><div class="newbutton cellinputtype">{}</div></td>\
      <td style="width: 100%; padding-left:5px">\
        <input type=text class="newfield cellinputname">\
      </td>\
      <td>\
        <input type=text class="newfield cellinputlang">\
      </td>\
      <td>\
        <div class="newbutton removecell">-</div>\
      </td>\
    </tr></table>\
  </div>\
  <div class="cic_container">\
    <div class="ace" id="ace_editor0"></div>\
  </div>';

TEXTAREA_HTML = '<textarea rows=2 class="newfield cellinputcontent"></textarea>';

CELL_NAME = "cell name";
CELL_CONTENT = "cell content";
TAGS = "tag1 tag2 ...";
POST_TITLE = "post title";
LANG = "language";

function modeify(mode_str){
  if (mode_str == "c" || mode == "c++" || mode == "cpp"){
    return "c_cpp";
  }
  return mode_str;
}
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
var csrftoken = getCookie('csrftoken');

function statusclear(){
  $('#status').html("");
}
function statuserror(error){
  $('#status').append("<p style='color:#c06060;'>"+error+"</p>");
}
function statusupdate(update){
  $('#status').append("<p>"+update+"</p>");
}


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


function setup_ace(i){
  var editor_id = "ace_editor" + i.toString();
  $('.ace')[i].id = editor_id;
  var editor = ace.edit(editor_id);
  editor.setTheme("ace/theme/chrome");
  editor.setOptions({
    minLines: 5,
    maxLines: 50
  });
  editor.getSession().setUseSoftTabs(true);
  editor.getSession().setUseWrapMode(true);
  editor.getSession().on("changeMode", function(){
    console.log('changed mode');
    $($(".cellinputlang")[i]).css("border-color", "#409060");
    $(".cellinputlang")[i].last_correct_mode = modeify($(".cellinputlang")[i].value.toLowerCase());
  });
}
function setup_inputs(i){
  setup_ace(i);
  $('.cellfield')[i].using_cell = true;
  //$('.newfield').prop('contenteditable',true);
  $($('.cellinputtype')[i]).click(function(){
    var i = $('.cellinputtype').index(this)
    if (this.innerHTML == 'Aa'){
      this.innerHTML = 'MD';
      this.style.fontSize = '11px';
      this.style.paddingTop = 8;
      $($('.cellinputlang')[i]).val("markdown").attr("disabled", true);
    } else if (this.innerHTML == 'MD'){
      this.innerHTML = '{}';
      this.style.fontSize = 'inherit';
      this.style.paddingTop = 7;
      this.style.fontFamily = "Consolas,monospace";
      $($('.cellinputlang')[i]).val("language").attr("disabled", false).css('color', '#909090');

    } else {
      this.style.paddingTop = 6;
      this.innerHTML = 'Aa';
      $($('.cellinputlang')[i]).val("text").css("color", "inherit").attr("disabled", true);
      //$('.cellinputcontent')[i].style.fontFamily = "inherit";
      this.style.fontFamily = "inherit";
    }
    $($('.cellinputlang')[i]).change();
  });

  $($('.cellinputlang')[i]).change(function(){
    mode = this.value.toLowerCase()
      if (modeify(mode) == this.last_correct_mode) {
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
      console.log("asking for mode change", editor);
      editor.getSession().setMode("ace/mode/" + modeify(mode));
  });

  $($('.removecell')[i]).on("click.new", function remove_cell_click(){
    this.style.background = "linear-gradient(#e0b0b0, #c8a0a0)";
    this.style.borderColor = "#a85050";
    $(this).on("click.new", function delete_cell(){
      n = $('.cellfield').length
      /*for (var j = i+1; j < n; j++){ //cascade ids for ace editors
        $('.ace')[j].id="ace_editor"+(j-1).toString();
      }*/
      $($('.cellfield')[i]).css('display', 'none');
      $('.cellfield')[i].using_cell = false;
    }).mouseleave(function(){
      this.style.background = "linear-gradient(#e8e8e8, #d6d6d6)";
      this.style.borderColor = "#b8b8b8";
      $(this).off("click.new");
      $(this).on("click.new", remove_cell_click);
    })
  });

  setup_placeholder($('.cellinputname')[i], CELL_NAME);
  setup_placeholder($('.cellinputlang')[i], LANG);
  $('.cellinputtype')[i].style.fontFamily = "Consolas,monospace";
  $(".cellinputlang")[i].last_correct_mode = "text";

  //setup_placeholder(".cellinputcontent", CELL_CONTENT);
}

$(function(){
  console.log('ready');
  $('.newfield').css('color', '#909090');
  setup_inputs(0);
  setup_placeholder("#titlefield", POST_TITLE);
  setup_placeholder("#tagfield", TAGS);

  $('#addcell').click(function (){
    $("#cellinputs").append(CELLINPUT_HTML);
    var i = $('.cellfield').length-1;
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
    post.anonymous = $("#anonymousbox").is('.checked');
    post.cells = [];
    var cellfields = $('.cellfield');
    var cellinputnames = $('.cellinputname');
    var cellinputtypes = $('.cellinputtype');
    var cellinputlangs = $('.cellinputlang');

    for (var i = 0; i < cellfields.length; i++){
      if (cellfields[i].using_cell){
        cell = {}
        cell.title = cellinputnames[i].value;
        if (cell.title == CELL_NAME) cell.title = "";
        var editor = ace.edit("ace_editor" + i.toString());
        cell.content = editor.getValue();
        if (cell.content == CELL_CONTENT) cell.content = "";
        cell.lang = cellinputlangs[i].value;
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
    }
    console.log(post)
    $.ajax({
      method: "POST",
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
