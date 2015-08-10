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
                   var field = elem.attr("name");
                   if(field in data) {
                     data[field].push(elem.val());
                   } else {
                     data[field] = [elem.val()];
                   }

            }
            break;
 
        case "SELECT":
            data[elem.attr("name")] = elem.select().val()
            console.log();
            break;

        default:
            console.log(elem.attr('type'));


    }
    console.log("data is " + data);
 /*   $.post("/create",
           data=data,
            function(err, data) {
               console.log(data);
           

           });*/
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
   $("#add-agents-dlg").modal('hide');
});


$('#add-track-dlg-update').click(function() {
  var track_for_listing = $('#track-for').val();
  if($('#tracks-list option:selected').length > 0) {
    var val = $("#tracks-list option:selected").val();
    var text = $("#tracks-list option:selected").text();
    console.log("Value is " + val + " text " + text);
    $('#'+track_for_listing + "-tracks").append('<li><input type="hidden" name="http://schema.org/track" value="' + val + '"></input>' + text + '</li>');
  }
  $('#add-track-dlg').modal('hide');
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

function validate(id, error_msg) {
  var key = "#"+id;
  if($(key).val()) {
     $(key).parent().attr("class", "form-group");
     return true;
  } else {
    alert(error_msg);
    $(key).parent().addClass("has-error");
    return false; 
  }
}

$('#save-new-playlist').click(function(event) {
  var data= { "type": "MusicPlaylist" }
  
  if(validate("playlist-name", "Music Playlist must have a name")) {
    data["http://schema.org/name"] = $("#playlist-name").val();
  } else {
    return;
  }
  var tracks = [];
  $("#playlist-tracks input").each(function(index) {
    tracks.push($(this).val());
  });
  data["http://schema.org/track"] = tracks;
  if($('#existing-canvas option:selected').length > 0) {
     data["http://schema.org/isPartOf"] =  $('#existing-canvas option:selected').val();
     
     $.post("create",
         data=data,
         function(data) {
          window.location = "/";
     });
  } else { 
    var canvas_data = {"type": "EducationalEvent"}
    if(validate("canvas_name", "Canvas Course Name must have a value")) { 
     canvas_data["http://schema.org/name"] = $("#canvas_name").val();
    } else {
       return;  
     }
  
     if(validate("canvas_id", "Canvas ID must have a value")) {
       canvas_data["http://schema.org/sameAs"] = $('#canvas_id').val();
     } else {
        return;
     }
     if($("#startDate").val()) {
       canvas_data["http://schema.org/startDate"] = $("#startDate").val();
     }
     if($("#endDate").val()) {
       canvas_data["http://schema.org/endDate"] = $("#endDate").val();
     }
      $.post("create",
       data=canvas_data,
       function(return_data) {   
        if(return_data["url"]) { 
          data['isPartOf'] = data['url'];
          $.post("create",
           data=data,
           function(data) {
             window.location = "/";
           });

          } else {
         alert("Error " + data['error']);
        }
      });
    }
});

$('#add-agents-dlg').on('show.bs.modal', function(event) {
  var button = $(event.relatedTarget);
  var role_to_resource = button.data('role');
  var modal = $(this);
  modal.find('.modal-title').text('Add ' + role_to_resource + ' to Music Recording');
  modal.find('#role-to-recording').val(role_to_resource);
})

$('#add-track-dlg').on('show.bs.modal', function(event) {
  var button = $(event.relatedTarget);
  var target = button.data('track');
  var modal = $(this);
  modal.find('.modal-title').text('Add track ' + target);
  modal.find('#track-for').val(target);
})
