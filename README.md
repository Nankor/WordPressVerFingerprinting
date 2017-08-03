# WordPressVerFingerprinting
Python for Programmers Course Final Project WordPress Version Fingerprinting
Osman Pamuk
## INTRODUCTION
WordPress is the most used content management (CMS) server in the world, and because of this, it is one of the most attacked CMS by the hackers. The first stage of a cyber-attack is to get more information about the target system, and for a CMS, the version of the CMS is the most valuable information. Because with version number one can see if a CMS is updated or not or if it has a major vulnerability or not. That’s why, for a security researcher to be able to determine the version of a CMS is an important problem. 
There are many tools that are trying to determine the version of a WordPress CMS but many of these tools are only looking for certain keywords in HTTP header information to do that. This method obviously is not a very safe way. Because the HTTP header information can be easily changed and these changes will not affect the way the web server works at all. 
In this project, I implemented a better method to determine the version of a WordPress CMS. Rather than trying to find some keywords in the HTTP response, I am trying to find some specific static web page files (like css, js, png files) on the webserver which are specific to certain WordPress versions. To do that, first, I downloaded all published releases (versions) of WordPress CMS. Second, I extracted the path and md5 information for all files for all versions and stored them on a MySQL database. Third, I implemented an algorithm to determine which web pages to request from the web server, and found an estimated version information. Last, I implemented a restful API as an interface to be able use this system more effectively, for example as an microservice.
## REQUIREMENTS
Python modules that need to be installed:
-	Django
-	Djangorestframework
-	mysql-connector-python
-	lxml
-	httpie (optional to test the restful service)
Also, it needs a MySQL database server.
## DESCRIPTION
### downloadWP.py Module
It downloads all releases of WordPress as zip files from its official web site. To find the download URL addresses, it uses xpath information.  
### processFiles.py Module
This module, first, tries to connect MySQL server’s “cms_files” schema and tries to create a table (“hashes”) if not present. Second, it traverses all zip files (WordPress releases) and extracts path and calculates md5 hashes of all files. Third, it stores all these information to database.
### fingerprinting.py Module
This module is the core module of this project. It has a class name “FingerPrinting”. This class has 9 methods:
#### __init__()
Initialize the instance by connecting the database.
#### md5_content(content)
It is a static method. It just calculates the md5 of the content given as an argument. 
#### getSignificantPaths() 
Query the path of the files that has the most content (and md5) diversity across the releases.  
#### getNextPaths(paths, vers)
Query the path of the files that has the most content (and md5) diversity across the releases for specific versions while excluding previously used paths.
#### getPossibleVers(md5, path)
Query the WordPress versions that has a specific file with a specific content (md5) from the database.
####  checkWebDomain(web_url)
It is a static method. It checks if the given argument is a valid web URL and this URL is related to a working web server.
#### getWebContentHash(web_domain, urlPath)
Gets the content for the given web page URL and calculates the md5 hash of this content. 
#### detect(web_domain)
It is the main method to be called to find the version of a WordPress web server. This method collects the hashes (md5) of the 10 carefully selected web page files and tries to find the possible version candidates with these hashes. 
To select the 10 web files to be requested from the target web server, first, it starts with the web file paths queried by the getSignificantPaths() method. Second, if a web file path is found at the target, it looks for the WordPress versions that has this file with the calculated hash on the database. Third, it queries the new set of web page paths with the getNextPaths() method with previously found versions while excluding previously used web page paths. 
After requesting 10 web pages and collecting possible CMS version candidates, it looks if there is an intersection within the found candidates. If there is, returns these values. If not, it calculates a percentage of possibility for all candidates and return this information. 
#### __del__()
This method is needed to properly close database connection.

### Djongo-Rest Module (wpdetectapp/views.py, wpdetectapp/urls.py, urls.py)
‘urls.py’ and ‘wpdetectapp/urls.py’ just directs the request to view method in the ‘wpdetectapp/views.py’. ‘wpdetectapp/views.py’ has only one view method, detectversion(request). This method parse the request, if it is a post request and it has JSON body with the web domain name which we want to detect its version. If there is one, it creates an instance of FingerPrinting class, and calls detect method. Then, is returns the result in JSON format.
