{# templates/package_pkg_system.tpl #}

<?xml version="1.0" encoding="utf-8"?>
<?AutomationStudio FileVersion="4.9"?>
<Package xmlns="http://br-automation.co.at/AS/Program">
  <Objects>
    <Object Type="Program" Language="ANSIC" Description="ZoneTask">System</Object>
    <Object Type="Program" Language="ANSIC" Description="ZoneTask">Comm</Object>
    {% for name in zone_names %}
    <Object Type="Program" Language="ANSIC" Description="ZoneTask">{{ name }}</Object>
    {% endfor %}
    <Object Type="File" Description="Global project variables" Private="true">Zone.var</Object>
  </Objects>
</Package>
