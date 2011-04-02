// My Scripts
$.ajaxSetup ({
    // Disable caching of AJAX responses */
    cache: false
});
switch(location.pathname)
{
case "/":
    break;
case "/dashboard":
    $(document).ready(function() {
        // Set hover state for Pages list
        $(".fbpage-item").hover(
            function () {
                $(this).addClass("boxer-hover");
              },
              function () {
                $(this).removeClass("boxer-hover");
              }
        ).click(
            function () {
                window.location = $(".fbpage-title a",this).attr('href');
              }
        );
        $(".upgrade-ribbon").click(
            function () {
                $(".fbpage-item").unbind('click');
                window.location = $("a",this).attr('href');
              }
        );
    });
    $(window).load(function() {
        //Resize Pages to match max height
        var postMaxHeight = 0;
        $(".fbpage-item").each(function (i) {
            var elHeight = $(this).height();
            if(parseInt(elHeight) > postMaxHeight){
                postMaxHeight = parseInt(elHeight);
            }
        });
        $(".fbpage-item").each(function (i) {
           $(this).css({'height':postMaxHeight+'px','display':'block'});
        });  
    });
  
  break;
case "/upgrade":

  break;
default:
    $(document).ready(function() {

        // Scroll Controller
        var topwin = $('#sb-widgets-menu').offset().top - parseFloat($('#sb-widgets-menu').css('marginTop').replace(/auto/, 0));
        $(window).scroll(function (event) {
          if(parseFloat($('#sb-widgets-menu').css('left')) == 840){
              var y = $(this).scrollTop();
              if (y >= topwin) {
                $('#sb-widgets-menu').addClass('fixed');
                $('#sb-widgets-menu').css('top',0);
              } else {
                $('#sb-widgets-menu').removeClass('fixed');
                $('#sb-widgets-menu').css('top',120);
              }
          }else{
             $('#sb-widgets-menu').addClass('fixed'); 
          }
        });
        //Globals
        var wDeleteId = '';
        // Header
        //$("#pagify-image").draggable();
		//$("#pagify-header").resizable({handles: 's',alsoResize: "#pagify-image"});
		//$( "#pagify-header" ).bind( "resizestop", function(event, ui) {
		//		$( "#widget-list" ).sortable( "refresh" );
		//});
		//Scrolll Widgets
		/*$(window).scroll(function()
		{
    		if($(window).scrollTop() < 100){
    		    $('#sb-widgets-menu').animate({top:115+"px" },{queue: false, duration: 500});
    		}else{
    		    $('#sb-widgets-menu').animate({top:$(window).scrollTop()+50+"px" },{queue: false, duration: 500});
    		}
		});*/
		//Dialogs
		$( "#upload-dialog" ).dialog({
			autoOpen: false,
			show: "fade",
			hide: "fade",
			modal: true,
			width: 450,
			open: function() { 
                $.get("/api/scripturl", function(data){scriptUrl=data;});
				}
		});

		$( "#pagify-image" ).bind('click',function() {
			$( "#upload-dialog" ).dialog( "open" );
			return false;
		});
        // Prepare Widget List for accordian and sortable
        var stop = false;
		$( "#widget-list .wheader" ).bind('click',function( event ) {
			if ( stop ) {
				event.stopImmediatePropagation();
				event.preventDefault();
				stop = false;
			}
		});
		$( "#widget-list" )
			.accordion({
				header: "> div > .wheader",
				autoHeight: false,
				collapsible: true
			})
			.sortable({
				axis: "y",
				handle: ".wheader",
				placeholder: "ui-state-highlight",
				forcePlaceholderSize:true,
				stop: function() {
					stop = true;
				}
			}).fadeIn();
		// override accordian keydown events
		$(".wheader").unbind('keydown');
		$('.widget-form').live("submit",function() {
          return false;
        });
		// Make Controller list draggable
		$( ".draggable" ).draggable({
			connectToSortable: "#widget-list",
			helper: "clone",
			revert: "invalid"
		});

		$( "ul, li" ).disableSelection();
		// After dragged and dropped destroy and recreate accordian
		$( ".draggable" ).bind( "dragstop click",function(event, ui) { 
			var wType = $(this).attr('id');
			var wName = $(this).html();
			var wId = uuid();
			var wContents = '';
			if(wType){
			   //get widget content
			   $.get("/api/getwidget", {wid:wId, wtype: wType},function(data){
			       wContents = data
			       wNew = '<div id="'+wId+'" class="widget-list-item"><span class="wheader"><h3><a href="#" class="inline-edit">'+wName+'</a></h3><span class="btn-delete"><span class="ui-icon ui-icon-trash"></span></span></span><div>'+wContents+'</div><span class="hidden wtype">'+wType.replace(/wi-/g,'')+'</span></div>';
			       if(event.type == 'click') {
			           $('#widget-list').prepend(wNew);
			           options = { to: "#"+wId, className: "ui-effects-transfer" };
			           $( "#"+wType ).effect('transfer', options, 500);
			       } else {
			           $('#widget-list #' + wType).replaceWith(wNew);
		           }
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
   						autoHeight: false,
   						collapsible: true
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
   					$( "#widget-list" ).sortable( "refresh" );
   					$(".wheader").unbind('keydown');
   					log('calling save');log(wId);
   					saveWidget(wId);
   					//$("#widget-list").accordion( "activate" , "#" + wId + " > .wheader" );
			   });//end ajax request
               	
			   } // end if
		});

		// Ajax Accordian
		$("#widget-list" ).bind('accordionchange', function(event, ui) {
		  log('accordionchange');
		  if($(ui.newContent).html() == 'Loading...'){
		      wid = $(ui.newContent).parent('div').attr('id');
		      $(ui.newContent).load("/api/getwidget?wid="+ encodeURIComponent(wid));
		  }
		});
		
		
		// Load default widget if there is one
		var firstWidget = $("#widget-list > div:eq(0) > div:eq(0)");
		if($(firstWidget)){
		    $(firstWidget).load("/api/getwidget?wid="+ encodeURIComponent($("#widget-list > div:eq(0)").attr('id')));
	    }
	    
	    // Save widget after drop
	    /*$( "#widget-list" ).bind( "sortreceive", function(event, ui) {
	      log(this);
          log('sortreceive');
        });*/
	    
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
            if (pageOrder != ''){
                $.post("/api/savepageorder", { pageorder: pageOrder},function(data){
            	    if(data){
            	        log('Saved Page Order');
            	    };
            	});//end ajax request
    	    }
        }); // end sort
        
        // Delete update
        $( "#dialog-delete-confirm" ).dialog({
                    autoOpen: false,
        			resizable: false,
        			draggable:false,
        			show: "fade",
        			hide: "fade",
        			modal: true,
        			buttons: {
        				"Delete Widget": function() {
        					$( this ).dialog( "close" );
        					$('#'+wDeleteId).fadeOut(function() {
                            $.post("/api/deletewidget", { wid: wDeleteId},function(data){
                        	    if(data){
                        	        $('#'+wDeleteId).remove();
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
        $('.inline-edit').live('mouseover mouseout', function(event) {
          if (event.type == 'mouseover') {
            $(this).addClass("ui-state-highlight");
          } else {
             $(this).removeClass("ui-state-highlight");
          }
        });

        $('.inline-edit').live("click", function(event, ui) {
            var oldVal = $(this).text();
            $(this).replaceWith("<input type='text' class='inline-text ui-state-highlight' value=\"" + oldVal + "\"/>");
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
        
        // Empty widget list message.
        /*$( "#widget-list" ).bind( "sortcreate sortupdate", function(event, ui) {
            var size = $("#widget-list > .widget-list-item").size();
            if(size > 0){
                $( "#widget-list" ).css("background-image","none");
            } else {
                $( "#widget-list" ).css("background","#fef7d5 url(/static/images/widget-area.png) no-repeat 165px 85px");
            }
        });*/
        
        //Controller Tabs
        $( "#sb-widgets-menu" ).draggable({handle:"#sb-widgets-header", opacity:0.7});
        $( "#controller-tabs" ).tabs();
        $( "#controller-tabs" ).fadeIn();
    });
}
// Validate defaults
$.validator.setDefaults({
	highlight: function(input) {
		$(input).addClass("ui-state-error");
	},
	unhighlight: function(input) {
		$(input).removeClass("ui-state-error");
	}
});
// Functions


//Save Widget
function saveWidget(id){
	var wId = id;
	var wType = $('#'+wId+' .wtype').text();
	var wName = $('#'+wId+' .inline-edit').text();
	var params = {};
    $.each($("#fm-"+wId).serializeArray(), function(index,value) {
    params[value.name] = value.value;
    });
	var wContents = $.toJSON(params);
	var pageId = $("#page-id").html();  
	if(wId!='' && $("#fm-"+wId).validate().form()){
	$.post("/api/savewidget", { wid: wId , wtype: wType , wname: wName, wcontents: wContents, pageid: pageId},function(data){
	    if(data){
	        log('Saved Widget');
	        location.href = location.href = "#reload"
	        $('#widget-list').trigger('sortupdate')
	        $('#saving').show().delay(1500).fadeOut('slow');
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
   

    



