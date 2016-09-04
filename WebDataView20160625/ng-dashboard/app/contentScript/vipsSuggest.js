//Initialization
vips = new VipsAPI(); //our API
globalBlocks = vips.getVisualBlockList(); //the list that contains your data, each item is a data element

//Your algorithm to analyze the data is here
//The following code manually specifies the result as a list of IDs.
//http://infolab.stanford.edu/db_pages/members.html 
/*************************************************************/

//leftcolumn: starting "1-6-1"; ending "1-27-1";
var ids = new Array("1-87","1-87-1","1-17-3-1","1-18-3-1","1-19-3-1","1-20-3-1","1-21-3-1","1-23-3-1","1-24-3-1","1-25-3-1","1-26-3-1","1-27-3-1","1-28-3-1","1-29-3-1","1-30-3-1","1-31-3-1","1-32-3-1","1-33-3-1","1-34-3-1","1-35-3-1","1-36-3-1","1-37-3-1","1-38-3-1","1-39-3-1","1-40-3-1","1-41-3-1","1-42-3-1","1-43-3-1","1-44-3-1","1-45-3-1","1-46-3-1","1-47-3-1","1-48-3-1","1-49-3-1","1-50-3-1","1-51-3-1","1-52-3-1","1-53-3-1","1-54-3-1","1-55-3-1","1-56-3-1","1-57-3-1","1-58-3-1","1-59-3-1","1-60-3-1","1-61-3-1","1-62-3-1","1-63-3-1","1-64-3-1","1-65-3-1","1-66-3-1","1-67-3-1","1-68-3-1","1-69-3-1","1-70-3-1","1-71-3-1","1-72-3-1","1-73-3-1","1-74-3-1","1-75-3-1","1-76-3-1");
/*************************************************************/

//Visualize the result
for (var i = 0; i < globalBlocks.length; i++) {
	for (var j = 0; j < ids.length; j++) {
		if (globalBlocks[i]['-vips-id']===ids[j])
			globalBlocks[i]['-att-box'].style.border = "4px solid orange";
	}
}
confirm("We think the highlighted blocks are interesting data in this page. Do you want to save it?");