odoo.define('get_google_map_location.GetGooglmapLocation', function(require) {
"use strict";

var core = require('web.core');
var form_common = require('web.form_common');
var Model = require('web.Model');
var utils = require('web.utils');

var _t = core._t;
var QWeb = core.qweb;

var GetGooglmapLocation = form_common.AbstractField.extend({ 
    events: {
        "click .get_google_map_location": "getLocation",
        "click .set_google_map_location": "setLocation",
        "click .current_gmap": "opennewwindow",
    },
    init: function(dataset) {
        this._super.apply(this, arguments);
        this.dataset = dataset;        
        this.set({
            res_id: false,
            google_map_location: false,
        });
        this.field_manager.on("field_changed:google_map_location", this, function() {
            this.set({"google_map_location": this.field_manager.get_field_value("google_map_location")});
            this.defaultmap(this.get('google_map_location'));
        });
        this.field_manager.on("field_changed:name", this, function() {               
            this.set({"res_id": this.view.datarecord.id});
        });
    },
    renderElement: function() {
        var self =  this;
        this._super();
        this.$el.html(QWeb.render("GetGooglemapLocation", {widget: this}));
    },
    defaultmap: function(map_location){
        var self = this;        
        var res_partner_obj=new Model('res.partner');
        res_partner_obj.call('get_default_google_maps_api_key').then(function(result){
            if (map_location && result['google_maps_api_key']){
                var google_maps_api_key = result['google_maps_api_key'];                
                var img_url  = "https://maps.googleapis.com/maps/api/staticmap?zoom=13&size=600x300&maptype=roadmap&markers=color:red%7Clabel:O%7C"+map_location+"&key="+ google_maps_api_key +"";        
                document.getElementById("current_gmap").innerHTML = "<img class='img img-responsive' src='"+img_url+"'>";
            }
            else{
                document.getElementById("current_gmap").innerHTML = "<img class='img img-responsive' src=''>";
            }
        });
    },
    setLocation: function(){
        var self =  this;
        var res_id = this.dataset.dataset.ids[0];
        this.do_action({
            type: 'ir.actions.act_window',
            res_model: 'set.google.map.location',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            context:{
                'active_id':res_id
            }
        });
    },
    getLocation: function(){
        var self =  this;
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                self.showLocationmap(position.coords.latitude,position.coords.longitude);
            });
        }
        else{
            alert("Sorry, Browser does not support Geolocation!");
        }
    },
    showLocationmap: function(latitude,longitude) {     
        var self = this;
        var latlongvalue = latitude + ","+ longitude; 
        
        var res_partner_obj=new Model('res.partner');
        res_partner_obj.call('get_default_google_maps_api_key').then(function(result){            
            if (result['google_maps_api_key']){                
                var img_url  = "https://maps.googleapis.com/maps/api/staticmap?zoom=13&size=600x300&maptype=roadmap&markers=color:red%7Clabel:O%7C"+latlongvalue+"&key="+ result['google_maps_api_key'] +"";        
                document.getElementById("current_gmap").innerHTML = "<img class='img img-responsive' src='"+img_url+"'>";
            }
        });
        
        var model_obj=new Model(this.dataset.model);
        var res_id = this.dataset.dataset.ids[0];
        model_obj.call('get_lat_long',[res_id,latitude,longitude],{context:{'active_id':res_id}}).then(function(result){
            return result;
        });        
    },
    opennewwindow: function(){
        var google_map_location = this.get('google_map_location');
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var url = "https://maps.google.com/?q=" + google_map_location;
                window.open(url);
            });
        }
    },
    is_false: function() {
        return false;
    },
});
core.form_widget_registry.add('get_google_map_location', GetGooglmapLocation);
return GetGooglmapLocation;
});
