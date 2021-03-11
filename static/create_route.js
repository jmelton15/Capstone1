async function initMap() {
    const pixabay_key = keys.pixabay;
    $("#load-gif").hide();
    const googleURL = "https://www.google.com/search?q="
    // const BASE_URL = "https://downtotherouteofit.herokuapp.com";
    const BASE_URL = "http://127.0.0.1:5000"
    const $currentUserID = $("#user_id").data("id")
    const $tripBtn = $("#trip-btn");
    const originIn = document.getElementById("origin-input");
    const destIn = document.getElementById("destination-input");
    const $txtAreaWaypts = $("#exampleFormControlTextarea1");

    let topRatedWaypoints = [];
    let waypointData = [];
    let savedMarkers = [];
    let savedStartPoint = "";
    let savedEndPoint = "";
    let memberStatus = false;
    let savedTripCount;

    /**
     * Quick function to reset the global arrays so the frontend doesn't keep unnecessary data
     */
    function resetGlobals() {
        topRatedWaypoints = [];
        waypointData = [];
    }
 ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
 /** SETTING UP GOOGLE API CLASS OBJECTS FOR USE IN THE APP**/

    /**
     * 
     * Everything below was taken from the google api documentation on how to setup global class objects
     * To make calls easier throughout the script. 
     * 
     * directionsService and directionsRenderer Handle getting directions and displaying a route
     * (currently I am not using the renderer functionality. I may or may not use it later on)
     * 
     * geocoder handles making requests to get latlng data back from google api
     * 
     * map handles setting up the map on the webpage
     * the options object is passed to the Map() method to tell the map how to load initially
     */
    const directionsService = new google.maps.DirectionsService();
    // const directionsRenderer = new google.maps.DirectionsRenderer({
    //     draggable: true,
    // });
    const geocoder = new google.maps.Geocoder();
    let options = {
        zoom:4,
        center:{lat:37.0902 ,lng:-95.7129} //start map on zoomed out united states, center
    };
    const map = new google.maps.Map(document.getElementById("map"),options);
    // await directionsRenderer.setMap(map);

 /////////////////////////////////////////////////////////////////////////////////////////////////////////////////
 /** CREATING MAP MARKERS **/
    /**
     * 
     * This function handles creating markes based on the unpacked data from the unpacking functions in this script
     * It sends a request to google.maps.Marker() with the parameters from the function and returns an array of markers
     *
     */
    // function createMarkerClusterer(topRatedWaypoints,infoWindowContent,waypointData) {
    //     const markers = topRatedWaypoints.map(function(waypoint, i) {
    //         const marker = new google.maps.Marker({
    //             position: waypoint,
    //             icon:waypointData[i]['icon'],
    //             label: (i+1).toString(),
    //             animation:google.maps.Animation.DROP,
    //         });
            // const infowindow = new google.maps.InfoWindow({
            //     content:infoWindowContent[i],
            // });
            // marker.addListener("click", () => {
            //     infowindow.open(map,marker);
            // });
    //         return marker;
    //     });
    //     return markers;
    // }
    function createMarkers(topRatedWaypoints,infoWindowContent,waypointData) {
        const markers = topRatedWaypoints.map(function(waypoint,i) {
            addNonClusterMarkers(waypoint,i,infoWindowContent,waypointData);
        })
        return markers;
    }
    // topRatedWaypoints.forEach((val,i) => {
    //     addNonClusterMarkers(val,i);
    // });
    function addNonClusterMarkers(location,i,infoWindowContent,waypointData) {
        const marker = new google.maps.Marker({
            position:location,
            icon:waypointData[i]['icon'],
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





 ////////////////////////////////////////////////////////////////////////////////////////////
 /**  DATA UNPACKING AND REPACKING FUNCTIONS FOR FRONTEND PROCESSING **/
 /**
  * 
  * The functions below take in waypoints (namely the top rated ones returned from the server)
  * and unpacks data into global variables to be used on the frontend for various reasons.
  * 
  * createLocationArray() returns an array of only coordinates of the waypoints
  * 
  * createContentArray() returns an array of html content we want to place in the infoWindows for markers
  * 
  * createWaypointDataArray() returns an array of all other waypoint data that we can use throughout the app
  *     this currently is icon,name, and place_id
  *
  */
    function createLocationArray(waypoints) {
        let arrayForMarkers = [];
        for (const wp in waypoints) {
            if (waypoints[wp] == []) {
                continue;
            }
            waypoints[wp].forEach(function(point) {
                for (const place in point) {
                    let lat = point[place]['lat'];
                    let lng = point[place]['lng'];
                    arrayForMarkers.push({lat:lat,lng:lng})
                }
            });
        }
        return arrayForMarkers;
    }
    function createContentArray(waypoints) {
        let namesArray = [];
        for (const wp in waypoints) {
            if (waypoints[wp] == []) {
                continue;
            }
            waypoints[wp].forEach(function(point,i) {
                for (const place in point) {
                    namesArray.push(
                        `<div class="d-flex flex-column">
                            <h1>${point[place]['name']}</h1>
                            <blockquote>${point[place]['address']}</blockquote>
                            <a href="${googleURL}${urlEncoder(point[place]['name'])}+${urlEncoder(point[place]['address'])}">Find It On The Web!</a>
                        </div>`
                    );
                }
            });
        }
        return namesArray;
    }
    function createWaypointDataArray(waypoints) {
        let waypointInfo = [];
        for (const wp in waypoints) {
            if (waypoints[wp] == []) {
                continue;
            }
            waypoints[wp].forEach(function(point) {
                for (const place in point) {
                    waypointInfo.push(
                        {   'name':point[place]['name'],
                            'address':point[place]['address'],
                            'icon':point[place]['icon'],
                            'place_id':point[place]['place_id']
                        }
                    );
                }
            });
        }
        return waypointInfo;
    }

    
 ////////////////////////////////////////////////////////////////////////////////////////////
 /** HANDLING MAP PAN AND ZOOM BASED ON USER INPUT **/
    /**
     * The next two eventlisteners call the two async functions below 
     * which pan the map based on the inputs from the user in the text boxes
     */
    let destInput;
    let originInput;
    originIn.addEventListener("focusout",async function(){
        if (destIn.value != "" && originIn.value == "") {
           await geocodeOriginInput(destInput);
        }
        else {
            let response = await geocodeOriginInput(); 
            originInput = response;
        }
    });

    destIn.addEventListener("focusout",async function(){
        if (destIn.value == "" && originIn.value != "") {
           await geocodeDestinationInput(originInput);
        }
        else {
            let response = await geocodeDestinationInput();
            destInput = response;
        } 
    });

    /** geocodeOriginInput and geocodeDestinationInput functions below **/
    /**
     * 
     * These functions are used to pan/move the map and zoom in on either a start location or end destination
     * when the user is done typing in the search boxes.
     * Not the cleanest code, but does the trick. I will be looking to refactor anything small later.
     * 
     */
    async function geocodeOriginInput(dest) {
        let center;
        let lat;
        let lng;
        if (originIn.value != "") {
            center = await geocoder.geocode({
                address:originIn.value
            });
            lat = center['results'][0]['geometry']['location'].lat();
            lng = center['results'][0]['geometry']['location'].lng();
            map.panTo({lat:lat,lng:lng});
            map.setZoom(6);
            return {lat:lat,lng:lng};
        }
        if (originIn.value == "" && destIn.value == ""){
            map.panTo({lat:37.0902 ,lng:-95.7129});
            map.setZoom(4);
        }
        if (dest == "") {
            return;
        }
        else {
            map.panTo(dest);
            map.setZoom(6);
        }
    }
    async function geocodeDestinationInput(org) {
        let center;
        let lat;
        let lng;
        if (destIn.value != "") {
            center = await geocoder.geocode({
                address:destIn.value
            });
            lat = center['results'][0]['geometry']['location'].lat();
            lng = center['results'][0]['geometry']['location'].lng();
            map.panTo({lat:lat,lng:lng});
            map.setZoom(6);
            return {lat:lat,lng:lng};
        }
        if (originIn.value == "" && destIn.value == ""){
            map.panTo({lat:37.0902 ,lng:-95.7129});
            map.setZoom(4);
        }
        if (org == "") {
            return;
        }
        else {
            map.panTo(org);
            map.setZoom(6);
        }
    }
 
 ////////////////////////////////////////////////////////////////////////////////////////////
    /**** CLICKING CREATE TRIP BUTTON *****/
    /**
     * 
     * When clicked, this button calls the processTripCreation() function to do all the requests
     * and data handling in order to process and create a trip of top rated places
     * 
     */
    
    $tripBtn.on("click", async function(e) {
        e.preventDefault();
        $(this).toggle();
        e.disabled = true;
        await processTripCreation();
        $("#load-gif").hide();
        $("#start-btn").addClass("collapsed");
        $("#collapseExample").removeClass("show");
    });

    /**
     * 
     * This function handles making requests to the server and google api to create a trip
     *  It first requests to the google api to get all the path coordinates of a start and stop point
     * Then it handles packing and unpacking the data to be loaded again to the google api, but this time
     * With toprated waypoints involved.
     * 
     * Once completed it has a final trip created showing the top rated place in each category that the user input'
     * and sends a request to google again to place markers at those waypoints
     * 
     */
    async function processTripCreation() {
        $("#load-gif").show();
        let data = getRouteData();
        
        if (data) {
            let routeData = await calculateRoute(directionsService,data[0],data[1]);
            let pointsArray = createPointsObject(routeData);
            
            let serverResponse = await axios.post(`${BASE_URL}/users/${$currentUserID}/trip`, {
                                                    "points":pointsArray,
                                                    "waypoints":data[2]
            });
            memberStatus = serverResponse.data.response.member_status;
            savedTripCount = serverResponse.data.response.saved_trips;
            const filteredWaypoints = serverResponse.data.response.top_rated_waypoints;
            
            let infoWindowContent = createContentArray(filteredWaypoints);
            topRatedWaypoints = createLocationArray(filteredWaypoints);
            waypointData = createWaypointDataArray(filteredWaypoints); //extra info about each waypoint
                
            savedMarkers = createMarkers(topRatedWaypoints,infoWindowContent,waypointData);
    
            // savedMarkers = createMarkerClusterer(topRatedWaypoints,infoWindowContent,waypointData);
            // await new MarkerClusterer(map,savedMarkers, {
            //     imagePath:
            //       "https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m",
            // });
            return;
        }
        return;
    }


    /**
     * This function just gathers up the form data and returns it in an array to be used later
     */
    function getRouteData() {
        savedStartPoint = originIn.value;
        savedEndPoint = destIn.value;
        const wayPoints = $txtAreaWaypts.val().split(/\r\n|\r|\n|,/g); 
        
        if (savedStartPoint != "" && savedEndPoint != "" && wayPoints[0] != "") {
            if (checkLength(wayPoints,10)) {
                return [savedStartPoint,savedEndPoint,wayPoints]
            }
            alert("You Have Input Too Many Waypoints. Limit is 9");
            return null;
        }
        alert("You Are Missing An Input(s). Please Make Sure You Fill Out The Points Of Interest Too")
        return null;
    }

    /**
     * 
     * This function gets direction data from a start and end point
     *   No waypoint data is gathered with this function
     * returns routeData object from google api
     * 
     */
    async function calculateRoute(directionsService,start,end) {
        let routeData = await directionsService.route(
            {
                origin:start,
                destination:end,
                optimizeWaypoints:true,
                travelMode: google.maps.TravelMode.DRIVING,
            }
        );
        return routeData;
    }

    
    /**
     * Function uses the lat() and lng() functions from google directions api
     *  These are found in the overview_path array from the route data gotten from
     *  the request to setDirections()
     * It returns an array where each index is an array or coordinates [lat,lng]
     * This is used to send back to the server with all the coordinates along a path
     * It will be used to search nearby locations on the server's end
     */
    function createPointsObject(routeData) {
        let pathArray = routeData.routes[0].overview_path;
        let pointsArray = [];
        pathArray.forEach(step => {
            const lat = step.lat();
            const lng = step.lng();
            pointsArray.push([lat,lng])
        });
        return pointsArray;
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

    /**
     * 
     * This function is for all get requests to Pixabay API to return photos based on a search term
     * it returns the entire data response
     * 
     */
    async function sendGetRequestToPixabay(search_term) {
        let response = await axios.get("https://pixabay.com/api/",{params:
            {
                key:pixabay_key,
                q:search_term,
                per_page:200
            }
        });
        return response;
    }

    /**
     * 
     * This function is used to generate a random photo url out of anywhere from 1-200 photos
     *  This allows for more versatile and unique travel journals for everyone
     * If the function finds no photos from pixabay, it goes to a default photo on the server
     * 
     */
    async function getRandomTripPhoto(encodedWaypointNames) {
        let photoArray = [];
        encodedWaypointNames.forEach(async function(wp) {
            let filteredArray = [];
            let response = await sendGetRequestToPixabay(wp);
            if (response.data.hits.length > 0) {
                response.data.hits.forEach((photo) => {
                    if (photo.webformatURL) {
                        filteredArray.push(photo.webformatURL);
                    }
                });
                photoArray.push(filteredArray[Math.floor(Math.random() * filteredArray.length)]);
            }
       });
       if (photoArray.length <= 0) {
            let response = sendGetRequestToPixabay(urlEncoder(savedEndPoint));
            if (photoArray.length <= 0) {
                return "/static/images/default_trip.jpg";
            }
            else { return response.data.hits[Math.floor(Math.random() * (response.data.hits.length))].webformatURL; }
            
       }
       else { return photoArray[Math.floor(Math.random() * photoArray.length)]; }
    } 

    /**
     * 
     * This function handles populating data to send to the server to save a trip for a user to the database
     *  and their travel journal
     * The post request sends a json object that looks like:
     *      {
                "start_point":savedStartPoint,
                "end_point":savedEndPoint,
                "waypoint_names":unpackedWaypointNames,
                "waypoint_latlng":unpackedWaypointLatLng,
                "photo": randomPhoto
            }
     *  Server responds with: 
        response {
                    "ok":"OK"
                 }
     * 
     */
    async function saveTrip() {
        let unpackedWaypointLatLng = [];
        let unpackedWaypointNames = [];
        let unpackedWaypointAddresses = [];
        topRatedWaypoints.forEach((wp) => {
            unpackedWaypointLatLng.push(`(${wp['lat']},${wp['lng']})`);
        });
        waypointData.forEach((wp) => {
            unpackedWaypointNames.push(wp['name']);
            unpackedWaypointAddresses.push(wp['address']);
        });
        let encodedPointNames = urlEncoder(unpackedWaypointNames);
        let randomPhoto = await getRandomTripPhoto(encodedPointNames);
        let response = await axios.post(`${BASE_URL}/users/${$currentUserID}/trips/save`,
            { 
                "start_point":savedStartPoint,
                "end_point":savedEndPoint,
                "waypoint_names":unpackedWaypointNames,
                "waypoint_addresses":unpackedWaypointAddresses,
                "waypoint_latlng":unpackedWaypointLatLng,
                "photo": randomPhoto
            }
        ); 
        return response.data;
    }

    /**
     * This function is used to verify that a non-member user isn't trying to save more trips than allowed
     */
    function checkMemberStatus() {
        if (savedTripCount >= 2 && !memberStatus) {
            return false;
        }
        return true;
    }

    /**
     * This handles the click event for saving a trip, calls the saveTrip() function
     */
    $("#save-trip-btn").on("click", async function() {
        if (topRatedWaypoints.length != 0 && waypointData.length != 0) {
            if (checkMemberStatus()) {
                await saveTrip();
                alert("Your Trip Details Have Been Saved!\n"+
                "You Can View Them In Your Travel Journal In Your Profile.")
                resetGlobals();
                return;
            }
            alert("You Have Saved The Maximum Amount Of Trips.\n" +
                "You Are Allowed 1 Saved Trip.");
            return;
        }
        alert("Inputs Are Empty, Please Input Trip Information Before Submitting");
        return;
    });

    /** This function validates the length of an input, namely the textarea for waypoints
     *  returns true if their are less than a given len or length, otherwise false
     */
    function checkLength(input,len) {
        if (input.length < len) {
            if (input.len == 1) {
                return input[0].length > 2 ? true : false;
            }
            return input.length == 0 ? false : true;
        }
        return false;
    }
 /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
 /** FUNCTION FOR MOBILE SCREEN ASTHETICS **/

 $("#start-btn").on("click",()=> {
    if ($(window).width() <= 900) {
        $("#how-to").toggle();
    }
 });
}





