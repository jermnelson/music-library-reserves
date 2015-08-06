$("#new-music-record").submit(function(event) {
  event.preventDefault();
  var self = $("#new-music-recording");
  var inputs = self.find("div").find(".form-control");
  var data = {"type": "MusicRecording"};
  for(i=0; i < inputs.length; i++) {
    var elem = $(inputs[i]);
    switch(elem.prop("tagName")) {
        case "INPUT":
            switch(elem.attr('type')) {
               case "file":
                 data['file'] = elem.files[0];
                 break;

               default:
                   data[elem.attr("name")] = elem.val()

            }
            break;
 
        case "SELECT":
            data[elem.attr("name")] = elem.select().val()
            console.log();
            break;

        default:
            console.log(elem.attr('type'));


    }
    console.log(data);
    $.post("/create",
           data=data,
           function(err, data) {


           });
  }
});

$("#creatorType").change(function(event) {
  if($(this).val() === "Person") {
    $('#person-info').prop( "disabled", false );
    $('#org-info').prop( "disabled", true );

  } else {
    $('#person-info').prop( "disabled", true );
    $('#org-info').prop( "disabled", false );

  }

});

$("#add-agents-dlg-update").click(function() {
   var data = { };
   var role_listing = $("#role-to-recording").val();
   if($('#persons-list option:selected').length > 0) { 
     $('#'+role_listing).append('<li><input type="hidden" name="http://schema.org/creator" value="' + $('#persons-list option:selected').val() + '"></input>' + $('#persons-list option:selected').text() + '</li>');
   }
   if($('#orgs-list option:selected').length > 0) {
     $('#'+role_listing).append('<li id="' + $('#orgs-list option:selected').val() + '">' + $('#orgs-list option:selected').text() + '</li>');
   }
});


$("#save-new-creator").click(function(event) {
 var data = {
    "type": $('#creatorType').val(),
  }
 fields = ['familyName', 'givenName', 'url'];
 for(i in fields) {
   var value = $('#'+fields[i]).val();
   if(value.length > 0) {
     data["http://schema.org/"+fields[i]] = value;
   }
 }
 if($('#org-name').val().length > 0) {
    data['http://schema.org/name'] = $('#org-name').val();   
 }

 if($('#person-name').val().length > 0) {
    data['http://schema.org/name'] = $('#person-name').val();   
 }

 if($('#loc').val().length > 0) {
    data['http://schema.org/sameAs'] = $('#loc').val();
 }

 if($('#viaf').val().length > 0) {
    if('http://schema.org/sameAs' in data) {
      data['http://schema.org/sameAs'].push($('#viaf').val());
    } else {
       data['http://schema.org/sameAs'] = $('#viaf').val();
    }
 }
 
/*for(i in data) {
   console.log(i, data[i]);
 }*/

 $.post("create",
   data=data,
   function(err, data) {
     console.log("Created creator " + data[0]);
     window.location = "/";

 }); 

});

$('#add-agents-dlg').on('show.bs.modal', function(event) {
  var button = $(event.relatedTarget);
  var role_to_resource = button.data('role');
  var modal = $(this);
  modal.find('.modal-title').text('Add ' + role_to_resource + ' to Music Recording');
  modal.find('#role-to-recording').val(role_to_resource);
})

$('#add-track-dlg').on('show.bs.model', function(event) {
  var button = $(event.relatedTarget);
  var target = button.data('track');
  var modal = $(this);
  modal.find('.modal-title').text('Add track ' + target);
  modal.find('#track-for').val(target);
})
