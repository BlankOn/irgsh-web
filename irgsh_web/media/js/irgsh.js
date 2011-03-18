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

/*= submit page =*/


var SourceOptionsHandler = function(form) {
    this.form = form;
}
SourceOptionsHandler.prototype = {
    init: function() {
        var self = this;

        // submit handler
        this.form.submit(function() {
            return self.submit();
        });

        // initial value
        this.so = this.form.find('#id_source_opts');
        this.soc = this.so.parent();
        this.soc.hide();
        this.initial = this.so.attr('value');

        // add bzr options
        this.options = {}
        this.options['bzr'] = this._add_options_bzr();

        this.so.hide();

        // type monitor
        this.st = this.form.find('#id_source_type');
        this.st.change(function() {
            self.update();
        });
        this.update();
    },

    update: function() {
        var value = this.st.find('option:selected').attr('value');
        this.form.find('.source_opts').slideUp();
        var opts = this.options[value];
        if (opts != undefined) {
            opts.show();
            this.soc.slideDown();
        }
        else {
            this.soc.slideUp();
        }
    },

    submit: function() {
        var value = this.st.find('option:selected').attr('value');
        var sovalue = '';
        if (value == 'bzr') {
            sovalue = this._get_value_bzr();
        }
        this.so.attr('value', sovalue);
        this.form.find('.source_opts').remove();
        this.so.show();
        return true;
    },

    _get_value_bzr: function() {
        var bzr = this.options['bzr'];
        var selected = bzr.find('input[type=radio]:checked');
        var value = selected.attr('value');
        var val = selected.parent().find('input[type=text]').attr('value');

        var sovalue = '';
        if (value == 'tag') {
            sovalue = 'tag=' + val;
        }
        else if (value == 'rev') {
            sovalue = 'rev=' + val;
        }
        return sovalue;
    },

    _add_options_bzr: function() {
        var bzr = $('<div id="id_source_opts_bzr" class="source_opts"/>');
        var ul = $('<ul/>');
        bzr.append(ul);

        var li_tag = $('<li><input type="radio" name="id_source_opts_bzr" id="id_source_opts_bzr_tag" value="tag"/> ' +
                       '<label for="id_source_opts_bzr_tag">tag</label> ' +
                       '<input type="text" name="id_source_opts_bzr_tag_value"/></li>');
        li_tag.find('input[type=text]').keypress(function(e) {
            if (e.keyCode != 9) { // tab
                li_tag.find('input[type=radio]').attr('checked', true);
            }
        });
        li_tag.find('input[type=radio]').change(function() {
            if ($(this).attr('checked')) {
                li_tag.find('input[type=text]').focus();
            }
        });

        var li_rev = $('<li><input type="radio" name="id_source_opts_bzr" id="id_source_opts_bzr_rev" value="rev"/> ' +
                       '<label for="id_source_opts_bzr_rev">revision</label> ' +
                       '<input type="text" name="id_source_opts_bzr_rev_value"/></li>');
        li_rev.find('input[type=text]').keypress(function(e) {
            if (e.keyCode != 9) { // tab
                li_rev.find('input[type=radio]').attr('checked', true);
            }
        });
        li_rev.find('input[type=radio]').change(function() {
            if ($(this).attr('checked')) {
                li_rev.find('input[type=text]').focus();
            }
        });

        var li_head = $('<li><input type="radio" name="id_source_opts_bzr" id="id_source_opts_bzr_head" value="head" checked="checked"/> ' +
                        '<label for="id_source_opts_bzr_head">last revision</label></li>');

        ul.append(li_head);
        ul.append(li_tag);
        ul.append(li_rev);

        // initial value
        var type = this.initial.split('=', 1);
        if (type == 'tag') {
            li_tag.find('input[type=radio]').attr('checked', true);
            li_tag.find('input[type=text]').attr('value', this.initial.substr(4, this.initial.length));
        }
        else if (type == 'rev') {
            li_rev.find('input[type=radio]').attr('checked', true);
            li_rev.find('input[type=text]').attr('value', this.initial.substr(4, this.initial.length));
        }

        this.soc.append(bzr);

        return bzr;
    }

}

var soh = undefined;
function init_submit_page() {
    soh = new SourceOptionsHandler($('#submit-page form'));
    soh.init();
}


$(document).ready(function() {
    if ($('#submit-page')) { init_submit_page(); }
});

