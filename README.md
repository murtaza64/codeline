# codeline
A webapp for programmers to post and share Jupyter- and Gist-like code snippet collections accompanied by text and or markdown. Users can view a timeline of all their previous posts (projects, challenges, tutorials etc) and also view public timelines of others.
## features
* a system for posts, containing a title, date, author, and JSON formatted body consisting of cells of either text, markdown or code (in one of many supported languages); either public or private (if private, are visible only in groups they are posted to)
* a system of users, where users can log in to post and view private posts or posts in groups they belong to
* a system of groups, wherein users can post to specific groups if they choose (instead of a general post to their main timeline) and either set posts to public view, where anyone can see that post in the group, or private view, where only logged in group members can see the posts
* a system of tags, where a post can have any number of tags associated with it

* a web based interface that allows you to view posts, with syntax highlighted code and private posts shown/hidden accordingly:
  * as a global timeline
  * as a user's timeline
  * as a group's timeline
  * as a tag's timeline
  * as an individual post

* and submit posts through a responsive form/editor

## implementation plan
I plan to use the Django web framework in combination with several web libraries to develop this app. Django will allow me to build a complex Model-View-Controller webapp with a lot of the process abstracted. For example, Django lets me create complex database structures with link tables without the need for any manual SQL writing - Django models are defined as Python classes. However, under the hood there is still a standard database, just not written directly. Django also has a built in user model with authentication which can be extended for the needs of this app.

The submission form will be an interactive JavaScript enabled page which assembles the post body into the correct JSON format before sending it to the server, with a separate page without JavaScript in which the user can enter the JSON formatted body directly if they wish not to enable scripts.
