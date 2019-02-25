# Item Catalog Project

This is the second project for Udacity's [Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004) program.

Completion of this project demonstrates proficiency with basic CRUD operations through the creation of a database with [SQLAlchemy](https://www.sqlalchemy.org/), running a web server with [Flask](http://flask.pocoo.org/), and sending information to the client using Flask templates.

Users should also be able to login to the website using [Google OAuth 2.0](https://developers.google.com/identity/protocols/OAuth2) to create, edit, and ad their own items.  

For this project, I chose to create a database of skincare products.  They are divided up into categories, and each item lists its name, price, company, and a description.  

## To run project

1. Clone this repo.
2. Download and install [VirtualBox](https://www.virtualbox.org/)
3. Download and install [Vagrant](https://www.vagrantup.com/) to create a virtual Linux environment.
4. Copy this repo into the `vagrant` folder on your machine.
5. Go inside the `vagrant` folder, then type `vagrant up` followed by `vagrant ssh` in your command line
7. Go to app folder by typing `cd /vagrant` then type `cd catalog`
8. Type `database_setup.py` to create the database.
9. Type `catalogitems.py` to populate it with some starter data.  
9. Type `project.py` to initiate the server.
10. Open your browser and go to `http://localhost:5000`

## Dependencies

- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask](http://flask.pocoo.org/)
- [VirtualBox](https://www.virtualbox.org/)
- [Vagrant](https://www.vagrantup.com/)
