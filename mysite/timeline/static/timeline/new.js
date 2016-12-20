cellinput_html = '\
<div class="container-fluid cellfield">\
  <div class="cellinputmeta">\
    <table><tr>\
    <td><button class="cellinputtype">0</button></td>\
    <td style="width: 100%"><div class="newfield cellinputname">cell name</div></td>\
  </tr></table>\
  </div>\
  <div class="newfield cellinputcontent">cell content</div>\
</div>\
'
function add_cell(){
  var cellinputs = $("#cellinputs")[0];
  cellinputs.innerHTML += cellinput_html;
  //cellfields = $(".cellfield");
  //$(cellfields[cellfields.length-1]).css("margin-bottom", "0");
  //$(cellfields[cellfields.length-2]).css("margin-bottom", "10px");
  setup_inputs()
}
$(function(){
  console.log('ready');
  $('.newfield').css('color', '#909090');
  setup_inputs()
  $('#submit').click(function(){
    post = {}
    post.title = $('#titlefield')[0].innerHTML;
    post.tagstring = $('#tagfield')[0].innerHTML;
    post.author = 'murtaza64' //TODO fix, uh, this whole thing
    post.body = [];
    var cellfields = $('.cellfield');
    var cellinputnames = $('.cellinputname');
    var cellinputcontents = $('.cellinputcontent');
    var cellinputtypes = $('.cellinputtype');
    for (var i = 0; i < cellfields.length; i++){
      cell = {}
      cellfield = cellfields[i]
      cell.title = cellinputnames[i].innerHTML
      cell.body = cellinputcontents[i].innerHTML
      cell.type = +cellinputtypes[i].innerHTML
      cell.lang = null
      post.body.push(cell)
    }
    console.log(post)
    $.ajax({
      //TODO
    })
  });
});

function setup_inputs(){
  $('.newfield').prop('contenteditable',true);
  $('.cellinputtype').click(function(){
    if (this.innerHTML == '0'){
      this.innerHTML = 1;
    } else if (this.innerHTML == '1'){
      this.innerHTML = 2;
    } else {
      this.innerHTML = 0;
    }
  });
  function focus_inputs(plchldr){
    f = function(){
      if (this.innerHTML == plchldr){
        this.innerHTML = "";
      }
      $(this).css('color', 'inherit');
    }
    return f;
  }
  function unfocus_inputs(plchldr){
    f = function(){
      if (this.innerHTML == ''){
        $(this).css('color', '#909090');
        this.innerHTML = plchldr;
      }
    }
    return f;
  }
  $('#titlefield').focus(focus_inputs("post title"));
  $('#tagfield').focus(focus_inputs("#tag1, #tag2 ..."));
  $('.cellinputname').focus(focus_inputs("cell name"));
  $('.cellinputcontent').focus(focus_inputs("cell content"));

  $('#titlefield').focusout(unfocus_inputs("post title"));
  $('#tagfield').focusout(unfocus_inputs("#tag1, #tag2 ..."));
  $('.cellinputname').focusout(unfocus_inputs("cell name"));
  $('.cellinputcontent').focusout(unfocus_inputs("cell content"));
}
