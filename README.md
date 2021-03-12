<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#data-storage-and-safety">Data Storage And Safety</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

### Capstone Project 1 - DTRI (Down To the Route of It)

This is my first ever capstone project completed fully from my own coding and knowledge. Needless to say, it is still a Project in the works! 
This project utilizes Google Maps APIs. The goal is to create an application that will create a trip for you based on top-rated places in certain-
categories. Many people search top rated-places in the categories they want to visit or go to along their trip and a big chunk of time is 
first used finding all the "best" places that are between where you are starting and where you are going. So, this app is aimed at giving that 
time back to you. It will find all those top-rated places for you and create your trip based on different stops, categories, genres, 
places you want to have on your trip. Users can then save their trip and the app will store it for that user in their own personal travel journal 
on their profile page.

Despite being up and running, this web application is definitely a baby. Any feedback, tips, ideas, or even bugs that you may find while trying it out,
please let me know!

### Future Plans

The code is still a 'baby' and I will be refactoring and cleaning it up as I continue to work on it and add new features. Bare with me if it isn't as clean as it can be
as I am new to development and trying out many new things. With that said, I am always open to suggestions and ideas! If something stands out to you that I did well, or that I can improve upon, feel free to reach out to me at the email in the contact section!

I plan on spending the summer learning new things and then applying it to this application. I'd like to make my database bigger and add more elements to store. With that, I'd like to make algorithms that will populate trips solely from my database as more and more popular trips appear in it. This will allow for quicker load times over time. I'd also like to create a social system like I mentioned above where users can interact with other user's pages/trips, maybe leave notes in eachother's journals, have globally saved trips for people to view, allow user's to recommend trips, etc! The list goes on! 

### Built With - Credits To The Following:

* [Python](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [postgreSQL](https://www.postgresql.org/)
* [SQL-Alchemy](https://www.sqlalchemy.org/)
* [flask-sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
* [Flask-WTForms](https://flask-wtf.readthedocs.io/en/stable/)
* [HTML & CSS](https://developer.mozilla.org/en-US/docs/Web/HTML)
* [JavaScript & Jquery](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
* [AJAX](https://developer.mozilla.org/en-US/docs/Web/Guide/AJAX)
* [AXIOS](https://github.com/axios/axios)
* [Jinja](https://jinja.palletsprojects.com/en/2.11.x/)
* [Bootstrap 5](https://getbootstrap.com/)
* [GOOGLE MAPS API](https://cloud.google.com/maps-platform/?utm_source=google&utm_medium=cpc&utm_campaign=FY18-Q2-global-demandgen-paidsearchonnetworkhouseads-cs-maps_contactsal_saf&utm_content=text-ad-none-none-DEV_c-CRE_274433407138-ADGP_Hybrid%20%7C%20AW%20SEM%20%7C%20BKWS%20~%20Google%20Maps%20API-KWID_43700033921822021-aud-599437145008%3Akwd-335425467-userloc_9017525&utm_term=KW_google%20maps%20api-ST_google%20maps%20api&gclid=Cj0KCQiA7NKBBhDBARIsAHbXCB5idACJ_A39gBkebSY75I0EkCuOraqAZKzGsgi3X4nirsE8FTh0j5caAmSUEALw_wcB)
* [TurnJS](http://www.turnjs.com/)
* [PIXABAY API](https://pixabay.com/)


<!-- GETTING STARTED -->
## Getting Started

On the website, you will have access to multiple places that will help you use the site and navigate your way around.
Steps to navigate smoothly are as follows (however, there are many ways to navigate):

1. Register An Account (create an account)
2. View your new profile page by clicking the "Profile" tab found on the top navigation bar, left-hand side
3. OR if you want to learn more, click the "About the App" tab found on the top navigation bar, left-hand side
4. Once at the profile page, feel free to update your username, so long as the username you want is available!
5. Also, have a look at your travel journal, which should still be empty (so long as you haven't created a trip yet). Try turning its pages!
6. Once that all feels good, go try creating your first trip!!! EXCITING! - Click the "Create Trip" tab found on the top navigation bar, left-hand side
7. On the left hand side of the creat trip page, you should see some information on how to use the application, definitely read that!
8. Once that makes sense and you think you have the idea, put in your route information including some categories of places you may want to stop
  - Some examples of points of interest are: Parks, State Parks, Playgrounds, Ice Cream, Beaches, Waterparks, rest stops, truck stops, hotels, etc.
  - Be as vague or explicit as you feel comfortable
  - The text area can currently read your input by new lines (enter key) and commas "Parks , Ice cream , etc."
9. When using the app for the first time, bare-with the loading time if you are travling a long distance and looking for many points of interest along the way.
Once the app has been used, the load times decrease exponentially, but there are a lot of checks that the program does to make sure it gets you a solid
amount of non-duplicated results and makes sure that the results represent top-rated places.
10. Each point of interest marker on the map is clickable. It will display the name, address, and a link to search the location online!  
11. Once you have successfully created a trip, click the "Save Trip" button found on the left hand side of the page by the trip form
12. A pop up alert should show up stating that your trip has been saved to your profile! Go have a look, your trip information including a photo should 
now be inside your travel journal; turn the pages!
13. You have now successfully completed a smooth create and save transaction!
14. From here, in your travel journal, you can click the button under each trip and it will remake your trip again on the map for you to see.


## Reasons Behind API Choice and Site Ideas

I opted to use Google Maps as my mapping API because of their nearby_places integration and depth. I have limited the number of trips users can make 
in order to prevent making too many requests to Google since it can become a non-free entity at that point. 

I added in the travel journal idea because I believe this application has lots of room for growth and expansion as time permits me. The travel journal
opens up worlds where there is the ability to like and comment on other users' trips, Share travel journals with friends, etc.
But the travel journal also gives users a way to come back to their saved data and use it again.

<!-- DATA STORAGE AND SAFETY -->
## Data Storage And Safety

Everything that is stored to be used later is encrypted and secured while stored. Decoding alogorithms are in places to bring back the stored data to be used
on the client side when asked by that specific user. I may have went a little overboard with the encryption even, but it was fun to learn and good practice! 

<!-- CONTACT -->
## Contact

Your Name - [John Melton]
Email - [johnmelton.projects@gmail.com]
Project Link: [https://github.com/jmelton15/DTRI](https://github.com/jmelton15/DTRI)



<!-- ACKNOWLEDGEMENTS -->
## [Google Maps](https://cloud.google.com/maps-platform/?utm_source=google&utm_medium=cpc&utm_campaign=FY18-Q2-global-demandgen-paidsearchonnetworkhouseads-cs-maps_contactsal_saf&utm_content=text-ad-none-none-DEV_c-CRE_274433407138-ADGP_Hybrid%20%7C%20AW%20SEM%20%7C%20BKWS%20~%20Google%20Maps%20API-KWID_43700033921822021-aud-599437145008%3Akwd-335425467-userloc_9017525&utm_term=KW_google%20maps%20api-ST_google%20maps%20api&gclid=Cj0KCQiA7NKBBhDBARIsAHbXCB5idACJ_A39gBkebSY75I0EkCuOraqAZKzGsgi3X4nirsE8FTh0j5caAmSUEALw_wcB)
## [PIXABAY API](https://pixabay.com/)
## [TurnJS](http://www.turnjs.com/)







