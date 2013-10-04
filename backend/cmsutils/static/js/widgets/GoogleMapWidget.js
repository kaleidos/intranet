/*
GoogleMapPosition - Turns an input box into a map to select a position.

Requires core.js and addevent.js.
*/

function GoogleMapPositionSelector(field_id, field_name, width, height, zoom, initial_lat, initial_lng) {
        this.from_box = document.getElementById(field_id);
        this.from_box.id += '_from'; // change its ID
        this.from_box.style.display = 'none';

        this.width = width;
        this.height = height;
        this.zoom = zoom;
        this.initial_lat = initial_lat;
        this.initial_lng = initial_lng;

        // Remove <p class="info">, because it just gets in the way.
        var ps = this.from_box.parentNode.getElementsByTagName('p');
        for(var i=0; i<ps.length; i++) {
            this.from_box.parentNode.removeChild(ps[i]);
        }

        this.map_div = quickElement('div', this.from_box.parentNode);
        this.map_div.className = 'gmap';
        this.map_div.id = "map_" + field_name;
        this.map_div.style.width= this.width + "px";
        this.map_div.style.height= this.height + "px";

        this.hidden_input = quickElement('input', this.from_box.parentNode, '', 'type', 'hidden');
        this.hidden_input.id = field_id;
        this.hidden_input.name = field_name;
        this.hidden_input.value = this.from_box.value;
        this.from_box.setAttribute('name', this.from_box.getAttribute('name') + '_old');

        var loc = this.from_box.value.split(",");
        if(loc.length==2) {
            lat = parseFloat(loc[0]);
            lng = parseFloat(loc[1]);
            this.blank = false;
        } else{
            lat = this.initial_lat;
            lng = this.initial_lng;
            this.blank = true;
            //this.hidden_input.value="37.303006,-6.302719";
        }

        this.init_map = function(lat, lng) {
         map_div = this.map_div;
         if (GBrowserIsCompatible()) {
            this.map = new GMap2(map_div);
            this.map.addControl(new GSmallMapControl());
            this.map.addControl(new GMapTypeControl());

            var point = new GLatLng(lat, lng);
            this.map.setCenter(point, zoom);
            this.m = new GMarker(point, {draggable: true});

            GEvent.bind(this.m, "dragend", this, function() {
                        point = this.m.getPoint();
                        this.save_position(point);
            });
            if (!this.blank) {        
                this.map.addOverlay(this.m);
            }
            /* save coordinates on clicks */
            GEvent.bind(this.map, "click", this, function (overlay, point) {
                this.save_position(point);
                this.map.clearOverlays();
                this.m = new GMarker(point, {draggable: true});
                GEvent.bind(this.m, "dragend", this, function() {
                    point = this.m.getPoint();
                    this.save_position(point);
                });
                this.map.addOverlay(this.m);
            });

          }
        }

        this.save_position = function(point) {
            this.hidden_input.value = point.lat().toFixed(6) + "," + point.lng().toFixed(6);
            this.map.panTo(point);
        }

        this.init_map(lat, lng);

        return this;
    }
