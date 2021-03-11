async function initMap() {
    const googleURL = "https://www.google.com/search?q="

    const $currentUserID = $("#user_id").data("id");
    const metaInfo = document.getElementById("trip-info");
    let tripInfo = JSON.parse(metaInfo.dataset.info);
 ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
 /** SETTING UP GOOGLE API CLASS OBJECTS FOR USE IN THE APP**/

    /**
     * 
     * Everything below was taken from the google api documentation on how to setup global class objects
     * To make calls easier throughout the script.
     * 
     * map handles setting up the map on the webpage
     * the options object is passed to the Map() method to tell the map how to load initially
     */
    let options = {
        zoom:4,
        center:{lat:37.0902 ,lng:-95.7129} //start map on zoomed out united states, center
    };
    const map = new google.maps.Map(document.getElementById("map"),options);

    const infoWindowContent = createContentArray(tripInfo);
    createMarkers(tripInfo["waypoint_latlng"],infoWindowContent)

 /////////////////////////////////////////////////////////////////////////////////////////////////////////////////
 /** CREATING MAP MARKERS **/
    /**
     * 
     * This function handles creating markes based on the unpacked data from the unpacking functions in this script
     * It sends a request to google.maps.Marker() with the parameters from the function and returns an array of markers
     *
     */
    function createMarkers(topRatedWaypoints,infoWindowContent) {
        const markers = topRatedWaypoints.map(function(waypoint,i) {
            addNonClusterMarkers(waypoint,i,infoWindowContent);
        })
        return markers;
    }
    function addNonClusterMarkers(location,i,infoWindowContent) {
        const marker = new google.maps.Marker({
            position:location,
            map:map,
            label:{text:(i+1).toString(),color:"black"},
            animation:google.maps.Animation.DROP,
        });
        const infowindow = new google.maps.InfoWindow({
            content:infoWindowContent[i],
        });
        marker.addListener("click", () => {
            infowindow.open(map,marker);
        });
        google.maps.event.addListener(marker, "mouseover", function(evt) {
            let label = this.getLabel();
            label.color="white";
            this.setLabel(label);
        });
        google.maps.event.addListener(marker, "mouseout", function(evt) {
            let label = this.getLabel();
            label.color="black";
            this.setLabel(label);
        });

    }
 ////////////////////////////////////////////////////////////////////////////////////////////////
    function createContentArray(tripInfo) {
        let namesArray = [];
        tripInfo.waypoint_latlng.forEach((point,i) => {
            namesArray.push(`<div class="d-flex flex-column">
                                <h1>${tripInfo.waypoint_names[i]}</h1>
                                <blockquote>${tripInfo.addresses[i]}</blockquote>
                                <a href="${googleURL}${urlEncoder(tripInfo.waypoint_names[i])}+${urlEncoder(tripInfo.addresses[i])}">Find It On The Web!</a>
                            </div>`)
        });
        return namesArray;
    }

    /**
     * 
     * This function is used to encode waypoint names into url encoded strings ("str+str+ .. etc")
     * but only if the waypoint name has spaces. Otherwise, it's just one word and can be sent as is.
     * Usually will take in an array of string names, however, it can handle single strings as well.
     *  This is because the pixabay api for pictures needs encoded url strings to search pictures
     * 
     * returns a new string or array of strings that are URL encoded ("str+str+ .. etc")
     */
     function urlEncoder(waypointnames) {
        if (Array.isArray(waypointnames)) {
            let encodedArray = [];
            waypointnames.forEach((wp) => {
               encodedArray.push(wp.replace(/\s+/g, "+"));
            })
            return encodedArray;
        }
        else {
            return waypointnames.replace(/\s+/g, "+");
        }
    }
}

