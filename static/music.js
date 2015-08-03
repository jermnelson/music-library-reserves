$("#new-music-recording").submit(function(event) {
  event.preventDefault();
  var self = $("#new-music-recording");
  var inputs = self.find("div").find(".form-control");
  data = {};
  console.log("In new music recording length inputs="+inputs.length);
  for(i=0; i < inputs.length; i++) {
    var elem = $(inputs[i]);
    switch(elem.prop("tagName")) {
        case "INPUT":
            switch(elem.attr('type')) {
               case "file":
                 console.log("Elem is a file");
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
  console.log("In creatorType " + $(this).val());
  if($(this).val() === "Person") {
    $('#person-info').prop( "disabled", false );
    $('#org-info').prop( "disabled", true );

  } else {
    $('#person-info').prop( "disabled", true );
    $('#org-info').prop( "disabled", false );

  }

});

$("#add-creator-dlg-update").click(function() {
   var data = { };
   $('#creators').append('<li id="' + $('#persons-list').val() + '">' + $('#persons-list').text() + '</li>');
   $('#creators').append('<li id="' + $('#orgs-list').val() + '">' + $('#orgs-list').text() + '</li>');
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
     $("#add-creator-dlg").model('close');

 }); 

});
