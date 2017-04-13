/* Javascript for StudioEditableXBlockMixin. */
function StudioDisabledEditXBlock(runtime, xblockElement) {
    "use strict";
    
    $(xblockElement).find('.cancel-button').bind('click', function(e) {
        runtime.notify('cancel', {});
    });
    
}