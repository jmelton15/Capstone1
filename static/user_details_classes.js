const $uID = $("#user-btns").data("id");
// const BASE_URL = `https://downtotherouteofit.herokuapp.com/users/${$uID}`;
const BASE_URL = `http://127.0.0.1:5000/users/${$uID}`;
class User {

    static async updateUsername(newUsername) {
        if (newUsername != "") {
            const user = await axios.patch(`${BASE_URL}/profile`,
                {
                    "new_username":newUsername,
                }
            );
            return user.data;
        }
    }

    static async deleteUser() {
        const response = await axios.delete(`${BASE_URL}/profile`);
        return response.data;
    }

    static async deleteTrip(trip_id) {
        const response = await axios.delete(`${BASE_URL}/trips/${trip_id}`);
        return response.data;
    }

}

