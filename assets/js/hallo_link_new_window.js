/*
    raw html edit button based on the original code by https://github.com/ejucovy
    https://gist.github.com/ejucovy/5c5370dc73b80b8896c8
*/

(function() {
    (function($) {
        return $.widget('IKS.openLinkInNewWindow', {
            options: {
                uuid: '',
                editable: null
            },
            populateToolbar: function(toolbar) {
                var button, widget;

                var getEnclosing = function(tag) {
                    var node;

                    node = widget.options.editable.getSelection().commonAncestorContainer;
                    return $(node).parents(tag).get(0);
                };

                widget = this;

                button = $('<span></span>');
                button.hallobutton({
                    uuid: this.options.uuid,
                    editable: this.options.editable,
                    label: 'Open link in new window',
                    icon: 'icon-placeholder',
                    command: null
                });

                toolbar.append(button);

                button.on('click', function(event) {

                    var lastSelection = widget.options.editable.getSelection();
                    var insertionPoint = $(lastSelection.endContainer).parentsUntil('.richtext').last();

                    $('body > .modal').remove();
                    var container = $('<div class="modal fade editor" tabindex="-1" role="dialog" aria-hidden="true">\n    <div class="modal-dialog">\n        <div class="modal-content"\
>\n            <button type="button" class="close text-replace" data-dismiss="modal" aria-hidden="true"><i class="icon icon-cross"></i></button>\n            <div class="modal-body"><hea\
der class="nice-padding hasform"><div class="row"><div class="left"><div class="col"><h1><i class="icon icon-placeholder"></i>&nbsp;Open link in new window</h1></div></header><div class="modal-bo\
dy-body"></div></div>\n        </div><!-- /.modal-content -->\n    </div><!-- /.modal-dialog -->\n</div>');

                    // add container to body and hide it, so content can be added to it before display
                    $('body').append(container);
                    container.modal('hide');
                    var modalBody = container.find('.modal-body-body');
                    modalBody.html('<p style="margin: 2% 4% 0 4%;">This link will open in a new window. This can be relative (e.g. /about) or full (e.g. http://google.co.uk) URLs. For external URLs, be sure to prefix http:// or https://.</p><textarea placeholder="http://google.co.uk" style="height: 50px; width: 92%; font: 14px/21px monospace; border: 1px solid #d8d8d8; background: #f4f4f4; margin: 2% 4%;" id="wagtail-edit-anchor-content"></textarea><button i\
d="wagtail-edit-anchor-save" type="button" style="margin: 0 4%; float: right;" class="button">Save</button>');


                    $("#wagtail-edit-anchor-save").on("click", function() {
                        
                        text = $("#wagtail-edit-anchor-content").val()

                        if(!text.includes(' ') && text != '')
                        {

                             // Create an anchor
                            var a;
                            a = document.createElement('a');
                            a.setAttribute('href', text);
                            a.setAttribute('target', 'blank');
                            a.innerHTML = lastSelection;
                            
                            lastSelection.deleteContents();                            
                            lastSelection.insertNode(a);

                            widget.options.editable.setModified();

                            container.modal('hide');
                        } else
                        {
                            alert('Please enter a valid URL.')
                        }
                    });
                    container.modal('show');
                });
            }
        });
    })(jQuery);
}).call(this);