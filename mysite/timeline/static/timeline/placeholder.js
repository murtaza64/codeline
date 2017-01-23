var $ = require('jquery')

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
module.exports = setup_placeholder