/*
Settings tabs
*/

$(document).ready(function() {
	
	
	$('#general_tab').on( 'click', function () {
	
	});
	
	$('#cat_tab').on( 'click', function () {
		list_cat();
	});
	
	$('#frmCat_tab').on( 'click', function () {
		list_fcat();
	});
	
	$('#perfume_types_tab').on( 'click', function () {
		list_ptypes();
	});
		
	$('#templates_tab').on( 'click', function () {
		list_templates();
	});
		
	$('#print_tab').on( 'click', function () {
		
	});
		
	$('#brand_tab').on( 'click', function () {
		
	});
		
	$('#maintenance_tab').on( 'click', function () {
		get_maintenance();
	});
		
	$('#pvOnline_tab').on( 'click', function () {
		get_pvonline();
	});
	
	$('#api_tab').on( 'click', function () {
		
	});
	
	$('#about_tab').on( 'click', function () {
		get_about();
	});
	
});