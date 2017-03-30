

// CELL_NAME = "cell name";
// CELL_CONTENT = "cell content";
// TAGS = "tag1 tag2 ...";
// POST_TITLE = "post title";
// LANG = "language";

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
    minLines: 8,
    maxLines: 5000
  });
  editor.getSession().setUseSoftTabs(true);
  editor.getSession().setUseWrapMode(true);
  editor.getSession().on("changeMode", function(){
    console.log('changed mode');
    var k = $('.ace').index(editor.container)
    $($(".cellinputlang")[k]).css("border-color", "#409060");
    $(".cellinputlang")[k].last_correct_mode = modeify($(".cellinputlang")[k].value.toLowerCase());
  });
}
function setup_inputs(i){
  setup_ace(i);
  $('.cellfield')[i].using_cell = true;
  //$('.newfield').prop('contenteditable',true);
  $($('.cellinputtype')[i]).click(function(){
    var i = $('.cellinputtype').index(this)
    type = this.innerHTML.replace(/^\s+|\s+$/g, '')
    if (type == 'Aa'){
      this.innerHTML = 'MD';
      this.style.fontSize = "13px";
      $($('.cellinputlang')[i]).val("markdown").attr("disabled", true);
    } else if (type == 'MD'){
      this.innerHTML = '{}';
      this.style.fontSize = "14px";
      this.style.fontFamily = "Consolas,monospace";
      $($('.cellinputlang')[i]).val("").attr("disabled", false);

    } else {
      this.innerHTML = 'Aa';
      $($('.cellinputlang')[i]).val("text").css("color", "inherit").attr("disabled", true);
      this.style.fontFamily = "inherit";
    }
    $($('.cellinputlang')[i]).change();
  });
  inputtype = $('.cellinputtype')[i]
  type = inputtype.innerHTML.replace(/^\s+|\s+$/g, '')
  if(type == 'MD'){
    console.log('MD')
    inputtype.style.fontSize = '13px';
    $($('.cellinputlang')[i]).val("markdown").attr("disabled", true);
  }
  if(type == '{}'){
    console.log('{}')
    inputtype.style.fontFamily = "Consolas,monospace";
    $($('.cellinputlang')[i]).attr("disabled", false);
  }
  if(type == 'Aa'){
    console.log('Aa')
    $($('.cellinputlang')[i]).val("text").css("color", "inherit").attr("disabled", true);
    inputtype.style.fontFamily = "inherit";
  }

  $($('.cellinputlang')[i]).change(function(){
    var k = $('.cellinputlang').index(this);
    mode = this.value.toLowerCase()
      if (modeify(mode) == this.last_correct_mode) {
        this.style.borderColor = "#409060";
        return;
      }
      this.style.borderColor = "#c06060";
      console.log('cellinputlang change');
      var editor = ace.edit("ace_editor" + k.toString());
      if (this.value == ""){
        this.style.borderColor = "#d8d8d8";
        return;
      }
      console.log("asking for mode change", editor);
      editor.getSession().setMode("ace/mode/" + modeify(mode));
  });

  $($('.moveup')[i]).click(function (){
    var k = $('.moveup').index(this);
    $($('#cellinputs').children()[k]).insertBefore($('#cellinputs').children()[k-1]);
    $($('.ace')[k-1]).attr("id", "temp");
    $($('.ace')[k]).attr("id", "ace_editor" + k.toString());
    $($('.ace')[k-1]).attr("id", "ace_editor" + (k-1).toString());

  })
  $($('.movedown')[i]).click(function (){
    var k = $('.movedown').index(this);
    $($('#cellinputs').children()[k]).insertAfter($('#cellinputs').children()[k+1]);
    $($('.ace')[k+1]).attr("id", "temp");
    $($('.ace')[k]).attr("id", "ace_editor" + k.toString());
    $($('.ace')[k+1]).attr("id", "ace_editor" + (k+1).toString());
  })


  $($('.removecell')[i]).on("click.new", function remove_cell_click(){
    this.style.borderColor = "#cc5555";
    this.style.backgroundColor = "#dd6666";
    $(this).on("click.new", function delete_cell(){
      this.style.backgroundColor="#ee7777";
      n = $('.cellfield').length
      $($('.cellfield')[i]).css('display', 'none');
      $('.cellfield')[i].using_cell = false;
    }).mouseleave(function(){
      this.style.backgroundColor = "";
      this.style.borderColor = "#aa3333";
      $(this).off("click.new");
      $(this).on("click.new", remove_cell_click);
    })
  });

  // setup_placeholder($('.cellinputname')[i], CELL_NAME);
  // setup_placeholder($('.cellinputlang')[i], LANG);
  // $('.cellinputtype')[i].style.fontFamily = "Consolas,monospace";
  $(".cellinputlang")[i].last_correct_mode = "text";
  $($('.cellinputlang')[i]).change();
  //setup_placeholder(".cellinputcontent", CELL_CONTENT);
}

$(function(){
  console.log('ready');
  CELLINPUT_HTML = $('#empty_cell_template')[0].innerHTML
  $('#empty_cell_template').remove()
  //$('.newfield').css('color', '#909090');
  var cellfield_n = $('.cellfield').length;
  for(var k = 0; k < cellfield_n; k++){
    setup_inputs(k);
  }
  // setup_placeholder("#titlefield", POST_TITLE);
  // setup_placeholder("#tagfield", TAGS);

  $('#addcell').click(function (){
    $("#cellinputs").append(CELLINPUT_HTML);
    i = $('.cellfield').length-1;
    setup_inputs(i);
  });

  

  $('#submit').click(function(){
    statusclear();
    statusupdate("submitting");
    post = {};
    post.title = $('#titlefield')[0].value;
    //if (post.title == POST_TITLE) post.title = "";
    post.tagstring = $('#tagfield')[0].value;
    //if (post.tagstring == "") post.tagstring = "untagged";
    post.anonymous = $("#anonymousbox").is(':checked');
    post.cells = [];
    var cellfields = $('.cellfield');
    var cellinputnames = $('.cellinputname');
    var cellinputtypes = $('.cellinputtype');
    var cellinputlangs = $('.cellinputlang');

    for (var i = 0; i < cellfields.length; i++){
      if (cellfields[i].using_cell){
        cell = {}
        cell.title = cellinputnames[i].value;
        // if (cell.title == CELL_NAME) cell.title = "";
        var editor = ace.edit("ace_editor" + i.toString());
        cell.content = editor.getValue();
        // if (cell.content == CELL_CONTENT) cell.content = "";
        cell.lang = cellinputlangs[i].value;
        // if (cell.lang == LANG) cell.lang = "";
        type_btn = cellinputtypes[i]
        type = type_btn.innerHTML.replace(/^\s+|\s+$/g, '')
        if (type == 'Aa'){
          cell.type = 0;
        } else if (type == 'MD'){
          cell.type = 1;
        } else {
          cell.type = 2;
        }
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
          if (data.message != ""){
            statuserror(data.message);
          }
          else {
            statuserror("unknown server side error")
          }
        }
        else{
          statusupdate(data.message);
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
