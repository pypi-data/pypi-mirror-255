{# templates/package_pkg_project.tpl #}

<?xml version="1.0" encoding="utf-8"?>
<?AutomationStudio FileVersion="4.9"?>
<Package Version="1.00.0" xmlns="http://br-automation.co.at/AS/Program">
  <Objects>
    {% for name in system_names %}
    <Object Type="Package" Description="Zones and multizones in the project">{{ name }}</Object>
    {% endfor %}
    <Object Type="File">config.txt</Object>
  </Objects>
</Package>
