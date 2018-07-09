/***********************************************************************

DATASCRIPTS.JS

These functions are used by the pipeline data page to load new content.

***********************************************************************/

//**** Function Declarations

// SetSelectAction: Sets the action for the select form.
//     For folder selections, the folder_selection input
//     value is also set.
function setselectaction(sel) {
    form = sel.form;
	foldersel = form.elements['folder_selection'];
	// If selection is a folder -> set folder_selection value
	if(sel.name.indexOf('folder') > -1) {
	    selectval = sel.options[sel.selectedIndex].value;
	    form.action = form.action + '/' + selectval;
	    foldersel.value = selectval;
	}
	// Add folder_selection value to action
	form.action = form.action + '/' + foldersel.value;
}	
