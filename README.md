# Hammerhead_Dashboard_route_autosynch
This automatically synchs your routes from externall sources like Strava and Komoot every X Minutes without manually clicking the synch-button on the dashboard

You need to use the developer tool in your browser to get your user ID. This ID should be static and not change over the time. Sadly this ID is somehow sourced by the java script or I just miss the information in the answer of the auth request.

Anyway if you log in, you will be redirected to the profile, what should in the network tab of the developer tool visible as a time slot.
Search under "name" for "profile.

If you now switch from "Headers" to "Preview" on the right next to the "name" section, you should see something like this:

id: "00000.user_profile", createdAt:

The ID of this user would be 00000. You will need to extract this number once for your self, so the refresh link can be generated correctly.
