(function (){
    var win = {{ window.render|safe }};

    function submitForm(btn, e, baseParams) { win.submitForm(btn, e, baseParams); }
    function cancelForm(){ win.close(); }

    {{ window.render_globals }}

    {% if window.force_show %}
    win.show();
    {% endif %}

    return win;
})()