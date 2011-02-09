$(document).ready(function() {
    $( "#pagify-widget-list-1" ).accordion();
});

function yqlQuery(query,cbFunc,format,env,maxage) {
    var yqlURL = 'http://query.yahooapis.com/v1/public/yql?q=' + encodeURIComponent('select * from html where url="' + site + '"') + '&format=xml&diagnostics=false&_maxage=3600';
    query = typeof(query) != 'undefined' ? encodeURIComponent(query) : '';
    format = typeof(format) != 'undefined' ? format : 'json';
    env = typeof(format) != 'undefined' ? env : 'store://datatables.org/alltableswithkeys';
    maxage = typeof(maxage) != 'undefined' ? maxage : '';
    yql = yqlURL + '?q=' + query + '&format=' + format + '&diagnostics=false&_maxage=' + maxage + '&env=' + env;
    $.ajax({url: yql, 
            dataType: 'jsonp',
            jsonp: 'callback', 
            jsonpCallback: cbFunc
            });
}        
        
function cbFunc(data) {
    log(data);
}

