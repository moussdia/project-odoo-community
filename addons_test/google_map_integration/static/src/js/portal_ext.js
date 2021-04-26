odoo.define('portal_ext.portal_ext', function (require) {
	'use strict';
	//var ajax = require('web.ajax');
	//var Class = require('web.Class');
	//var core = require('web.core');
	//var ColorpickerDialog = require('web.colorpicker');
	//var mixins = require('web.mixins');
	//var base = require('web_editor.base');
	//var weContext = require('web_editor.context');
	//var rte = require('web_editor.rte');
	//var weWidgets = require('web_editor.widget');

	//var QWeb = core.qweb;
	//var _t = core._t;

	//var dom = $.summernote.core.dom;
	//var range = $.summernote.core.range;
	//var eventHandler = $.summernote.eventHandler;
	//var renderer = $.summernote.renderer;

	//var tplButton = renderer.getTemplate().button;
	//var tplIconButton = renderer.getTemplate().iconButton;
	//var tplDropdown = renderer.getTemplate().dropdown;


	console.log('printfffsss');
	//require('auth_opportunity_signup_ext.fields');
	    
	
	$(document).ready(function () {
	
	/*$('#image').change(function () {
	console.log("The value of a is liju");
    });
	$('#image_upload').mouseover(function(){
		$('#image_upload').css("background-color", "yellow");
	});
	$('#image_upload').dblclick(function(e){
		console.log("liju liju");
		console.log(e);
		
				
	});*/
	
	
	
	function readURL(input) {

		  if (input.files && input.files[0]) {
		    var reader = new FileReader();

		    reader.onload = function(e) {
		      $('#blah').attr('src', e.target.result);
		      $("#image").val(e.target.result);
		      console.log(e.target.result);
		    }

		    reader.readAsDataURL(input.files[0]);
		  }
		}
		//debugger;
		$("#imgInp").change(function() {
		  readURL(this);
		});
	
	
		
	});
	
		
});


