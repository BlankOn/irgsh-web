function toggle_next(curr) {
    $(curr).next().slideToggle();
}
function collapse_changelog(target) {
    var lines = target.html().split("\n");
    var html = "<pre onclick='toggle_next(this);'>" + lines[0] + "</pre>\n";
    html += '<pre style="display:none">\n' + lines.slice(1).join("\n") + '</pre>';
    target.parent().html(html);
}
function rot13(inp) {
    // From http://djangosnippets.org/snippets/1475/
    return inp.replace(/[a-zA-Z]/g, function(c) {
        return String.fromCharCode((c<="Z"?90:122) >= (c=c.charCodeAt(0)+13)?c:c-26);
    });
}
function fix_email(targets) {
    targets.each(function() {
        var target = $(this);
        var content = target.attr('title');
        var res = rot13(content);
        target.html(res);
        target.attr('title', '');
    });
}

