# Classic Car Dealer Catalog
This Udacity item catalog project submission has been adapted to the car dealership
business.  In particular is a catalog of classic car dealerships and classic
cars.

## Table of Contents
1. Introduction
2. Basic Requirements
3. Installing and Running the Car Catalog Locally
4. Testing the Car Catalog on Local Web Server
5. Code Verification
6. References

### Introduction
The main categories for this catalog consist of fictitious classic car dealers.
The category items are classic cars.  The catalog has public views that anyone
browsing the catalog can see.  Any user that logs into the catalog can see all
the dealerships and their cars.  Furthermore, logged in users can create a new
dealership and populate it with cars. Logged in users can only perform full
CRUD operations on dealerships and cars they create.  Otherwise they only have
read access.  

Some of the views do not allow editing of cars at all. These are strictly there
to provide different views of the cars in the catalog.  These views are Sedans,
Sports Cars, Coupes and Trucks.  To edit a dealership and its inventory, a
logged in user has to click on a dealership they own in order to see the
dealership's inventory and make the desired changes.

### Basic Requirements
There are some basic requirements for this blog to function properly.  These
requirements assume that you are developing in a Windows 10 environment and
that you are using Git and Git Bash.  They are as follows:

1. Make sure you are connected to the internet.  While there are static
files in directories, some of the methods and scripts are pulled in from the
web.
2. Install Python on your computer; version 2.7 at least.
3. Make sure Git is installed on your Windows 10 machine.  If you don't have
it download it using the following URL: [download Git from git-scm.com.](http://git-scm.com/downloads)
4. Install VirtualBox on your computer. VirtualBox is the software that
actually runs the VM. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Downloads)

5. Install Vagrant. Vagrant is the software that configures the VM and lets you
share files between your host computer and the VM's filesystem.  [You can download it from vagrantup.com.](https://www.vagrantup.com/downloads.html)

### Installing and Running the Car Catalog Locally
After Git, VirtualBox and Vagrant are installed, you are ready to setup the localhost
environment to run the Car Catalog app.  The following steps should complete this
process:

1. Open a Git Bash shell and navigate to the directory where you want to install
the subdirectory for the car catalog application.  You are now ready to fetch
the source code and VM Configuration for the car catalog project. From the
terminal, run:

    git clone https://github.com/ljfarre/car-catalog.git catalog

This will give you a directory named **catalog** complete with the source code for
the flask application, a vagrantfile, and a pg_config.sh file for configuring
the VM environment.  

2. Using the terminal, change directory to catalog (**cd catalog**),
then type **vagrant up** to launch your virtual machine.

3. Once your VM is up and running, type **vagrant ssh**. This will log your
terminal into the virtual machine, and you'll get a Linux shell prompt.  
Change to the /vagrant directory by typing **cd //vagrant**.  Once
there, type **ls** and make sure you are in the directory that contains the Classic
Car Catalog application files.  The directory should contain project.py,
database_setup.py, Vagrantfile, pg_config.sh, lotsofdealers.py, client_secrets.json,
cardealerships.db, README.md and three directories named 'templates', 'static'
and 'oauth2client'.

4. When you are in the /catalog directory, the following commands will setup
your Car Catalog db, populate it with a few dealerships and cars, and launch
the app.  If you want to run the app with the prepopulated test data beyond what is
in the lotsofdealers.py file just skip to the third instruction below.

* type **python database_setup.py** to initialize the database.

* Type **python lotsofdealers.py** to populate the database with dealerships and
cars. (Optional)

* Type **python project.py** to run the Flask web server.

5. To access the app and begin testing, in your browser visit
**http://localhost:5000** to view the Car Catalog app.  You should
be able to view, add, edit, and delete cars and dealerships that you own.

6. When you want to log out, type **exit** at the shell prompt.  To turn the
 virtual machine off (without deleting anything), type **vagrant halt**. If you
 do this, you'll need to run **vagrant up** again before you can log into it.

### Testing the Car Catalog on Local Web Server
Once the Car Catalog has launched successfully, the various functions can be tested.
This application was tested using two Google accounts and the third party
authentication worked well.  The following is a high level test suite:

1. Test the menu functions: All Dealerships, Sedans, Sports Cars, Coupes and
Trucks.
2. Test the Login and logout options.  Login should trigger third party Google
authentication.  If you are logged in to your Google account, you should authenticate
successfully and be able to create new dealerships and new car inventory records.
You should also be able to edit and delete dealerships and car records you created.
All CRUD aoperations should work.
3. Once logged in, test CRUD operation.  Add a dealership, add a car to the
dealership, delete the car and then delete the dealership you created.
All fields are designated as required in the HTML input forms so if you leave a
field blank, you should not be able to save the form and will be prompted to input
something into the blank field.
4. From wherever you are in the catalog, selecting the All Dealership menu option
should take you back to a list of all the dealerships in the catalog.  The
dealership list consists of active links so if you click on a dealership name,
it will take you to the inventory for that dealership.
5. Once in a dealer inventory, you should be able to able to create a new car and
edit existing car records assuming you created the dealership and its inventory.
You should also be able to edit and delete the dealership record.
6. If you did not create a dealership you should only be able to browse the
dealership inventory.
7. The Sedans, Sports Cars, Coupes and Trucks menu options are setup for browsing
only even if you are logged in and authenticated.  All editing must be done
within the dealership inventory context.
8. Test the four JSON functions: /dealership/JSON, /dealership/<int:dealership_id>/inventory/JSON,
/coupes/JSON, /sedans/JSON, /sportscars/JSON, /trucks/JSON, /allcars/JSON
9. Test the footer links to make sure they work.

### Code Verification
Every effort was made to verify the code for this project. The Python code in
project.py was cleaned up and determined to be error free by PEP8 online.  The
HTML template files were checked with Nu Html Checker.  Styles.css file was
verified with W3C css validator.

Within the code proper authentication and authorization methods were used and
should be in line with what was covered in the course material for this project.
There should also be CSRF protection and some rudimentary image handling.  I did
some research on interactively inputting images into and HTML form and then
committing them to a DB as part of a CRUD operation but was not successful.  
A good reference on how to do this would be appreciated.

### References
This catalog was pieced together using Udacity class materials and code from
class assignments only.  For the first time, I created a Git Hub project instance.
You should be able to clone it to your desktop, and it should work properly if
the virtual environment configuration has been setup correctly including all the
required dependencies.
