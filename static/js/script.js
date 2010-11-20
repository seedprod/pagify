// My Scripts
$.ajaxSetup ({
    // Disable caching of AJAX responses */
    cache: false
});
switch(location.pathname)
{
case "/dashboard":
    $(document).ready(function() {
        // Set hover state for Pages list
        $(".scroll-content-item").hover(
            function () {
                $(this).addClass("ui-state-hover hand");
              },
              function () {
                $(this).removeClass("ui-state-hover hand");
              }
        ).click(
            function () {
                window.location = $(".page-title a",this).attr('href');
              }
        );
    });
    $(window).load(function() {
        //Resize Pages to match max height
        var postMaxHeight = 0;
        $(".scroll-content-item").each(function (i) {
            var elHeight = $(this).height();
            if(parseInt(elHeight) > postMaxHeight){
                postMaxHeight = parseInt(elHeight);
            }
        });
        $(".scroll-content-item").each(function (i) {
           $(this).css({'height':postMaxHeight+'px','display':'block'});
        });  
    });
  
  break;
case "/upgrade":
    $(document).ready(function() {
        $(".btn-upgrade").button();
    });
  break;
default:
    $(document).ready(function() {
        //Globals
        wDeleteId = '';
        // Header
        $("#pagify-image").draggable();
		$("#pagify-header").resizable({handles: 's',alsoResize: "#pagify-image"});
		$( "#pagify-header" ).bind( "resizestop", function(event, ui) {
				$( "#widget-list" ).sortable( "refresh" );
		});
		//Scrolll Widgets
		$(window).scroll(function()
		{
    		if($(window).scrollTop() < 100){
    		    $('#sb-widgets-menu').animate({top:115+"px" },{queue: false, duration: 500});
    		}else{
    		    $('#sb-widgets-menu').animate({top:$(window).scrollTop()+50+"px" },{queue: false, duration: 500});
    		}
		});
		//Dialogs
		var left= 20;
		var top= 20;
		$( "#upload-dialog" ).dialog({
			autoOpen: false,
			show: "fade",
			hide: "fade",
			open: function() { 
						$(".ui-dialog").position({
						       my: 'right',
						       at: 'right',
						       of: "#pagify-header"
						    });
				}
		});

		$( "#pagify-header" ).click(function() {
			$( "#upload-dialog" ).dialog( "open" );
			return false;
		});
        // Prepare Widget List for accordian and sortable
        var stop = false;
		$( "#widget-list .wheader" ).click(function( event ) {
			if ( stop ) {
				event.stopImmediatePropagation();
				event.preventDefault();
				stop = false;
			}
		});
		$( "#widget-list" )
			.accordion({
				header: "> div > .wheader",
				autoHeight: false
			})
			.sortable({
				axis: "y",
				handle: ".wheader",
				placeholder: "ui-state-highlight",
				forcePlaceholderSize:true,
				stop: function() {
					stop = true;
				}
			});
		// override accordian keydown events
		$(".wheader").unbind('keydown');
		$('.widget-form').live("submit",function() {
          return false;
        });
		// Make widget list draggable
		$( ".draggable" ).draggable({
			connectToSortable: "#widget-list",
			helper: "clone",
			revert: "invalid"
		});

		$( "ul, li" ).disableSelection();
		// After dragged and dropped destroy and recreate accordian
		$( ".draggable" ).draggable({
		   stop: function(event, ui) { 
			var wType = $(this).attr('id');
			var wName = $(this).html();
			var wId = uuid();
			var wContents = '';
			if(wType){
			   //get widget content
			   $.get("/api/getwidget", {wid:wId, wtype: wType},function(data){
			       wContents = data
			       $('#widget-list #' + wType).replaceWith('<div id="'+wId+'" class="widget-list-item"><span class="wheader"><h3><a href="#" class="inline-edit">'+wName+'</a></h3><span class="btn-delete"><span class="ui-icon ui-icon-trash"></span></span></span><div>'+wContents+'</div><span class="hidden wtype">'+wType.replace(/wi-/g,'')+'</span></div>');
			       var stop = false;
      				$( "#widget-list .wheader" ).click(function( event ) {
      					if ( stop ) {
      						event.stopImmediatePropagation();
      						event.preventDefault();
      						stop = false;
      					}
      				});
   				    $( "#widget-list" ).accordion('destroy').accordion({
   						header: "> div > .wheader",
   						autoHeight: false
   					})
   					.sortable({
   						axis: "y",
   						handle: ".wheader",
   						stop: function() {
   							stop = true;
   						}
   					});
   					$(".wheader").unbind('keydown');
			   });//end ajax request
               	
			   } // end if
			}
		});

		// Ajax Accordian
		$("#widget-list" ).bind('accordionchange', function(event, ui) {
		  log('accordionchange');
		  if($(ui.newContent).html() == 'Loading...'){
		      $(ui.newContent).load("/api/getwidget?wid="+ encodeURIComponent($(ui.newContent).parent('div').attr('id')));
		  }
		});
		
		// Load default widget if there is one
		var firstWidget = $("#widget-list > div:eq(0) > div:eq(0)");
		if($(firstWidget)){
		    $(firstWidget).load("/api/getwidget?wid="+ encodeURIComponent($("#widget-list > div:eq(0)").attr('id')));
	    }
	    
	    // Sort update
	    $( "#widget-list" ).bind( "sortupdate", function(event, ui) {
	        log('sortupdate');
	        var pageOrder = '';
            $("#widget-list > div").each(function(index) {
                if (pageOrder != ''){
                    pageOrder = pageOrder + ',';
                }
                pageOrder = pageOrder + $(this).attr('id');
            });
            $.post("/api/savepageorder", { pageorder: pageOrder},function(data){
        	    if(data){
        	        log('Saved Page Order');
        	    };
        	});//end ajax request
        }); // end sort
        
        // Delete update
        $( "#dialog-delete-confirm" ).dialog({
                    autoOpen: false,
        			resizable: false,
        			draggable:false,
        			modal: true,
        			buttons: {
        				"Delete Widget": function() {
        					$( this ).dialog( "close" );
        					$('#'+wDeleteId).fadeOut(function() {
                            $.post("/api/deletewidget", { wid: wDeleteId},function(data){
                        	    if(data){
                        	        log('Widget Deleted');
                        	        wDeleteId = '';
                        	    };
                        	});//end ajax request
                        	});//end fadeout
        				},
        				Cancel: function() {
        					$( this ).dialog( "close" );
        					wDeleteId = '';
        				}
        			}
        		});
        $( ".btn-delete" ).live( "click", function(event, ui) {
            wDeleteId = $(this).parents('div').attr('id');
            $( "#dialog-delete-confirm" ).dialog( "open" );
        }); // end delete
        
        // Make Title editable
        $('.inline-edit').live("dblclick", function(event, ui) {
            var oldVal = $(this).text();
            $(this).replaceWith("<input type='text' class='inline-text' value=\"" + oldVal + "\"/>");
            $('.inline-text').focus();
            $('.inline-text').bind("blur", function(event, ui) {
                var oldVal = $(this).val();
                var id = $(this).parents('div').attr('id');log(id);
                $(this).replaceWith("<a href='#' class='inline-edit'>" + oldVal + "</a>");
                saveWidget(id);
            });
            $('.inline-text').bind('keydown', function(e) {
                    if(e.keyCode==13){
                           var oldVal = $(this).val();
                           var id = $(this).parents('div').attr('id');log(id);
                           $(this).replaceWith("<a href='#' class='inline-edit'>" + oldVal + "</a>");
                           saveWidget(id);
                    }
            });
            
        }); // end editable


    });
}

// Functions

//Save Widget
function saveWidget(id){
	var wId = id;
	var wType = $('#'+id+' .wtype').text();
	var wName = $('#'+id+' .inline-edit').text();
	var params = {};
    $.each($("#fm-"+id).serializeArray(), function(index,value) {
    params[value.name] = value.value;
    });
	var wContents = $.toJSON(params);
	var pageId = $("#page-id").html();  
	if(wId!=''){
	$.post("/api/savewidget", { wid: wId , wtype: wType , wname: wName, wcontents: wContents, pageid: pageId},function(data){
	    if(data){
	        log('Saved Widget');
	        $('#widget-list').trigger('sortupdate')
	    };
	});//end ajax request
    }
}

function getParameterByName( name )
{
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var results = regex.exec( window.location.href );
  if( results == null )
    return "";
  else
    return decodeURIComponent(results[1].replace(/\+/g, " "));
}
   
function S4() {
   return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
}

function uuid(p) {
   if (p === undefined){p=''};
   return (p+S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}  
   

    



