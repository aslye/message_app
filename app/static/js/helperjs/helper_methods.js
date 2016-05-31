function mmsDropdown(mmsGroupObj){
  var html = '<option value="all">No MMS Group Selected</option>';
  for(key in mmsGroupObj){
    if(key != '' || key == undefined){
      html += '<option value="' + key + '">' + key + '</option>';
    }
  }
  $('#mms_categories').html(html);
  return;
}


function validate(evt) {
  var theEvent = evt || window.event;
  var key = theEvent.keyCode || theEvent.which;
  key = String.fromCharCode( key );
  var regex = /[0-9]|\./;
  if( !regex.test(key) ) {
    theEvent.returnValue = false;
    if(theEvent.preventDefault) theEvent.preventDefault();
  }
}

function createInputField(){
  var item = $('#phonenumber1').val().length;
  if(item != 0){
    $('#phone_inputs').append('<tr><<td><input class=\'name\' type="text" ></td>td><input class=\'phone-number\' maxlength="10" minlength="10" type="text" id="phonenumber1" name="phonenumber" onkeypress=\'validate(event);\' placeholder="Enter 10 digit number" class="phone_input"></td><td><select width="100%" style="width:100%" data-init-plugin="" placeholder="" class="provider_catergories" id="provider_catergories"><option value="unknown">Unknown</option><option value="att">A &amp; TT</option><option value="tmobile">Tmobile</option><option value="metro pcs">Metro Pcs</option><option value="verizon">Verizon</option></select></td></tr>');
  }
}

function createInputField2(){
  $('#group_data').append('<tr><td><input class=\'name\' type="text" ></td><td><input class=\'edit-phone-number\' maxlength="10" minlength="10" type="text" id="edit_phonenumber" name="phonenumber" onkeypress=\'validate(event);\' placeholder="Enter 10 digit number" class="phone_input"></td><td><select width="100%" style="width:100%" data-init-plugin="" placeholder="" class="edit_provider_catergories" id="edit_provider_catergories"><option value="unknown">Unknown</option><option value="att">A &amp; TT</option><option value="tmobile">Tmobile</option><option value="metro pcs">Metro Pcs</option><option value="verizon">Verizon</option></select></td></tr>');
}

function createAssociativeArray(arr1, arr2) {
  var arr = {};
  for(var i = 0, ii = arr1.length; i<ii; i++) {
    arr[arr1[i]] = arr2[i];
  }
  return arr;
}