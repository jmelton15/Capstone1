$(document).ready(function() {
    const updateButton = document.getElementById("update-cc");
    const deleteAccountButton = document.getElementById("delete-acct");
    const deleteTripButtons = document.querySelectorAll("#delete-trip");

    /** 
     * Function deleteAccount() calls the User class's deleteUser() method
     * found in the user_details_classes.js file.
     * 
     **/
    async function deleteAccount() {
       let response = await User.deleteUser();
       
       alert(response.response.alert);
        // location.href = "https://downtotherouteofit.herokuapp.com/register";
        location.href = "http://127.0.0.1:5000/register";
    }
    /** 
     * Function updateUser() calls the User class's updateUsername() method
     * found in the user_details_classes.js file.
     * 
     **/
    async function updateUser() {
        const $newUsername = $("#username").val();
        let response = await User.updateUsername($newUsername);
        
        if (response && response.response.ok == "OK") {
            $("#error-code").text("");
            $("#user-name").text(`Hello, ${$newUsername}`);
            $("#front-page-header").text(`${$newUsername}'s Travel Journal`);
        }
        else {
            $("#error-code").text(`${response.response.error}`);
        }
    }
    /** 
     * Function deleteATrip() calls the User class's deleteTrip() method
     * found in the user_details_classes.js file.
     * 
     * 
     **/
    async function deleteATrip(trip_id) {
        let response = await User.deleteTrip(trip_id);
        alert(response.response.alert);
        location.href = `${BASE_URL}/profile`;
    }
    /** Whenever the page is loaded, we assign an evenListener to each trash button **/
    deleteTripButtons.forEach((btn) => {
        btn.addEventListener("click", async function(e) {
            let trip_id = e.target.dataset.id;
            
            await deleteATrip(trip_id);
        });
    });

    updateButton.addEventListener("click",() => {
        updateUser();
    })
    deleteAccountButton.addEventListener("click",() => {
        deleteAccount();
    })
     
    /**  FLIPBOOK EVENTS AND OPTIONS **/
/////////////////////////////////////////////////////////////////////////////////
    if (window.screen.width >= 900) {
        $("#flipbook").turn({
            autoCenter: true,
            gradients:true,
            acceleration:true
        });
    }
    else {
        $("#flipbook").turn({
            autoCenter: true,
            gradients:true,
            acceleration:true,
            display:"single"
        });
    }
    
    

});



    



    


