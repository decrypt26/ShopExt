Browser extension to compare products on shopping websites
This work was done as a part of CS412 project by:
1. Dhruv Gelda
2. Tarun Giri 
3. Sahil Gaba
4. Nishanth Lingala

This repository contains:
1. Script to classify similar objects together, ExtensionSim.py
2. Web Data View extension, WebDataView20160625

To run the script, from WebDataView20160625, add ng-dashboard folder as an extension to chrome. Go to amazon and search for anything you want. Use extension to export all visual elements. This would generate a json file. You can highlight all elements and see ids of different objects by hovering over them.

Set the pathnm and filenm variables according to where the json file is downloaded.

selectedVIPSids: 
a list of vips-ids that are of the same shopping product. If you put only one vips-id (say, that of an image), then you would get a list of all  vips-ids of the images. If you put vips-id of image and the price, then you would get a list of all the vips-ids of the images, of the prices, and the corresponding associative pairing. Excel file will be written.

threshFrac:
If objects A and B have more than threshFrac*100 number of attributes, then A is classified to be of the same type as B. This should be 0.63 for Amazon

javaScriptFilePath:
This is the location of vipsSuggest.js file. This file would be overwritten by the python script. So, when you ask for suggestions, vips would highlight those vips-id classified by the algorithm.
	
	
 




	
