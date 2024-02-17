(function (){
    var win = {{ window.render|safe }};

    function closeWindow(){ win.close(); }
    
    {{ window.render_globals }}

    {% if window.force_show %}
    win.show();
    {% endif %}

    return win;
})()



