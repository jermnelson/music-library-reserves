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
