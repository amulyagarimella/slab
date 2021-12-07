## Design Doc
### Slab: Better Lab Notes

## Motivations

### Background
I spent the summer before my freshman year working in a laboratory. Every method we carried out was guided by a protocol. Our lab manager had a beautiful and meticulously crafted OneNote notebook filled with default protocols; we would copy each protocol template and fill it in with notes (for example, we might write the volume of bacterial culture or stock solution we produced from a given method). My lab manager's protocol setup was fantastic but took an immense amount of work to set up and was extremely susceptible to human error. There was a whole process for copying and filling out templates, and if we did not copy and fill out the templates correctly, the whole system would fall apart. Additionally, the fact that protocol steps can change added an extra layer of complexity.

### Why Slab?
I thought this was a problem I could help solve! I took a look at some existing Electronic Lab Notebook, or ELN, software (e.g. [Benchling](https://www.benchling.com/notebook/), [CDD Vault](https://www.collaborativedrug.com/benefits/eln/?utm_source=google&utm_medium=cpc&utm_campaign=competition&utm_content=eln&utm_term=benchling%20eln&utm_campaign=Competitors+-+US&utm_source=adwords&utm_medium=ppc&hsa_acc=1785135633&hsa_cam=13033093838&hsa_grp=125663763561&hsa_ad=520338472262&hsa_src=g&hsa_tgt=kwd-824946336453&hsa_kw=benchling%20eln&hsa_mt=b&hsa_net=adwords&hsa_ver=3&gclid=CjwKCAiAhreNBhAYEiwAFGGKPGp9CTqi74tp7npjGJRp1b3M2iX51SSynif_Y00tXx-ZvIk51qHi1BoCnCcQAvD_BwE)). ELNs can be very pricey and it's very difficult to choose the right one (see this [Nature article](https://www.nature.com/articles/d41586-018-05895-3) about how to choose an ELN — there were over 72 ELN products available as of just 2018!). I thought that a simple, elegant solution that still afforded the researcher a LOT of editing power would be helpful.

Slab is different than a typical ELN because it splits protocols into steps, creating a standardized view for protocols instead of making the researcher write everything out. This allows for much easier viewing, editing, and note-taking. 

## Under the hood

### App structure
* `slab/`
    * `README.md` Getting started and using Slab.
    * `DESIGN.md` Design doc. You are here!📍
    * `app.py` Main app routes: login/logout, registration, protocol creation, protocol editing, protocol viewing, error handling.
    * `helpers.py` Helper functions: one to flash form errors and one to be used as a Jinja filter to display times in user's local timezone.
    * `models.py` Objects that represent tables in our database.
    * `forms.py` Various forms we use in the app: login, registration, protocol creation, protocol editing.
    * `static/`
        * `main.css` CSS styling for the app.
        * `slab.svg` Our logo.
        * `gummy-macbook.svg` `gummy-medical-lab.svg` `gummy-sweet-home.svg` Vector illustrations by Vijay Verma. 
    * `templates/`
        * `base.html` Base page template.
        * `edit.html` Protocol editing form.
        * `index.html` Main page.
        * `login.html` Login page.
        * `new.html` New protocol creation page.
        * `protocols.html` Contains all of a user's protocols.
        * `register.html` Registration page.

### My stack

##### Bootstrap
I use Bootstrap to build and style Slab. Bootstrap's elegant and easy-to-use premade components make it easier to create a nice-looking website with the functionality I need.

##### jQuery
I use jQuery to add some dynamic functionality to Slab. Via jQuery, autocomplete is turned off for every input and the "active" class is automatically attached to active links.

##### Flask & Python
I use Flask and Python to create Slab's backend. I chose to use Flask to build my app not only because I have the most familiarity with Python, but also because there are a wide array of Flask extensions and frameworks that make app-building much easier and more intuitive.

##### SQLAlchemy
Undergirding Slab is its backend database. I use [SQLAlchemy](https://www.sqlalchemy.org), along with the [Flask-SQLAlchemy extension](https://flask-sqlalchemy.palletsprojects.com/en/2.x/), to make database functions really simple. SQLAlchemy is an ORM, or object-relational mapper, that allows us to represent SQL tables as Python objects. What does this mean for Slab? It means that creating databases is super intuitive and simple — I created and stored all my tables in `models.py`, and easily edited them right in the Python code. Using SQLAlchemy also allows for extremely easy table updates without having to worry about SQL queries.

##### Flask-Login
I use [Flask-Login](https://flask-login.readthedocs.io/en/latest/) for Slab's login and session management instead of just using Flask's built-in Sessions. Flask-Login does all the same things as Sessions but heavily simplifies user login and logout, and also plays well with SQLAlchemy, allowing me to access attributes of the current user without having to use SQL queries.

##### WTForms
I use [WTForms](https://wtforms.readthedocs.io/en/3.0.x/) to simplify and streamline the several forms Slab uses. WTForms lets me represent forms as Python objects (which I store in `forms.py`) and elegantly handles HTML rendering along with form validation (!). WTForms provides tools that make more complicated functionality straightforward to implement: for example, in the protocol editing view, I dynamically generate form fields based on how many steps a given protocol has, and WTForms has functionality for this (I go into this example more later on in the doc when I explain Slab's functionality). Additionally, WTForms works really well with SQLAlchemy, as form data is very easy to pass to object fields. 

### A functional tour of Slab

Let me take you on a tour through Slab's functionality. I'll discuss features of each implementation and my motivations behind certain choices I made!

##### Slab's Database
I ues SQLAlchemy for my database needs, so all my tables are represented with Python classes and stored in `models.py`, and all constituent elements of those databases are Python objects. Slab's database consists of three tables: one storing Users, one storing Protocols, and one storing Steps. Protocols are the children of Users and Steps are the children of protocols. I set up my databases like this because any given user can have an unlimited number of protocols associated to them and any protocol can have an unlimited number of steps associated to it. Users, Protocols, and Steps are all assigned unique IDs which function as primary keys in their respective tables. Protocols are also associated with the ID of the User that created them, and Steps are associated with the ID of the Protocol they're a part of along with the ID of the User that created them (these are all foreign keys in their respective tables).

Users have a few special features: in addition to initialization and representation functions, which all of the models have, it also has a function to verify passwords based on a given User object. Users are also created with the Flask-Login UserMixin base to allow us to gain additional info about the user, such as whether they're currently logged in.

Associated with Protocols are timestamps corresponding to when the protocol was created and last edited. For maximum app flexibility, these timestamps are stored in UTC, then represented with the system timezone on the client side using a custom-created Jinja filter. Storing timezone-specific user data in databases would be complicated and add unnecessary overhead especially considering different users can be in different timezones and travel between different timezones. For this reason, storing timezone-specific data in databases is a huge backend dev no-no! However, I thought it'd be asking a little too much of the user to set their own timezone in-app (especially considering timezones can change if a user travels). It's best to just quietly filter the timestamp on our own! I use the included datetime library to handle timezone storage, as well as pytz for timezone representation (to get UTC timezone info compatible with datetime), and finally the tzlocal library to get the local timezone. Additionally, there's a protocol title that represents the overall method.

Associated with Steps are the text of the step itself, as well as associated notes and the amount of time the step took. These are both text fields (well, the time taken field is technically a string field, which I chose because I liked the HTML rendering a bit better, and it doesn't need to be multiline). I decided to represent the amount of time taken with a text field instead of an integer field in order to allow for maximum flexible. Protocol steps in a real lab could occur on timescales of seconds, minutes, hours, or days, so limiting users to a number without associated text input possible to represent the time unit would be silly and unnecessarily rigid.

##### Registration
Any new user needs to start by creating a new account! Registration is handled with WTForms and SQLALchemy (along with some Bootstrap for the form creation and styling). I use WTForms to create and render a registration form, and use WTForms "validators" to impose constraints on user input: length limits, password/confirmation matching, and username uniqueness. Upon submission of the form, the data is retrieved from the table and a new User object is created with the passed-in name, username, and password. The User table is updated with the new User information. Finally, the user is redirected to log in with their new account. Using WTForms allows me to easily build in form validation without having to write tons of inline HTML or if-statements in the Python code, and using SQLAlchemy lets me easily and intuitively update tables with new information.

##### Login (and Logout)
Login is handled with WTForms, Flask-Login, and SQLAlchemy (plus, again, Bootstrap to construct and style for form). First, I use WTForms to create and render the login form, again taking advantage of WTForms's built-in validators. If the form validates and is submitted via a POST request, I query my Users table using SQLAlchemy to find out if the user exists, check the inputted password, then log them in and start their session using Flask-Login. 

Logout is easily handled by Flask-Login, which contains a function to log users out and end their session.

##### Adding protocols
OK, now to the actual protocol-related functionality!! When the user goes to add a protocol, they're prompted for a protocl title and a list of steps that needs to be separated line by line. I chose to make the user submit like this since it's relatively easy on the user's end and also easy to parse on the backend! The user is then directed to the protocol editing view. I chose to direct the user this way (instead of just redirecting back to the index once the protocol is created) so that the user could add any notes or fix any typos. Upon saving the protocol, the user can view or make edits to it by going to My Protocols, or add another protocol.

The protocol submission is handled again by WTForms because it's easy to validate the form this way (i.e. impose limits on title length and make sure there are actual steps inputed) and also because it's easy to retrieve text info from the form and parse it into steps!

Once the form is validated and the data retreived from the form, a new Protocol object is created and added to the database. The protocol parsing is handled in a single line, and a simple for loop is all we need to create new step objects using each parsed line of the submitted protocol and add them to the step database.

##### Editing protocols
Protocol editing is probably the most complex view I had to implement. The first bit of complexity is that, to represent an editable protocol we must have access to both the protocol object and to all associated step objects. Additionally, the editing view must be accessible through a route of its own (instead of just passing the necessary objects to render_template along with the edit.html page) since multiple pages redirect to protocol editing (e.g. a click from the protocol viewing screen, editing after creating a new protocol) and we also need to create and render a new form on the editing screen. Therefore, we need a way to pass in protocol-related info to the editing screen. I create an edit route with I a URL parameter passed in that represents the protocol being edited (this parameter is the protocol ID, which is enough because the protocol object and child step objects are accessible using protocol ID alone). This was a new concept to me but I was ultimately able to implement the feature with the url_for feature included in Flask. 

I use special features of WTForms, along with SQLAlchemy, to implement the form editing view. The next bit of complexity comes up when we take into account that different protocols can have different numbers of steps. In other words, we need to create a form that dynamically renders steps with all associated fields. I accomplish this by creating two forms to render the protocol editor: one form called `StepEditor` that creates a form allowing for the editing of a single step, and other form called `ProtocolEditor` that allows for the editing of the entire protocol. Intuitively, the `ProtocolEditor` is composed of a list of several `StepEditor`s. I create this implementation using the special WTForms functionality `FieldList`, which is a form field which consists of a list of `FormFields` which are essentially user-created custom form components (in turn composed of default WTForms form components like `StringField` and `TextAreaField`). I then simply use for loops to render the form on the HTML page.

The final bit of complexity is that we must pre-send some form data to the HTML form to allow the user to edit the existing data in the protocol, while also retrieving the new form data the user writes in. I achieve this by having `GET` and `POST` methods available for the editing route and doing different things when each request method is used. When the `GET` method is used — i.e., when the user clicks a link to edit a protocol — I pass data from the protocol object corresponding to the passed-in protocol ID and from the child step objects into the form. When the `POST` method is used, I retrieve the data from the form and update the Protocol and Step tables. Finally, I log the timestamp at which the edit took place.

##### Viewing protocols
Any self-respecting ELN will let you view all the protocols you create, and the protocol-viewing view allows users to see all their protocols represented cleanly and elegantly, while providing them a hub to edit the steps or add notes. Slab's protocol-viewing view is simple: we pass our current user's steps to the view template; then, using Jinja, we simply render each step as a clickable Bootstrap card (I had to implement this component on my own by editing the typical Bootstrap card). Users can also see when they've created and last edited each protocol. As stated before, timestamp data is stored in UTC but represented in the system's timezone using a custom Jinja filter! This allows for maximum flexibility.

##### What about errors?
I flash all form-related errors using a special helper function (adapted from StackOverflow) along with a dedicated section of base HTML dedicated to flashed messages (so that flashed messages can show up on every page). This allows for simpler communication with the user and circumvents the typical solution of navigating to an apology/error page upon receiving an error, which can be very user-unfriendly.

Using Flask-Login, users who are not logged in and go to protected URLS (who would typically get an unauthorized error) are redirected to the login page. And any other errors are displayed on a dedicated error page. This makes navigating the website easy and user-friendly!

##### Styling
I designed Slab's logo, which appears in the navbar and as the favicon. Slab incorporates vector illustrations from [Vijay Verma](https://illlustrations.co) on main pages for added fun and flair (and does not incorporate illustrations on protocol adding, editing, and viewing pages for maximum seriousness and minimum distraction). Slab uses the Karla font, which I like better than the typical sans-serif.

## Conclusion
Slab is a user-friendly, streamlined, elegant, and simple ELN. I rely on a combination of SQLALchemy, Flask-Login, WTForms, and a few other libraries that work well together to implement several features of Slab, and I create each feature with user-friendliness and real-life use in mind!

## Next Steps
##### Making protocol editing more user-friendly
Users should be able to add and delete steps from their protocols! I would implement this using the existing SQLAlchemy functionality I've put in place, along with WTForms to handle the client-side requests involved. From a database-updating perspective, this should be easy to implement, but one difficulty I anticipate is dynamically rendering the form so that a deleted step disappears and an added step appears! I anticipate needing to add JS functionality to my stack to make this happen.

It might also be nice if viewing and editing protocols occurred in two separate views so that if users wanted to just view a protocol while carrying it out in the lab, they could just do that, instead of having to worry about perhaps accidentally editing their protocol!

##### Version control
Version control for protocols would be hard to implement elegantly considering that in a finished Slab app, steps could be deleted or added at will (so steps in the newest version of a protocol may not line up to steps in the past version). It's still important, though, in a real-life lab setting, to be able to access previous versions of protocols! To accomplish this, I'd have to save all versions of protocols in the Protocol database, make sure protocols line up with past versions of themselves, and add some type of variable denoting current and past protocol versions, and create new views for users to see past versions of protocols. Plus even more functionality to revert to past versions if desired!

##### File uploading
In my initial proposal, I said that I wanted to make it easy for users to upload files that correspond to each step. I didn't realize how heavy of an implementation that would be! I still think this feature would be very useful to real-world adaptations, so to further improve Slab I would like to learn how to use S3, AWS, and/or Firebase to facilitate users' file uploading and accession.

##### Accessibility features
Adding image and HTML component descriptions, making sure illustrations use colorblind-friendly palettes, and investigating support for text-to-speech would help make Slab more accessible.