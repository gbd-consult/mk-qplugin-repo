# mk-qplugin-repo
Create and update a QGIS Plugin Repository 

## Configuration
QGIS does not understand relative paths for the _downloadurl_ tag.
This is why you need to change the URL in the script.

    repoURL = 'http://myawesomepluginrepo.com'

## Directory Structure
The Structure of the repository containing the all important .xml file (that qgis uses to access the Plugins).
The script generates an index.html as well containing a list of the available plugins.
Styling of the .html is done through the style.xsl template.

    .
    └── repo
        ├── style.xsl (template for the index.html)
        ├── index.html (generated automatically)
        ├── plugins.xml (generated automatically)
        └── plugins (put your plugins .zip here)
            ├── awesomeplugin.zip
            └── mediocreplugin.zip

## Usage
To add Plugins to your Repository put the .zip file in the repo/plugins directory and run the script as follows:

    ./mk_qplugin_repo repo
This generates the .xml and .html files.
If you wish to remove a Plugin, just remove it from the repo/plugins directory and run the script again
