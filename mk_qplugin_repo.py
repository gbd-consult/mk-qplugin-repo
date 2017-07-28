# Python script to automatically update a Qgis Plugin Repository

import sys
import os
import hashlib
import ConfigParser
from zipfile import ZipFile
from lxml import etree

# We have to use absolute paths in the XML
repoURL = 'http://localhost:8000'


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def extractMetadata(filename):
    """ Extract the metatata from a zip file
        returns an XML tree node
    """
    zf = ZipFile(filename)
    metadataFile = filter(lambda x: x.endswith('metadata.txt'), zf.namelist())[0]
    metadata = zf.open(metadataFile)

    config = ConfigParser.ConfigParser()
    config.readfp(metadata)

    root = etree.Element('pyqgis_plugin',
            version = config.get('general', 'version'),
            name = config.get('general', 'name'))

    
    values = [  ('description', 'description'),
                ('version', 'version'),
                ('qgisMinimumVersion', 'qgis_minimum_version'),
                ('qgisMaximumVersion', 'qgis_maximum_version'),
                ('author', 'author_name'),
                ('homepage', 'homepage')]

    for (mtd, xml) in values:
        attribute = etree.SubElement(root, xml)
        if config.has_option('general', mtd):
            attribute.text = config.get('general', mtd).decode('utf-8')

    download = etree.SubElement(root, 'download_url')
    download.text = os.path.join(repoURL, 'plugins', os.path.basename(filename))
    
    md5_sum = etree.SubElement(root, 'md5_sum')
    md5_sum.text = md5(filename)

    file_name = etree.SubElement(root, 'file_name')
    file_name.text = os.path.basename(filename)

    return root

def removeDeadEntries(element, pluginDir):
    """ remove Entries with non existent Zip files """
    for child in element:
        filename = child.findtext('file_name')
        if filename \
        and not os.path.exists(os.path.join(pluginDir, filename)):
            print 'Removing Plugin %s because the corresponding .zip file was removed' % child.get('name')
            element.remove(child)
    return element

def fileExists(filename, element):
    """ check if a file with that checksum exists
    in our plugins.xml
    """
    checksums = map(lambda x: x.text, element.xpath('//md5_sum'))
    if md5(filename) in checksums:
        return True
    else:
        return False
        

if __name__ == '__main__':
    repoDir = sys.argv[1]
    pluginDir = os.path.join(repoDir, 'plugins')
    
    if os.path.exists(os.path.join(repoDir, 'plugins.xml')):
        pluginRoot = etree.parse(os.path.join(repoDir, 'plugins.xml')).getroot()
        pluginRoot = removeDeadEntries(pluginRoot, pluginDir)
    else:
        pluginRoot = etree.Element('plugins')

    files = [os.path.join(pluginDir, f) \
            for f in os.listdir(pluginDir) \
            if f.endswith('.zip') \
            and not fileExists(os.path.join(pluginDir, f), pluginRoot)]

    if len(files) > 0:
        print 'Found %d new Plugins!' % len(files)
    else:
        print 'No new Plugins found in "%s", exiting' % repoDir
        exit()

    for f in files:
        print 'Updating Plugin %s ...' % f
        try:
            pluginRoot.append(extractMetadata(f))
        except Exception as e:
            err = type(e).__name__
            print 'ERROR extracting %s:\n\t%s: %s' % (f, err, e)
            z = ZipFile(f)
    transform = etree.XSLT(etree.parse(os.path.join(repoDir, 'style.xsl'))) 
    tree = etree.ElementTree(pluginRoot)
    tree.write(os.path.join(repoDir, 'plugins.xml'),
        xml_declaration=True)
    htmltree = transform(tree)
    htmltree.write(os.path.join(repoDir, 'index.html'))
